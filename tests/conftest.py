import pytest


@pytest.fixture
def seller(accounts):
    return accounts[0]


@pytest.fixture
def buyer(accounts):
    return accounts[1]


@pytest.fixture
def agent(accounts):
    return accounts[2]


@pytest.fixture
def test_token(buyer, project):
    initial_supply = 1_000_000 * 10 ** 18
    return buyer.deploy(project.MyTestToken, initial_supply)


@pytest.fixture
def sales_contract(seller, buyer, agent, test_token, project):
    contract_amount = 1000 * 10 ** 18
    time_execution_delta = 86400
    sales_contract = seller.deploy(
        project.Sales,
        test_token.address,
        seller,
        buyer,
        agent,
        contract_amount,
        time_execution_delta
    )
    return sales_contract


@pytest.fixture
def sales_test_contract(seller, buyer, agent, test_token, project):
    # A test contract with public access to deploymentTime for testing purposes
    contract_amount = 1000 * 10 ** 18
    time_execution_delta = 86400
    sales_test_contract = seller.deploy(
        project.SalesTest,
        test_token.address,
        seller,
        buyer,
        agent,
        contract_amount,
        time_execution_delta
    )
    return sales_test_contract


@pytest.fixture
def allocate_tokens_default(test_token, buyer, sales_contract, sales_test_contract):
    contract_amount = 1000 * 10 ** 18
    test_token.transfer(sales_contract, contract_amount, sender=buyer)
    test_token.transfer(sales_test_contract, contract_amount, sender=buyer)


@pytest.fixture
def allocate_tokens_factory(test_token, buyer, sales_contract):
    def _allocate_tokens(contract_amount=None):
        contract_amount = contract_amount or 1000 * 10 ** 18
        test_token.transfer(sales_contract, contract_amount, sender=buyer)
    return _allocate_tokens