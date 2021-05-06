import json
from collections import defaultdict
from typing import Dict

import pkg_resources

from network_analyzer.csv_export import export_bridge_information_as_csv

HOME_BRIDGE_CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000401"


def load_contracts_json(path="contracts.json") -> Dict:

    with open(pkg_resources.resource_filename(__name__, path)) as file:
        return json.load(file)


class Analyzer:
    def __init__(self, web3, output_path):
        self.web3 = web3
        self.output_path = output_path
        self.contracts_dict = load_contracts_json()

        self.home_bridge_contract = self.web3.eth.contract(
            abi=self.contracts_dict["HomeBridge"]["abi"],
            bytecode=self.contracts_dict["HomeBridge"]["bytecode"],
            address=HOME_BRIDGE_CONTRACT_ADDRESS,
        )

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

        export_bridge_information_as_csv(
            completed_transfers=completed_transfers,
            value_transferred=value_transferred,
            pending_transfers=pending_transfers,
            output_path=self.output_path,
        )
