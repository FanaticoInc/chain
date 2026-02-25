from web3 import Web3
import json

# Connect to RPC
w3 = Web3(Web3.HTTPProvider('http://paratime.fanati.co:8545'))

print("=" * 70)
print("v0.4.7 RECEIPT STRUCTURE CHECK (Python)")
print("Testing if transactionIndex and cumulativeGasUsed are present")
print("=" * 70)
print()

# Test account (same as JavaScript tests)
private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'
account = w3.eth.account.from_key(private_key)
sender = account.address

print(f"Sender: {sender}")
print(f"Chain ID: {w3.eth.chain_id}")
print(f"Balance: {w3.from_wei(w3.eth.get_balance(sender), 'ether')} FCO")
print()

# Send a transaction
print("=" * 70)
print("Sending test transaction...")
print("=" * 70)

recipient = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'

tx = {
    'from': sender,
    'to': recipient,
    'value': w3.to_wei(0.001, 'ether'),
    'gas': 21000,
    'gasPrice': w3.to_wei(10, 'gwei'),
    'nonce': w3.eth.get_transaction_count(sender),
    'chainId': w3.eth.chain_id
}

# Sign and send
signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print(f"✅ Transaction sent: {tx_hash.hex()}")
print()

# Wait for mining (5 seconds typical)
print("Waiting for transaction to be mined (6 seconds)...")
import time
time.sleep(6)

# Get receipt
print()
print("=" * 70)
print("Fetching transaction receipt...")
print("=" * 70)
print()

receipt = w3.eth.get_transaction_receipt(tx_hash)

if receipt:
    print("✅ Receipt received!")
    print()
    print("📋 Receipt Structure:")
    print(json.dumps(dict(receipt), indent=2, default=str))
    print()
    
    # Check for v0.4.7 fields
    print("=" * 70)
    print("v0.4.7 FIELD VALIDATION")
    print("=" * 70)
    print()
    
    has_tx_index = 'transactionIndex' in receipt and receipt['transactionIndex'] is not None
    has_cumulative_gas = 'cumulativeGasUsed' in receipt and receipt['cumulativeGasUsed'] is not None
    has_v = 'v' in receipt and receipt['v'] is not None
    has_r = 'r' in receipt and receipt['r'] is not None
    has_s = 's' in receipt and receipt['s'] is not None
    
    print(f"{'✅' if has_tx_index else '❌'} transactionIndex: {receipt.get('transactionIndex', 'MISSING')}")
    print(f"{'✅' if has_cumulative_gas else '❌'} cumulativeGasUsed: {receipt.get('cumulativeGasUsed', 'MISSING')}")
    print(f"{'✅' if has_v else '⚠️ '} v (signature): {receipt.get('v', 'MISSING')}")
    print(f"{'✅' if has_r else '⚠️ '} r (signature): {receipt.get('r', 'MISSING') if not has_r else receipt.get('r')[:10] + '...'}")
    print(f"{'✅' if has_s else '⚠️ '} s (signature): {receipt.get('s', 'MISSING') if not has_s else receipt.get('s')[:10] + '...'}")
    print()
    
    # Verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()
    
    if has_tx_index and has_cumulative_gas:
        print("🎉 v0.4.7 CRITICAL FIELDS PRESENT!")
        print("   ✅ transactionIndex: FOUND")
        print("   ✅ cumulativeGasUsed: FOUND")
        if has_v and has_r and has_s:
            print("   ✅ Signature fields (v,r,s): FOUND")
        print()
        print("🟢 FIX APPEARS TO BE APPLIED!")
        print()
        print("Next step: Test with ethers.js to verify JavaScript compatibility")
    else:
        print("❌ v0.4.7 CRITICAL FIELDS MISSING!")
        if not has_tx_index:
            print("   🔴 transactionIndex: MISSING")
        if not has_cumulative_gas:
            print("   🔴 cumulativeGasUsed: MISSING")
        print()
        print("🔴 FIX NOT APPLIED")
    
else:
    print("❌ No receipt found (transaction not mined yet)")

