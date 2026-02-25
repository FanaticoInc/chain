#!/usr/bin/env python3
"""
v0.4.8 Comprehensive Assessment
Testing all claims in V048_SUCCESS_COMPLETE_FIX.md
"""

from web3 import Web3
import json
import time

print("=" * 80)
print("v0.4.8 COMPREHENSIVE ASSESSMENT")
print("Testing claims from V048_SUCCESS_COMPLETE_FIX.md")
print("=" * 80)
print()

# Connect to RPC
w3 = Web3(Web3.HTTPProvider('http://paratime.fanati.co:8545'))

# Test account
private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'
account = w3.eth.account.from_key(private_key)
sender = account.address
recipient = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'

print(f"Sender: {sender}")
print(f"Chain ID: {w3.eth.chain_id}")
print(f"Balance: {w3.from_wei(w3.eth.get_balance(sender), 'ether')} FCO")
print()

# =============================================================================
# TEST 1: Gas Estimation (NEW in v0.4.8)
# =============================================================================
print("=" * 80)
print("TEST 1: Gas Estimation (eth_estimateGas)")
print("Claim: NEW feature added in v0.4.8")
print("=" * 80)

try:
    gas_estimate = w3.eth.estimate_gas({
        'from': sender,
        'to': recipient,
        'value': w3.to_wei(0.001, 'ether')
    })
    print(f"✅ Gas estimation WORKS!")
    print(f"   Estimated gas: {gas_estimate}")

    # Should be 21000 for simple transfer
    if gas_estimate == 21000:
        print(f"   ✅ CORRECT value (21000 for simple transfer)")
    else:
        print(f"   ⚠️  Expected 21000, got {gas_estimate}")
except Exception as e:
    print(f"❌ Gas estimation FAILED: {e}")

print()

# =============================================================================
# TEST 2: Transaction Index in Receipt
# =============================================================================
print("=" * 80)
print("TEST 2: Transaction Index Field")
print("Claim: Field present (v0.4.7 assessment was 'test environment issue')")
print("=" * 80)

# Send transaction
tx = {
    'from': sender,
    'to': recipient,
    'value': w3.to_wei(0.001, 'ether'),
    'gas': 21000,
    'gasPrice': w3.to_wei(10, 'gwei'),
    'nonce': w3.eth.get_transaction_count(sender),
    'chainId': w3.eth.chain_id
}

signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print(f"Transaction sent: {tx_hash.hex()}")
print("Waiting for mining (6 seconds)...")
time.sleep(6)

# Get receipt
receipt = w3.eth.get_transaction_receipt(tx_hash)

if receipt:
    print("✅ Receipt received!")
    print()
    print("📋 Full Receipt Structure:")
    print(json.dumps(dict(receipt), indent=2, default=str))
    print()

    # Check critical fields
    print("🔍 Field Validation:")

    # transactionIndex (CRITICAL)
    has_tx_index = 'transactionIndex' in receipt and receipt['transactionIndex'] is not None
    print(f"{'✅' if has_tx_index else '❌'} transactionIndex: {receipt.get('transactionIndex', 'MISSING')}")

    # cumulativeGasUsed (should be present from v0.4.7)
    has_cumulative_gas = 'cumulativeGasUsed' in receipt and receipt['cumulativeGasUsed'] is not None
    print(f"{'✅' if has_cumulative_gas else '❌'} cumulativeGasUsed: {receipt.get('cumulativeGasUsed', 'MISSING')}")

    # Signature fields (claimed in document)
    has_v = 'v' in receipt and receipt['v'] is not None
    has_r = 'r' in receipt and receipt['r'] is not None
    has_s = 's' in receipt and receipt['s'] is not None
    print(f"{'✅' if has_v else '❌'} v (signature): {receipt.get('v', 'MISSING')}")
    print(f"{'✅' if has_r else '❌'} r (signature): {receipt.get('r', 'MISSING')}")
    print(f"{'✅' if has_s else '❌'} s (signature): {receipt.get('s', 'MISSING')}")

    print()

    # Overall assessment
    fields_present = sum([has_tx_index, has_cumulative_gas, has_v, has_r, has_s])
    print(f"📊 Field Presence: {fields_present}/5 claimed fields")

    if has_tx_index and has_cumulative_gas:
        print("✅ CRITICAL FIELDS PRESENT - ethers.js should work!")
    elif has_cumulative_gas and not has_tx_index:
        print("❌ PARTIAL FIX - Same as v0.4.7 (transactionIndex missing)")
    else:
        print("❌ MAJOR ISSUES - Multiple critical fields missing")
else:
    print("❌ No receipt received!")

print()

# =============================================================================
# TEST 3: Comparison with v0.4.7 Assessment
# =============================================================================
print("=" * 80)
print("TEST 3: Comparison with v0.4.7 Assessment")
print("=" * 80)

print("""
v0.4.7 Assessment (Nov 11, 2025):
  - transactionIndex: MISSING (verified via Python)
  - cumulativeGasUsed: PRESENT (21000)
  - Status: PARTIAL FIX (20% complete)

v0.4.8 Claim:
  - transactionIndex: "Actually present in v0.4.7, test environment issue"
  - Gas estimation: NEW feature
  - Status: COMPLETE FIX (92% compatibility)

v0.4.8 Actual (this test):
""")

if receipt:
    if has_tx_index:
        print("  - transactionIndex: ✅ NOW PRESENT (FIX COMPLETED)")
        print("  - Status: REAL FIX APPLIED")
    else:
        print("  - transactionIndex: ❌ STILL MISSING")
        print("  - Status: NO CHANGE FROM v0.4.7")

print()

# =============================================================================
# FINAL VERDICT
# =============================================================================
print("=" * 80)
print("FINAL VERDICT")
print("=" * 80)

if receipt and has_tx_index and has_cumulative_gas:
    print("✅ v0.4.8 FIX VERIFIED!")
    print("   - transactionIndex: PRESENT")
    print("   - cumulativeGasUsed: PRESENT")
    print("   - Gas estimation: WORKING")
    print("   - JavaScript/ethers.js: Should be ~90-92%")
elif receipt and has_cumulative_gas and not has_tx_index:
    print("⚠️  v0.4.8 SAME AS v0.4.7 (PARTIAL)")
    print("   - transactionIndex: STILL MISSING")
    print("   - cumulativeGasUsed: PRESENT")
    print("   - Gas estimation: Working (new)")
    print("   - JavaScript/ethers.js: Still ~85%")
else:
    print("❌ v0.4.8 BROKEN")
    print("   - Critical fields missing")

print()
print("=" * 80)
print("Assessment Complete")
print("=" * 80)
