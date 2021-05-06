import pytest


@pytest.fixture(scope="session")
def bridge_contract(deploy_contract):
    return deploy_contract("TestHomeBridge")
