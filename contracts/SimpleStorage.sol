// SPDX-License-Identifier: MIT
pragma solidity ^0.8.27;

/**
 * @title SimpleStorage
 * @dev Store & retrieve value in a variable
 */
contract SimpleStorage {
    uint256 private storedData;
    address public owner;

    event ValueChanged(uint256 oldValue, uint256 newValue, address indexed changedBy);

    constructor() {
        owner = msg.sender;
        storedData = 0;
    }

    /**
     * @dev Store value in variable
     * @param x value to store
     */
    function set(uint256 x) public {
        uint256 oldValue = storedData;
        storedData = x;
        emit ValueChanged(oldValue, x, msg.sender);
    }

    /**
     * @dev Return value
     * @return value of 'storedData'
     */
    function get() public view returns (uint256) {
        return storedData;
    }

    /**
     * @dev Increment value by 1
     */
    function increment() public {
        uint256 oldValue = storedData;
        storedData++;
        emit ValueChanged(oldValue, storedData, msg.sender);
    }

    /**
     * @dev Reset value to 0
     */
    function reset() public {
        require(msg.sender == owner, "Only owner can reset");
        uint256 oldValue = storedData;
        storedData = 0;
        emit ValueChanged(oldValue, 0, msg.sender);
    }
}
