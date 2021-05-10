import csv
from typing import List

TLC_DIVISOR = 10 ** 18

OUTPUT_FILE_BRIDGE = "bridge_information.csv"
OUTPUT_FILE_CURRENCY_NETWORK = "currency_networks.csv"


def export_bridge_information(
    *, completed_transfers, value_transferred, pending_transfers, output_path=None
):
    if output_path is None:
        output_path = OUTPUT_FILE_BRIDGE
    else:
        output_path += "/" + OUTPUT_FILE_BRIDGE

    with open(output_path, "w+", newline="") as csvfile:

        writer = csv.writer(csvfile)
        writer.writerow(["Completed Bridge Transfers"])
        writer.writerow(["Initiator", "Total value"])

        for initiator in value_transferred.keys():
            writer.writerow([initiator, value_transferred[initiator] / TLC_DIVISOR])

        writer.writerow(
            ["Total number of different addresses", len(value_transferred.keys())]
        )
        writer.writerow(
            ["Total number of different transfers", len(completed_transfers)]
        )
        writer.writerow(
            [
                "Total value transferred",
                sum(
                    [
                        initiator_value_tuple[1]
                        for initiator_value_tuple in value_transferred.items()
                    ]
                )
                / TLC_DIVISOR,
            ]
        )

        writer.writerow([])
        writer.writerow(
            ["Pending Bridge Transfers (confirmed by at least 1 validator)"]
        )
        writer.writerow(["Initiator", "value", "transaction hash"])
        for pending_transfer in pending_transfers.values():
            writer.writerow(
                [
                    pending_transfer.recipient,
                    pending_transfer.amount / TLC_DIVISOR,
                    pending_transfer.transactionHash.hex(),
                ]
            )
        writer.writerow(["Total number of pending transfers", len(pending_transfers)])


def export_currency_network_information(
    *, information_dictionaries: List, output_path: str = None
):
    if output_path is None:
        output_path = OUTPUT_FILE_CURRENCY_NETWORK
    else:
        output_path += "/" + OUTPUT_FILE_CURRENCY_NETWORK

    with open(output_path, "w+", newline="") as csvfile:

        writer = csv.writer(csvfile)
        writer.writerow(["Currency network infos"])

        if len(information_dictionaries) != 0:
            dict_writer = csv.DictWriter(
                csvfile, fieldnames=information_dictionaries[0].keys()
            )
            dict_writer.writeheader()
            for dict in information_dictionaries:
                dict_writer.writerow(dict)
