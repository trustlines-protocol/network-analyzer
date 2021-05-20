import json
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict

import click
import pkg_resources
import requests
from web3 import Web3

from network_analyzer.csv_export import (
    export_bridge_information,
    export_currency_network_information,
)
from network_analyzer.netwrok_graph import CurrencyNetworkGraph

HOME_BRIDGE_CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000401"
IDENTITY_PROXY_FACTORY_ADDRESS = "0x43e7ed7F5bcc0beBE8758118fae8609607CD874f"


def load_contracts_json(path="contracts.json") -> Dict:

    with open(pkg_resources.resource_filename(__name__, path)) as file:
        return json.load(file)


class Analyzer:
    def __init__(self, jsonrpc, output_path, relay_api_url):
        self.web3 = Web3(Web3.HTTPProvider(jsonrpc, request_kwargs={"timeout": 180}))
        self.output_path = output_path
        self.contracts_dict = load_contracts_json()
        self.relay_api_url = relay_api_url

        self.home_bridge_contract = self.web3.eth.contract(
            abi=self.contracts_dict["HomeBridge"]["abi"],
            bytecode=self.contracts_dict["HomeBridge"]["bytecode"],
            address=HOME_BRIDGE_CONTRACT_ADDRESS,
        )
        self.identity_factory_contract = self.web3.eth.contract(
            abi=self.contracts_dict["IdentityProxyFactory"]["abi"],
            bytecode=self.contracts_dict["IdentityProxyFactory"]["bytecode"],
            address=IDENTITY_PROXY_FACTORY_ADDRESS,
        )

        self.graphs: Dict[str, CurrencyNetworkGraph] = {}

    def analyze_bridge_transfers(self):

        transfer_completed_events = self.home_bridge_contract.events.TransferCompleted.getLogs(
            fromBlock=0
        )
        confirmation_events = self.home_bridge_contract.events.Confirmation.getLogs(
            fromBlock=0
        )

        completed_transfers = [event["args"] for event in transfer_completed_events]
        confirmations = [
            confirmation_event["args"] for confirmation_event in confirmation_events
        ]

        value_transferred = defaultdict(lambda: 0)
        confirmed_hashs = set()
        for transfer in completed_transfers:
            value_transferred[transfer.recipient] += transfer.amount
            confirmed_hashs.add(transfer.transferHash)

        pending_transfers = dict()
        for confirmation in confirmations:
            if confirmation.transferHash not in confirmed_hashs.union(
                pending_transfers.keys()
            ):
                pending_transfers[confirmation.transferHash] = confirmation

        export_bridge_information(
            completed_transfers=completed_transfers,
            value_transferred=value_transferred,
            pending_transfers=pending_transfers,
            output_path=self.output_path,
        )

    def analyze_networks(self):
        networks_list = self.request_relay_api("networks")

        for network in networks_list:
            network_address = network["address"]

            network_graph = CurrencyNetworkGraph(
                capacity_imbalance_fee_divisor=100,  # TODO: The endpoint of the relay does not return the actual value
                default_interest_rate=network["defaultInterestRate"],
                prevent_mediator_interests=network["preventMediatorInterests"],
            )
            self.graphs[network_address] = network_graph

            trustlines = self.request_relay_api(
                f"networks/{network_address}/trustlines"
            )
            network_graph.generate_graph(trustlines)
            transfer_events = self.request_relay_api(
                f"networks/{network_address}/events?type=Transfer"
            )

            info_dictionary = build_network_info_dictionary(
                network, network_graph, transfer_events
            )
            user_dictionaries = self.build_user_dictionaries(network)
            transfer_dictionaries = self.build_transfer_dictionaries(
                network, transfer_events
            )

            export_currency_network_information(
                network_information_dictionary=info_dictionary,
                user_dictionaries=user_dictionaries,
                transfer_dictionaries=transfer_dictionaries,
            )

    def request_relay_api(self, endpoint):
        return requests.get(self.relay_api_url + "/" + endpoint).json()

    def build_user_dictionaries(self, network):
        user_lists = self.request_relay_api(f"networks/{network['address']}/users")
        user_dictionaries = []
        for user in user_lists:
            user_details = self.request_relay_api(
                f"networks/{network['address']}/users/{user}"
            )
            user_dictionary = {
                "user": user,
                "credit limits given": int(user_details["given"])
                / 10 ** network["decimals"],
                "credit limits received": int(user_details["received"])
                / 10 ** network["decimals"],
                "balance": int(user_details["balance"]) / 10 ** network["decimals"],
            }
            user_dictionaries.append(user_dictionary)
        return user_dictionaries

    def build_transfer_dictionaries(self, network, transfer_events):
        transfer_dictionaries = []
        for transfer_event in transfer_events:
            transfer_dictionary = {
                "transaction hash": transfer_event["transactionHash"],
                "sender": transfer_event["from"],
                "recipient": transfer_event["to"],
                "amount": int(transfer_event["amount"]) / 10 ** network["decimals"],
                "date": datetime.fromtimestamp(transfer_event["timestamp"]),
                "time": transfer_event["timestamp"],
            }
            transfer_dictionaries.append(transfer_dictionary)
        return transfer_dictionaries

    def analyze_dead_identities(self):

        identity_addresses = set()
        identity_deployment_events = self.identity_factory_contract.events.ProxyDeployment.getLogs(
            fromBlock=0
        )
        for identity_deployment_event in identity_deployment_events:
            identity_addresses.add(identity_deployment_event["args"]["proxyAddress"])

        users_that_have_a_trustlines = set()
        networks_list = self.request_relay_api("networks")
        for network in networks_list:
            network_address = network["address"]
            trustlines = self.request_relay_api(
                f"networks/{network_address}/trustlines"
            )
            for trustline in trustlines:
                users_that_have_a_trustlines.add(trustline["user"])
                users_that_have_a_trustlines.add(trustline["counterParty"])

        identities_with_no_trustlines = (
            identity_addresses - users_that_have_a_trustlines
        )

        click.echo(
            f"Number of identities with no trustlines: {len(identities_with_no_trustlines)}"
        )


def build_network_info_dictionary(network, network_graph, transfer_events):

    current_time = time.time()
    one_month = 30 * 24 * 3600
    transfer_events_last_month = filter_events_for_time_window(
        transfer_events, current_time - one_month, current_time
    )

    return {
        "Name": network["name"],
        "Address": network["address"],
        "Is network frozen": network["isFrozen"],
        "Number of users": network["numUsers"],
        "Average number of people connected within one hop": network_graph.average_degree_of_power(
            1
        ),
        "Average number of people connected within two hops": network_graph.average_degree_of_power(
            2
        ),
        "Average number of people connected within three hops": network_graph.average_degree_of_power(
            3
        ),
        "Average number of people connected within four hops": network_graph.average_degree_of_power(
            4
        ),
        "Average number of people connected within five hops": network_graph.average_degree_of_power(
            5
        ),
        "Average number of people connected within six hops": network_graph.average_degree_of_power(
            6
        ),
        "Minimal number of trustlines of a user": network_graph.calculate_min_degree(),
        "Maximal number of trustlines of a user": network_graph.calculate_max_degree(),
        "Number of users with 3 or more trustlines": network_graph.number_of_vertex_of_degree_at_least(
            3
        ),
        "Total number of transfers": len(transfer_events),
        "Number of transfers last month": len(transfer_events_last_month),
        "Number of different transfer initiators": number_of_transfer_initiators(
            transfer_events
        ),
        "Number of different transfer initiators last month": number_of_transfer_initiators(
            transfer_events_last_month
        ),
        "Total amount transferred": total_value_transferred(transfer_events)
        / 10 ** network["decimals"],
        "Total amount transferred last month": total_value_transferred(
            transfer_events_last_month
        )
        / 10 ** network["decimals"],
        "Average value transferred": average_value_transferred(transfer_events)
        / 10 ** network["decimals"],
        "Average value transferred last month": average_value_transferred(
            transfer_events
        )
        / 10 ** network["decimals"],
    }


def number_of_transfer_initiators(transfer_events):
    different_initiators = set()
    for transfer_event in transfer_events:
        different_initiators.add(transfer_event["from"])
    return len(different_initiators)


def total_value_transferred(transfer_events):
    total_value_transferred = 0
    for transfer_event in transfer_events:
        total_value_transferred += int(transfer_event["amount"])
    return total_value_transferred


def average_value_transferred(transfer_events):
    if len(transfer_events) == 0:
        return 0
    return total_value_transferred(transfer_events) / len(transfer_events)


def filter_events_for_time_window(events, start_time, end_time):

    filtered = []
    for event in events:
        if event["timestamp"] >= start_time and event["timestamp"] <= end_time:
            filtered.append(event)
    return filtered
