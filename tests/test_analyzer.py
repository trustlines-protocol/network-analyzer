import pytest

from network_analyzer.analyzer import Analyzer
from network_analyzer.csv_export import OUTPUT_FILE_BRIDGE, TLC_DIVISOR

ZERO_ADDRESS = "0x" + "0" * 40


@pytest.fixture(scope="session")
def temporary_path(tmpdir_factory):
    return tmpdir_factory.getbasetemp()


@pytest.fixture(scope="session")
def analyzer(web3, bridge_contract, temporary_path):
    analyzer = Analyzer(web3, temporary_path)
    # replace the hard coded address of the bridge to the one of the test bridge
    analyzer.home_bridge_contract = web3.eth.contract(
        abi=analyzer.contracts_dict["HomeBridge"]["abi"],
        bytecode=analyzer.contracts_dict["HomeBridge"]["bytecode"],
        address=bridge_contract.address,
    )
    return analyzer


@pytest.fixture(scope="session")
def transfer_1(accounts):
    return {
        "initiator": accounts[1],
        "amount": int(123.456 * 10 ** 18),
        "transaction_hash": bytes.fromhex(
            "0000000000000000000000000000000000000000000000000000000000001234"
        ),
        "transfer_hash": "1234000000000000000000000000000000000000000000000000000000000000",
    }


@pytest.fixture(scope="session")
def transfer_2(accounts):
    return {
        "initiator": accounts[2],
        "amount": int(100 * 10 ** 18),
        "transaction_hash": bytes.fromhex(
            "00000000000000000000000000000000000000000000000000000000dcbaabcd"
        ),
        "transfer_hash": "dcbaabcd00000000000000000000000000000000000000000000000000000000",
    }


@pytest.fixture(scope="session")
def transfer_3(accounts):
    return {
        "initiator": accounts[1],
        "amount": int(321 * 10 ** 18),
        "transaction_hash": bytes.fromhex(
            "00000000000000000000000000000000000000000000000000000000deadbeef"
        ),
        "transfer_hash": "deadbeef00000000000000000000000000000000000000000000000000000000",
    }


@pytest.fixture(scope="session")
def transfers(transfer_1, transfer_2, transfer_3):
    return [transfer_1, transfer_2, transfer_3]


@pytest.fixture()
def bridge_with_pending_transfer(bridge_contract, transfers):
    for transfer in transfers:
        bridge_contract.functions.emitConfirmation(
            transfer["transfer_hash"],
            transfer["transaction_hash"],
            transfer["amount"],
            transfer["initiator"],
            ZERO_ADDRESS,
        ).transact()
    return bridge_contract


@pytest.fixture()
def bridge_with_completed_transfers(bridge_contract, transfers):
    for transfer in transfers:
        bridge_contract.functions.emitTransferCompleted(
            transfer["transfer_hash"],
            transfer["transaction_hash"],
            transfer["amount"],
            transfer["initiator"],
        ).transact()
    return bridge_contract


def assert_similar_strings(string_1, string_2):
    """Assert that the string are equal to the exception of white spaces and new lines"""
    assert string_1.translate({ord(" "): None, ord("\n"): None}) == string_2.translate(
        {ord(" "): None, ord("\n"): None}
    )


@pytest.mark.usefixtures("bridge_with_pending_transfer")
def test_bridge_analysis_pending_transfer(analyzer, transfers, temporary_path):
    expected_result = f"""
    Completed Bridge Transfers
    Initiator,Total value
    Total number of different addresses,0
    Total number of different transfers,0
    Total value transferred,0.0

    Pending Bridge Transfers (confirmed by at least 1 validator)
    Initiator,value,transaction hash
    {transfers[0]['initiator']}, {transfers[0]["amount"] / TLC_DIVISOR}, {transfers[0]['transaction_hash'].hex()}
    {transfers[1]['initiator']}, {transfers[1]["amount"] / TLC_DIVISOR}, {transfers[1]['transaction_hash'].hex()}
    {transfers[2]['initiator']}, {transfers[2]["amount"] / TLC_DIVISOR}, {transfers[2]['transaction_hash'].hex()}
    Total number of pending transfers,3
    """

    analyzer.analyze_bridge_transfers()

    with open(temporary_path / OUTPUT_FILE_BRIDGE) as csvfile:
        analyzer_result = csvfile.read()

    assert_similar_strings(expected_result, analyzer_result)


@pytest.mark.usefixtures("bridge_with_completed_transfers")
def test_bridge_analysis_completed_transfer(analyzer, transfers, temporary_path):
    expected_result = f"""
    Completed Bridge Transfers
    Initiator,Total value
    {transfers[0]['initiator']}, {(transfers[0]["amount"] + transfers[2]["amount"]) / TLC_DIVISOR}
    {transfers[1]['initiator']}, {transfers[1]["amount"] / TLC_DIVISOR}
    Total number of different addresses, 2
    Total number of different transfers, 3
    Total value transferred, {sum([transfer["amount"] for transfer in transfers]) / TLC_DIVISOR}

    Pending Bridge Transfers (confirmed by at least 1 validator)
    Initiator,value,transaction hash
    Total number of pending transfers,0
    """

    analyzer.analyze_bridge_transfers()

    with open(temporary_path / OUTPUT_FILE_BRIDGE) as csvfile:
        analyzer_result = csvfile.read()

    assert_similar_strings(expected_result, analyzer_result)
