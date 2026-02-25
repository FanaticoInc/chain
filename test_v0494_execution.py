#!/usr/bin/env python3
"""
Test v0.4.9.4 EVM Execution Fix
Tests all critical bugs have been fixed
"""

import json
import requests

# v0.4.9.4 endpoint
RPC_URL = "http://127.0.0.1:8552"

def make_rpc_call(method, params=None):
    """Make an RPC call to the Web3 API"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or [],
        "id": 1
    }

    response = requests.post(RPC_URL, json=payload)
    result = response.json()

    if "error" in result:
        print(f"Error in {method}: {result['error']}")
        return None

    return result.get("result")

def test_basic_arithmetic():
    """Test that the EVM can do basic arithmetic via bytecode execution"""
    print("\nTest: Basic Arithmetic (ADD opcode)")
    print("-" * 40)

    # Bytecode that adds two numbers
    # PUSH1 0x64 (100)
    # PUSH1 0xC8 (200)
    # ADD
    # PUSH1 0x00
    # MSTORE
    # PUSH1 0x20
    # PUSH1 0x00
    # RETURN
    bytecode = ("0x6064" +   # PUSH1 100
                "60c8" +     # PUSH1 200
                "01" +       # ADD
                "6000" +     # PUSH1 0x00
                "52" +       # MSTORE
                "6020" +     # PUSH1 0x20
                "6000" +     # PUSH1 0x00
                "f3")        # RETURN

    # Deploy the contract
    print("Deploying arithmetic test contract...")
    deploy_result = make_rpc_call("eth_sendTransaction", [{
        "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
        "data": bytecode,
        "gas": "0x100000",
        "gasPrice": "0x4a817c800"
    }])

    if not deploy_result:
        print("❌ FAIL: Could not deploy contract")
        return False

    print(f"Transaction hash: {deploy_result}")

    # Get the contract address from receipt
    receipt = make_rpc_call("eth_getTransactionReceipt", [deploy_result])
    if not receipt or not receipt.get("contractAddress"):
        # For testing, assume a contract address
        contract_address = "0x1234567890123456789012345678901234567890"
    else:
        contract_address = receipt["contractAddress"]

    print(f"Contract deployed at: {contract_address}")

    # Call the contract (it should return 300)
    print("\nCalling contract to get result of 100 + 200...")
    result = make_rpc_call("eth_call", [{
        "to": contract_address,
        "data": "0x"
    }, "latest"])

    if result:
        # Convert hex result to number
        value = int(result, 16) if result != "0x" else 0
        print(f"Result: {result} = {value} decimal")

        if value == 300:
            print("✅ PASS: Addition works! 100 + 200 = 300")
            return True
        else:
            print(f"❌ FAIL: Expected 300, got {value}")
            return False
    else:
        print("❌ FAIL: No result from contract call")
        return False

def test_storage():
    """Test that the EVM can store and retrieve values"""
    print("\nTest: Storage Operations (SSTORE/SLOAD)")
    print("-" * 40)

    # Bytecode that stores a value and retrieves it
    # PUSH1 0x42 (66 decimal)
    # PUSH1 0x00 (slot 0)
    # SSTORE
    # PUSH1 0x00 (slot 0)
    # SLOAD
    # PUSH1 0x00
    # MSTORE
    # PUSH1 0x20
    # PUSH1 0x00
    # RETURN
    bytecode = ("0x6042" +   # PUSH1 66
                "6000" +     # PUSH1 0 (slot)
                "55" +       # SSTORE
                "6000" +     # PUSH1 0 (slot)
                "54" +       # SLOAD
                "6000" +     # PUSH1 0x00
                "52" +       # MSTORE
                "6020" +     # PUSH1 0x20
                "6000" +     # PUSH1 0x00
                "f3")        # RETURN

    # Deploy the contract
    print("Deploying storage test contract...")
    deploy_result = make_rpc_call("eth_sendTransaction", [{
        "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
        "data": bytecode,
        "gas": "0x100000",
        "gasPrice": "0x4a817c800"
    }])

    if not deploy_result:
        print("❌ FAIL: Could not deploy contract")
        return False

    print(f"Transaction hash: {deploy_result}")

    # Get the contract address
    receipt = make_rpc_call("eth_getTransactionReceipt", [deploy_result])
    if not receipt or not receipt.get("contractAddress"):
        contract_address = "0x2345678901234567890123456789012345678901"
    else:
        contract_address = receipt["contractAddress"]

    print(f"Contract deployed at: {contract_address}")

    # Check storage at slot 0
    print("\nChecking storage at slot 0...")
    storage_value = make_rpc_call("eth_getStorageAt", [contract_address, "0x0", "latest"])

    if storage_value:
        value = int(storage_value, 16)
        print(f"Storage value: {storage_value} = {value} decimal")

        if value == 66:
            print("✅ PASS: Storage works! Stored and retrieved value 66")
            return True
        else:
            print(f"❌ FAIL: Expected 66, got {value}")
            return False
    else:
        print("❌ FAIL: Could not read storage")
        return False

def test_conditional_logic():
    """Test that the EVM can handle conditional logic (JUMPI)"""
    print("\nTest: Conditional Logic (JUMPI opcode)")
    print("-" * 40)

    # Bytecode with conditional jump
    # PUSH1 0x01 (1 = true)
    # PUSH1 0x0A (jump destination)
    # JUMPI
    # PUSH1 0x00 (should skip this)
    # JUMP
    # JUMPDEST (0x0A)
    # PUSH1 0xFF (255)
    # PUSH1 0x00
    # MSTORE
    # PUSH1 0x20
    # PUSH1 0x00
    # RETURN
    bytecode = ("0x6001" +   # PUSH1 1 (condition = true)
                "600a" +     # PUSH1 0x0A (jump destination)
                "57" +       # JUMPI
                "6000" +     # PUSH1 0 (should be skipped)
                "56" +       # JUMP (should be skipped)
                "5b" +       # JUMPDEST
                "60ff" +     # PUSH1 255
                "6000" +     # PUSH1 0x00
                "52" +       # MSTORE
                "6020" +     # PUSH1 0x20
                "6000" +     # PUSH1 0x00
                "f3")        # RETURN

    print("Deploying conditional logic test contract...")
    deploy_result = make_rpc_call("eth_sendTransaction", [{
        "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
        "data": bytecode,
        "gas": "0x100000",
        "gasPrice": "0x4a817c800"
    }])

    if not deploy_result:
        print("❌ FAIL: Could not deploy contract")
        return False

    print(f"Transaction hash: {deploy_result}")

    # Get the contract address
    receipt = make_rpc_call("eth_getTransactionReceipt", [deploy_result])
    if not receipt or not receipt.get("contractAddress"):
        contract_address = "0x3456789012345678901234567890123456789012"
    else:
        contract_address = receipt["contractAddress"]

    print(f"Contract deployed at: {contract_address}")

    # Call the contract (should return 255 if jump worked)
    print("\nCalling contract to test conditional jump...")
    result = make_rpc_call("eth_call", [{
        "to": contract_address,
        "data": "0x"
    }, "latest"])

    if result:
        value = int(result, 16) if result != "0x" else 0
        print(f"Result: {result} = {value} decimal")

        if value == 255:
            print("✅ PASS: Conditional logic works! JUMPI executed correctly")
            return True
        else:
            print(f"❌ FAIL: Expected 255, got {value}")
            return False
    else:
        print("❌ FAIL: No result from contract call")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing v0.4.9.3 - Real EVM Execution")
    print("=" * 50)

    # Check if service is running
    try:
        result = make_rpc_call("eth_chainId")
        if result:
            chain_id = int(result, 16)
            print(f"✓ Connected to chain ID: {chain_id}")
        else:
            print("❌ Could not connect to RPC endpoint")
            return
    except Exception as e:
        print(f"❌ Service not running on {RPC_URL}: {e}")
        return

    # Run tests
    tests_passed = 0
    tests_total = 3

    if test_basic_arithmetic():
        tests_passed += 1

    if test_storage():
        tests_passed += 1

    if test_conditional_logic():
        tests_passed += 1

    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    print(f"Tests Passed: {tests_passed}/{tests_total}")

    if tests_passed == tests_total:
        print("🎉 SUCCESS: All tests passed! EVM execution is working!")
    elif tests_passed > 0:
        print("⚠️  PARTIAL: Some tests passed, but not all")
    else:
        print("❌ FAILURE: No tests passed - EVM execution not working")

    print(f"\nPass Rate: {tests_passed/tests_total*100:.1f}%")

if __name__ == "__main__":
    main()