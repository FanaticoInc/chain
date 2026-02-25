// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ExecutionDiagnostic
 * @dev Diagnose whether contract code is actually executing
 */

contract ExecutionDiagnostic {
    // State variables with explicit initialization
    uint256 public hardcodedValue = 12345;
    uint256 public constructorValue;
    uint256 public externalCallCount;

    event ConstructorExecuted(uint256 timestamp, address sender);
    event FunctionCalled(string functionName, uint256 count);

    constructor() {
        // Set value in constructor
        constructorValue = 99999;

        // Emit event
        emit ConstructorExecuted(block.timestamp, msg.sender);
    }

    // Simple function that just returns a constant
    function returnConstant() public pure returns (uint256) {
        return 777;
    }

    // Function that modifies state
    function incrementCounter() public returns (uint256) {
        externalCallCount++;
        emit FunctionCalled("incrementCounter", externalCallCount);
        return externalCallCount;
    }

    // Function that reads state
    function getHardcodedValue() public view returns (uint256) {
        return hardcodedValue;
    }

    // Function that reads constructor-set state
    function getConstructorValue() public view returns (uint256) {
        return constructorValue;
    }

    // Function that returns multiple values
    function getMultiple() public view returns (uint256, uint256, uint256) {
        return (hardcodedValue, constructorValue, externalCallCount);
    }

    // Simple arithmetic
    function add(uint256 a, uint256 b) public pure returns (uint256) {
        return a + b;
    }

    // Test if/else logic
    function testLogic(uint256 x) public pure returns (string memory) {
        if (x > 100) {
            return "greater";
        } else if (x < 100) {
            return "less";
        } else {
            return "equal";
        }
    }
}
