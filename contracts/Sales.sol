// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Sales {

    address payable public buyer;
    address payable public seller;
    address public agent;
    address public token;
    uint256 public contractAmount;
    uint32 public timeExecutionDelta;
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
        token = _tokenAddress;
        seller = _sellerAddress;
        buyer = _buyerAddress;
        agent = _agentAddress;
        contractAmount = _contractAmount;
        timeExecutionDelta = _timeExecutionDelta;
        status = Status.DEPLOYED;
    }

    error FunctionInvalidAtThisStatus();

    modifier onlyBuyer {
        require(
            msg.sender == buyer,
            "Only buyer can call this function."
        );
        _;
    }

    modifier onlyAgent {
        require(
            msg.sender == agent,
            "Only agent can call this function."
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

    event DebugTime(uint256 releaseTime, uint256 deploymentTime, uint256 delta);

    function confirmFulfillment() public onlySeller atStatus(Status.DEPLOYED) {
        uint256 balance = IERC20(token).balanceOf(address(this));
        require(balance == contractAmount, 'Not enough tokens on this contract');
        deploymentTime = block.timestamp;
        status = Status.FULFILLED;
    }

    function release() public payable onlySellerOrBuyer {
        uint256 balance = IERC20(token).balanceOf(address(this));
        require(balance == contractAmount, 'Not enough tokens on this contract');
        require(
            status == Status.DEPLOYED || status == Status.FULFILLED || status == Status.DISPUTED,
            "Status can be only DEPLOYED, FULFILLED or DISPUTED"
        );
        if (msg.sender == seller) {
            require(status == Status.FULFILLED, "Seller cannot call the function with status is not equal FULFILLED");
            uint256 releaseTime = block.timestamp;
            emit DebugTime(releaseTime, deploymentTime, releaseTime - deploymentTime);
            require(releaseTime - deploymentTime < timeExecutionDelta, "Save buyer time is not finished yet");
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

    function sendMoney(uint8 agentFeePercent, uint8 buyerFeePercent, uint8 sellerFeePercent) public payable onlyAgent {
        uint256 balance = IERC20(token).balanceOf(address(this));
        require(balance == contractAmount, 'Not enough tokens on this contract');
        require(agentFeePercent + buyerFeePercent + sellerFeePercent == 100, "Percentages must add up to 100");
        uint256 agentFee = balance * agentFeePercent / 100;
        uint256 buyerFee = balance * buyerFeePercent / 100;
        uint256 sellerFee = balance * sellerFeePercent / 100;
        require(IERC20(token).transfer(agent, agentFee), "Transfer failed");
        require(IERC20(token).transfer(buyer, buyerFee), "Transfer failed");
        require(IERC20(token).transfer(seller, sellerFee), "Transfer failed");
        status = Status.DISPUTE_FINISHED;
    }

    function returnWrongToken(address _token) public payable onlyBuyer {
        require(address(token) == address(_token), 'Wrong token address');
        uint256 balance = IERC20(_token).balanceOf(address(this));
        require(balance != 0, 'Not enough tokens');
        require(IERC20(_token).transfer(buyer, balance), "Transfer failed");
    }

    function getBalanceOfContract(address _token) public view returns (uint256 balance) {
        return IERC20(_token).balanceOf(address(this));
    }
}