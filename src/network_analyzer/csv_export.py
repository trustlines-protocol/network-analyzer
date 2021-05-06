import csv

TLC_DIVISOR = 10 ** 18

OUTPUT_FILE_BRIDGE = "bridge_information.csv"


def export_bridge_information_as_csv(
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
