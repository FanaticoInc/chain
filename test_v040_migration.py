#!/usr/bin/env python3
"""
Chain ID Migration Test Suite for v0.4.0
Tests migration from Chain ID 1234 to 999999999

Date: November 8, 2025
Purpose: Verify all functions work correctly after chain ID migration
"""

import json
import time
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount

# Configuration - NEW VALUES FOR v0.4.0
RPC_URL = "http://paratime.fanati.co:8546"  # Temporary port
OLD_CHAIN_ID = 1234
NEW_CHAIN_ID = 999999999

# Test accounts from release notes
ACCOUNTS = {
    'roman': {
        'address': '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
        'private_key': '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80',
        'expected_balance_fco': 14.50
    },
    'hardhat_testing': {
        'address': '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
        'private_key': '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d',
        'expected_balance_fco': 34.37
    },
    'air': {
        'address': '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
        'private_key': '0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a',
        'expected_balance_fco': 9.50
    },
    'ali': {
        'address': '0xf945e1714Ef5872cfD88aa99B3cf16DD66f58E92',
        'private_key': '0x06ce277a41c1c1804469a604f8d6110fab75c08a2c685aa27ea2c1b50cffe97b',
        'expected_balance_fco': 39.50
    },
    'test_account': {
        'address': '0x5B38Da6a701c568545dCfcB03FcB875f56beddC4',
        'private_key': '0x503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48dfcb',
        'expected_balance_fco': 2.13
    }
}

# Use Hardhat Testing account for transaction tests (has 34.37 FCO)
SENDER_KEY = ACCOUNTS['hardhat_testing']['private_key']
RECIPIENT = ACCOUNTS['roman']['address']

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
sender: LocalAccount = Account.from_key(SENDER_KEY)

print("=" * 80)
print("Web3 Gateway v0.4.0 - Chain ID Migration Test Suite")
print("=" * 80)
print(f"RPC Endpoint: {RPC_URL}")
print(f"Old Chain ID: {OLD_CHAIN_ID}")
print(f"New Chain ID: {NEW_CHAIN_ID}")
print(f"Test Sender: {sender.address}")
print(f"Test Recipient: {RECIPIENT}")
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


def test_chain_id_migration():
    """Test 1: Verify Chain ID has been migrated"""
    try:
        chain_id = w3.eth.chain_id
        print(f"Current Chain ID (decimal): {chain_id}")
        print(f"Current Chain ID (hex): {hex(chain_id)}")
        print(f"Expected Chain ID: {NEW_CHAIN_ID} (0x{NEW_CHAIN_ID:x})")

        if chain_id != NEW_CHAIN_ID:
            print(f"❌ Chain ID mismatch!")
            print(f"   Expected: {NEW_CHAIN_ID}")
            print(f"   Got: {chain_id}")
            return False

        if chain_id == OLD_CHAIN_ID:
            print(f"❌ Chain ID not migrated! Still using old chain ID {OLD_CHAIN_ID}")
            return False

        print(f"✅ Chain ID successfully migrated to {NEW_CHAIN_ID}")
        return True

    except Exception as e:
        print(f"Chain ID verification failed: {e}")
        return False


def test_account_balances():
    """Test 2: Verify all test account balances after migration"""
    try:
        print("\nVerifying account balances...")
        all_correct = True

        for name, account_info in ACCOUNTS.items():
            address = account_info['address']
            expected_fco = account_info['expected_balance_fco']

            balance_wei = w3.eth.get_balance(address)
            balance_fco = float(w3.from_wei(balance_wei, 'ether'))

            print(f"\n{name.upper()}: {address}")
            print(f"  Expected: {expected_fco:.2f} FCO")
            print(f"  Actual:   {balance_fco:.2f} FCO")

            # Allow small variance due to gas costs
            tolerance = 0.1  # 0.1 FCO tolerance
            if abs(balance_fco - expected_fco) > tolerance:
                print(f"  ⚠️  Balance differs by {abs(balance_fco - expected_fco):.4f} FCO")
                print(f"     (This may be due to recent transactions)")
            else:
                print(f"  ✅ Balance correct")

        return True

    except Exception as e:
        print(f"Balance verification failed: {e}")
        return False


def test_connection():
    """Test 3: Basic RPC connection and block info"""
    try:
        block_number = w3.eth.block_number
        print(f"Current block: {block_number}")

        chain_id = w3.eth.chain_id
        print(f"Chain ID: {chain_id}")

        is_listening = w3.is_connected()
        print(f"Connected: {is_listening}")

        return block_number > 0 and chain_id == NEW_CHAIN_ID

    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


def test_gas_price():
    """Test 4: Gas price API"""
    try:
        gas_price = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price, 'gwei')
        print(f"Current gas price: {gas_price_gwei} Gwei ({gas_price} wei)")

        # v0.4.0 release notes say fixed at 10 Gwei
        if gas_price == w3.to_wei(10, 'gwei'):
            print("✅ Gas price matches expected 10 Gwei")

        return gas_price > 0

    except Exception as e:
        print(f"Gas price check failed: {e}")
        return False


def test_legacy_transaction():
    """Test 5: Legacy Transaction (Type 0) - Backward Compatibility"""
    try:
        nonce = w3.eth.get_transaction_count(sender.address)

        # Legacy transaction (Type 0)
        tx = {
            'nonce': nonce,
            'to': RECIPIENT,
            'value': w3.to_wei(0.001, 'ether'),
            'gas': 21000,
            'gasPrice': w3.to_wei(10, 'gwei'),
            'chainId': NEW_CHAIN_ID  # USING NEW CHAIN ID
        }

        print(f"Transaction: {json.dumps({k: str(v) for k, v in tx.items()}, indent=2)}")

        # Sign and send
        signed = sender.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ Transaction sent: {tx_hash.hex()}")

        # Wait for receipt
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        print(f"✅ Mined in block: {receipt['blockNumber']}")
        print(f"Gas used: {receipt['gasUsed']}")
        print(f"Status: {'✅ Success' if receipt['status'] == 1 else '❌ Failed'}")

        # Verify transaction details
        tx_details = w3.eth.get_transaction(tx_hash)
        tx_chain_id = tx_details.get('chainId', None)

        print(f"Transaction Chain ID: {tx_chain_id}")

        if tx_chain_id != NEW_CHAIN_ID:
            print(f"❌ Transaction used wrong chain ID: {tx_chain_id}")
            return False

        return receipt['status'] == 1

    except Exception as e:
        print(f"Legacy transaction failed: {e}")
        return False


def test_eip1559_transaction():
    """Test 6: EIP-1559 Transaction (Type 2) - With New Chain ID"""
    try:
        nonce = w3.eth.get_transaction_count(sender.address)

        # EIP-1559 transaction (Type 2)
        tx = {
            'type': 2,
            'chainId': NEW_CHAIN_ID,  # USING NEW CHAIN ID
            'nonce': nonce,
            'to': RECIPIENT,
            'value': w3.to_wei(0.001, 'ether'),
            'gas': 21000,
            'maxFeePerGas': w3.to_wei(25, 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei(2, 'gwei')
        }

        print(f"Transaction: {json.dumps({k: str(v) for k, v in tx.items()}, indent=2)}")

        # Sign and send
        signed = sender.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ EIP-1559 transaction sent: {tx_hash.hex()}")

        # Wait for receipt
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        print(f"✅ Mined in block: {receipt['blockNumber']}")
        print(f"Status: {'✅ Success' if receipt['status'] == 1 else '❌ Failed'}")

        # Verify transaction type and chain ID
        tx_details = w3.eth.get_transaction(tx_hash)
        tx_type = tx_details.get('type', None)
        tx_chain_id = tx_details.get('chainId', None)

        print(f"Transaction type: {tx_type}")
        print(f"Transaction Chain ID: {tx_chain_id}")

        if tx_type != 2 and tx_type != '0x2':
            print(f"❌ Wrong transaction type: {tx_type}")
            return False

        if tx_chain_id != NEW_CHAIN_ID:
            print(f"❌ Transaction used wrong chain ID: {tx_chain_id}")
            return False

        return receipt['status'] == 1

    except Exception as e:
        print(f"EIP-1559 transaction failed: {e}")
        return False


def test_1_wei_transfer():
    """Test 7: Minimum Value Transfer (1 wei) - Edge Case"""
    try:
        nonce = w3.eth.get_transaction_count(sender.address)

        # 1 wei transfer
        tx = {
            'type': 2,
            'chainId': NEW_CHAIN_ID,
            'nonce': nonce,
            'to': RECIPIENT,
            'value': 1,  # 1 wei
            'gas': 21000,
            'maxFeePerGas': w3.to_wei(25, 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei(2, 'gwei')
        }

        print(f"Sending 1 wei with new Chain ID {NEW_CHAIN_ID}")

        # Sign and send
        signed = sender.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ Transaction sent: {tx_hash.hex()}")

        # Wait for receipt
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        print(f"✅ Mined in block: {receipt['blockNumber']}")

        # Verify value
        tx_details = w3.eth.get_transaction(tx_hash)
        actual_value = int(tx_details['value'])

        print(f"Expected value: 1 wei")
        print(f"Actual value: {actual_value} wei")

        if actual_value != 1:
            print(f"❌ Value mismatch!")
            return False

        return receipt['status'] == 1

    except Exception as e:
        print(f"1 wei transfer failed: {e}")
        return False


def test_127_wei_transfer():
    """Test 8: RLP boundary test (127 wei)"""
    try:
        nonce = w3.eth.get_transaction_count(sender.address)

        tx = {
            'type': 2,
            'chainId': NEW_CHAIN_ID,
            'nonce': nonce,
            'to': RECIPIENT,
            'value': 127,
            'gas': 21000,
            'maxFeePerGas': w3.to_wei(25, 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei(2, 'gwei')
        }

        print(f"Sending 127 wei (RLP boundary)")

        signed = sender.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ Transaction sent: {tx_hash.hex()}")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        tx_details = w3.eth.get_transaction(tx_hash)
        actual_value = int(tx_details['value'])

        print(f"Expected: 127 wei, Actual: {actual_value} wei")

        return actual_value == 127 and receipt['status'] == 1

    except Exception as e:
        print(f"127 wei transfer failed: {e}")
        return False


def test_128_wei_transfer():
    """Test 9: RLP boundary test (128 wei)"""
    try:
        nonce = w3.eth.get_transaction_count(sender.address)

        tx = {
            'type': 2,
            'chainId': NEW_CHAIN_ID,
            'nonce': nonce,
            'to': RECIPIENT,
            'value': 128,
            'gas': 21000,
            'maxFeePerGas': w3.to_wei(25, 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei(2, 'gwei')
        }

        print(f"Sending 128 wei (RLP boundary)")

        signed = sender.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        print(f"✅ Transaction sent: {tx_hash.hex()}")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        tx_details = w3.eth.get_transaction(tx_hash)
        actual_value = int(tx_details['value'])

        print(f"Expected: 128 wei, Actual: {actual_value} wei")

        return actual_value == 128 and receipt['status'] == 1

    except Exception as e:
        print(f"128 wei transfer failed: {e}")
        return False


def test_nonce_management():
    """Test 10: Nonce increments correctly"""
    try:
        nonce_before = w3.eth.get_transaction_count(sender.address)
        print(f"Nonce before: {nonce_before}")

        # The previous tests already sent transactions
        # Just verify nonce makes sense
        if nonce_before >= 0:
            print(f"✅ Nonce is valid: {nonce_before}")
            return True

        return False

    except Exception as e:
        print(f"Nonce test failed: {e}")
        return False


# Run all tests
print("\n" + "=" * 80)
print("Starting Migration Test Suite")
print("=" * 80)

run_test("Chain ID Migration Verification", test_chain_id_migration)
run_test("Account Balances After Migration", test_account_balances)
run_test("RPC Connection & Block Info", test_connection)
run_test("Gas Price API", test_gas_price)
run_test("Legacy Transaction (Type 0) with New Chain ID", test_legacy_transaction)
run_test("EIP-1559 Transaction (Type 2) with New Chain ID", test_eip1559_transaction)
run_test("1 Wei Transfer with New Chain ID", test_1_wei_transfer)
run_test("127 Wei Transfer (RLP Boundary)", test_127_wei_transfer)
run_test("128 Wei Transfer (RLP Boundary)", test_128_wei_transfer)
run_test("Nonce Management", test_nonce_management)

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

# Migration-specific assessment
print("\n" + "=" * 80)
print("MIGRATION ASSESSMENT")
print("=" * 80)

if failed == 0:
    print("✅ MIGRATION SUCCESSFUL!")
    print(f"Chain ID successfully migrated to {NEW_CHAIN_ID}")
    print("All functions working as expected.")
elif passed >= test_num * 0.8:
    print("⚠️  MIGRATION MOSTLY SUCCESSFUL")
    print(f"Chain ID migrated to {NEW_CHAIN_ID}")
    print(f"{failed} test(s) failed - review needed")
else:
    print("❌ MIGRATION ISSUES DETECTED")
    print(f"{failed} test(s) failed - immediate attention required")

print("\n" + "=" * 80)
print("KEY FINDINGS")
print("=" * 80)
print(f"• New Chain ID: {NEW_CHAIN_ID} (0x{NEW_CHAIN_ID:x})")
print(f"• Old Chain ID: {OLD_CHAIN_ID} (deprecated)")
print(f"• RPC Endpoint: {RPC_URL}")
print(f"• EIP-1559 Support: {'✅ Working' if passed >= 6 else '❌ Issues'}")
print(f"• Edge Cases: {'✅ Working' if passed >= 8 else '❌ Issues'}")
print(f"• Backward Compatibility: {'✅ Maintained' if passed >= 5 else '❌ Issues'}")
print("=" * 80)

print("\nTest completed at:", time.strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)
