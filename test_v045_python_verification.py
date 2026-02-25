#!/usr/bin/env python3
"""Quick Python verification for v0.4.5"""

from web3 import Web3

RPC_URL = "http://paratime.fanati.co:8546"
PRIVATE_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
CHAIN_ID = 999999999

print("=" * 70)
print("v0.4.5 PYTHON VERIFICATION")
print("=" * 70)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

print(f"\nAccount: {account.address}")
balance = w3.eth.get_balance(account.address)
print(f"Balance: {w3.from_wei(balance, 'ether')} FCO")

# Quick transaction test
try:
    nonce = w3.eth.get_transaction_count(account.address)

    tx = {
        'from': account.address,
        'to': '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
        'value': w3.to_wei(0.001, 'ether'),
        'gas': 21000,
        'gasPrice': w3.to_wei(10, 'gwei'),
        'nonce': nonce,
        'chainId': CHAIN_ID
    }

    print(f"\nSending Python transaction (nonce {nonce})...")
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Transaction sent: {tx_hash.hex()}")

    print("Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    print(f"✅ Confirmed in block {receipt['blockNumber']}")
    print(f"   Status: {receipt['status']}")
    print(f"   Gas Used: {receipt['gasUsed']}")

    print("\n✅ PYTHON WORKING - Transaction successful")

except Exception as e:
    print(f"\n❌ PYTHON FAILED: {e}")

print("=" * 70)
