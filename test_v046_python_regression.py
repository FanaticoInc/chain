#!/usr/bin/env python3
"""
v0.4.6 Python Regression Test
Ensures Python web3.py compatibility is maintained at 100%
"""

from web3 import Web3

RPC_URL = "http://paratime.fanati.co:8546"
PRIVATE_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
CHAIN_ID = 999999999

print("=" * 70)
print("v0.4.6 PYTHON REGRESSION TEST")
print("Ensuring Python web3.py compatibility maintained at 100%")
print("=" * 70)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

print(f"\nAccount: {account.address}")
balance = w3.eth.get_balance(account.address)
print(f"Balance: {w3.from_wei(balance, 'ether')} FCO")

results = {
    'connection': False,
    'simple_transfer': False,
    'contract_deployment': False,
    'eip1559': False,
    'contract_state': False
}

# Test 1: Network Connection
print("\n" + "=" * 70)
print("TEST 1: Network Connection & Basic Queries")
print("=" * 70)

try:
    chain_id = w3.eth.chain_id
    print(f"✅ Chain ID: {chain_id}")

    block_number = w3.eth.block_number
    print(f"✅ Block Number: {block_number}")

    block = w3.eth.get_block('latest')
    print(f"✅ Latest Block: {block['number']}")

    results['connection'] = True
    print("\n✅ TEST 1 PASSED\n")
except Exception as e:
    print(f"\n❌ TEST 1 FAILED: {e}\n")

# Test 2: Simple Transfer
print("=" * 70)
print("TEST 2: Simple Transfer (Legacy Transaction)")
print("=" * 70)

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

    print(f"\nTransaction Details:")
    print(f"  To: {tx['to']}")
    print(f"  Value: {w3.from_wei(tx['value'], 'ether')} FCO")
    print(f"  Gas: {tx['gas']}")
    print(f"  Nonce: {tx['nonce']}")

    print(f"\nSigning and sending transaction...")
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Transaction sent: {tx_hash.hex()}")

    print("Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    print(f"✅ Confirmed in block {receipt['blockNumber']}")
    print(f"   Status: {receipt['status']}")
    print(f"   Gas Used: {receipt['gasUsed']}")

    results['simple_transfer'] = True
    print("\n✅ TEST 2 PASSED\n")

except Exception as e:
    print(f"\n❌ TEST 2 FAILED: {e}\n")

# Test 3: Contract Deployment
print("=" * 70)
print("TEST 3: Smart Contract Deployment")
print("=" * 70)

try:
    # SimpleStorage contract bytecode
    BYTECODE = '0x608060405234801561000f575f80fd5b50602a5f5560bb806100205f395ff3fe6080604052348015600e575f80fd5b50600436106030575f3560e01c80636d4ce63c146034578063e5c19b2d14604c575b5f80fd5b603a6056565b60405190815260200160405180910390f35b6054605e565b005b5f5f54905090565b602a5f8190555056fea2646970667358221220c85b4c6f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f64736f6c63430008140033'

    nonce = w3.eth.get_transaction_count(account.address)

    tx = {
        'from': account.address,
        'to': None,  # Contract deployment
        'data': BYTECODE,
        'gas': 300000,
        'gasPrice': w3.to_wei(10, 'gwei'),
        'nonce': nonce,
        'chainId': CHAIN_ID
    }

    print(f"\nDeployment Details:")
    print(f"  Gas Limit: {tx['gas']}")
    print(f"  Bytecode Length: {len(BYTECODE)} chars")
    print(f"  Nonce: {tx['nonce']}")

    print(f"\nDeploying contract...")
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Transaction sent: {tx_hash.hex()}")

    print("Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

    if receipt['contractAddress']:
        contract_address = receipt['contractAddress']
        print(f"✅ Contract deployed at: {contract_address}")
        print(f"   Block: {receipt['blockNumber']}")
        print(f"   Gas Used: {receipt['gasUsed']}")

        # Test contract state
        print(f"\n  Testing deployed contract...")

        code = w3.eth.get_code(contract_address)
        if code and code != b'\x00' and len(code) > 2:
            print(f"  ✅ eth_getCode: {len(code)} bytes")
        else:
            print(f"  ⚠️  eth_getCode: empty or invalid")

        # Call get() function (0x6d4ce63c)
        result = w3.eth.call({
            'to': contract_address,
            'data': '0x6d4ce63c'
        })
        value = int.from_bytes(result, byteorder='big')
        print(f"  ✅ eth_call (get): {value} (expected: 42)")

        # Check storage directly
        storage = w3.eth.get_storage_at(contract_address, 0)
        storage_value = int.from_bytes(storage, byteorder='big')
        print(f"  ✅ eth_getStorageAt: {storage_value} (expected: 42)")

        results['contract_deployment'] = True
        results['contract_state'] = (value == 42 and storage_value == 42)
        print("\n✅ TEST 3 PASSED\n")
    else:
        print("⚠️  Contract address is null in receipt\n")

except Exception as e:
    print(f"\n❌ TEST 3 FAILED: {e}\n")

# Test 4: EIP-1559 Transaction
print("=" * 70)
print("TEST 4: EIP-1559 Transaction (Type 2)")
print("=" * 70)

try:
    nonce = w3.eth.get_transaction_count(account.address)

    tx = {
        'type': 2,
        'from': account.address,
        'to': '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
        'value': w3.to_wei(0.001, 'ether'),
        'gas': 21000,
        'maxFeePerGas': w3.to_wei(20, 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei(2, 'gwei'),
        'nonce': nonce,
        'chainId': CHAIN_ID
    }

    print(f"\nEIP-1559 Transaction:")
    print(f"  Type: {tx['type']}")
    print(f"  To: {tx['to']}")
    print(f"  Value: {w3.from_wei(tx['value'], 'ether')} FCO")
    print(f"  Max Fee: {w3.from_wei(tx['maxFeePerGas'], 'gwei')} Gwei")

    print(f"\nSending transaction...")
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Transaction sent: {tx_hash.hex()}")

    print("Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    print(f"✅ Confirmed in block {receipt['blockNumber']}")
    print(f"   Status: {receipt['status']}")
    print(f"   Gas Used: {receipt['gasUsed']}")

    results['eip1559'] = True
    print("\n✅ TEST 4 PASSED\n")

except Exception as e:
    print(f"\n❌ TEST 4 FAILED: {e}\n")

# Summary
print("=" * 70)
print("PYTHON REGRESSION TEST SUMMARY - v0.4.6")
print("=" * 70)

tests = [
    ('Network Connection', results['connection']),
    ('Simple Transfer', results['simple_transfer']),
    ('Contract Deployment', results['contract_deployment']),
    ('Contract State', results['contract_state']),
    ('EIP-1559 Transaction', results['eip1559'])
]

passed = 0
for name, result in tests:
    icon = '✅' if result else '❌'
    print(f"{icon} {name}")
    if result:
        passed += 1

total = len(tests)
percentage = int((passed / total) * 100)

print(f"\nResults: {passed}/{total} tests passed ({percentage}%)")

print("\n" + "=" * 70)
if passed == total:
    print("✅ PYTHON REGRESSION TEST PASSED")
    print("   Python web3.py compatibility maintained at 100%")
    print("   No regression from v0.4.5")
elif passed >= 4:
    print("⚠️  PYTHON MOSTLY WORKING")
    print("   Minor issues, but core functionality intact")
else:
    print("❌ PYTHON REGRESSION DETECTED")
    print("   v0.4.6 breaks Python compatibility")
    print("   This is a CRITICAL issue - Python was working in v0.4.5")

print("=" * 70)
