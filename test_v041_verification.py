#!/usr/bin/env python3
"""
v0.4.1 Release Verification Test
Date: November 10, 2025
Purpose: Verify all claims in v0.4.1 release notes
"""

import requests
import json
import time
from eth_account import Account
from web3 import Web3
from datetime import datetime

# Configuration
ENDPOINT_URL = "http://paratime.fanati.co:8546"
CHAIN_ID = 999999999
PRIVATE_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

# Simple Storage contract bytecode (compiled 0.8.27)
# constructor() { storedData = 42; }
# get() returns uint256
# set(uint256)
BYTECODE = "0x608060405234801561000f575f80fd5b50602a60015560bb806100225f395ff3fe6080604052348015600e575f80fd5b50600436106030575f3560e01c806360fe47b11460345780636d4ce63c14604c575b5f80fd5b604a60048036038101906046919060895b6001819055506056565b005b60526064565b604051605b9190609f565b60405180910390f35b5f600154905090565b5f8135905060778160ad565b92915050565b5f60208284031215609957609860a9565b5b5f60a484828501606c565b91505092915050565b5f819050919050565b5f80fd5b60b5816092565b811460be575f80fd5b5056fea2646970667358221220f8c9e6a7e4d3c2b1a9f8e7d6c5b4a3928f1e0d9c8b7a69584736f6c63430008130033"

# ABI for the contract
ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "get",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "x", "type": "uint256"}],
        "name": "set",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]


def rpc_call(method, params=None):
    """Make JSON-RPC call"""
    if params is None:
        params = []

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }

    response = requests.post(ENDPOINT_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
    return response.json()


def print_test(num, name):
    """Print test header"""
    print(f"\n{'='*70}")
    print(f"Test {num}: {name}")
    print(f"{'='*70}")


def main():
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║           v0.4.1 RELEASE VERIFICATION TEST                ║")
    print("║                                                           ║")
    print("║  Testing All Claims from Release Notes                   ║")
    print("║  Date: November 10, 2025                                 ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("\n")

    w3 = Web3(Web3.HTTPProvider(ENDPOINT_URL))
    account = Account.from_key(PRIVATE_KEY)

    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "v0.4.1",
        "endpoint": ENDPOINT_URL,
        "chainId": CHAIN_ID,
        "tests": []
    }

    # Test 1: Network Connectivity
    print_test(1, "Network Connectivity")
    try:
        response = rpc_call("eth_blockNumber")
        if "result" in response:
            block = int(response["result"], 16)
            print(f"✅ Connected - Current block: {block}")
            results["tests"].append({"name": "Network Connectivity", "status": "PASS", "block": block})
        else:
            print(f"❌ Failed: {response}")
            results["tests"].append({"name": "Network Connectivity", "status": "FAIL"})
            return results
    except Exception as e:
        print(f"❌ Exception: {e}")
        results["tests"].append({"name": "Network Connectivity", "status": "FAIL", "error": str(e)})
        return results

    # Test 2: Account Balance
    print_test(2, "Account Balance")
    try:
        response = rpc_call("eth_getBalance", [account.address, "latest"])
        balance_wei = int(response["result"], 16)
        balance_fco = balance_wei / 10**18
        print(f"Account: {account.address}")
        print(f"Balance: {balance_fco:.4f} FCO")
        results["tests"].append({"name": "Account Balance", "status": "PASS", "balance": balance_fco})
    except Exception as e:
        print(f"❌ Exception: {e}")
        results["tests"].append({"name": "Account Balance", "status": "FAIL", "error": str(e)})

    # Test 3: Get Nonce
    print_test(3, "Get Transaction Nonce")
    try:
        response = rpc_call("eth_getTransactionCount", [account.address, "latest"])
        nonce = int(response["result"], 16)
        print(f"Nonce: {nonce}")
        results["tests"].append({"name": "Get Nonce", "status": "PASS", "nonce": nonce})
    except Exception as e:
        print(f"❌ Exception: {e}")
        nonce = 0
        results["tests"].append({"name": "Get Nonce", "status": "FAIL", "error": str(e)})

    # Test 4: Deploy Contract
    print_test(4, "Contract Deployment (Gas Usage Check)")
    try:
        contract = w3.eth.contract(abi=ABI, bytecode=BYTECODE)
        deploy_txn = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 500000,
            'gasPrice': w3.to_wei('10', 'gwei'),
            'chainId': CHAIN_ID
        })

        signed_txn = account.sign_transaction(deploy_txn)

        print("Sending deployment transaction...")
        response = rpc_call("eth_sendRawTransaction", [signed_txn.raw_transaction.hex()])

        if "result" in response:
            tx_hash = response["result"]
            print(f"TX Hash: {tx_hash}")
            print("Waiting 10 seconds for confirmation...")
            time.sleep(10)

            receipt_response = rpc_call("eth_getTransactionReceipt", [tx_hash])

            if "result" in receipt_response and receipt_response["result"]:
                receipt = receipt_response["result"]
                contract_address = receipt.get("contractAddress")
                status = receipt.get("status")
                gas_used = int(receipt.get("gasUsed", "0x0"), 16)

                if contract_address:
                    contract_address = w3.to_checksum_address(contract_address)

                print(f"Contract Address: {contract_address}")
                print(f"Status: {status}")
                print(f"Gas Used: {gas_used}")

                # CRITICAL: Check if gas usage is proper for deployment
                if gas_used == 21000:
                    print(f"⚠️  WARNING: Gas used is 21000 (transfer amount, NOT deployment!)")
                    results["tests"].append({
                        "name": "Contract Deployment",
                        "status": "FAIL",
                        "reason": "Gas usage indicates deployment didn't execute",
                        "gasUsed": gas_used,
                        "contractAddress": contract_address
                    })
                elif gas_used > 100000:
                    print(f"✅ Gas usage indicates actual deployment ({gas_used} gas)")
                    results["tests"].append({
                        "name": "Contract Deployment",
                        "status": "PASS",
                        "gasUsed": gas_used,
                        "contractAddress": contract_address,
                        "txHash": tx_hash
                    })
                    nonce += 1
                else:
                    print(f"⚠️  WARNING: Unexpected gas usage: {gas_used}")
                    results["tests"].append({
                        "name": "Contract Deployment",
                        "status": "WARNING",
                        "gasUsed": gas_used,
                        "contractAddress": contract_address
                    })
            else:
                print("❌ Receipt not available")
                results["tests"].append({"name": "Contract Deployment", "status": "FAIL", "reason": "No receipt"})
                return results
        else:
            print(f"❌ Deployment failed: {response}")
            results["tests"].append({"name": "Contract Deployment", "status": "FAIL", "error": response})
            return results
    except Exception as e:
        print(f"❌ Exception: {e}")
        results["tests"].append({"name": "Contract Deployment", "status": "FAIL", "error": str(e)})
        return results

    # Test 5: eth_getCode (Claim: Now Working)
    print_test(5, "eth_getCode - Verify Deployment")
    try:
        response = rpc_call("eth_getCode", [contract_address, "latest"])

        if "result" in response:
            code = response["result"]
            print(f"Code length: {len(code)} characters")
            print(f"Code preview: {code[:66]}..." if len(code) > 66 else f"Code: {code}")

            if code != "0x" and len(code) > 10:
                print(f"✅ eth_getCode WORKING - Contract bytecode found")
                results["tests"].append({
                    "name": "eth_getCode",
                    "status": "PASS",
                    "codeLength": len(code)
                })
            else:
                print(f"❌ eth_getCode returns empty - Contract not deployed or method broken")
                results["tests"].append({
                    "name": "eth_getCode",
                    "status": "FAIL",
                    "reason": "Returns empty code",
                    "code": code
                })
        else:
            print(f"❌ eth_getCode failed: {response}")
            results["tests"].append({"name": "eth_getCode", "status": "FAIL", "error": response})
    except Exception as e:
        print(f"❌ Exception: {e}")
        results["tests"].append({"name": "eth_getCode", "status": "FAIL", "error": str(e)})

    # Test 6: eth_call (Claim: Now Working)
    print_test(6, "eth_call - Read Contract State")
    try:
        contract_instance = w3.eth.contract(address=contract_address, abi=ABI)
        # Use encode_abi for web3.py, not encodeABI
        call_data = contract_instance.encode_abi(fn_name="get")

        response = rpc_call("eth_call", [{"to": contract_address, "data": call_data}, "latest"])

        if "result" in response:
            result = response["result"]
            print(f"Raw result: {result}")

            if result != "0x" and result != "0x0":
                value = int(result, 16)
                print(f"Decoded value: {value}")

                # Constructor sets initial value to 42
                if value == 42:
                    print(f"✅ eth_call WORKING - Correct value returned (42 from constructor)")
                    results["tests"].append({
                        "name": "eth_call",
                        "status": "PASS",
                        "value": value
                    })
                else:
                    print(f"⚠️  eth_call works but unexpected value: {value} (expected 42)")
                    results["tests"].append({
                        "name": "eth_call",
                        "status": "WARNING",
                        "value": value,
                        "expected": 42
                    })
            else:
                print(f"❌ eth_call returns empty data")
                results["tests"].append({
                    "name": "eth_call",
                    "status": "FAIL",
                    "reason": "Returns empty data",
                    "result": result
                })
        else:
            print(f"❌ eth_call failed: {response}")
            results["tests"].append({"name": "eth_call", "status": "FAIL", "error": response})
    except Exception as e:
        print(f"❌ Exception: {e}")
        results["tests"].append({"name": "eth_call", "status": "FAIL", "error": str(e)})

    # Test 7: eth_getStorageAt (Claim: Now Working)
    print_test(7, "eth_getStorageAt - Read Storage Slot")
    try:
        response = rpc_call("eth_getStorageAt", [contract_address, "0x1", "latest"])  # Slot 1 has storedData

        if "result" in response:
            storage_value = response["result"]
            print(f"Storage slot 1 (raw): {storage_value}")

            if storage_value != "0x" and storage_value != "0x0":
                value = int(storage_value, 16)
                print(f"Storage slot 1 (decoded): {value}")

                if value == 42:
                    print(f"✅ eth_getStorageAt WORKING - Correct value in storage (42)")
                    results["tests"].append({
                        "name": "eth_getStorageAt",
                        "status": "PASS",
                        "value": value
                    })
                else:
                    print(f"⚠️  eth_getStorageAt works but unexpected value: {value}")
                    results["tests"].append({
                        "name": "eth_getStorageAt",
                        "status": "WARNING",
                        "value": value,
                        "expected": 42
                    })
            else:
                print(f"❌ eth_getStorageAt returns zero/empty")
                results["tests"].append({
                    "name": "eth_getStorageAt",
                    "status": "FAIL",
                    "reason": "Returns zero",
                    "result": storage_value
                })
        else:
            print(f"❌ eth_getStorageAt failed: {response}")
            results["tests"].append({"name": "eth_getStorageAt", "status": "FAIL", "error": response})
    except Exception as e:
        print(f"❌ Exception: {e}")
        results["tests"].append({"name": "eth_getStorageAt", "status": "FAIL", "error": str(e)})

    # Test 8: Write Operation
    print_test(8, "Write Operation - Set Value to 999")
    try:
        contract_instance = w3.eth.contract(address=contract_address, abi=ABI)
        set_txn = contract_instance.functions.set(999).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3.to_wei('10', 'gwei'),
            'chainId': CHAIN_ID
        })

        signed_txn = account.sign_transaction(set_txn)

        print("Sending set(999) transaction...")
        response = rpc_call("eth_sendRawTransaction", [signed_txn.raw_transaction.hex()])

        if "result" in response:
            tx_hash = response["result"]
            print(f"TX Hash: {tx_hash}")
            time.sleep(5)

            receipt_response = rpc_call("eth_getTransactionReceipt", [tx_hash])
            if "result" in receipt_response and receipt_response["result"]:
                receipt = receipt_response["result"]
                if receipt.get("status") == "0x1":
                    print(f"✅ Transaction confirmed")
                    results["tests"].append({
                        "name": "Write Operation",
                        "status": "PASS",
                        "txHash": tx_hash
                    })
                    nonce += 1
                else:
                    print(f"❌ Transaction failed")
                    results["tests"].append({"name": "Write Operation", "status": "FAIL"})
            else:
                print(f"⚠️  Receipt not found")
                results["tests"].append({"name": "Write Operation", "status": "WARNING"})
        else:
            print(f"❌ Transaction failed: {response}")
            results["tests"].append({"name": "Write Operation", "status": "FAIL", "error": response})
    except Exception as e:
        print(f"❌ Exception: {e}")
        results["tests"].append({"name": "Write Operation", "status": "FAIL", "error": str(e)})

    # Test 9: Read After Write
    print_test(9, "Read After Write - Verify Value Changed to 999")
    try:
        call_data = contract_instance.encode_abi(fn_name="get")
        response = rpc_call("eth_call", [{"to": contract_address, "data": call_data}, "latest"])

        if "result" in response and response["result"] != "0x":
            value = int(response["result"], 16)
            print(f"Value: {value}")

            if value == 999:
                print(f"✅ State persistence WORKING - Value correctly updated to 999")
                results["tests"].append({
                    "name": "Read After Write",
                    "status": "PASS",
                    "value": value
                })
            else:
                print(f"❌ State NOT persisted - Expected 999, got {value}")
                results["tests"].append({
                    "name": "Read After Write",
                    "status": "FAIL",
                    "value": value,
                    "expected": 999
                })
        else:
            print(f"❌ Read failed: {response}")
            results["tests"].append({"name": "Read After Write", "status": "FAIL", "error": response})
    except Exception as e:
        print(f"❌ Exception: {e}")
        results["tests"].append({"name": "Read After Write", "status": "FAIL", "error": str(e)})

    # Summary
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                    TEST SUMMARY                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("\n")

    passed = sum(1 for t in results["tests"] if t["status"] == "PASS")
    failed = sum(1 for t in results["tests"] if t["status"] == "FAIL")
    warnings = sum(1 for t in results["tests"] if t["status"] == "WARNING")
    total = len(results["tests"])

    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Warnings: {warnings}")
    print(f"Success Rate: {(passed/total*100):.2f}%")
    print("\n")

    for i, test in enumerate(results["tests"], 1):
        status_symbol = "✅" if test["status"] == "PASS" else "❌" if test["status"] == "FAIL" else "⚠️"
        print(f"{i}. {status_symbol} {test['name']}: {test['status']}")

    # Save results
    output_file = f"v041_verification_results_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Results saved to: {output_file}\n")

    # Verdict
    if passed / total >= 0.9:
        print("✅ VERDICT: v0.4.1 CLAIMS VERIFIED - Smart contracts fully functional")
        return 0
    elif passed / total >= 0.7:
        print("⚠️  VERDICT: v0.4.1 PARTIALLY VERIFIED - Most functionality working")
        return 1
    else:
        print("❌ VERDICT: v0.4.1 CLAIMS NOT VERIFIED - Significant issues remain")
        return 2


if __name__ == "__main__":
    import sys
    sys.exit(main())
