#!/usr/bin/env python3
"""
Check balances of all Hardhat default accounts
"""
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://paratime.fanati.co:8545'))

print("Checking Hardhat default accounts...")
print()

# Hardhat default accounts (first 10)
accounts = [
    "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",  # Account #0
    "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",  # Account #1
    "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",  # Account #2
    "0x90F79bf6EB2c4f870365E785982E1f101E93b906",  # Account #3
    "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65",  # Account #4
    "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc",  # Account #5
    "0x976EA74026E726554dB657fA54763abd0C3a0aa9",  # Account #6
    "0x14dC79964da2C08b23698B3D3cc7Ca32193d9955",  # Account #7
    "0x23618e81E3f5cdF7f54C3d65f7FBc0aBf5B21E8f",  # Account #8
    "0xa0Ee7A142d267C1f36714E4a8F75612F20a79720",  # Account #9
]

private_keys = [
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
    "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
    "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",
    "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",
    "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",
    "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e",
    "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356",
    "0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97",
    "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6",
]

total_balance = 0
funded_accounts = []

for i, addr in enumerate(accounts):
    balance = w3.eth.get_balance(addr)
    balance_fco = w3.from_wei(balance, 'ether')
    total_balance += balance

    status = "✅" if balance > 0 else "  "
    print(f"{status} Account #{i}: {addr}")
    print(f"   Balance: {balance_fco} FCO")

    if balance > 0:
        funded_accounts.append({
            "index": i,
            "address": addr,
            "private_key": private_keys[i],
            "balance": balance,
            "balance_fco": float(balance_fco)
        })
    print()

print("=" * 80)
print(f"Total Balance: {w3.from_wei(total_balance, 'ether')} FCO")
print(f"Funded Accounts: {len(funded_accounts)}")
print()

if funded_accounts:
    print("Use one of these funded accounts for testing:")
    for acc in funded_accounts:
        print(f"  Account #{acc['index']}: {acc['address']} ({acc['balance_fco']} FCO)")
else:
    print("❌ No funded accounts found!")
    print("You need to fund accounts using the faucet or genesis allocation.")
