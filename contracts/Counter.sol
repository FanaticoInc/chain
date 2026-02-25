// SPDX-License-Identifier: MIT
pragma solidity ^0.8.27;

/**
 * @title Counter
 * @dev Simple counter contract with increment and decrement
 */
contract Counter {
    int256 private count;
    address public owner;

    event CountChanged(int256 oldCount, int256 newCount, string operation);

    constructor(int256 initialCount) {
        owner = msg.sender;
        count = initialCount;
        emit CountChanged(0, initialCount, "initialized");
    }

    function increment() public returns (int256) {
        int256 oldCount = count;
        count++;
        emit CountChanged(oldCount, count, "increment");
        return count;
    }

    function decrement() public returns (int256) {
        int256 oldCount = count;
        count--;
        emit CountChanged(oldCount, count, "decrement");
        return count;
    }

    function incrementBy(int256 value) public returns (int256) {
        require(value > 0, "Value must be positive");
        int256 oldCount = count;
        count += value;
        emit CountChanged(oldCount, count, "incrementBy");
        return count;
    }

    function getCount() public view returns (int256) {
        return count;
    }

    function reset() public {
        require(msg.sender == owner, "Only owner can reset");
        int256 oldCount = count;
        count = 0;
        emit CountChanged(oldCount, 0, "reset");
    }
}
