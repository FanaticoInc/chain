#!/usr/bin/env python3
"""
Detailed v0.3.3 Testing - Investigate transaction issues
"""

from web3 import Web3
from eth_account import Account
import time

w3 = Web3(Web3.HTTPProvider('http://paratime.fanati.co:8545'))

print("=" * 80)
print("v0.3.3 Detailed Investigation")
print("=" * 80)
print()

# Test account
test_account = {
    "address": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4",
    "private_key": "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6"
}

recipient = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

# Create account object
account = Account.from_key(test_account["private_key"])

print(f"Test Account Address: {test_account['address']}")
print(f"Account from Private Key: {account.address}")
print(f"Match: {account.address.lower() == test_account['address'].lower()}")
print()

# Check balance
balance = w3.eth.get_balance(test_account["address"])
print(f"Balance: {w3.from_wei(balance, 'ether')} FCO")
print()

# Test Case 1: Simple 1 wei transaction
print("=" * 80)
print("Test 1: Sending 1 wei (CRITICAL edge case from v0.3.2)")
print("=" * 80)

try:
    nonce = w3.eth.get_transaction_count(test_account["address"])
    print(f"Current Nonce: {nonce}")

    tx = {
        'nonce': nonce,
        'to': recipient,
        'value': 1,  # 1 wei
        'gas': 21000,
        'gasPrice': w3.to_wei(20, 'gwei'),
        'chainId': 1234
    }

    print(f"Transaction: {tx}")
    print()

    # Sign
    signed = account.sign_transaction(tx)
    print(f"Raw Transaction: {signed.raw_transaction.hex()[:100]}...")
    print()

    # Send
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    tx_hash_hex = tx_hash.hex()
    print(f"TX Hash: {tx_hash_hex}")
    print()

    # Wait for mining
    print("Waiting 5 seconds for mining...")
    time.sleep(5)

    # Get transaction
    try:
        tx_data = w3.eth.get_transaction(tx_hash)
        print(f"Transaction Found: ✅")
        print(f"  FROM: {tx_data['from']}")
        print(f"  TO: {tx_data['to']}")
        print(f"  VALUE: {tx_data['value']} wei")
        print(f"  NONCE: {tx_data['nonce']}")
        print(f"  BLOCK: {tx_data.get('blockNumber', 'pending')}")
        print()

        # Check FROM address
        if tx_data['from'].lower() == test_account['address'].lower():
            print(f"  FROM Address: ✅ CORRECT")
        else:
            print(f"  FROM Address: ❌ WRONG")
            print(f"    Expected: {test_account['address']}")
            print(f"    Got: {tx_data['from']}")
        print()

        # Check VALUE
        if tx_data['value'] == 1:
            print(f"  VALUE: ✅ CORRECT (v0.3.3 FIX WORKING!)")
        else:
            print(f"  VALUE: ❌ WRONG (v0.3.3 fix NOT working)")
            print(f"    Expected: 1 wei")
            print(f"    Got: {tx_data['value']} wei")
        print()

        # Get receipt
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            print(f"Receipt Found: ✅")
            print(f"  Status: {receipt['status']} ({'SUCCESS' if receipt['status'] == 1 else 'FAILED'})")
            print(f"  Block: {receipt['blockNumber']}")
            print(f"  Gas Used: {receipt['gasUsed']}")
            print()
        except Exception as e:
            print(f"Receipt Error: {e}")
            print()

    except Exception as e:
        print(f"❌ Transaction Not Found: {e}")
        print()

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print()

# Test Case 2: Check block production
print("=" * 80)
print("Test 2: Check recent blocks")
print("=" * 80)

try:
    current_block = w3.eth.block_number
    print(f"Current Block: {current_block}")
    print()

    # Check last 5 blocks
    for i in range(max(0, current_block - 4), current_block + 1):
        try:
            block = w3.eth.get_block(i, full_transactions=True)
            tx_count = len(block['transactions'])
            print(f"Block {i}: {tx_count} transaction(s)")

            if tx_count > 0:
                for tx in block['transactions']:
                    print(f"  TX: {tx['hash'].hex()}")
                    print(f"    FROM: {tx.get('from', 'N/A')}")
                    print(f"    TO: {tx.get('to', 'N/A')}")
                    print(f"    VALUE: {tx.get('value', 0)} wei")
        except Exception as e:
            print(f"Block {i}: Error - {e}")

    print()

except Exception as e:
    print(f"❌ Block Error: {e}")
    print()

print("=" * 80)
print("Investigation Complete")
print("=" * 80)
