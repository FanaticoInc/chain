#!/usr/bin/env python3
"""
Test EIP-1559 vs Legacy Transaction Encoding on FCO Chain
Reproduce the RLP encoding error seen in the screenshot
"""

from web3 import Web3
from eth_account import Account
import json

# Connect to FCO chain
w3 = Web3(Web3.HTTPProvider('http://paratime.fanati.co:8545'))

print("=" * 80)
print("EIP-1559 vs Legacy Transaction Test")
print("=" * 80)
print()

# Check connection
if not w3.is_connected():
    print("❌ ERROR: Cannot connect to paratime.fanati.co:8545")
    exit(1)

print(f"✅ Connected to FCO chain")
print(f"Chain ID: {w3.eth.chain_id}")
print()

# Test account (from screenshot - Hardhat account #0)
test_account = {
    "address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
}

recipient = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

# Check balance
balance = w3.eth.get_balance(test_account["address"])
print(f"Account: {test_account['address']}")
print(f"Balance: {w3.from_wei(balance, 'ether')} FCO")
print()

if balance == 0:
    print("❌ ERROR: Test account has zero balance")
    exit(1)

account = Account.from_key(test_account["private_key"])
nonce = w3.eth.get_transaction_count(test_account["address"])

print(f"Current Nonce: {nonce}")
print()

# Test 1: EIP-1559 Transaction (Type 2) - EXPECTED TO FAIL
print("=" * 80)
print("Test 1: EIP-1559 Transaction (Type 2)")
print("=" * 80)
print()

try:
    tx_eip1559 = {
        'type': 2,  # EIP-1559
        'chainId': 1234,
        'nonce': nonce,
        'to': recipient,
        'value': w3.to_wei(0.001, 'ether'),  # 1 finney like in screenshot
        'gas': 21000,
        'maxFeePerGas': w3.to_wei(1, 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei(1, 'gwei'),
    }

    print("Transaction object:")
    print(json.dumps({k: str(v) for k, v in tx_eip1559.items()}, indent=2))
    print()

    # Sign transaction
    signed = account.sign_transaction(tx_eip1559)

    print(f"Signed transaction (raw):")
    print(f"  Length: {len(signed.raw_transaction)} bytes")
    print(f"  Hex: {signed.raw_transaction.hex()[:100]}...")
    print()

    # Try to send
    print("Sending EIP-1559 transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    print(f"✅ SUCCESS: EIP-1559 transaction sent!")
    print(f"TX Hash: {tx_hash.hex()}")
    print()

except Exception as e:
    print(f"❌ FAILED: EIP-1559 transaction rejected")
    print(f"Error: {e}")
    print()

    # Check if it's the RLP error we expect
    error_str = str(e)
    if "Invalid RLP" in error_str or "superfluous bytes" in error_str:
        print("✅ REPRODUCED: This is the same error as in the screenshot!")
        print("   'Invalid RLP encoded transaction: RLP string ends with X superfluous bytes'")
    print()

# Test 2: Legacy Transaction (Type 0) - EXPECTED TO WORK
print("=" * 80)
print("Test 2: Legacy Transaction (Type 0)")
print("=" * 80)
print()

try:
    tx_legacy = {
        'nonce': nonce,
        'to': recipient,
        'value': w3.to_wei(0.001, 'ether'),  # Same value as EIP-1559 test
        'gas': 21000,
        'gasPrice': w3.to_wei(20, 'gwei'),  # Use gasPrice instead of maxFee
        'chainId': 1234
    }

    print("Transaction object:")
    print(json.dumps({k: str(v) for k, v in tx_legacy.items()}, indent=2))
    print()

    # Sign transaction
    signed = account.sign_transaction(tx_legacy)

    print(f"Signed transaction (raw):")
    print(f"  Length: {len(signed.raw_transaction)} bytes")
    print(f"  Hex: {signed.raw_transaction.hex()[:100]}...")
    print()

    # Try to send
    print("Sending legacy transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    print(f"✅ SUCCESS: Legacy transaction sent!")
    print(f"TX Hash: {tx_hash.hex()}")
    print()

    # Wait for confirmation
    import time
    time.sleep(2)

    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        print(f"Transaction mined in block: {receipt['blockNumber']}")
        print(f"Status: {'✅ Success' if receipt['status'] == 1 else '❌ Failed'}")
        print()
    except:
        print("Transaction pending confirmation...")
        print()

except Exception as e:
    print(f"❌ FAILED: Legacy transaction also rejected")
    print(f"Error: {e}")
    print()

# Summary
print("=" * 80)
print("Summary & Diagnosis")
print("=" * 80)
print()
print("The FCO chain's RLP decoder does not support EIP-1559 transactions (Type 2).")
print()
print("**Root Cause:**")
print("  - EIP-1559 uses a different RLP envelope: 0x02 || RLP([...])")
print("  - Legacy transactions use: RLP([nonce, gasPrice, gasLimit, to, value, data, v, r, s])")
print("  - The decoder expects legacy format and sees 'extra bytes' in EIP-1559 format")
print()
print("**Solution:**")
print("  - Use legacy transactions (Type 0) with 'gasPrice' instead of EIP-1559")
print("  - OR: Update FCO chain to support EIP-1559 transaction decoding")
print()
print("**Workaround for users:**")
print("  - In Hardhat: Set 'type: 0' in transaction config")
print("  - In ethers.js: Use legacy transaction type")
print("  - In web3.py: Omit 'type' field and use 'gasPrice' instead of 'maxFeePerGas'")
print()
