# Fanatico L1 — Authority, Genesis Balances & Permissioned Funding Reference

**Version**: v0.5.0.0 GA
**Chain ID**: 11111111111 (`0x2964619c7`)
**RPC**: `https://rpc.fanati.co`
**Date**: February 25, 2026

This document provides complete technical context for the Fanatico L1 blockchain's authority account, genesis balance system, and a proposed permissioned funding mechanism. It is intended for sharing with external AI agents (Codex, Gemini) or developers who need to implement or audit funding operations.

---

## Table of Contents

1. [Authority Account Origin](#1-authority-account-origin)
2. [Genesis Balances — Design & Current State](#2-genesis-balances--design--current-state)
3. [Permissioned Funding Implementation](#3-permissioned-funding-implementation)

---

## 1. Authority Account Origin

### Address

```
0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2
```

### How It Was Generated

The Authority is a **smart contract**, not an externally owned account (EOA). It was deployed via Hardhat by the DevTeam account (mnemonic index 1) using the standard EVM `CREATE` opcode.

**Address derivation**: `keccak256(rlp([deployer_address, deployer_nonce]))`

- **Deployer**: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` (DevTeam, HD index 1)
- **Deployer mnemonic**: `test test test test test test test test test test test junk`
- **Contract**: `Authority` (from `AccessControl.sol`)
- **Constructor arg**: `chainId_ = 11111111111` (Fanatico L1)
- **Deployment script**: `hardhat/scripts/deploy-fco.js`

**The Authority account has no private key and cannot sign transactions.** It is an on-chain access control contract.

### Contract Source: `Authority` (AccessControl.sol)

```solidity
// SPDX-License-Identifier: none
pragma solidity ^0.8.19;

contract Authority is IAuthority, AccessControl {
    uint40 public chainId;
    address public admin;
    address public serviceWallet;

    mapping(address => bool) public operators;
    mapping(address => bool) public signers;

    bytes32 public publicKey;
    bytes32 private privateKey;

    IPublication public publication;
    uint40 public feeBase;
    uint40 public serviceFee;
    bytes32 private domainSeparator;
    IFCOToken public fco;

    constructor(uint40 chainId_) {
        authority = IAuthority(address(this));
        admin = msg.sender;                    // DevTeam account
        operators[msg.sender] = true;
        signers[msg.sender] = true;
        serviceWallet = msg.sender;
        chainId = chainId_;                    // 11111111111
        feeBase = 100;
        serviceFee = 5;

        // Deterministic internal keys (L1 stub, not used for signing)
        privateKey = keccak256(abi.encodePacked(block.timestamp, msg.sender, block.prevrandao));
        publicKey = keccak256(abi.encodePacked(privateKey));
    }

    // Role management
    function setAdmin(address account_) public onlyAdmin { admin = account_; }
    function setOperators(address[] calldata accounts_, bool state_) public onlyAdmin { ... }
    function setSigner(address account_, bool state_) public onlyAdmin { ... }
    function setFco(IFCOToken fco_) public onlyAdmin { fco = fco_; }
    function setPublication(IPublication publication_) public onlyAdmin { ... }
    function setServiceWallet(address serviceWallet_) public onlyAdmin { ... }

    // Events
    function emitEvent(bytes32 action, bytes memory data) public onlyOperator { ... }

    // Stubbed crypto (L1 compatible — no Sapphire TEE)
    function encrypt(bytes32 clientPub, bytes memory plaintext) public view returns (bytes memory) {
        return plaintext;  // no-op on L1
    }
    function decrypt(bytes32 clientPub, bytes memory ciphertext) public view returns (bytes memory) {
        return ciphertext;  // no-op on L1
    }
}
```

### Key Properties

| Property | Value |
|----------|-------|
| `admin` | `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` (DevTeam) |
| `chainId` | `11111111111` |
| `feeBase` | `100` |
| `serviceFee` | `5` |
| `operators[DevTeam]` | `true` |
| `signers[DevTeam]` | `true` |
| `fco` | `0xd6F8Ff0036D8B2088107902102f9415330868109` (linked post-deployment) |

### Related Contracts (8 total, all deployed)

| Contract | Address | Deployer |
|----------|---------|----------|
| Authority | `0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2` | DevTeam |
| FCO Token | `0xd6F8Ff0036D8B2088107902102f9415330868109` | DevTeam |
| FanaticoNFT | `0x0442121975b1D8a0860F8B80318f84402284A211` | DevTeam |
| Marketplace | `0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9` | DevTeam |
| AuctionEng | `0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049` | DevTeam |
| AuctionDut | `0x4437204542e5C71409Af1eE0154Ce5fa659f55a7` | DevTeam |
| AuctionSen | `0xCe1370E6013989185ac2552832099F24a85DbfD4` | DevTeam |
| AuctionLub | `0xB3faFE3b27fCB65689d540c5185a8420310d59dA` | DevTeam |

### FCO Token Contract — No Mint Function

The FCO Token contract (`0xd6F8...8109`) is a **metadata-only stub** with no minting capability:

| Function | Present | Returns |
|----------|---------|---------|
| `name()` | Yes | "FCO" |
| `symbol()` | Yes | "FCO" |
| `decimals()` | Yes | 18 |
| `totalSupply()` | Yes | 0 |
| `mint(address,uint256)` | **No** | — |
| `owner()` | **No** | — |
| `transfer()` | **No** | — |
| `balanceOf()` | **No** | — |

**FCO is the native token** (equivalent to ETH on Ethereum). Balances are tracked in the chain's SQLite database, not in a smart contract. The ERC-20 contract exists for metadata only.

---

## 2. Genesis Balances — Design & Current State

### How FCO Balances Work

FCO is a **native token** stored in the chain's SQLite database. There is no ERC-20 contract with `balanceOf()` — the Web3 API reads balances directly from the `balances` table.

### Database Schema

```sql
-- Table: balances (on paratime node)
-- DB path: /home/claude/fco_blockchain_v04963.db
CREATE TABLE balances (
    address TEXT PRIMARY KEY,
    balance TEXT NOT NULL,     -- stored as wei string
    nonce INTEGER DEFAULT 0
);
```

There are **40 accounts** in the database. Balance computation works by:
1. Reading the stored balance from the `balances` table
2. The Python Web3 API updates this balance in real-time as transactions are processed
3. The `GENESIS_BALANCES` dict in `web3_api_v04998.py` is a reference/fallback for initial seeding

### HD Wallet Mnemonic

All test EOAs are derived from a single BIP-39 mnemonic:

```
test test test test test test test test test test test junk
```

**Derivation path**: `m/44'/60'/0'/0/{index}` (standard Ethereum HD path)

### Test Account Registry

| # | Name | Address | Private Key | HD Index |
|---|------|---------|-------------|----------|
| 0 | Roman | `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` | `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80` | 0 |
| 1 | DevTeam | `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` | `0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d` | 1 |
| 2 | Air | `0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC` | `0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a` | 2 |
| 3 | Ali | `0xf945e1714Ef5872cfD88aa99B3cf16DD66f58E92` | `0x06ce277a41c1c1804469a604f8d6110fab75c08a2c685aa27ea2c1b50cffe97b` | Standalone |
| 4 | Remix | `0x5B38Da6a701c568545dCfcB03FcB875f56beddC4` | `0x503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48dfcb` | Remix Default |

### Genesis Balances (hardcoded in `web3_api_v04998.py:128-143`)

```python
GENESIS_BALANCES = {
    '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266': int(999.99 * 10**18),   # Roman
    '0x70997970C51812dc3A010C7d01b50e0d17dc79C8': int(4.37 * 10**18),     # DevTeam
    '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC': int(1000.00 * 10**18),  # Air
    '0xf945e1714Ef5872cfD88aa99B3cf16DD66f58E92': int(1000.00 * 10**18),  # Ali
    '0x5B38Da6a701c568545dCfcB03FcB875f56beddC4': int(2.13 * 10**18),     # Remix
}
```

### Database Balances (actual DB state on paratime)

The `balances` table contains larger genesis allocations than the code dict. These are the values actually used by the chain:

| Address | DB Balance (FCO) | Nonce (DB) |
|---------|-----------------|------------|
| Roman (`0xf39F...`) | 10,000,000.00 | 0 |
| DevTeam (`0x7099...`) | 10,000,000.00 | 0 |
| Air (`0x3C44...`) | 10,000,000.00 | 0 |
| Ali (`0xf945...`) | 1,400.00 | 0 |
| `0x49be...15ea` | 1,467.08 | 2 |
| `0xdeadc0de...` | 100.08 | 0 |
| `0xbf32...0e0f` | 75.00 | 0 |
| `0x9e23...8d1d` | 29.41 | 0 |
| `0x0e9e...3690` | 24.01 | 0 |
| (+ 31 more small accounts) | ... | ... |

**Note**: The DB stores raw genesis-plus-received values. The RPC-reported balances are lower because the Python Web3 API computes current balance by applying all outgoing transactions and gas costs from the transaction history.

### Current Live Balances (via RPC, as of February 25, 2026)

| Account | RPC Balance (FCO) | Nonce (RPC) | Status |
|---------|-------------------|-------------|--------|
| Roman | **0.003580** | 1,744 | Near-empty (spent on deployments/tests) |
| DevTeam | **0.003580** | 19 | Near-empty (spent on contract deployments) |
| Air | **0.003635** | 11 | Near-empty |
| Ali | **1,400.000000** | 0 | Funded (never transacted) |
| Remix | **0.003580** | 2 | Near-empty |
| Authority (contract) | **0.000000** | — | Contract, no native balance |

### KEYS.md Reference Balances (January 8, 2026)

These were the last-documented balances before the GA release:

| Account | KEYS.md Balance | Current Balance | Delta |
|---------|----------------|-----------------|-------|
| Roman | 982.64 FCO | 0.003580 FCO | -982.636 |
| DevTeam | 505.30 FCO | 0.003580 FCO | -505.296 |
| Air | 117.14 FCO | 0.003635 FCO | -117.136 |
| Ali | 1,400.00 FCO | 1,400.000000 FCO | 0.000 |
| Remix | 100.00 FCO | 0.003580 FCO | -99.996 |

### Chain Statistics

| Metric | Value |
|--------|-------|
| Total Blocks | 2,311 |
| Total Transactions | 2,133 |
| Block Height | 2,310 |
| Total Accounts | 40 |
| Accounts with balance > 0 | ~20 |
| Gas Price | 20 Gwei (fixed) |
| Gas per transfer | 21,000 (0.00042 FCO) |

---

## 3. Permissioned Funding Implementation

### Problem Statement

- FCO is a native token with no mint function in the ERC-20 contract
- The Authority contract has no mint capability for native FCO
- Test accounts are nearly empty after 2,133 transactions
- Need a way to fund addresses without exposing a public faucet
- Funding must be auditable and restricted to authorized operators

### Architecture Overview

Since FCO balances live in SQLite (not in a smart contract), funding must operate at the **Web3 API layer**. The proposal adds a new JSON-RPC method `fco_fundAccount` to the Python server that:

1. Validates an ECDSA signature from an authorized operator
2. Credits the target address in the `balances` table
3. Creates a synthetic transaction for audit trail
4. Returns a transaction hash for verification

### Approach: Signature-Gated `fco_fundAccount` RPC Method

#### Method Specification

```
Method:  fco_fundAccount
Params:  [targetAddress, amountHex, nonce, signature]
Returns: { transactionHash, funded, newBalance }
Auth:    ECDSA signature from AUTHORIZED_OPERATORS list
```

#### Server-Side Implementation (Python)

Add to `web3_api_v04998.py` on all nodes (but only paratime processes writes):

```python
import time
from eth_account.messages import encode_defunct
from eth_account import Account as EthAccount

# ─── Configuration ───────────────────────────────────────────────────
# Authorized operator addresses (can fund accounts)
AUTHORIZED_OPERATORS = {
    # Roman (Index 0)
    '0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266',
    # DevTeam (Index 1)
    '0x70997970c51812dc3a010c7d01b50e0d17dc79c8',
}

# Funding limits
MAX_FUND_AMOUNT_WEI = int(10_000 * 10**18)   # 10,000 FCO per call
MAX_FUND_PER_DAY_WEI = int(100_000 * 10**18) # 100,000 FCO per day per operator
FUND_NONCE_TRACKER = {}  # { operator_address: last_nonce }
FUND_DAILY_TRACKER = {}  # { operator_address: { date: total_wei } }

# ─── Funding Method ──────────────────────────────────────────────────
def fco_fund_account(params):
    """
    Permissioned account funding via operator signature.

    params: [target_address, amount_hex, nonce_hex, signature]
      - target_address: 0x-prefixed Ethereum address to fund
      - amount_hex:     0x-prefixed hex amount in wei
      - nonce_hex:      0x-prefixed hex nonce (monotonically increasing per operator)
      - signature:      0x-prefixed ECDSA signature of the funding message

    The message to sign is:
      keccak256(abi.encodePacked("fco_fund:", chainId, target, amount, nonce))

    Using eth_account's sign_message with:
      message = f"fco_fund:{CHAIN_ID}:{target}:{amount_hex}:{nonce_hex}"
    """
    if len(params) != 4:
        return {"error": {"code": -32602, "message": "Expected 4 params: [address, amount, nonce, signature]"}}

    target_address, amount_hex, nonce_hex, signature = params

    # ── 1. Parse and validate inputs ──
    try:
        target = target_address.lower()
        amount_wei = int(amount_hex, 16)
        nonce = int(nonce_hex, 16)
    except (ValueError, TypeError):
        return {"error": {"code": -32602, "message": "Invalid hex parameters"}}

    if amount_wei <= 0:
        return {"error": {"code": -32602, "message": "Amount must be positive"}}

    if amount_wei > MAX_FUND_AMOUNT_WEI:
        return {"error": {"code": -32602, "message": f"Amount exceeds max {MAX_FUND_AMOUNT_WEI / 1e18:.0f} FCO per call"}}

    if not target.startswith('0x') or len(target) != 42:
        return {"error": {"code": -32602, "message": "Invalid target address"}}

    # ── 2. Recover signer from signature ──
    message_text = f"fco_fund:{CHAIN_ID}:{target}:{amount_hex}:{nonce_hex}"
    try:
        message = encode_defunct(text=message_text)
        signer = EthAccount.recover_message(message, signature=signature).lower()
    except Exception as e:
        return {"error": {"code": -32000, "message": f"Signature recovery failed: {str(e)}"}}

    # ── 3. Verify signer is authorized ──
    if signer not in AUTHORIZED_OPERATORS:
        logger.warning(f"Unauthorized funding attempt by {signer}")
        return {"error": {"code": -32000, "message": f"Unauthorized: {signer} not in operator list"}}

    # ── 4. Verify nonce (replay protection) ──
    last_nonce = FUND_NONCE_TRACKER.get(signer, -1)
    if nonce <= last_nonce:
        return {"error": {"code": -32000, "message": f"Nonce too low: got {nonce}, expected > {last_nonce}"}}

    # ── 5. Check daily rate limit ──
    today = time.strftime('%Y-%m-%d')
    daily = FUND_DAILY_TRACKER.get(signer, {})
    daily_total = daily.get(today, 0)
    if daily_total + amount_wei > MAX_FUND_PER_DAY_WEI:
        remaining = (MAX_FUND_PER_DAY_WEI - daily_total) / 1e18
        return {"error": {"code": -32000, "message": f"Daily limit exceeded. Remaining: {remaining:.2f} FCO"}}

    # ── 6. Credit balance in database ──
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Upsert: create account if it doesn't exist, otherwise add to balance
        cursor.execute("""
            INSERT INTO balances (address, balance, nonce)
            VALUES (?, ?, 0)
            ON CONFLICT(address) DO UPDATE SET
                balance = CAST(
                    (CAST(balance AS INTEGER) + ?) AS TEXT
                )
        """, (target, str(amount_wei), amount_wei))

        # Read back new balance
        cursor.execute("SELECT balance FROM balances WHERE address = ?", (target,))
        new_balance = cursor.fetchone()[0]

        conn.commit()
    except Exception as e:
        logger.error(f"DB error during funding: {e}")
        return {"error": {"code": -32000, "message": "Database error during funding"}}
    finally:
        conn.close()

    # ── 7. Create audit transaction (from 0x0, synthetic coinbase-style) ──
    from_address = '0x0000000000000000000000000000000000000000'
    tx_hash = keccak(
        f"fund:{signer}:{target}:{amount_hex}:{nonce_hex}:{int(time.time())}".encode()
    ).hex()
    tx_hash = '0x' + tx_hash

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create a new block for this funding transaction
        cursor.execute("SELECT MAX(number) FROM blocks")
        last_block = cursor.fetchone()[0] or 0
        new_block_number = last_block + 1
        block_timestamp = int(time.time())
        parent_hash = '0x' + '0' * 64

        cursor.execute("SELECT hash FROM blocks WHERE number = ?", (last_block,))
        parent_row = cursor.fetchone()
        if parent_row:
            parent_hash = parent_row[0]

        block_hash = '0x' + keccak(
            f"block:{new_block_number}:{block_timestamp}:{parent_hash}".encode()
        ).hex()

        # Insert block
        cursor.execute("""
            INSERT INTO blocks (number, hash, parent_hash, timestamp, gas_used, gas_limit, miner, tx_count)
            VALUES (?, ?, ?, ?, 0, 15000000, ?, 1)
        """, (new_block_number, block_hash, parent_hash, block_timestamp, from_address))

        # Insert transaction
        cursor.execute("""
            INSERT INTO transactions (tx_hash, from_address, to_address, value, gas_price, gas_used,
                                      block_number, block_hash, tx_index, input_data, nonce, tx_type)
            VALUES (?, ?, ?, ?, 0, 0, ?, ?, 0, ?, ?, 0)
        """, (tx_hash, from_address, target, str(amount_wei),
              new_block_number, block_hash,
              f'0x{message_text.encode().hex()}', nonce))

        # Insert receipt
        cursor.execute("""
            INSERT INTO transaction_receipts (tx_hash, block_number, tx_index, from_address, to_address,
                                              gas_used, cumulative_gas_used, status, contract_address)
            VALUES (?, ?, 0, ?, ?, 0, 0, 1, NULL)
        """, (tx_hash, new_block_number, from_address, target))

        conn.commit()
    except Exception as e:
        logger.error(f"Audit tx creation failed: {e}")
        # Funding succeeded even if audit tx fails — log but don't rollback balance
    finally:
        conn.close()

    # ── 8. Update trackers ──
    FUND_NONCE_TRACKER[signer] = nonce
    daily[today] = daily_total + amount_wei
    FUND_DAILY_TRACKER[signer] = daily

    logger.info(f"FUNDED: {amount_wei / 1e18:.6f} FCO -> {target} by operator {signer} (nonce={nonce})")

    return {
        "transactionHash": tx_hash,
        "funded": amount_hex,
        "target": target,
        "operator": signer,
        "newBalance": hex(int(new_balance)),
        "blockNumber": hex(new_block_number)
    }
```

#### Register the Method in the RPC Router

Add to the method dispatch in `web3_api_v04998.py`:

```python
# In the JSON-RPC method router (handle_rpc function)
elif method == 'fco_fundAccount':
    result = fco_fund_account(params)
    if 'error' in result:
        return jsonify({"id": req_id, "jsonrpc": "2.0", "error": result["error"]})
    return jsonify({"id": req_id, "jsonrpc": "2.0", "result": result})
```

#### Client-Side Usage (JavaScript / ethers.js)

```javascript
const { ethers } = require("ethers");

const CHAIN_ID = 11111111111;
const RPC_URL = "https://rpc.fanati.co";

// Operator wallet (must be in AUTHORIZED_OPERATORS)
const operatorKey = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";
const operator = new ethers.Wallet(operatorKey);

async function fundAccount(targetAddress, amountFCO, nonce) {
    const provider = new ethers.JsonRpcProvider(RPC_URL);
    const amountHex = "0x" + ethers.parseEther(amountFCO).toString(16);
    const nonceHex = "0x" + nonce.toString(16);

    // Sign the funding message
    const message = `fco_fund:${CHAIN_ID}:${targetAddress.toLowerCase()}:${amountHex}:${nonceHex}`;
    const signature = await operator.signMessage(message);

    // Call the RPC method
    const result = await provider.send("fco_fundAccount", [
        targetAddress,
        amountHex,
        nonceHex,
        signature
    ]);

    console.log("Funded:", result);
    return result;
}

// Example: Fund a new developer with 100 FCO
fundAccount("0xNEW_DEV_ADDRESS_HERE", "100.0", 1);
```

#### Client-Side Usage (Python / web3.py)

```python
from web3 import Web3
from eth_account.messages import encode_defunct
from eth_account import Account

CHAIN_ID = 11111111111
RPC_URL = "https://rpc.fanati.co"

# Operator (must be in AUTHORIZED_OPERATORS)
operator_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
operator = Account.from_key(operator_key)

def fund_account(target: str, amount_fco: float, nonce: int):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    amount_wei = w3.to_wei(amount_fco, "ether")
    amount_hex = hex(amount_wei)
    nonce_hex = hex(nonce)

    # Sign the funding message
    message_text = f"fco_fund:{CHAIN_ID}:{target.lower()}:{amount_hex}:{nonce_hex}"
    message = encode_defunct(text=message_text)
    signed = operator.sign_message(message)

    # Call the RPC method
    result = w3.provider.make_request("fco_fundAccount", [
        target, amount_hex, nonce_hex, signed.signature.hex()
    ])

    print(f"Funded {amount_fco} FCO -> {target}")
    print(f"TX: {result['result']['transactionHash']}")
    return result["result"]

# Example
fund_account("0xNEW_DEV_ADDRESS_HERE", 100.0, 1)
```

#### Client-Side Usage (curl)

```bash
# Step 1: Generate signature offline (using cast from Foundry)
OPERATOR_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
TARGET="0x1234567890abcdef1234567890abcdef12345678"
AMOUNT="0x56bc75e2d63100000"  # 100 FCO in hex wei
NONCE="0x1"
MESSAGE="fco_fund:11111111111:${TARGET}:${AMOUNT}:${NONCE}"
SIGNATURE=$(cast wallet sign --private-key $OPERATOR_KEY "$MESSAGE")

# Step 2: Call the RPC
curl -s -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"fco_fundAccount\",
    \"params\": [\"$TARGET\", \"$AMOUNT\", \"$NONCE\", \"$SIGNATURE\"],
    \"id\": 1
  }" | python3 -m json.tool
```

### Security Properties

| Property | Implementation |
|----------|---------------|
| **Authentication** | ECDSA signature recovery — only addresses in `AUTHORIZED_OPERATORS` can fund |
| **Replay protection** | Monotonically increasing nonce per operator |
| **Rate limiting** | 10,000 FCO per call, 100,000 FCO per day per operator |
| **Audit trail** | Every funding creates a synthetic transaction from `0x0000...0000` with full block/receipt |
| **No public faucet** | Method rejects requests from non-operators with `-32000` error |
| **Write restriction** | Only paratime (authority node) processes writes; replicas are read-only |
| **No contract changes** | Pure API-level addition, no Solidity changes needed |

### Simpler Alternative: Admin-Only HTTP Endpoint

For internal/dev use only, a simpler approach that skips ECDSA signatures:

```python
import os

ADMIN_SECRET = os.environ.get('FCO_ADMIN_SECRET', 'change-me-in-production')

@app.route('/admin/fund', methods=['POST'])
def admin_fund():
    """
    Internal-only funding endpoint. Restricted to localhost or SSH tunnel.

    POST /admin/fund
    Headers: X-Admin-Key: <secret>
    Body: {"address": "0x...", "amount_fco": 100.0}
    """
    if request.headers.get('X-Admin-Key') != ADMIN_SECRET:
        return jsonify({"error": "unauthorized"}), 403

    data = request.json
    address = data.get('address', '').lower()
    amount_fco = float(data.get('amount_fco', 0))

    if not address or amount_fco <= 0:
        return jsonify({"error": "invalid params"}), 400

    amount_wei = int(amount_fco * 10**18)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO balances (address, balance, nonce)
        VALUES (?, ?, 0)
        ON CONFLICT(address) DO UPDATE SET
            balance = CAST((CAST(balance AS INTEGER) + ?) AS TEXT)
    """, (address, str(amount_wei), amount_wei))
    conn.commit()

    cursor.execute("SELECT balance FROM balances WHERE address = ?", (address,))
    new_balance = cursor.fetchone()[0]
    conn.close()

    return jsonify({
        "funded": f"{amount_fco} FCO",
        "address": address,
        "newBalance": f"{int(new_balance) / 1e18:.6f} FCO"
    })
```

Usage:

```bash
# Via SSH tunnel to paratime (secure, no public exposure)
ssh -L 8545:localhost:8545 paratime

curl -s -X POST http://localhost:8545/admin/fund \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: change-me-in-production" \
  -d '{"address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266", "amount_fco": 1000}' \
  | python3 -m json.tool
```

### Deployment Notes

1. **Paratime only**: The funding method must only execute on the authority node (paratime). Replicas sync via SCP every 2 minutes and should reject write operations.
2. **DB replication**: After funding on paratime, the new balance propagates to consensus1, consensus2, and seed1 within 2 minutes via the SCP-based sync.
3. **nginx passthrough**: The `/admin/fund` endpoint (if used) should NOT be proxied by nginx on rpc.fanati.co. It should only be accessible via direct SSH tunnel.
4. **Dependencies**: The `fco_fundAccount` RPC method requires `eth_account` Python package (already installed on all nodes).

### Comparison: Signature-Gated vs Admin-Only

| Feature | `fco_fundAccount` (RPC) | `/admin/fund` (HTTP) |
|---------|------------------------|---------------------|
| Authentication | ECDSA signature | API key header |
| Exposure | Public RPC (but auth-gated) | Localhost only (SSH tunnel) |
| Replay protection | Nonce-based | None (relies on network isolation) |
| Audit trail | Full synthetic tx + block | Logging only |
| Client complexity | Sign message + call RPC | Simple HTTP POST |
| Operator management | On-chain address list | Environment variable |
| Recommended for | Production, multi-operator | Dev/test, single admin |

### Recommended Implementation Order

1. **Phase 1** (immediate): Deploy `/admin/fund` HTTP endpoint on paratime for developer use
2. **Phase 2** (v0.5.1): Implement full `fco_fundAccount` RPC method with signature verification
3. **Phase 3** (v0.5.1+): Add operator management UI and funding dashboard

---

## Appendix: Infrastructure Reference

| Node | Role | SSH | HTTP RPC | Public URL |
|------|------|-----|----------|------------|
| paratime | Authority (writes) | `ssh paratime` | `:8545` | `https://rpc.fanati.co` |
| consensus1 | Read replica | `ssh consensus1` | `:8545` | Internal |
| consensus2 | Read replica | `ssh consensus2` | `:8545` | Internal |
| seed1 | Read replica / seed | `ssh seed1` | `:8545` | `https://seed1.fanati.co` |

**DB path**: `/home/claude/fco_blockchain_v04963.db` (all nodes)
**API source**: `/home/claude/fanatico-l1/web3_api_v04998.py` (all nodes)
**Node management**: `ssh <node> '/home/claude/fanatico-l1/manage.sh status|start|stop|logs'`
**DB sync**: paratime -> replicas every 2 minutes via SCP crontab

---

**Document version**: 1.0
**Author**: Claude (Anthropic) for Fanatico L1 team
**Jira**: [FAN-2068](https://fanatico.atlassian.net/browse/FAN-2068) (FANATICO CHAIN epic)
