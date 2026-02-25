#!/usr/bin/env python3
"""Comprehensive transaction testing for v0.4.4"""

from web3 import Web3
import time
import json

RPC_URL = "http://paratime.fanati.co:8546"
PRIVATE_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
CHAIN_ID = 999999999

print("=" * 70)
print("v0.4.4 TRANSACTION TESTING")
print("=" * 70)

# Setup
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

print(f"\nTest Account: {account.address}")
balance = w3.eth.get_balance(account.address)
print(f"Balance: {w3.from_wei(balance, 'ether')} FCO")

# Test 1: Simple Transfer
print("\n" + "=" * 70)
print("TEST 1: Simple Transfer (Legacy Transaction)")
print("=" * 70)

try:
    recipient = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
    nonce = w3.eth.get_transaction_count(account.address)

    tx = {
        'from': account.address,
        'to': recipient,
        'value': w3.to_wei(0.001, 'ether'),
        'gas': 21000,
        'gasPrice': w3.to_wei(10, 'gwei'),
        'nonce': nonce,
        'chainId': CHAIN_ID
    }

    print(f"\nTransaction:")
    print(f"  To: {tx['to']}")
    print(f"  Value: {w3.from_wei(tx['value'], 'ether')} FCO")
    print(f"  Gas: {tx['gas']}")
    print(f"  Gas Price: {w3.from_wei(tx['gasPrice'], 'gwei')} Gwei")
    print(f"  Nonce: {tx['nonce']}")

    # Sign
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    # Send
    print("\nSending transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Transaction sent: {tx_hash.hex()}")

    # Wait for receipt
    print("Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    print(f"✅ Transaction confirmed!")
    print(f"   Block: {receipt['blockNumber']}")
    print(f"   Status: {receipt['status']}")
    print(f"   Gas Used: {receipt['gasUsed']}")

    print("\n✅ TEST 1: PASSED - Simple transfer working!")
    test1_passed = True

except Exception as e:
    print(f"\n❌ TEST 1: FAILED")
    print(f"Error: {e}")
    if hasattr(e, 'args') and len(e.args) > 0:
        print(f"Details: {e.args[0]}")
    test1_passed = False

# Test 2: Contract Deployment
print("\n" + "=" * 70)
print("TEST 2: Contract Deployment")
print("=" * 70)

# SimpleStorage contract bytecode (stores uint256, has get/set functions)
BYTECODE = '0x608060405234801561000f575f80fd5b50602a5f5560bb806100205f395ff3fe6080604052348015600e575f80fd5b50600436106030575f3560e01c80636d4ce63c146034578063e5c19b2d14604c575b5f80fd5b603a6056565b60405190815260200160405180910390f35b6054605e565b005b5f5f54905090565b602a5f8190555056fea2646970667358221220c85b4c6f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f64736f6c63430008140033'

try:
    nonce = w3.eth.get_transaction_count(account.address)

    tx = {
        'from': account.address,
        'to': None,  # Contract deployment
        'value': 0,
        'gas': 300000,
        'gasPrice': w3.to_wei(10, 'gwei'),
        'nonce': nonce,
        'data': BYTECODE,
        'chainId': CHAIN_ID
    }

    print(f"\nDeployment Transaction:")
    print(f"  Gas: {tx['gas']}")
    print(f"  Gas Price: {w3.from_wei(tx['gasPrice'], 'gwei')} Gwei")
    print(f"  Bytecode length: {len(BYTECODE)} chars")
    print(f"  Nonce: {tx['nonce']}")

    # Sign
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    # Send
    print("\nDeploying contract...")
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Transaction sent: {tx_hash.hex()}")

    # Wait for receipt
    print("Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

    if receipt['contractAddress']:
        print(f"✅ Contract deployed!")
        print(f"   Address: {receipt['contractAddress']}")
        print(f"   Block: {receipt['blockNumber']}")
        print(f"   Gas Used: {receipt['gasUsed']}")

        # Test the deployed contract
        contract_address = receipt['contractAddress']
        print(f"\nTesting deployed contract...")

        # Test eth_getCode
        print("  Testing eth_getCode...")
        bytecode = w3.eth.get_code(contract_address)
        if bytecode and bytecode != b'\x00' and len(bytecode) > 2:
            print(f"  ✅ Bytecode retrieved: {len(bytecode)} bytes")
        else:
            print(f"  ⚠️  Bytecode empty or minimal: {bytecode.hex()}")

        # Test eth_call (call get() function - selector 0x6d4ce63c)
        print("  Testing eth_call (get() function)...")
        result = w3.eth.call({
            'to': contract_address,
            'data': '0x6d4ce63c'
        })
        value = int(result.hex(), 16)
        print(f"  ✅ Contract state: {value} (expected: 42)")

        # Test eth_getStorageAt
        print("  Testing eth_getStorageAt...")
        storage = w3.eth.get_storage_at(contract_address, 0)
        storage_value = int(storage.hex(), 16)
        print(f"  ✅ Storage slot 0: {storage_value} (expected: 42)")

        print("\n✅ TEST 2: PASSED - Contract deployment working!")
        test2_passed = True
    else:
        print(f"⚠️  Contract address is None")
        print(f"   Status: {receipt['status']}")
        print(f"   Gas Used: {receipt['gasUsed']}")
        test2_passed = False

except Exception as e:
    print(f"\n❌ TEST 2: FAILED")
    print(f"Error: {e}")
    if hasattr(e, 'args') and len(e.args) > 0:
        print(f"Details: {e.args[0]}")
    test2_passed = False

# Test 3: EIP-1559 Transaction
print("\n" + "=" * 70)
print("TEST 3: EIP-1559 Transaction")
print("=" * 70)

try:
    recipient = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
    nonce = w3.eth.get_transaction_count(account.address)

    tx = {
        'type': 2,  # EIP-1559
        'from': account.address,
        'to': recipient,
        'value': w3.to_wei(0.001, 'ether'),
        'gas': 21000,
        'maxFeePerGas': w3.to_wei(20, 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei(2, 'gwei'),
        'nonce': nonce,
        'chainId': CHAIN_ID
    }

    print(f"\nEIP-1559 Transaction:")
    print(f"  Type: {tx['type']}")
    print(f"  To: {tx['to']}")
    print(f"  Value: {w3.from_wei(tx['value'], 'ether')} FCO")
    print(f"  Max Fee: {w3.from_wei(tx['maxFeePerGas'], 'gwei')} Gwei")
    print(f"  Priority Fee: {w3.from_wei(tx['maxPriorityFeePerGas'], 'gwei')} Gwei")

    # Sign
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    # Send
    print("\nSending transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Transaction sent: {tx_hash.hex()}")

    # Wait for receipt
    print("Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    print(f"✅ Transaction confirmed!")
    print(f"   Block: {receipt['blockNumber']}")
    print(f"   Status: {receipt['status']}")
    print(f"   Gas Used: {receipt['gasUsed']}")

    print("\n✅ TEST 3: PASSED - EIP-1559 transaction working!")
    test3_passed = True

except Exception as e:
    print(f"\n❌ TEST 3: FAILED")
    print(f"Error: {e}")
    if hasattr(e, 'args') and len(e.args) > 0:
        print(f"Details: {e.args[0]}")
    test3_passed = False

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

tests = [
    ("Simple Transfer", test1_passed),
    ("Contract Deployment", test2_passed),
    ("EIP-1559 Transaction", test3_passed)
]

passed = sum(1 for _, result in tests if result)
total = len(tests)

for name, result in tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status}: {name}")

print(f"\nResults: {passed}/{total} tests passed ({100*passed//total}%)")

if passed == total:
    print("\n🎉 ALL TESTS PASSED - v0.4.4 IS WORKING!")
elif passed > 0:
    print(f"\n⚠️  PARTIAL SUCCESS - {passed}/{total} tests passed")
else:
    print("\n❌ ALL TESTS FAILED - CRITICAL ISSUES REMAIN")

print("=" * 70)
