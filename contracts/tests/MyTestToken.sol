// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyTestToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("MyTestToken", "MTT") {
        _mint(msg.sender, initialSupply);
    }
}