// SalesTest.sol
pragma solidity ^0.8.0;

import "../Sales.sol";

contract SalesTest is Sales {
    constructor(
        address _tokenAddress,
        address payable _sellerAddress,
        address payable _buyerAddress,
        address _agentAddress,
        uint256 _contractAmount,
        uint32 _timeExecutionDelta
    ) Sales(_tokenAddress, _sellerAddress, _buyerAddress, _agentAddress, _contractAmount, _timeExecutionDelta) {}

    function getDeploymentTime() external view returns (uint256) {
        return deploymentTime;
    }
}
