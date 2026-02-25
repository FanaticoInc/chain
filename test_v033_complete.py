#!/usr/bin/env python3
"""
Complete v0.3.3 Testing Suite
Tests all edge cases documented in V033_TESTING_DEVELOPER_RELEASE_NOTES.md
"""

from web3 import Web3
from eth_account import Account
import time
import json

# Connect to v0.3.3 deployment
w3 = Web3(Web3.HTTPProvider('http://paratime.fanati.co:8545'))

print("=" * 80)
print("v0.3.3 Complete Edge Case Testing Suite")
print("=" * 80)
print()

# Test accounts (using funded test account - Remix IDE default account #0)
test_account = {
    "address": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4",
    "private_key": "0x503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48dfcb"
}

recipient = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

# Check connectivity and version
try:
    connected = w3.is_connected()
    print(f"Connected to network: {connected}")
    chain_id = w3.eth.chain_id
    print(f"Chain ID: {chain_id}")
    block_number = w3.eth.block_number
    print(f"Current Block: {block_number}")

    # Get version if available
    try:
        version = w3.client_version
        print(f"Client Version: {version}")
    except:
        print("Client Version: Not available")

    print()
except Exception as e:
    print(f"❌ Connection Error: {e}")
    exit(1)

# Check account balance
balance = w3.eth.get_balance(test_account["address"])
print(f"Test Account Balance: {w3.from_wei(balance, 'ether')} FCO")
print()

if balance == 0:
    print("❌ ERROR: Test account has zero balance. Cannot run tests.")
    exit(1)

# Define comprehensive test cases
test_cases = [
    # Critical Edge Cases (v0.3.2 failures)
    {
        "name": "Single Wei",
        "value_wei": 1,
        "value_fco": "0.000000000000000001",
        "priority": "CRITICAL",
        "v032_result": "❌ Returns 0"
    },
    {
        "name": "Boundary Single-Byte (127 wei)",
        "value_wei": 127,
        "value_fco": "0.000000000000000127",
        "priority": "HIGH",
        "v032_result": "❌ Returns 0"
    },
    {
        "name": "Boundary Two-Byte (128 wei)",
        "value_wei": 128,
        "value_fco": "0.000000000000000128",
        "priority": "HIGH",
        "v032_result": "❌ Returns 0"
    },
    {
        "name": "Sub-cent Value (0.001 FCO)",
        "value_wei": int(0.001 * 10**18),
        "value_fco": "0.001",
        "priority": "HIGH",
        "v032_result": "❌ Returns 0"
    },
    {
        "name": "High Precision (50.12345678 FCO)",
        "value_wei": int(50.12345678 * 10**18),
        "value_fco": "50.12345678",
        "priority": "MEDIUM",
        "v032_result": "❌ Returns 0"
    },

    # Boundary Testing
    {
        "name": "255 wei (max single byte)",
        "value_wei": 255,
        "value_fco": "0.000000000000000255",
        "priority": "MEDIUM",
        "v032_result": "Unknown"
    },
    {
        "name": "256 wei (min two bytes)",
        "value_wei": 256,
        "value_fco": "0.000000000000000256",
        "priority": "MEDIUM",
        "v032_result": "Unknown"
    },

    # Standard Values (Regression Testing)
    {
        "name": "Zero Value",
        "value_wei": 0,
        "value_fco": "0.0",
        "priority": "MEDIUM",
        "v032_result": "✅ Working"
    },
    {
        "name": "Standard 0.1 FCO",
        "value_wei": int(0.1 * 10**18),
        "value_fco": "0.1",
        "priority": "LOW",
        "v032_result": "✅ Working"
    },
    {
        "name": "Standard 1.0 FCO",
        "value_wei": int(1.0 * 10**18),
        "value_fco": "1.0",
        "priority": "LOW",
        "v032_result": "✅ Working"
    },
    {
        "name": "Pi Approximation (3.14159 FCO)",
        "value_wei": int(3.14159 * 10**18),
        "value_fco": "3.14159",
        "priority": "LOW",
        "v032_result": "✅ Working"
    },
    {
        "name": "Large Value (100 FCO)",
        "value_wei": int(100 * 10**18),
        "value_fco": "100.0",
        "priority": "LOW",
        "v032_result": "✅ Working"
    }
]

# Run tests
results = []
account = Account.from_key(test_account["private_key"])

print("=" * 80)
print("Running Test Suite")
print("=" * 80)
print()

for i, test in enumerate(test_cases, 1):
    print(f"Test {i}/{len(test_cases)}: {test['name']}")
    print(f"  Priority: {test['priority']}")
    print(f"  Value: {test['value_wei']} wei ({test['value_fco']} FCO)")
    print(f"  v0.3.2 Result: {test['v032_result']}")

    try:
        # Get current nonce
        nonce = w3.eth.get_transaction_count(test_account["address"])

        # Create transaction
        tx = {
            'nonce': nonce,
            'to': recipient,
            'value': test['value_wei'],
            'gas': 21000,
            'gasPrice': w3.to_wei(20, 'gwei'),
            'chainId': chain_id
        }

        # Sign and send
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        tx_hash_hex = tx_hash.hex()

        print(f"  TX Hash: {tx_hash_hex}")

        # Wait for confirmation
        time.sleep(2)

        # Get transaction receipt
        receipt = w3.eth.get_transaction_receipt(tx_hash)

        # Get transaction details
        tx_data = w3.eth.get_transaction(tx_hash)

        # Extract value
        extracted_value = int(tx_data['value'])
        expected_value = test['value_wei']

        # Check if correct
        is_correct = extracted_value == expected_value
        variance = extracted_value - expected_value

        status = "✅ PASS" if is_correct else "❌ FAIL"

        print(f"  Expected: {expected_value} wei")
        print(f"  Extracted: {extracted_value} wei")
        print(f"  Variance: {variance} wei")
        print(f"  Result: {status}")

        # Check FROM address
        from_correct = tx_data['from'].lower() == test_account["address"].lower()
        print(f"  FROM Address: {'✅ Correct' if from_correct else '❌ Wrong'}")

        # Check receipt status
        tx_status = receipt['status']
        print(f"  TX Status: {'✅ Success' if tx_status == 1 else '❌ Failed'}")

        results.append({
            "test": test['name'],
            "priority": test['priority'],
            "expected": expected_value,
            "extracted": extracted_value,
            "variance": variance,
            "correct": is_correct,
            "from_correct": from_correct,
            "tx_status": tx_status,
            "tx_hash": tx_hash_hex,
            "block": receipt['blockNumber'],
            "v032_result": test['v032_result']
        })

        print()

        # Small delay between tests
        time.sleep(1)

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results.append({
            "test": test['name'],
            "priority": test['priority'],
            "expected": test['value_wei'],
            "extracted": 0,
            "variance": 0,
            "correct": False,
            "from_correct": False,
            "tx_status": 0,
            "error": str(e),
            "v032_result": test['v032_result']
        })
        print()

# Print Summary
print("=" * 80)
print("Test Results Summary")
print("=" * 80)
print()

# Overall statistics
total_tests = len(results)
passed = sum(1 for r in results if r['correct'])
failed = total_tests - passed
accuracy = (passed / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests: {total_tests}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Accuracy: {accuracy:.1f}%")
print()

# By priority
for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
    priority_results = [r for r in results if r['priority'] == priority]
    if priority_results:
        priority_passed = sum(1 for r in priority_results if r['correct'])
        priority_total = len(priority_results)
        priority_accuracy = (priority_passed / priority_total * 100) if priority_total > 0 else 0
        status_icon = "✅" if priority_accuracy == 100 else "⚠️" if priority_accuracy >= 50 else "❌"
        print(f"{priority} Priority: {priority_passed}/{priority_total} ({priority_accuracy:.0f}%) {status_icon}")

print()

# v0.3.2 Regression Analysis
print("=" * 80)
print("v0.3.2 → v0.3.3 Comparison")
print("=" * 80)
print()

v032_failures = [r for r in results if "❌ Returns 0" in r['v032_result']]
if v032_failures:
    print(f"v0.3.2 Known Failures: {len(v032_failures)} tests")
    v033_fixed = sum(1 for r in v032_failures if r['correct'])
    print(f"v0.3.3 Fixed: {v033_fixed}/{len(v032_failures)}")
    print()

    for r in v032_failures:
        status = "✅ FIXED" if r['correct'] else "❌ STILL BROKEN"
        print(f"  {r['test']}: {status}")
        if not r['correct']:
            print(f"    Expected: {r['expected']} wei, Got: {r['extracted']} wei")
    print()

# Detailed failure analysis
failures = [r for r in results if not r['correct']]
if failures:
    print("=" * 80)
    print("Failed Test Details")
    print("=" * 80)
    print()

    for r in failures:
        print(f"Test: {r['test']}")
        print(f"  Expected Value: {r['expected']} wei")
        print(f"  Extracted Value: {r['extracted']} wei")
        print(f"  Variance: {r['variance']} wei")
        print(f"  Block: {r.get('block', 'N/A')}")
        print(f"  TX Hash: {r.get('tx_hash', 'N/A')}")
        if 'error' in r:
            print(f"  Error: {r['error']}")
        print()

# Final verdict
print("=" * 80)
print("Final Verdict")
print("=" * 80)
print()

if accuracy == 100:
    print("✅ SUCCESS: v0.3.3 achieves 100% accuracy!")
    print("All edge cases are now handled correctly.")
    print("Release notes claim VERIFIED.")
elif accuracy >= 90:
    print(f"⚠️  MOSTLY WORKING: v0.3.3 shows {accuracy:.0f}% accuracy")
    print(f"Minor issues remain in {failed} test case(s).")
elif accuracy >= 77:
    print(f"⚠️  IMPROVEMENT: v0.3.3 shows {accuracy:.0f}% accuracy (up from 77% in v0.3.2)")
    print(f"Still has issues with {failed} test case(s).")
else:
    print(f"❌ NO IMPROVEMENT: v0.3.3 shows only {accuracy:.0f}% accuracy")
    print(f"Critical issues remain in {failed} test case(s).")

print()

# Production readiness
if accuracy == 100 and all(r.get('from_correct', False) for r in results):
    print("✅ PRODUCTION READY: All tests pass")
elif accuracy >= 90:
    print("⚠️  CONDITIONAL PRODUCTION READY: Minor issues exist")
else:
    print("❌ NOT PRODUCTION READY: Critical issues remain")

print()
print("=" * 80)
print("Test Suite Complete")
print("=" * 80)

# Save results to file
with open('/Users/sebastian/CODE/L1/v033_test_results.json', 'w') as f:
    json.dump({
        "version": "0.3.3",
        "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "endpoint": "http://paratime.fanati.co:8545",
        "chain_id": chain_id,
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "accuracy": accuracy,
        "results": results
    }, f, indent=2)

print()
print("Results saved to: v033_test_results.json")
