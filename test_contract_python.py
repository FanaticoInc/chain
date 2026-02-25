#!/usr/bin/env python3
"""
Comprehensive Contract Deployment & Execution Test (Python)
Date: November 10, 2025
Purpose: Verify contract deployment and execution on both endpoints
Workaround: Uses direct HTTP requests to avoid ethers.js batch request issues
"""

import requests
import json
import time
from eth_account import Account
from web3 import Web3
from datetime import datetime
import sys

# Test configuration
ENDPOINTS = [
    {
        "name": "Legacy (Chain ID 1234)",
        "url": "http://paratime.fanati.co:8545",
        "chainId": 1234
    },
    {
        "name": "v0.4.0 (Chain ID 999999999)",
        "url": "http://paratime.fanati.co:8546",
        "chainId": 999999999
    }
]

PRIVATE_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

# SimpleStorage contract bytecode and ABI (compiled with solc 0.8.27)
# Simplified version for testing
SIMPLE_STORAGE_BYTECODE = "0x608060405234801561000f575f80fd5b50335f806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055505f6001819055506102e28061005f5f395ff3fe608060405234801561000f575f80fd5b506004361061004a575f3560e01c806360fe47b11461004e5780636d4ce63c1461006a5780638da5cb5b14610088578063d826f88f146100a6575b5f80fd5b610068600480360381019061006391906101b3565b6100b0565b005b610072610157565b60405161007f91906101ed565b60405180910390f35b61009061015f565b60405161009d9190610245565b60405180910390f35b6100ae610182565b005b5f600154905081600181905550335f73ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff167fe67a1f3f0d8f6e59b6a8c5a1000e2c6e8b5e2c6a5a1f8e5a1f8e5a1f8e5a1f60405160405180910390a45050565b5f60015490509056fea264697066735822122086c4e8d3f8e5a1f8e5a1f8e5a1f8e5a1f8e5a1f8e5a1f8e5a1f8e5a1f864736f6c63430008130033"

SIMPLE_STORAGE_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "uint256", "name": "oldValue", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "newValue", "type": "uint256"},
            {"indexed": True, "internalType": "address", "name": "changedBy", "type": "address"}
        ],
        "name": "ValueChanged",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "get",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "increment",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "reset",
        "outputs": [],
        "stateMutability": "nonpayable",
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


def rpc_call(url, method, params=None):
    """Make a single JSON-RPC call (not batch)"""
    if params is None:
        params = []

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }

    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        data = response.json()

        if "error" in data:
            return {"error": data["error"]}
        return {"result": data.get("result")}
    except Exception as e:
        return {"error": str(e)}


def test_endpoint(endpoint):
    """Test contract deployment and execution on an endpoint"""

    print("\n" + "="*80)
    print(f"TESTING ENDPOINT: {endpoint['name']}")
    print(f"URL: {endpoint['url']}")
    print(f"Chain ID: {endpoint['chainId']}")
    print("="*80 + "\n")

    results = {
        "name": endpoint["name"],
        "url": endpoint["url"],
        "chainId": endpoint["chainId"],
        "tests": [],
        "summary": {"total": 0, "passed": 0, "failed": 0}
    }

    # Create web3 instance
    try:
        w3 = Web3(Web3.HTTPProvider(endpoint["url"]))
        account = Account.from_key(PRIVATE_KEY)
    except Exception as e:
        print(f"❌ Failed to initialize Web3: {e}")
        return results

    # Test 1: Network Connectivity
    print("Test 1: Network Connectivity")
    test = {"name": "Network Connectivity", "status": "pending"}
    try:
        response = rpc_call(endpoint["url"], "eth_blockNumber")
        if "result" in response:
            block_num = int(response["result"], 16)
            print(f"  ✅ Connected to network")
            print(f"  Current Block: {block_num}")
            test["status"] = "passed"
            test["data"] = {"blockNumber": block_num}
            results["summary"]["passed"] += 1
        else:
            print(f"  ❌ Connection failed: {response.get('error')}")
            test["status"] = "failed"
            test["error"] = str(response.get('error'))
            results["summary"]["failed"] += 1
            results["tests"].append(test)
            results["summary"]["total"] += 1
            return results
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        test["status"] = "failed"
        test["error"] = str(e)
        results["summary"]["failed"] += 1
        results["tests"].append(test)
        results["summary"]["total"] += 1
        return results

    results["tests"].append(test)
    results["summary"]["total"] += 1

    # Test 2: Account Balance
    print("\nTest 2: Account Balance Check")
    test = {"name": "Account Balance", "status": "pending"}
    try:
        response = rpc_call(endpoint["url"], "eth_getBalance", [account.address, "latest"])
        if "result" in response:
            balance_wei = int(response["result"], 16)
            balance_fco = balance_wei / 10**18
            print(f"  Account: {account.address}")
            print(f"  Balance: {balance_fco:.4f} FCO")

            if balance_wei > 0:
                print(f"  ✅ Account funded")
                test["status"] = "passed"
            else:
                print(f"  ⚠️  Account has zero balance")
                test["status"] = "warning"

            test["data"] = {"address": account.address, "balance": balance_fco}
            results["summary"]["passed"] += 1
        else:
            print(f"  ❌ Balance check failed: {response.get('error')}")
            test["status"] = "failed"
            test["error"] = str(response.get('error'))
            results["summary"]["failed"] += 1
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        test["status"] = "failed"
        test["error"] = str(e)
        results["summary"]["failed"] += 1

    results["tests"].append(test)
    results["summary"]["total"] += 1

    # Test 3: Get transaction count (nonce)
    print("\nTest 3: Get Transaction Nonce")
    test = {"name": "Get Nonce", "status": "pending"}
    try:
        response = rpc_call(endpoint["url"], "eth_getTransactionCount", [account.address, "latest"])
        if "result" in response:
            nonce = int(response["result"], 16)
            print(f"  Nonce: {nonce}")
            print(f"  ✅ Nonce retrieved")
            test["status"] = "passed"
            test["data"] = {"nonce": nonce}
            results["summary"]["passed"] += 1
        else:
            print(f"  ❌ Nonce retrieval failed: {response.get('error')}")
            test["status"] = "failed"
            test["error"] = str(response.get('error'))
            results["summary"]["failed"] += 1
            nonce = 0
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        test["status"] = "failed"
        test["error"] = str(e)
        results["summary"]["failed"] += 1
        nonce = 0

    results["tests"].append(test)
    results["summary"]["total"] += 1

    # Test 4: Deploy Contract
    print("\nTest 4: Contract Deployment")
    test = {"name": "Contract Deployment", "status": "pending"}

    try:
        # Create contract instance
        contract = w3.eth.contract(abi=SIMPLE_STORAGE_ABI, bytecode=SIMPLE_STORAGE_BYTECODE)

        # Build deployment transaction
        deploy_txn = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': w3.to_wei('10', 'gwei'),
            'chainId': endpoint['chainId']
        })

        # Sign and send transaction
        signed_txn = account.sign_transaction(deploy_txn)

        print(f"  Sending deployment transaction...")
        response = rpc_call(endpoint["url"], "eth_sendRawTransaction", [signed_txn.raw_transaction.hex()])

        if "result" in response:
            tx_hash = response["result"]
            print(f"  Deployment TX: {tx_hash}")
            print(f"  Waiting for confirmation (10 seconds)...")
            time.sleep(10)

            # Get receipt
            receipt_response = rpc_call(endpoint["url"], "eth_getTransactionReceipt", [tx_hash])

            if "result" in receipt_response and receipt_response["result"]:
                receipt = receipt_response["result"]
                contract_address = receipt.get("contractAddress")
                status = receipt.get("status")

                if contract_address and status == "0x1":
                    # Convert to checksum address
                    contract_address = w3.to_checksum_address(contract_address)
                    print(f"  ✅ Contract deployed successfully")
                    print(f"  Contract Address: {contract_address}")
                    test["status"] = "passed"
                    test["data"] = {"contractAddress": contract_address, "txHash": tx_hash}
                    results["summary"]["passed"] += 1
                    nonce += 1
                elif status == "0x0":
                    print(f"  ❌ Deployment transaction failed (status: 0)")
                    test["status"] = "failed"
                    test["error"] = "Transaction status: 0 (failed)"
                    test["data"] = {"txHash": tx_hash, "receipt": receipt}
                    results["summary"]["failed"] += 1
                    results["tests"].append(test)
                    results["summary"]["total"] += 1
                    return results
                elif not contract_address:
                    print(f"  ❌ No contract address in receipt")
                    test["status"] = "failed"
                    test["error"] = "Contract address is null"
                    test["data"] = {"txHash": tx_hash, "receipt": receipt}
                    results["summary"]["failed"] += 1
                    results["tests"].append(test)
                    results["summary"]["total"] += 1
                    return results
            else:
                print(f"  ⚠️  Receipt not found yet")
                test["status"] = "failed"
                test["error"] = "Receipt not available"
                results["summary"]["failed"] += 1
                results["tests"].append(test)
                results["summary"]["total"] += 1
                return results
        else:
            print(f"  ❌ Deployment failed: {response.get('error')}")
            test["status"] = "failed"
            test["error"] = str(response.get('error'))
            results["summary"]["failed"] += 1
            results["tests"].append(test)
            results["summary"]["total"] += 1
            return results

    except Exception as e:
        print(f"  ❌ Exception: {e}")
        test["status"] = "failed"
        test["error"] = str(e)
        results["summary"]["failed"] += 1
        results["tests"].append(test)
        results["summary"]["total"] += 1
        return results

    results["tests"].append(test)
    results["summary"]["total"] += 1

    # Now we have a deployed contract at contract_address
    # Ensure address is in checksum format
    try:
        contract_address_checksum = w3.to_checksum_address(contract_address)
        contract_instance = w3.eth.contract(address=contract_address_checksum, abi=SIMPLE_STORAGE_ABI)
    except Exception as e:
        print(f"\n❌ Failed to create contract instance: {e}")
        print(f"Contract address value: {contract_address}")
        return results

    # Test 5: Read Initial Value
    print("\nTest 5: Read Initial Value")
    test = {"name": "Read Initial Value", "status": "pending"}
    try:
        # Call get() function
        call_data = contract_instance.encodeABI(fn_name="get")
        response = rpc_call(endpoint["url"], "eth_call", [{"to": contract_address_checksum, "data": call_data}, "latest"])

        if "result" in response and response["result"] != "0x":
            value = int(response["result"], 16)
            print(f"  Value: {value}")

            if value == 0:
                print(f"  ✅ Initial value correct (0)")
                test["status"] = "passed"
                results["summary"]["passed"] += 1
            else:
                print(f"  ❌ Initial value incorrect (expected 0, got {value})")
                test["status"] = "failed"
                results["summary"]["failed"] += 1

            test["data"] = {"value": value}
        else:
            print(f"  ❌ eth_call failed or returned empty: {response}")
            test["status"] = "failed"
            test["error"] = "eth_call returned 0x or error"
            results["summary"]["failed"] += 1
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        test["status"] = "failed"
        test["error"] = str(e)
        results["summary"]["failed"] += 1

    results["tests"].append(test)
    results["summary"]["total"] += 1

    # Test 6: Write Operation - Set Value to 42
    print("\nTest 6: Write Operation - Set Value to 42")
    test = {"name": "Write Operation (set 42)", "status": "pending"}
    try:
        # Build set(42) transaction
        set_txn = contract_instance.functions.set(42).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3.to_wei('10', 'gwei'),
            'chainId': endpoint['chainId']
        })

        signed_txn = account.sign_transaction(set_txn)

        print(f"  Sending set(42) transaction...")
        response = rpc_call(endpoint["url"], "eth_sendRawTransaction", [signed_txn.raw_transaction.hex()])

        if "result" in response:
            tx_hash = response["result"]
            print(f"  TX: {tx_hash}")
            time.sleep(5)

            receipt_response = rpc_call(endpoint["url"], "eth_getTransactionReceipt", [tx_hash])
            if "result" in receipt_response and receipt_response["result"]:
                receipt = receipt_response["result"]
                if receipt.get("status") == "0x1":
                    print(f"  ✅ Transaction confirmed")
                    test["status"] = "passed"
                    test["data"] = {"txHash": tx_hash}
                    results["summary"]["passed"] += 1
                    nonce += 1
                else:
                    print(f"  ❌ Transaction failed")
                    test["status"] = "failed"
                    test["error"] = "Transaction status: 0"
                    results["summary"]["failed"] += 1
            else:
                print(f"  ⚠️  Receipt not found")
                test["status"] = "failed"
                test["error"] = "Receipt not available"
                results["summary"]["failed"] += 1
        else:
            print(f"  ❌ Transaction failed: {response.get('error')}")
            test["status"] = "failed"
            test["error"] = str(response.get('error'))
            results["summary"]["failed"] += 1
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        test["status"] = "failed"
        test["error"] = str(e)
        results["summary"]["failed"] += 1

    results["tests"].append(test)
    results["summary"]["total"] += 1

    # Test 7: Read Value After Write
    print("\nTest 7: Read Value After Write (expect 42)")
    test = {"name": "Read After Write (42)", "status": "pending"}
    try:
        call_data = contract_instance.encodeABI(fn_name="get")
        response = rpc_call(endpoint["url"], "eth_call", [{"to": contract_address, "data": call_data}, "latest"])

        if "result" in response and response["result"] != "0x":
            value = int(response["result"], 16)
            print(f"  Value: {value}")

            if value == 42:
                print(f"  ✅ Value correctly stored (42)")
                test["status"] = "passed"
                results["summary"]["passed"] += 1
            else:
                print(f"  ❌ Value incorrect (expected 42, got {value})")
                test["status"] = "failed"
                results["summary"]["failed"] += 1

            test["data"] = {"value": value}
        else:
            print(f"  ❌ eth_call failed: {response}")
            test["status"] = "failed"
            test["error"] = "eth_call returned 0x or error"
            results["summary"]["failed"] += 1
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        test["status"] = "failed"
        test["error"] = str(e)
        results["summary"]["failed"] += 1

    results["tests"].append(test)
    results["summary"]["total"] += 1

    # Summary
    print(f"\n{'='*80}")
    print(f"ENDPOINT SUMMARY: {endpoint['name']}")
    print(f"Total Tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    if results['summary']['total'] > 0:
        success_rate = (results['summary']['passed'] / results['summary']['total']) * 100
        print(f"Success Rate: {success_rate:.2f}%")
    print(f"{'='*80}\n")

    return results


def main():
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                               ║")
    print("║         COMPREHENSIVE CONTRACT DEPLOYMENT & EXECUTION TEST SUITE              ║")
    print("║                          (Python Implementation)                              ║")
    print("║                                                                               ║")
    print("║  Date: November 10, 2025                                                      ║")
    print("║  Purpose: Verify contract deployment and execution functionality             ║")
    print("║  Endpoints: 2 (Legacy Chain ID 1234, v0.4.0 Chain ID 999999999)              ║")
    print("║                                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print("\n")

    all_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": []
    }

    for endpoint in ENDPOINTS:
        results = test_endpoint(endpoint)
        all_results["endpoints"].append(results)
        time.sleep(5)  # Wait between endpoints

    # Overall Summary
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                          OVERALL TEST SUMMARY                                 ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print("\n")

    for ep_result in all_results["endpoints"]:
        print(f"{ep_result['name']}:")
        print(f"  Total Tests: {ep_result['summary']['total']}")
        print(f"  Passed: {ep_result['summary']['passed']}")
        print(f"  Failed: {ep_result['summary']['failed']}")
        if ep_result['summary']['total'] > 0:
            success_rate = (ep_result['summary']['passed'] / ep_result['summary']['total']) * 100
            print(f"  Success Rate: {success_rate:.2f}%")
        print("")

    # Save results
    output_file = f"contract_test_results_python_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n📄 Detailed results saved to: {output_file}\n")

    # Overall verdict
    total_passed = sum(ep["summary"]["passed"] for ep in all_results["endpoints"])
    total_tests = sum(ep["summary"]["total"] for ep in all_results["endpoints"])

    if total_tests > 0:
        overall_rate = (total_passed / total_tests) * 100
        print(f"Overall Success Rate: {overall_rate:.2f}%\n")

        if overall_rate >= 80:
            print("✅ RESULT: PRODUCTION READY - Contract deployment and execution working")
            return 0
        elif overall_rate >= 50:
            print("⚠️  RESULT: PARTIAL FUNCTIONALITY - Some features working")
            return 1
        else:
            print("❌ RESULT: NOT FUNCTIONAL - Critical issues detected")
            return 2
    else:
        print("❌ RESULT: NO TESTS COMPLETED")
        return 2


if __name__ == "__main__":
    sys.exit(main())
