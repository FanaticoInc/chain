#!/usr/bin/env python3
"""
v0.4.2 Current Status Test
Tests contract deployment, eth_call, eth_getCode, eth_getStorageAt
"""

import json
import requests
from web3 import Web3
import time

# Configuration
RPC_URL = "http://paratime.fanati.co:8546"
CHAIN_ID = 999999999

# Test account (Hardhat account #1)
PRIVATE_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
ACCOUNT = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

# SimpleStorage bytecode (sets storage[0] = 42 in constructor)
BYTECODE = "0x608060405234801561000f575f80fd5b50602a5f5560bb806100205f395ff3fe6080604052348015600e575f80fd5b50600436106030575f3560e01c80636d4ce63c146034578063e5c19b2d14604c575b5f80fd5b603a6056565b60405190815260200160405180910390f35b6054605e565b005b5f5f54905090565b602a5f8190555056fea2646970667358221220c85b4c6f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f64736f6c63430008140033"

def rpc_call(method, params):
    """Make JSON-RPC call"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    response = requests.post(RPC_URL, json=payload, headers={"Content-Type": "application/json"})
    return response.json()

def main():
    print("=" * 70)
    print("Fanatico FCO Chain v0.4.2 - Current Status Test")
    print("=" * 70)
    print()

    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tests": []
    }

    # Test 1: Network Connectivity
    print("Test 1: Network Connectivity")
    print("-" * 70)
    try:
        chain_id_response = rpc_call("eth_chainId", [])
        chain_id = int(chain_id_response["result"], 16)
        print(f"✅ PASS - Chain ID: {chain_id}")
        results["tests"].append({"test": "Network Connectivity", "status": "PASS", "details": f"Chain ID: {chain_id}"})
    except Exception as e:
        print(f"❌ FAIL - {e}")
        results["tests"].append({"test": "Network Connectivity", "status": "FAIL", "error": str(e)})
    print()

    # Test 2: Account Balance
    print("Test 2: Account Balance")
    print("-" * 70)
    try:
        balance_response = rpc_call("eth_getBalance", [ACCOUNT, "latest"])
        balance_wei = int(balance_response["result"], 16)
        balance_fco = balance_wei / 10**18
        print(f"✅ PASS - Balance: {balance_fco:.4f} FCO")
        results["tests"].append({"test": "Account Balance", "status": "PASS", "details": f"{balance_fco:.4f} FCO"})
    except Exception as e:
        print(f"❌ FAIL - {e}")
        results["tests"].append({"test": "Account Balance", "status": "FAIL", "error": str(e)})
    print()

    # Test 3: Contract Deployment
    print("Test 3: Contract Deployment")
    print("-" * 70)
    try:
        nonce_response = rpc_call("eth_getTransactionCount", [ACCOUNT, "latest"])
        nonce = int(nonce_response["result"], 16)

        # Build deployment transaction
        tx = {
            "from": ACCOUNT,
            "nonce": nonce,
            "gasPrice": 10000000000,  # 10 Gwei
            "gas": 500000,
            "data": BYTECODE,
            "chainId": CHAIN_ID
        }

        # Sign transaction
        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

        # Send transaction (handle different web3.py versions)
        raw_tx = signed.rawTransaction if hasattr(signed, 'rawTransaction') else signed.raw_transaction
        if isinstance(raw_tx, bytes):
            raw_tx_hex = "0x" + raw_tx.hex()
        else:
            raw_tx_hex = raw_tx if raw_tx.startswith("0x") else "0x" + raw_tx

        tx_hash_response = rpc_call("eth_sendRawTransaction", [raw_tx_hex])

        if "error" in tx_hash_response:
            print(f"❌ FAIL - {tx_hash_response['error']}")
            results["tests"].append({"test": "Contract Deployment", "status": "FAIL", "error": tx_hash_response['error']})
        else:
            tx_hash = tx_hash_response["result"]
            print(f"Transaction Hash: {tx_hash}")

            # Wait for receipt
            time.sleep(3)

            receipt_response = rpc_call("eth_getTransactionReceipt", [tx_hash])
            receipt = receipt_response.get("result")

            if receipt:
                contract_address = receipt.get("contractAddress")
                gas_used = int(receipt.get("gasUsed", "0x0"), 16)
                status = int(receipt.get("status", "0x0"), 16)

                print(f"Contract Address: {contract_address}")
                print(f"Gas Used: {gas_used}")
                print(f"Status: {status}")

                # Check gas usage
                if gas_used == 21000:
                    print("⚠️  WARNING - Gas usage is 21000 (simple transfer, not deployment)")
                    results["tests"].append({
                        "test": "Contract Deployment",
                        "status": "WARNING",
                        "details": f"Gas: {gas_used} (suspicious)",
                        "contract_address": contract_address
                    })
                elif gas_used > 100000:
                    print(f"✅ PASS - Deployment gas usage looks correct ({gas_used})")
                    results["tests"].append({
                        "test": "Contract Deployment",
                        "status": "PASS",
                        "details": f"Gas: {gas_used}",
                        "contract_address": contract_address
                    })

                    # Test 4: eth_getCode
                    print()
                    print("Test 4: eth_getCode")
                    print("-" * 70)
                    try:
                        code_response = rpc_call("eth_getCode", [contract_address, "latest"])

                        if "error" in code_response:
                            print(f"❌ FAIL - {code_response['error']}")
                            results["tests"].append({"test": "eth_getCode", "status": "FAIL", "error": code_response['error']})
                        else:
                            code = code_response["result"]
                            print(f"Bytecode: {code[:66]}... ({len(code)} chars)")

                            if code == "0x" or code == "0x0":
                                print("❌ FAIL - No bytecode at contract address")
                                results["tests"].append({"test": "eth_getCode", "status": "FAIL", "details": "No bytecode"})
                            else:
                                print("✅ PASS - Bytecode exists")
                                results["tests"].append({"test": "eth_getCode", "status": "PASS", "details": f"Bytecode length: {len(code)}"})
                    except Exception as e:
                        print(f"❌ FAIL - {e}")
                        results["tests"].append({"test": "eth_getCode", "status": "FAIL", "error": str(e)})

                    # Test 5: eth_call (read constructor value)
                    print()
                    print("Test 5: eth_call (read constructor value = 42)")
                    print("-" * 70)
                    try:
                        # Call get() function (0x6d4ce63c)
                        call_response = rpc_call("eth_call", [{
                            "to": contract_address,
                            "data": "0x6d4ce63c"
                        }, "latest"])

                        if "error" in call_response:
                            print(f"❌ FAIL - {call_response['error']}")
                            results["tests"].append({"test": "eth_call (constructor)", "status": "FAIL", "error": call_response['error']})
                        else:
                            value_hex = call_response["result"]
                            value = int(value_hex, 16)
                            print(f"Value: {value} (expected 42)")

                            if value == 42:
                                print("✅ PASS - Constructor executed correctly")
                                results["tests"].append({"test": "eth_call (constructor)", "status": "PASS", "details": f"Value: {value}"})
                            else:
                                print(f"❌ FAIL - Expected 42, got {value}")
                                results["tests"].append({"test": "eth_call (constructor)", "status": "FAIL", "details": f"Expected 42, got {value}"})
                    except Exception as e:
                        print(f"❌ FAIL - {e}")
                        results["tests"].append({"test": "eth_call (constructor)", "status": "FAIL", "error": str(e)})

                    # Test 6: eth_getStorageAt
                    print()
                    print("Test 6: eth_getStorageAt (slot 0 = 42)")
                    print("-" * 70)
                    try:
                        storage_response = rpc_call("eth_getStorageAt", [contract_address, "0x0", "latest"])

                        if "error" in storage_response:
                            print(f"❌ FAIL - {storage_response['error']}")
                            results["tests"].append({"test": "eth_getStorageAt", "status": "FAIL", "error": storage_response['error']})
                        else:
                            storage_hex = storage_response["result"]
                            storage_value = int(storage_hex, 16)
                            print(f"Storage[0]: {storage_value} (expected 42)")

                            if storage_value == 42:
                                print("✅ PASS - Storage initialized correctly")
                                results["tests"].append({"test": "eth_getStorageAt", "status": "PASS", "details": f"Value: {storage_value}"})
                            else:
                                print(f"❌ FAIL - Expected 42, got {storage_value}")
                                results["tests"].append({"test": "eth_getStorageAt", "status": "FAIL", "details": f"Expected 42, got {storage_value}"})
                    except Exception as e:
                        print(f"❌ FAIL - {e}")
                        results["tests"].append({"test": "eth_getStorageAt", "status": "FAIL", "error": str(e)})

            else:
                print("❌ FAIL - No receipt received")
                results["tests"].append({"test": "Contract Deployment", "status": "FAIL", "error": "No receipt"})
    except Exception as e:
        print(f"❌ FAIL - {e}")
        results["tests"].append({"test": "Contract Deployment", "status": "FAIL", "error": str(e)})

    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)

    # Count results
    passed = sum(1 for t in results["tests"] if t["status"] == "PASS")
    failed = sum(1 for t in results["tests"] if t["status"] == "FAIL")
    warnings = sum(1 for t in results["tests"] if t["status"] == "WARNING")
    total = len(results["tests"])

    print(f"✅ PASS: {passed}")
    print(f"❌ FAIL: {failed}")
    print(f"⚠️  WARNING: {warnings}")
    print(f"Total: {total}")
    print()

    if failed == 0 and warnings == 0:
        print("🎉 ALL TESTS PASSED - v0.4.2 is 100% functional!")
    elif failed == 0:
        print("⚠️  All tests passed but with warnings")
    else:
        print("❌ Some tests failed")

    # Save results
    with open("v042_current_status_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to: v042_current_status_results.json")

if __name__ == "__main__":
    main()
