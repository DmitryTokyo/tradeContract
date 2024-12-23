// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Sales {

    address public immutable buyer;
    address public immutable seller;
    address public immutable agent;
    address public immutable token;
    uint256 public immutable contractAmount;
    uint32 public immutable timeExecutionDelta;
    uint256 internal deploymentTime;

    enum Status {
        DEPLOYED,
        FULFILLED,
        EXECUTED,
        DISPUTED,
        AGENT_INVITED,
        DISPUTE_FINISHED
    }
    Status public status;

    constructor (
        address _tokenAddress, 
        address payable _sellerAddress, 
        address payable _buyerAddress,
        address _agentAddress,
        uint256 _contractAmount,
        uint32 _timeExecutionDelta
        ) {
        require(isContract(_tokenAddress), "Token address must be a contract");
        token = _tokenAddress;
        seller = _sellerAddress;
        buyer = _buyerAddress;
        agent = _agentAddress;
        contractAmount = _contractAmount;
        timeExecutionDelta = _timeExecutionDelta;
        status = Status.DEPLOYED;
    }

    function isContract(address _addr) internal view returns (bool) {
        uint256 size;
        assembly {
            size := extcodesize(_addr)
        }
        return size > 0;
    }

    error FunctionInvalidAtThisStatus();

    modifier onlyBuyer {
        require(
            msg.sender == buyer,
            "Only buyer can call this function."
        );
        _;
    }

    modifier onlySeller {
        require(
            msg.sender == seller,
            "Only seller can call this function."
        );
        _;
    }

    modifier onlySellerOrBuyer {
        require(
            msg.sender == seller || msg.sender == buyer,
            "Only seller or buyer can call this function."
        );
        _;
    }

    modifier atStatus(Status status_) {
        if (status != status_)
            revert FunctionInvalidAtThisStatus();
        _;
    }

    function confirmFulfillment() public onlySeller atStatus(Status.DEPLOYED) {
        uint256 balance = IERC20(token).balanceOf(address(this));
        require(balance >= contractAmount, 'Not enough tokens on this contract');
        deploymentTime = block.timestamp;
        status = Status.FULFILLED;
    }

    function release() public onlySellerOrBuyer {
        uint256 balance = IERC20(token).balanceOf(address(this));
        require(balance >= contractAmount, 'Not enough tokens on this contract');
        require(
            status == Status.DEPLOYED || status == Status.FULFILLED || status == Status.DISPUTED,
            "Status can be only DEPLOYED, FULFILLED or DISPUTED"
        );
        if (msg.sender == seller) {
            require(status == Status.FULFILLED, "Seller cannot call the function with status is not equal FULFILLED");
            require(block.timestamp - deploymentTime > timeExecutionDelta, "Save buyer time is not finished yet");
        }
        require(IERC20(token).transfer(seller, balance), "Transfer failed");
        status = Status.EXECUTED;
    }

    function openDispute() public onlyBuyer atStatus(Status.FULFILLED){
        status = Status.DISPUTED;
    }

    function inviteAgent() public onlySellerOrBuyer atStatus(Status.DISPUTED){
        status = Status.AGENT_INVITED;
    }

    function sendMoney(uint8 agentFeePercent, uint8 buyerFeePercent, uint8 sellerFeePercent) public atStatus(Status.AGENT_INVITED){
        require(msg.sender == agent, "Only agent can call this function.");
        require(0 < agentFeePercent && agentFeePercent <= 3, "Agent fee percent must be between 1 and 3 inclusive");
        uint256 balance = IERC20(token).balanceOf(address(this));
        require(balance >= contractAmount, 'Not enough tokens on this contract');
        require(agentFeePercent + buyerFeePercent + sellerFeePercent == 100, "Percentages must add up to 100");
        uint256 agentFee = contractAmount * agentFeePercent / 100;
        uint256 buyerFee = contractAmount * buyerFeePercent / 100;
        uint256 sellerFee = contractAmount * sellerFeePercent / 100;
        require(IERC20(token).transfer(agent, agentFee), "Transfer failed");
        require(IERC20(token).transfer(buyer, buyerFee), "Transfer failed");
        require(IERC20(token).transfer(seller, sellerFee), "Transfer failed");
        status = Status.DISPUTE_FINISHED;
    }

    function returnWrongToken(address _token) public onlyBuyer {
        require(address(token) != address(_token), "Cannot return the primary contract token");
        uint256 balance = IERC20(_token).balanceOf(address(this));
        require(balance > 0, "No balance available for the provided token");
        require(IERC20(_token).transfer(buyer, balance), "Transfer failed");
    }

    function getBalanceOfContract(address _token) public view returns (uint256 balance) {
        return IERC20(_token).balanceOf(address(this));
    }
}