#!/usr/bin/env python3
"""
Find which private key corresponds to address 0x5B38Da6a701c568545dCfcB03FcB875f56beddC4
"""
from eth_account import Account

target_address = "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"

# Hardhat default accounts private keys
hardhat_keys = [
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",  # #0
    "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",  # #1
    "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",  # #2
    "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",  # #3
    "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",  # #4
    "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",  # #5
    "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e",  # #6
    "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356",  # #7
    "0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97",  # #8
    "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6",  # #9
]

# Remix IDE default accounts private keys (first 10)
remix_keys = [
    "0x503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48dfcb",  # Remix #0
    "0x7e5bfb82febc4c2c8529167104271ceec190eafdca277314912eaabdb67c6e5f",  # Remix #1
    "0xcc6d63f85de8fef05446ebdd3c537c72152d0fc437fd7aa62b3019b79bd1fdd4",  # Remix #2
    "0x638b5c6c8a2b33a63a607c2e02f1854d12de5e2c63e3f4e9b99a1ec8b5d4a3f1",  # Remix #3 (example)
]

print(f"Target Address: {target_address}")
print()
print("Checking Hardhat private keys...")
print("-" * 80)

for i, key in enumerate(hardhat_keys):
    account = Account.from_key(key)
    match = account.address.lower() == target_address.lower()
    status = "✅ MATCH!" if match else "  "
    print(f"{status} Hardhat #{i}: {account.address}")
    if match:
        print(f"   Private Key: {key}")
        print()

print()
print("Checking Remix private keys...")
print("-" * 80)

for i, key in enumerate(remix_keys):
    account = Account.from_key(key)
    match = account.address.lower() == target_address.lower()
    status = "✅ MATCH!" if match else "  "
    print(f"{status} Remix #{i}: {account.address}")
    if match:
        print(f"   Private Key: {key}")
        print()

# Check common test private keys
common_test_keys = [
    "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    "0x1000000000000000000000000000000000000000000000000000000000000000",
    "0x2000000000000000000000000000000000000000000000000000000000000000",
]

print()
print("Checking common test keys...")
print("-" * 80)

for key in common_test_keys:
    try:
        account = Account.from_key(key)
        match = account.address.lower() == target_address.lower()
        status = "✅ MATCH!" if match else "  "
        print(f"{status} {account.address} -> {key}")
    except:
        pass

print()
print("=" * 80)
print("Note: 0x5B38Da6a701c568545dCfcB03FcB875f56beddC4 is a well-known Remix IDE")
print("JavaScript VM address. The actual private key needs to be obtained from")
print("the genesis file or faucet system.")
print("=" * 80)
