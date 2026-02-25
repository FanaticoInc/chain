// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title RequireTest
 * @dev Minimal contract to test require() statement enforcement
 *
 * This contract tests require() in different contexts to isolate the bug
 */

contract RequireTest {
    uint256 public value;
    bool public constructorCalled;
    bool public staticcallSuccess;

    // Test 1: Simple require in constructor
    constructor() {
        constructorCalled = true;
        value = 42;
    }

    // Test 2: Explicit require with true condition
    function testRequireTrue() public pure returns (uint256) {
        require(true, "This should pass");
        return 1;
    }

    // Test 3: Explicit require with false condition
    function testRequireFalse() public pure returns (uint256) {
        require(false, "This should revert");
        return 1;
    }

    // Test 4: require after successful staticcall
    function testRequireAfterSuccessfulStaticcall() public view returns (uint256) {
        // Call this contract's value getter (should succeed)
        (bool success, ) = address(this).staticcall(
            abi.encodeWithSignature("value()")
        );
        require(success, "staticcall should succeed");
        return value;
    }

    // Test 5: require after failed staticcall (non-existent function)
    function testRequireAfterFailedStaticcall() public view returns (uint256) {
        // Call non-existent function (should fail)
        (bool success, ) = address(this).staticcall(
            abi.encodeWithSignature("nonExistentFunction()")
        );
        require(success, "This should revert - staticcall failed");
        return 999; // Should never reach here
    }

    // Test 6: require after failed staticcall to non-existent precompile
    function testRequireAfterPrecompileCall() public view returns (uint256) {
        // Call Oasis Sapphire RANDOM_BYTES precompile (doesn't exist on Fanatico)
        address RANDOM_BYTES = 0x0100000000000000000000000000000000000001;
        (bool success, ) = RANDOM_BYTES.staticcall(
            abi.encode(uint256(32), bytes(""))
        );
        require(success, "This should revert - precompile missing");
        return 999; // Should never reach here
    }

    // Test 7: Store staticcall result for inspection
    function checkStaticallSuccess() public returns (bool) {
        address RANDOM_BYTES = 0x0100000000000000000000000000000000000001;
        (bool success, ) = RANDOM_BYTES.staticcall(
            abi.encode(uint256(32), bytes(""))
        );
        staticcallSuccess = success;
        return success;
    }
}

/**
 * @title RequireTestConstructor
 * @dev Test require() failure in constructor
 */
contract RequireTestConstructor {
    uint256 public value = 12345;
    bool public didRevert;

    constructor() {
        // This should revert and prevent deployment
        require(false, "Constructor require() should prevent deployment");
        value = 99999; // Should never execute
        didRevert = true; // Should never execute
    }

    function getValue() public view returns (uint256) {
        return value;
    }
}

/**
 * @title RequireTestConstructorStaticall
 * @dev Test require() failure after staticcall in constructor
 */
contract RequireTestConstructorStaticcall {
    uint256 public value = 12345;
    bool public success;

    constructor() {
        // Call non-existent precompile
        address RANDOM_BYTES = 0x0100000000000000000000000000000000000001;
        (bool s, ) = RANDOM_BYTES.staticcall(
            abi.encode(uint256(32), bytes(""))
        );
        success = s;

        // This should revert and prevent deployment
        require(s, "Precompile staticcall failed - should revert");

        value = 99999; // Should never execute
    }

    function getValue() public view returns (uint256) {
        return value;
    }
}
