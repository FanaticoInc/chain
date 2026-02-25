#!/usr/bin/env python3
"""
Test batch request handling
"""

import json
import requests

RPC_URL = "http://paratime.fanati.co:8546"

def test_batch_request():
    """Test if batch requests work"""
    print("Testing batch request handling...")
    print("-" * 70)

    # Create a batch request (array of requests)
    batch = [
        {
            "jsonrpc": "2.0",
            "method": "eth_chainId",
            "params": [],
            "id": 1
        },
        {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 2
        },
        {
            "jsonrpc": "2.0",
            "method": "eth_gasPrice",
            "params": [],
            "id": 3
        }
    ]

    try:
        response = requests.post(
            RPC_URL,
            json=batch,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text[:500]}")

        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    print(f"\n✅ PASS - Batch request returned array with {len(result)} items")
                    for item in result:
                        print(f"  - ID {item.get('id')}: {item.get('result', item.get('error'))}")
                    return True
                else:
                    print(f"\n❌ FAIL - Expected array, got: {type(result)}")
                    return False
            except json.JSONDecodeError as e:
                print(f"\n❌ FAIL - Invalid JSON response: {e}")
                return False
        else:
            print(f"\n❌ FAIL - HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"\n❌ FAIL - Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_batch_request()
    exit(0 if success else 1)
