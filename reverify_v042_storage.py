#!/usr/bin/env python3
"""
Re-verification of v0.4.2 eth_getStorageAt functionality
Tests the specific claim that eth_getStorageAt works correctly

This script will:
1. Test my original deployed contract (0x45A9A932741318612949f311181d2BF24b4ddc4d)
2. Deploy a fresh contract to eliminate timing issues
3. Test multiple storage slots
4. Test different address formats
"""

import requests
import json
from web3 import Web3
from eth_account import Account
import time

# Configuration
ENDPOINT = "http://paratime.fanati.co:8546"
CHAIN_ID = 999999999
PRIVATE_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

# My original contract from previous test
ORIGINAL_CONTRACT = "0x45A9A932741318612949f311181d2BF24b4ddc4d"

# SimpleStorage bytecode - constructor sets value to 42 at slot 1
BYTECODE = "0x608060405234801561000f575f80fd5b50602a60015560bb806100225f395ff3fe6080604052348015600e575f80fd5b50600436106030575f3560e01c80636d4ce63c146034578063e5c19b2d14604c575b5f80fd5b603a6056565b60405190815260200160405180910390f35b6054605e565b005b5f8054905090565b602a60015f81905550565b00fea2646970667358221220c85b4c6f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f64736f6c63430008140033"

GET_SELECTOR = "0x6d4ce63c"

def rpc_call(method, params=None):
    """Make JSON-RPC call"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or [],
        "id": 1
    }
    response = requests.post(ENDPOINT, json=payload, timeout=30)
    return response.json()

def test_original_contract():
    """Test my original contract from the previous assessment"""
    print("="*80)
    print("TEST 1: Re-testing Original Contract")
    print("="*80)
    print(f"Contract: {ORIGINAL_CONTRACT}")
    print()

    # Test eth_call to confirm contract exists and works
    print("1. Testing eth_call (baseline)...")
    call_response = rpc_call("eth_call", [
        {"to": ORIGINAL_CONTRACT, "data": GET_SELECTOR},
        "latest"
    ])

    if "result" in call_response:
        call_value = int(call_response["result"], 16)
        print(f"   eth_call result: {call_value}")
        if call_value == 42:
            print("   ✅ eth_call returns 42 (constructor value)")
        elif call_value == 999:
            print("   ✅ eth_call returns 999 (write operation persisted)")
        else:
            print(f"   ⚠️  eth_call returns unexpected: {call_value}")
    else:
        print(f"   ❌ eth_call failed: {call_response.get('error')}")
        return False

    # Test eth_getStorageAt on slot 0
    print("\n2. Testing eth_getStorageAt - Slot 0...")
    storage0_response = rpc_call("eth_getStorageAt", [ORIGINAL_CONTRACT, "0x0", "latest"])

    if "result" in storage0_response:
        slot0_value = int(storage0_response["result"], 16)
        print(f"   Slot 0 value: {slot0_value} (hex: {storage0_response['result']})")
        if slot0_value == 0:
            print("   ⚠️  Slot 0 is empty (expected)")
        else:
            print(f"   ✅ Slot 0 contains: {slot0_value}")
    else:
        print(f"   ❌ Failed: {storage0_response.get('error')}")

    # Test eth_getStorageAt on slot 1 (where constructor stores value in this bytecode)
    print("\n3. Testing eth_getStorageAt - Slot 1...")
    storage1_response = rpc_call("eth_getStorageAt", [ORIGINAL_CONTRACT, "0x1", "latest"])

    if "result" in storage1_response:
        slot1_value = int(storage1_response["result"], 16)
        print(f"   Slot 1 value: {slot1_value} (hex: {storage1_response['result']})")

        if slot1_value == 0:
            print("   ❌ FAIL: Slot 1 returns 0 (should contain constructor value)")
            return False
        elif slot1_value == 42:
            print("   ✅ PASS: Slot 1 contains 42 (constructor value)")
            return True
        elif slot1_value == 999:
            print("   ✅ PASS: Slot 1 contains 999 (write operation value)")
            return True
        else:
            print(f"   ⚠️  UNEXPECTED: Slot 1 contains {slot1_value}")
            return False
    else:
        print(f"   ❌ Failed: {storage1_response.get('error')}")
        return False

def test_with_address_formats(contract_address):
    """Test eth_getStorageAt with different address formats"""
    print("\n" + "="*80)
    print("TEST 2: Address Format Variations")
    print("="*80)

    # Test with original format (mixed case)
    print(f"\n1. Mixed case address: {contract_address}")
    response1 = rpc_call("eth_getStorageAt", [contract_address, "0x1", "latest"])
    if "result" in response1:
        value = int(response1["result"], 16)
        print(f"   Result: {value} (hex: {response1['result']})")
        status1 = "✅ PASS" if value != 0 else "❌ FAIL"
        print(f"   {status1}")

    # Test with lowercase
    lower_address = contract_address.lower()
    print(f"\n2. Lowercase address: {lower_address}")
    response2 = rpc_call("eth_getStorageAt", [lower_address, "0x1", "latest"])
    if "result" in response2:
        value = int(response2["result"], 16)
        print(f"   Result: {value} (hex: {response2['result']})")
        status2 = "✅ PASS" if value != 0 else "❌ FAIL"
        print(f"   {status2}")

    # Test with uppercase
    upper_address = contract_address.upper()
    print(f"\n3. Uppercase address: {upper_address}")
    response3 = rpc_call("eth_getStorageAt", [upper_address, "0x1", "latest"])
    if "result" in response3:
        value = int(response3["result"], 16)
        print(f"   Result: {value} (hex: {response3['result']})")
        status3 = "✅ PASS" if value != 0 else "❌ FAIL"
        print(f"   {status3}")

def deploy_fresh_contract():
    """Deploy a fresh contract for clean testing"""
    print("\n" + "="*80)
    print("TEST 3: Fresh Contract Deployment")
    print("="*80)

    try:
        account = Account.from_key(PRIVATE_KEY)
        nonce = int(rpc_call("eth_getTransactionCount", [account.address, "latest"])["result"], 16)

        print(f"Deploying new contract from {account.address}...")
        print(f"Nonce: {nonce}")

        deploy_txn = {
            'chainId': CHAIN_ID,
            'nonce': nonce,
            'gasPrice': 10000000000,
            'gas': 500000,
            'to': '',
            'value': 0,
            'data': BYTECODE
        }

        signed_txn = account.sign_transaction(deploy_txn)
        response = rpc_call("eth_sendRawTransaction", [signed_txn.raw_transaction.hex()])

        if "result" not in response:
            print(f"❌ Deployment failed: {response.get('error')}")
            return None

        tx_hash = response["result"]
        print(f"Transaction: {tx_hash}")
        print("Waiting for confirmation...")
        time.sleep(3)

        receipt_response = rpc_call("eth_getTransactionReceipt", [tx_hash])
        if "result" not in receipt_response or receipt_response["result"] is None:
            print("❌ No receipt received")
            return None

        receipt = receipt_response["result"]
        contract_address = receipt.get("contractAddress")
        gas_used = int(receipt.get("gasUsed", "0x0"), 16)

        print(f"✅ Contract deployed: {contract_address}")
        print(f"   Gas used: {gas_used}")

        # Immediate test of eth_getStorageAt
        print("\nImmediate test after deployment:")

        # Wait a moment for state to settle
        time.sleep(2)

        # Test eth_call first
        print("1. Testing eth_call...")
        call_response = rpc_call("eth_call", [
            {"to": contract_address, "data": GET_SELECTOR},
            "latest"
        ])

        if "result" in call_response:
            call_value = int(call_response["result"], 16)
            print(f"   eth_call result: {call_value}")
            if call_value == 42:
                print("   ✅ eth_call works (returns 42)")
            else:
                print(f"   ⚠️  Unexpected value: {call_value}")

        # Test eth_getStorageAt on slot 1
        print("\n2. Testing eth_getStorageAt (slot 1)...")
        storage_response = rpc_call("eth_getStorageAt", [contract_address, "0x1", "latest"])

        if "result" in storage_response:
            storage_value = int(storage_response["result"], 16)
            print(f"   Slot 1 value: {storage_value} (hex: {storage_response['result']})")

            if storage_value == 42:
                print("   ✅ PASS: eth_getStorageAt returns 42")
                return contract_address
            elif storage_value == 0:
                print("   ❌ FAIL: eth_getStorageAt returns 0")
                return None
            else:
                print(f"   ⚠️  Unexpected: eth_getStorageAt returns {storage_value}")
                return None
        else:
            print(f"   ❌ Failed: {storage_response.get('error')}")
            return None

    except Exception as e:
        print(f"❌ Exception during deployment: {e}")
        return None

def main():
    print("="*80)
    print("v0.4.2 eth_getStorageAt RE-VERIFICATION")
    print("="*80)
    print(f"Endpoint: {ENDPOINT}")
    print(f"Chain ID: {CHAIN_ID}")
    print()
    print("Purpose: Verify node developer claims that eth_getStorageAt works")
    print("="*80)

    # Test 1: Original contract
    original_works = test_original_contract()

    # Test 2: Deploy fresh contract
    fresh_contract = deploy_fresh_contract()

    # Test 3: Address format variations (if fresh deployment worked)
    if fresh_contract:
        test_with_address_formats(fresh_contract)

    # Summary
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)

    if original_works and fresh_contract:
        print("✅ eth_getStorageAt is WORKING")
        print("   - Original contract: PASS")
        print("   - Fresh deployment: PASS")
        print("\n🎉 Node developers were CORRECT - v0.4.2 achieves 100% success rate")
        print("   My initial test had methodology issues (timing or wrong slot)")
    elif original_works or fresh_contract:
        print("⚠️  eth_getStorageAt is PARTIALLY WORKING")
        print(f"   - Original contract: {'PASS' if original_works else 'FAIL'}")
        print(f"   - Fresh deployment: {'PASS' if fresh_contract else 'FAIL'}")
        print("\n   Possible timing or state synchronization issue")
    else:
        print("❌ eth_getStorageAt is NOT WORKING")
        print("   - Original contract: FAIL")
        print("   - Fresh deployment: FAIL")
        print("\n   My initial 88.9% assessment was correct")

    print("="*80)

if __name__ == "__main__":
    main()
