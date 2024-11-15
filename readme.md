# Sales Contract Smart Contract

This repository contains a Solidity smart contract designed to facilitate escrow-style transactions between a buyer and a seller, with the possibility of dispute resolution involving a third-party agent. The contract operates with a single token for payments and supports multiple transaction statuses to manage various stages of the transaction lifecycle.

## Contract Overview

The smart contract enables secure transactions between parties, using tokens as payment. It supports the following roles:

- **Buyer**: Purchases the item or service.
- **Seller**: Provides the item or service.
- **Agent**: Third-party mediator for dispute resolution.

### Contract Statuses

The contract uses an `enum` to manage and track different statuses of the transaction. These statuses include:
1. **DEPLOYED**: Initial status upon contract deployment.
2. **FULFILLED**: Indicates that the seller has fulfilled the terms.
3. **EXECUTED**: Transaction is completed, and funds are released to the seller.
4. **DISPUTED**: Dispute has been raised by the buyer.
5. **AGENT_INVITED**: A dispute agent has been called upon.
6. **DISPUTE_FINISHED**: Dispute is resolved, and funds are distributed.

### Constructor Parameters

The constructor takes the following arguments:
- `_tokenAddress`: The token address used for the transaction.
- `_sellerAddress`: Seller’s address.
- `_buyerAddress`: Buyer’s address.
- `_agentAddress`: Dispute resolution agent’s address.
- `_contractAmount`: The amount to be paid for the transaction.
- `_timeExecutionDelta`: The time limit (in seconds) during which the buyer can raise a dispute.

## Functions

The smart contract provides the following functions:

1. **confirmFulfillment**: Called by the seller to confirm the fulfillment of the terms. The contract checks for a minimum token balance to ensure payment is available.
2. **release**: Transfers funds to the seller, available to both buyer and seller with conditional checks for each.
3. **openDispute**: Called by the buyer if they are unsatisfied with the product or service, changing the contract status to `DISPUTED`.
4. **inviteAgent**: Called by the buyer or seller to invite an agent for dispute resolution when in the `DISPUTED` status.
5. **sendMoney**: Used by the agent to allocate funds between the buyer, seller, and themselves based on specified percentages.
6. **returnWrongToken**: Allows the buyer to retrieve any tokens mistakenly sent to the contract that do not match the primary transaction token.
7. **getBalanceOfContract**: Returns the current token balance of the contract for the specified token.

## Modifiers

The contract uses modifiers to enforce access control and check the current status:
- **onlyBuyer**: Ensures that only the buyer can call the function.
- **onlySeller**: Ensures that only the seller can call the function.
- **onlyAgent**: Ensures that only the agent can call the function.
- **onlySellerOrBuyer**: Ensures that only the buyer or seller can call the function.
- **atStatus**: Enforces that a function can only be called when the contract is at a specified status.

## Installation and Deployment

To deploy and interact with the contract, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2. **Install dependencies**:
    This project requires [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/) and a compatible Ethereum development environment such as [Foundry](https://getfoundry.sh/) or [Ape](https://www.apeworx.io/).

3. **Configure environment**:
    Ensure you have the following setup:
    - A compatible ERC-20 token deployed on a test network.
    - Buyer, seller, and agent addresses with access to this network.

4. **Deploy the contract**:
   Use a deployment tool like Foundry or Ape:
    ```bash
    forge create --rpc-url <RPC_URL> --private-key <PRIVATE_KEY> SalesContract --constructor-args <args>
    ```

## Usage Example

1. **Confirm Fulfillment**:
   The seller calls `confirmFulfillment` to mark the terms as fulfilled.

    ```solidity
    salesContract.confirmFulfillment();
    ```

2. **Raise a Dispute**:
   The buyer can call `openDispute` if unsatisfied with the service.

    ```solidity
    salesContract.openDispute();
    ```

3. **Invite Agent**:
   Either the buyer or seller can invite the agent to resolve the dispute.

    ```solidity
    salesContract.inviteAgent();
    ```

4. **Release Funds**:
   Once conditions are met, funds can be released to the seller or distributed by the agent.

    ```solidity
    salesContract.release();
    ```

5. **Return Wrong Tokens**:
   The buyer can retrieve tokens mistakenly sent to the contract.

    ```solidity
    salesContract.returnWrongToken(<tokenAddress>);
    ```

## Testing

We use the [Ape Framework](https://www.apeworx.io/) for testing smart contracts. Follow these steps to set up the environment, install plugins, compile contracts, and run tests.

### Foundry Installation

Foundry is a powerful development toolset for testing and deploying smart contracts. To integrate Foundry with Ape Framework, you need to install it separately.

#### Step 1: Install Foundry

Run the following commands to install Foundry, which includes `forge` and `cast`:

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

#### Step 2: Verify Installation
After installation, check that Foundry tools are installed correctly:

```shell
forge --version
cast --version
```

### Prerequisites

Ensure you have Python 3.8 or later installed on your system. Additionally, install `Ape` globally using `pip`:
```shell
pip install eth-ape
```

### Plugin Installation

Install the necessary Ape plugins for Solidity compilation and testing. Run the following commands:
```shell
ape plugins install .
```

### Verify Foundry Integration with Ape
Check that Foundry is available as a network provider in Ape by running:
```shell
ape networks list
```

### Compilation

To compile the contracts, use the following command:
```shell
ape compile
```

This will generate the necessary artifacts (ABIs, bytecode, etc.) for your contracts.

### Running Tests

Tests are organized using the `pytest` framework. You can run all tests with:

The `Makefile` includes a predefined command for running tests:
```shell
make tests
```

Alternatively, you can manually invoke tests using `ape test`:

### Additional Resources

For more information on Ape Framework testing, refer to the [official documentation](https://docs.apeworx.io/ape/stable/).

## License

This project is licensed under the MIT License.
