import ape
import pytest


def test_initial_contract_status(sales_contract, test_token, buyer, seller):
    assert sales_contract.buyer() == buyer
    assert sales_contract.seller() == seller
    assert sales_contract.token() == test_token.address
    assert sales_contract.contractAmount() == 1000 * 10 ** 18
    assert sales_contract.timeExecutionDelta() == 86400
    assert sales_contract.status() == 0


def test_confirm_fulfilment_successfully(sales_contract, seller, allocate_tokens_default):
    tx = sales_contract.confirmFulfillment(sender=seller)
    assert tx is not None
    assert sales_contract.status() == 1


def test_confirm_fulfillment_with_fixed_time(sales_test_contract, seller, allocate_tokens_default, test_token):
    sales_test_contract.confirmFulfillment(sender=seller)
    deployment_time = sales_test_contract.getDeploymentTime()
    assert deployment_time == ape.chain.blocks[-1].timestamp


def test_confirm_fulfillment_restricted_to_seller(sales_contract, buyer, allocate_tokens_default):
    with pytest.raises(Exception, match='Only seller can call this function.'):
        sales_contract.confirmFulfillment(sender=buyer)


def test_confirm_fulfilment_failed_by_wrong_status(sales_contract, seller, allocate_tokens_default):
    sales_contract.confirmFulfillment(sender=seller)
    with pytest.raises(Exception, match='Transaction failed.'):
        sales_contract.confirmFulfillment(sender=seller)


def test_confirm_fulfilment_failed_by_small_amount(sales_contract, seller, allocate_tokens_factory):
    allocate_tokens_factory(1)
    with pytest.raises(Exception, match='Not enough tokens on this contract'):
        sales_contract.confirmFulfillment(sender=seller)


def test_release_called_seller_successfully(sales_test_contract, seller, allocate_tokens_default, chain):
    sales_test_contract.confirmFulfillment(sender=seller)
    deployment_time = sales_test_contract.getDeploymentTime()
    time_execution_delta = 86400
    chain.provider.set_timestamp(deployment_time + time_execution_delta + 10)
    chain.mine()
    sales_test_contract.release(sender=seller)
    assert sales_test_contract.status() == 2


def test_release_called_buyer_successfully_with_initial_deploy_status(sales_contract, buyer, allocate_tokens_default):
    assert sales_contract.status() == 0
    sales_contract.release(sender=buyer)
    assert sales_contract.status() == 2


def test_release_called_buyer_successfully_with_initial_fulfilled_status(
    sales_contract, buyer, allocate_tokens_default, seller,
):
    sales_contract.confirmFulfillment(sender=seller)
    sales_contract.release(sender=buyer)
    assert sales_contract.status() == 2


def test_release_called_buyer_successfully_with_initial_disputed_status(
    sales_contract, buyer, allocate_tokens_default, seller,
):
    sales_contract.confirmFulfillment(sender=seller)
    sales_contract.openDispute(sender=buyer)
    sales_contract.release(sender=buyer)
    assert sales_contract.status() == 2


def test_release_called_with_not_enough_balance(sales_contract, buyer, allocate_tokens_factory):
    allocate_tokens_factory(1)
    with pytest.raises(Exception, match='Not enough tokens on this contract'):
        sales_contract.release(sender=buyer)


def test_release_called_with_not_acceptable_status(sales_contract, buyer, allocate_tokens_default, seller, agent):
    sales_contract.confirmFulfillment(sender=seller)
    sales_contract.openDispute(sender=buyer)
    sales_contract.inviteAgent(sender=buyer)
    with pytest.raises(Exception, match='Status can be only DEPLOYED, FULFILLED or DISPUTED'):
        sales_contract.release(sender=buyer)


def test_release_called_with_not_acceptable_status_for_seller(sales_contract, allocate_tokens_default, seller, buyer):
    sales_contract.confirmFulfillment(sender=seller)
    sales_contract.openDispute(sender=buyer)
    with pytest.raises(Exception, match='Seller cannot call the function with status is not equal FULFILLED'):
        sales_contract.release(sender=seller)


def test_release_buyer_time_not_finished(sales_test_contract, seller, allocate_tokens_default, chain):
    sales_test_contract.confirmFulfillment(sender=seller)
    deployment_time = sales_test_contract.getDeploymentTime()
    time_execution_delta = 86400
    chain.provider.set_timestamp(deployment_time + time_execution_delta - 10)
    with pytest.raises(Exception, match="Save buyer time is not finished yet"):
        sales_test_contract.release(sender=seller)


def test_open_dispute_called_successfully(sales_contract, allocate_tokens_default, seller, buyer):
    sales_contract.confirmFulfillment(sender=seller)
    sales_contract.openDispute(sender=buyer)
    assert sales_contract.status() == 3


def test_open_dispute_called_wrong_by_seller(sales_contract, allocate_tokens_default, seller, buyer):
    sales_contract.confirmFulfillment(sender=seller)
    with pytest.raises(Exception, match="Only buyer can call this function."):
        sales_contract.openDispute(sender=seller)


def test_open_dispute_called_by_wrong_status(sales_contract, allocate_tokens_default, buyer):
    with pytest.raises(Exception):
        sales_contract.openDispute(sender=buyer)


def test_invite_agent_called_successfully(sales_contract, allocate_tokens_default, seller, buyer):
    sales_contract.confirmFulfillment(sender=seller)
    sales_contract.openDispute(sender=buyer)
    sales_contract.inviteAgent(sender=buyer)
    assert sales_contract.status() == 4


def test_invite_agent_called_wrong_by_seller(sales_contract, allocate_tokens_default, seller, agent):
    sales_contract.confirmFulfillment(sender=seller)
    with pytest.raises(Exception, match="Only seller or buyer can call this function."):
        sales_contract.inviteAgent(sender=agent)


def test_invite_agent_called_by_wrong_status(sales_contract, allocate_tokens_default, seller):
    sales_contract.confirmFulfillment(sender=seller)
    with pytest.raises(Exception):
        sales_contract.inviteAgent(sender=seller)


def test_send_money_success(sales_contract, allocate_tokens_factory, test_token, agent, buyer, seller):
    allocate_tokens_factory(1000 * 10 ** 18)
    sales_contract.confirmFulfillment(sender=seller)
    sales_contract.openDispute(sender=buyer)
    sales_contract.inviteAgent(sender=buyer)
    agent_fee_percent = 2
    buyer_fee_percent = 48
    seller_fee_percent = 50

    initial_agent_balance = test_token.balanceOf(agent.address)
    initial_buyer_balance = test_token.balanceOf(buyer.address)
    initial_seller_balance = test_token.balanceOf(seller.address)
    contract_balance = test_token.balanceOf(sales_contract.address)
    assert contract_balance == 1000 * 10 ** 18

    sales_contract.sendMoney(agent_fee_percent, buyer_fee_percent, seller_fee_percent, sender=agent)
    final_contract_balance = test_token.balanceOf(sales_contract.address)
    assert final_contract_balance == 0

    expected_agent_balance = initial_agent_balance + (contract_balance * agent_fee_percent // 100)
    expected_buyer_balance = initial_buyer_balance + (contract_balance * buyer_fee_percent // 100)
    expected_seller_balance = initial_seller_balance + (contract_balance * seller_fee_percent // 100)

    assert test_token.balanceOf(agent.address) == expected_agent_balance
    assert test_token.balanceOf(buyer.address) == expected_buyer_balance
    assert test_token.balanceOf(seller.address) == expected_seller_balance
    assert sales_contract.status() == 5


def test_send_money_invalid_percentages(sales_contract, allocate_tokens_default, agent, buyer, seller):
    sales_contract.confirmFulfillment(sender=seller)
    sales_contract.openDispute(sender=buyer)
    sales_contract.inviteAgent(sender=buyer)
    with pytest.raises(Exception, match="Percentages must add up to 100"):
        sales_contract.sendMoney(2, 48, 49, sender=agent)


@pytest.mark.parametrize(
    'agent_percentage',
    [
        0, 10,
    ],
)
def test_send_money_invalid_percentages_amount_for_agent(
    sales_contract, allocate_tokens_default, agent, agent_percentage, buyer, seller,
):
    sales_contract.confirmFulfillment(sender=seller)
    sales_contract.openDispute(sender=buyer)
    sales_contract.inviteAgent(sender=buyer)
    with pytest.raises(Exception, match="Agent fee percent must be between 1 and 3 inclusive"):
        sales_contract.sendMoney(agent_percentage, 40, 49, sender=agent)
