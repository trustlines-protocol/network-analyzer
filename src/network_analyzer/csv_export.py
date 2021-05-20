import csv
from typing import List

TLC_DIVISOR = 10 ** 18

OUTPUT_FILE_BRIDGE = "bridge_information.csv"


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
    *,
    network_information_dictionary: dict,
    user_dictionaries: List,
    transfer_dictionaries: List,
    output_path: str = None,
):
    network_address = network_information_dictionary["Address"]
    file_name = f"currency_networks-{network_address}.csv"
    if output_path is None:
        output_path = file_name
    else:
        output_path += "/" + file_name

    with open(output_path, "w+", newline="") as csvfile:

        writer = csv.writer(csvfile)
        writer.writerow(["Currency network infos"])

        dict_writer = csv.DictWriter(
            csvfile, fieldnames=network_information_dictionary.keys()
        )
        dict_writer.writeheader()
        dict_writer.writerow(network_information_dictionary)

        if len(user_dictionaries) >= 1:
            writer.writerow([])
            writer.writerow(["User list"])
            dict_writer = csv.DictWriter(
                csvfile, fieldnames=user_dictionaries[0].keys()
            )
            dict_writer.writeheader()
            for user_dictionary in user_dictionaries:
                dict_writer.writerow(user_dictionary)

        if len(transfer_dictionaries) >= 1:
            writer.writerow([])
            writer.writerow(["Transfer list"])
            dict_writer = csv.DictWriter(
                csvfile, fieldnames=transfer_dictionaries[0].keys()
            )
            dict_writer.writeheader()
            for transfer_dictionary in transfer_dictionaries:
                dict_writer.writerow(transfer_dictionary)
