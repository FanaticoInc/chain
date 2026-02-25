#!/usr/bin/env python3
"""
Comprehensive test for v0.4.9.4 with proper contract tracking
"""

import json
import requests
import time

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
    if 'error' in result:
        raise Exception(f"RPC Error: {result['error']}")
    return result.get('result')

def deploy_contract(bytecode):
    """Deploy a contract and return its address"""
    # Deploy contract
    tx_hash = make_rpc_call("eth_sendTransaction", [{
        "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
        "data": "0x" + bytecode,
        "gas": "0x100000",
        "gasPrice": "0x4a817c800"
    }])

    print(f"  Transaction hash: {tx_hash}")

    # Get receipt to find contract address
    receipt = make_rpc_call("eth_getTransactionReceipt", [tx_hash])

    if not receipt:
        print("  ERROR: No receipt returned!")
        return None

    contract_address = receipt.get('contractAddress')
    if not contract_address:
        print(f"  ERROR: No contract address in receipt! Receipt: {receipt}")
        return None

    print(f"  Contract deployed at: {contract_address}")
    return contract_address

def call_contract(contract_address, data="0x"):
    """Call a contract and return the result"""
    result = make_rpc_call("eth_call", [{
        "to": contract_address,
        "data": data
    }, "latest"])
    return result

def check_storage(contract_address, slot):
    """Check storage at a specific slot"""
    result = make_rpc_call("eth_getStorageAt", [
        contract_address,
        hex(slot),
        "latest"
    ])
    return result

def test_addition():
    """Test simple addition: 100 + 200 = 300"""
    print("\n1. Testing Addition (100 + 200)")
    print("-" * 40)

    # Bytecode: PUSH1 0x64 (100) PUSH1 0xC8 (200) ADD PUSH1 0x00 MSTORE PUSH1 0x20 PUSH1 0x00 RETURN
    # This should return 300 (0x12c)
    bytecode = "606460c80160005260206000f3"

    contract_address = deploy_contract(bytecode)
    if not contract_address:
        return False

    # Call the contract
    result = call_contract(contract_address)

    # Convert result to number
    if result and result != "0x":
        value = int(result, 16)
        print(f"  Result: {result} = {value} decimal")
        if value == 300:
            print("  ✅ PASS: Addition works correctly!")
            return True
        else:
            print(f"  ❌ FAIL: Expected 300, got {value}")
    else:
        print(f"  ❌ FAIL: No result or empty result: {result}")

    return False

def test_storage():
    """Test storage operations"""
    print("\n2. Testing Storage Operations")
    print("-" * 40)

    # Bytecode: PUSH1 0x42 (66) PUSH1 0x00 SSTORE PUSH1 0x00 SLOAD PUSH1 0x00 MSTORE PUSH1 0x20 PUSH1 0x00 RETURN
    # This stores 66 at slot 0, then loads it and returns it
    bytecode = "604260005560005460005260206000f3"

    contract_address = deploy_contract(bytecode)
    if not contract_address:
        return False

    # Check storage directly
    storage_value = check_storage(contract_address, 0)
    if storage_value:
        value = int(storage_value, 16)
        print(f"  Storage at slot 0: {storage_value} = {value} decimal")
        if value == 66:
            print("  ✅ PASS: Storage works correctly!")
            return True
        else:
            print(f"  ❌ FAIL: Expected 66, got {value}")
    else:
        print(f"  ❌ FAIL: No storage value returned")

    return False

def test_multiplication():
    """Test multiplication: 7 * 8 = 56"""
    print("\n3. Testing Multiplication (7 * 8)")
    print("-" * 40)

    # Bytecode: PUSH1 0x07 PUSH1 0x08 MUL PUSH1 0x00 MSTORE PUSH1 0x20 PUSH1 0x00 RETURN
    bytecode = "600760080260005260206000f3"

    contract_address = deploy_contract(bytecode)
    if not contract_address:
        return False

    # Call the contract
    result = call_contract(contract_address)

    # Convert result to number
    if result and result != "0x":
        value = int(result, 16)
        print(f"  Result: {result} = {value} decimal")
        if value == 56:
            print("  ✅ PASS: Multiplication works correctly!")
            return True
        else:
            print(f"  ❌ FAIL: Expected 56, got {value}")
    else:
        print(f"  ❌ FAIL: No result or empty result: {result}")

    return False

def main():
    print("=" * 50)
    print("Testing v0.4.9.4 - Comprehensive Test Suite")
    print("=" * 50)

    # Verify connection
    chain_id = make_rpc_call("eth_chainId")
    print(f"✓ Connected to chain ID: {int(chain_id, 16)}")

    # Run tests
    tests_passed = 0
    total_tests = 3

    if test_addition():
        tests_passed += 1

    if test_storage():
        tests_passed += 1

    if test_multiplication():
        tests_passed += 1

    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    print(f"Tests Passed: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("✅ SUCCESS: All tests passed!")
        print("\nv0.4.9.4 is FULLY FUNCTIONAL!")
    elif tests_passed > 0:
        print("⚠️ PARTIAL SUCCESS: Some tests passed")
        print("\nv0.4.9.4 has partial functionality")
    else:
        print("❌ FAILURE: No tests passed")
        print("\nv0.4.9.4 is NOT functional")

    print(f"\nPass Rate: {(tests_passed/total_tests)*100:.1f}%")

    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)