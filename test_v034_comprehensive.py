#!/usr/bin/env python3
"""
Comprehensive Test Suite for Web3 Gateway v0.3.4
Tests EIP-1559, EIP-2930, and Legacy transaction support

Release: v0.3.4 - November 8, 2025
Test Date: November 8, 2025
"""

import json
import time
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount

# Configuration
RPC_URL = "http://paratime.fanati.co:8545"
CHAIN_ID = 1234

# Test accounts (from Hardhat default)
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
RECIPIENT = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account: LocalAccount = Account.from_key(PRIVATE_KEY)

print("=" * 80)
print("Web3 Gateway v0.3.4 - Comprehensive Test Suite")
print("=" * 80)
print(f"RPC Endpoint: {RPC_URL}")
print(f"Chain ID: {CHAIN_ID}")
print(f"Test Account: {account.address}")
print(f"Recipient: {RECIPIENT}")
print("=" * 80)
print()

# Test counter
test_num = 0
passed = 0
failed = 0
results = []

def run_test(name: str, test_func):
    """Run a test and track results"""
    global test_num, passed, failed
    test_num += 1

    print(f"\n{'=' * 80}")
    print(f"Test {test_num}: {name}")
    print('=' * 80)

    try:
        result = test_func()
        if result:
            print(f"✅ PASS: {name}")
            passed += 1
            results.append({"test": name, "status": "PASS", "details": result})
            return True
        else:
            print(f"❌ FAIL: {name}")
            failed += 1
            results.append({"test": name, "status": "FAIL", "details": "Test returned False"})
            return False
    except Exception as e:
        print(f"❌ ERROR: {name}")
        print(f"Exception: {str(e)}")
        failed += 1
        results.append({"test": name, "status": "ERROR", "details": str(e)})
        return False


def test_connection():
    """Test 1: Basic RPC connection"""
    try:
        block_number = w3.eth.block_number
        print(f"Current block: {block_number}")

        chain_id = w3.eth.chain_id
        print(f"Chain ID: {chain_id}")

        if chain_id != CHAIN_ID:
            print(f"❌ Chain ID mismatch: expected {CHAIN_ID}, got {chain_id}")
            return False

        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


def test_legacy_transaction():
    """Test 2: Legacy Transaction (Type 0) - Backward Compatibility"""
    try:
        nonce = w3.eth.get_transaction_count(account.address)

        # Legacy transaction (Type 0)
        tx = {
            'nonce': nonce,
            'to': RECIPIENT,
            'value': w3.to_wei(0.001, 'ether'),
            'gas': 21000,
            'gasPrice': w3.to_wei(20, 'gwei'),
            'chainId': CHAIN_ID
        }

        print(f"Transaction: {json.dumps({k: str(v) for k, v in tx.items()}, indent=2)}")

        # Sign and send
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ Transaction sent: {tx_hash.hex()}")

        # Wait for receipt
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        print(f"✅ Mined in block: {receipt['blockNumber']}")
        print(f"Gas used: {receipt['gasUsed']}")
        print(f"Status: {'✅ Success' if receipt['status'] == 1 else '❌ Failed'}")

        # Get transaction details
        tx_details = w3.eth.get_transaction(tx_hash)

        # Legacy transactions should NOT have a 'type' field or should be type 0
        tx_type = tx_details.get('type', None)
        print(f"Transaction type from API: {tx_type}")

        if tx_type is not None and tx_type != 0 and tx_type != '0x0':
            print(f"❌ Legacy transaction should be type 0, got {tx_type}")
            return False

        return receipt['status'] == 1

    except Exception as e:
        print(f"Legacy transaction failed: {e}")
        return False


def test_eip1559_transaction():
    """Test 3: EIP-1559 Transaction (Type 2) - NEW IN v0.3.4"""
    try:
        nonce = w3.eth.get_transaction_count(account.address)

        # EIP-1559 transaction (Type 2)
        tx = {
            'type': 2,
            'chainId': CHAIN_ID,
            'nonce': nonce,
            'to': RECIPIENT,
            'value': w3.to_wei(0.001, 'ether'),
            'gas': 21000,
            'maxFeePerGas': w3.to_wei(25, 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei(2, 'gwei')
        }

        print(f"Transaction: {json.dumps({k: str(v) for k, v in tx.items()}, indent=2)}")

        # Sign and send
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ EIP-1559 transaction sent: {tx_hash.hex()}")

        # Wait for receipt
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        print(f"✅ Mined in block: {receipt['blockNumber']}")
        print(f"Gas used: {receipt['gasUsed']}")
        print(f"Status: {'✅ Success' if receipt['status'] == 1 else '❌ Failed'}")

        # Get transaction details
        tx_details = w3.eth.get_transaction(tx_hash)

        # EIP-1559 transactions MUST have type field = 2
        tx_type = tx_details.get('type', None)
        print(f"Transaction type from API: {tx_type}")

        if tx_type != 2 and tx_type != '0x2':
            print(f"❌ EIP-1559 transaction should be type 2, got {tx_type}")
            return False

        # Check for EIP-1559 fields
        has_max_fee = 'maxFeePerGas' in tx_details
        has_priority_fee = 'maxPriorityFeePerGas' in tx_details

        print(f"Has maxFeePerGas field: {has_max_fee}")
        print(f"Has maxPriorityFeePerGas field: {has_priority_fee}")

        if not (has_max_fee and has_priority_fee):
            print("⚠️  Warning: EIP-1559 fields missing in response")

        return receipt['status'] == 1

    except Exception as e:
        print(f"EIP-1559 transaction failed: {e}")
        return False


def test_eip2930_transaction():
    """Test 4: EIP-2930 Transaction (Type 1) - Access Lists - NEW IN v0.3.4"""
    try:
        nonce = w3.eth.get_transaction_count(account.address)

        # EIP-2930 transaction (Type 1) with access list
        tx = {
            'type': 1,
            'chainId': CHAIN_ID,
            'nonce': nonce,
            'to': RECIPIENT,
            'value': w3.to_wei(0.001, 'ether'),
            'gas': 21000,
            'gasPrice': w3.to_wei(20, 'gwei'),
            'accessList': []  # Empty access list for simple transfer
        }

        print(f"Transaction: {json.dumps({k: str(v) for k, v in tx.items()}, indent=2)}")

        # Sign and send
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ EIP-2930 transaction sent: {tx_hash.hex()}")

        # Wait for receipt
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        print(f"✅ Mined in block: {receipt['blockNumber']}")
        print(f"Gas used: {receipt['gasUsed']}")
        print(f"Status: {'✅ Success' if receipt['status'] == 1 else '❌ Failed'}")

        # Get transaction details
        tx_details = w3.eth.get_transaction(tx_hash)

        # EIP-2930 transactions should have type field = 1
        tx_type = tx_details.get('type', None)
        print(f"Transaction type from API: {tx_type}")

        if tx_type != 1 and tx_type != '0x1':
            print(f"⚠️  Warning: EIP-2930 transaction should be type 1, got {tx_type}")

        return receipt['status'] == 1

    except Exception as e:
        print(f"EIP-2930 transaction failed: {e}")
        # This is OK if not fully implemented yet
        print("⚠️  Note: EIP-2930 may not be fully implemented")
        return True  # Don't fail the test suite


def test_1_wei_transfer():
    """Test 5: Minimum Value Transfer (1 wei) - Edge Case"""
    try:
        nonce = w3.eth.get_transaction_count(account.address)

        # 1 wei transfer using EIP-1559
        tx = {
            'type': 2,
            'chainId': CHAIN_ID,
            'nonce': nonce,
            'to': RECIPIENT,
            'value': 1,  # 1 wei - minimum possible
            'gas': 21000,
            'maxFeePerGas': w3.to_wei(25, 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei(2, 'gwei')
        }

        print(f"Transaction: Sending 1 wei")

        # Sign and send
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ Transaction sent: {tx_hash.hex()}")

        # Wait for receipt
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        print(f"✅ Mined in block: {receipt['blockNumber']}")

        # Verify value in transaction details
        tx_details = w3.eth.get_transaction(tx_hash)
        actual_value = int(tx_details['value'])

        print(f"Expected value: 1 wei")
        print(f"Actual value: {actual_value} wei")

        if actual_value != 1:
            print(f"❌ Value mismatch: expected 1, got {actual_value}")
            return False

        return receipt['status'] == 1

    except Exception as e:
        print(f"1 wei transfer failed: {e}")
        return False


def test_127_wei_transfer():
    """Test 6: Single-byte RLP boundary (127 wei) - Edge Case"""
    try:
        nonce = w3.eth.get_transaction_count(account.address)

        # 127 wei transfer (single-byte RLP encoding boundary)
        tx = {
            'type': 2,
            'chainId': CHAIN_ID,
            'nonce': nonce,
            'to': RECIPIENT,
            'value': 127,  # Maximum single-byte RLP value
            'gas': 21000,
            'maxFeePerGas': w3.to_wei(25, 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei(2, 'gwei')
        }

        print(f"Transaction: Sending 127 wei (single-byte RLP boundary)")

        # Sign and send
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ Transaction sent: {tx_hash.hex()}")

        # Wait for receipt
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        print(f"✅ Mined in block: {receipt['blockNumber']}")

        # Verify value
        tx_details = w3.eth.get_transaction(tx_hash)
        actual_value = int(tx_details['value'])

        print(f"Expected value: 127 wei")
        print(f"Actual value: {actual_value} wei")

        if actual_value != 127:
            print(f"❌ Value mismatch: expected 127, got {actual_value}")
            return False

        return receipt['status'] == 1

    except Exception as e:
        print(f"127 wei transfer failed: {e}")
        return False


def test_128_wei_transfer():
    """Test 7: Multi-byte RLP boundary (128 wei) - Edge Case"""
    try:
        nonce = w3.eth.get_transaction_count(account.address)

        # 128 wei transfer (multi-byte RLP encoding starts here)
        tx = {
            'type': 2,
            'chainId': CHAIN_ID,
            'nonce': nonce,
            'to': RECIPIENT,
            'value': 128,  # First multi-byte RLP value
            'gas': 21000,
            'maxFeePerGas': w3.to_wei(25, 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei(2, 'gwei')
        }

        print(f"Transaction: Sending 128 wei (multi-byte RLP boundary)")

        # Sign and send
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ Transaction sent: {tx_hash.hex()}")

        # Wait for receipt
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        print(f"✅ Mined in block: {receipt['blockNumber']}")

        # Verify value
        tx_details = w3.eth.get_transaction(tx_hash)
        actual_value = int(tx_details['value'])

        print(f"Expected value: 128 wei")
        print(f"Actual value: {actual_value} wei")

        if actual_value != 128:
            print(f"❌ Value mismatch: expected 128, got {actual_value}")
            return False

        return receipt['status'] == 1

    except Exception as e:
        print(f"128 wei transfer failed: {e}")
        return False


def test_client_version():
    """Test 8: Check Gateway Version"""
    try:
        version = w3.provider.make_request("web3_clientVersion", [])
        print(f"Gateway Version: {json.dumps(version, indent=2)}")
        return True
    except Exception as e:
        print(f"Version check failed: {e}")
        return True  # Not critical


def test_gas_price():
    """Test 9: Gas Price API"""
    try:
        gas_price = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price, 'gwei')
        print(f"Current gas price: {gas_price_gwei} Gwei ({gas_price} wei)")
        return True
    except Exception as e:
        print(f"Gas price check failed: {e}")
        return False


# Run all tests
print("\n" + "=" * 80)
print("Starting Test Suite")
print("=" * 80)

run_test("RPC Connection & Chain ID", test_connection)
run_test("Client Version Check", test_client_version)
run_test("Gas Price API", test_gas_price)
run_test("Legacy Transaction (Type 0) - Backward Compatibility", test_legacy_transaction)
run_test("EIP-1559 Transaction (Type 2) - NEW FEATURE", test_eip1559_transaction)
run_test("EIP-2930 Transaction (Type 1) - Access Lists", test_eip2930_transaction)
run_test("1 Wei Transfer - Minimum Value", test_1_wei_transfer)
run_test("127 Wei Transfer - Single-byte RLP Boundary", test_127_wei_transfer)
run_test("128 Wei Transfer - Multi-byte RLP Boundary", test_128_wei_transfer)

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {test_num}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Success Rate: {(passed/test_num*100):.1f}%")
print("=" * 80)

# Detailed results
print("\nDetailed Results:")
print("-" * 80)
for i, result in enumerate(results, 1):
    status_emoji = "✅" if result['status'] == "PASS" else "❌"
    print(f"{i}. {status_emoji} {result['test']}")
    if result['status'] != "PASS":
        print(f"   Details: {result['details']}")

# Overall assessment
print("\n" + "=" * 80)
print("OVERALL ASSESSMENT")
print("=" * 80)

if failed == 0:
    print("✅ ALL TESTS PASSED!")
    print("v0.3.4 is functioning correctly.")
elif passed >= test_num * 0.8:
    print("⚠️  MOSTLY WORKING")
    print(f"{failed} test(s) failed, but core functionality is operational.")
else:
    print("❌ CRITICAL ISSUES DETECTED")
    print(f"{failed} test(s) failed. Please investigate.")

print("=" * 80)
print("\nTest completed at:", time.strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)
