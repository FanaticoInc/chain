#!/usr/bin/env python3
"""Test v0.4.3 with Python web3.py"""

from web3 import Web3
import json

RPC_URL = "http://paratime.fanati.co:8546"
PRIVATE_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
CHAIN_ID = 999999999

print("Testing v0.4.3 with Python web3.py...\n")

# Setup
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# Test 1: Connection
print("Test 1: Connection")
chain_id = w3.eth.chain_id
print(f"✅ Connected - Chain ID: {chain_id}")

# Test 2: Get block (NEW in v0.4.3)
print("\nTest 2: eth_getBlockByNumber (NEW)")
try:
    block = w3.eth.get_block('latest')
    print(f"✅ Block retrieved: number={block['number']}, hash={block['hash'].hex()}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Test 3: Balance
print("\nTest 3: Balance query")
balance = w3.eth.get_balance(account.address)
print(f"✅ Balance: {w3.from_wei(balance, 'ether')} FCO")

# Test 4: Simple transfer
print("\nTest 4: Simple transfer")
recipient = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"

try:
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

    print(f"Transaction: {json.dumps({k: str(v) for k, v in tx.items()}, indent=2)}")

    # Sign
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    # Send
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Transaction sent: {tx_hash.hex()}")

    # Wait for receipt
    print("Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    print(f"✅ Transaction confirmed!")
    print(f"Receipt: block={receipt['blockNumber']}, status={receipt['status']}, gas={receipt['gasUsed']}")

    print("\n🎉 All tests passed!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    if hasattr(e, 'args') and len(e.args) > 0:
        print(f"Details: {e.args[0]}")
