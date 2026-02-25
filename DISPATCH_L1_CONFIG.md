# Dispatch Service Configuration for Fanatico L1

**Jira**: [FAN-2302](https://fanatico.atlassian.net/browse/FAN-2302)
**Date**: 2026-02-04
**Status**: Configuration Ready

---

## Overview

Dispatch is a backend middleware service for transaction queuing and signature orchestration. It is NOT a smart contract. This document provides the configuration updates needed to migrate Dispatch from Ethereum/Polygon to Fanatico L1.

---

## Network Configuration

### Current (Ethereum/Polygon)

```env
CHAIN_ID=137
RPC_URL=https://polygon-rpc.com
GAS_PRICE=dynamic (EIP-1559)
```

### New (Fanatico L1)

```env
L1_CHAIN_ID=11111111111
L1_RPC_URL=https://rpc.fanati.co
L1_RPC_INTERNAL=http://paratime.fanati.co:8545
L1_GAS_PRICE=20000000000
L1_CURRENCY=FCO
```

---

## Contract Addresses

All contracts are deployed and verified on Fanatico L1 (Chain ID: 11111111111).

### Core Contracts

```env
AUTHORITY_CONTRACT_L1=0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2
FCO_CONTRACT_L1=0xd6F8Ff0036D8B2088107902102f9415330868109
NFT_CONTRACT_L1=0x0442121975b1D8a0860F8B80318f84402284A211
MARKETPLACE_CONTRACT_L1=0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9
```

### Auction Contracts

```env
AUCTION_ENG_CONTRACT_L1=0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049
AUCTION_DUT_CONTRACT_L1=0x4437204542e5C71409Af1eE0154Ce5fa659f55a7
AUCTION_SEN_CONTRACT_L1=0xCe1370E6013989185ac2552832099F24a85DbfD4
AUCTION_LUB_CONTRACT_L1=0xB3faFE3b27fCB65689d540c5185a8420310d59dA
```

### API Services

```env
FCO_METRICS_API=http://paratime.fanati.co:3001
```

---

## EIP-712 Domain Configuration

Update the EIP-712 typed data domain for Fanatico L1:

### Current Domain

```javascript
const domain = {
  name: "Fanatico",
  version: "1",
  chainId: 137, // Polygon
  verifyingContract: "0x..." // Polygon contract
};
```

### New Domain (L1)

```javascript
const EIP712_DOMAIN = {
  name: "Fanatico",
  version: "1",
  chainId: 11111111111n, // Fanatico L1
  verifyingContract: "0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2" // Authority
};
```

### Type Definitions (unchanged)

```javascript
const EIP712_TYPES = {
  Transfer: [
    { name: "wallet", type: "address" },
    { name: "amount", type: "uint256" },
    { name: "deadline", type: "uint256" },
    { name: "nonce", type: "uint256" },
    { name: "description", type: "string" }
  ],
  Mint: [
    { name: "to", type: "address" },
    { name: "tokenURI", type: "string" },
    { name: "deadline", type: "uint256" },
    { name: "nonce", type: "uint256" }
  ],
  List: [
    { name: "tokenId", type: "uint256" },
    { name: "price", type: "uint256" },
    { name: "deadline", type: "uint256" },
    { name: "nonce", type: "uint256" }
  ]
};
```

---

## Gas Configuration

Fanatico L1 uses **fixed gas pricing** (not EIP-1559 dynamic).

### Gas Settings

```javascript
const GAS_CONFIG = {
  gasPrice: 20000000000n, // 20 Gwei (fixed)
  maxFeePerGas: 20000000000n, // Same as gasPrice
  maxPriorityFeePerGas: 0n, // No priority fee needed

  // Gas limits by operation
  gasLimits: {
    transfer: 100000n,
    mint: 500000n,
    list: 300000n,
    buy: 500000n,
    bid: 200000n,
    approve: 100000n
  }
};
```

### Remove Dynamic Fee Estimation

```javascript
// REMOVE this code:
// const feeData = await provider.getFeeData();
// const maxFeePerGas = feeData.maxFeePerGas;

// USE this instead:
const gasPrice = 20000000000n; // Fixed 20 Gwei
```

---

## Provider Configuration

### ethers.js v6

```javascript
import { ethers } from "ethers";

const L1_CONFIG = {
  chainId: 11111111111,
  name: "Fanatico L1",
  rpcUrl: "https://rpc.fanati.co"
};

// Create provider
const provider = new ethers.JsonRpcProvider(L1_CONFIG.rpcUrl, {
  chainId: L1_CONFIG.chainId,
  name: L1_CONFIG.name
});

// Create signer (for backend operations)
const signer = new ethers.Wallet(process.env.BACKEND_PRIVATE_KEY, provider);
```

### web3.js

```javascript
const Web3 = require("web3");

const web3 = new Web3("https://rpc.fanati.co");

// Verify chain ID
const chainId = await web3.eth.getChainId();
console.assert(chainId === 11111111111n, "Wrong chain!");
```

---

## Service Data Endpoint Updates

### GET /dispatch/serviceData

Update response to include L1 configuration:

```javascript
// Response format
{
  chainId: 11111111111,
  rpcUrl: "https://rpc.fanati.co",
  gasPrice: "20000000000", // 20 Gwei
  currency: "FCO",
  contracts: {
    authority: "0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2",
    fco: "0xd6F8Ff0036D8B2088107902102f9415330868109",
    nft: "0x0442121975b1D8a0860F8B80318f84402284A211",
    marketplace: "0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9",
    auctions: {
      eng: "0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049",
      dut: "0x4437204542e5C71409Af1eE0154Ce5fa659f55a7",
      sen: "0xCe1370E6013989185ac2552832099F24a85DbfD4",
      lub: "0xB3faFE3b27fCB65689d540c5185a8420310d59dA"
    }
  }
}
```

---

## Files to Update

| File | Changes |
|------|---------|
| `config/blockchain.js` | Chain ID, RPC URL, gas price |
| `services/dispatch.service.js` | Provider initialization |
| `services/web3.service.js` | L1 provider setup |
| `utils/eip712.utils.js` | Domain configuration |
| `controllers/dispatch.controller.js` | Contract addresses |
| `.env` or secrets | All contract addresses |

---

## Migration Checklist

### Backend Configuration

- [ ] Update `.env` with L1 contract addresses
- [ ] Update chain ID to 11111111111
- [ ] Update RPC URL to https://rpc.fanati.co
- [ ] Update gas price to fixed 20 Gwei
- [ ] Remove dynamic fee estimation code
- [ ] Update EIP-712 domain with L1 chain ID

### Testing

- [ ] Test provider connection to L1 RPC
- [ ] Test chain ID verification
- [ ] Test dispatch create with L1 contracts
- [ ] Test EIP-712 signature generation
- [ ] Test transaction submission to L1
- [ ] Verify gas estimation works

### Verification Commands

```bash
# Test RPC connection
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
# Expected: {"result":"0x2964619c7"}

# Test FCO contract
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_call","params":[{"to":"0xd6F8Ff0036D8B2088107902102f9415330868109","data":"0x06fdde03"},"latest"],"id":1}'
# Expected: Returns "Fanatico" encoded

# Test NFT contract
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_call","params":[{"to":"0x0442121975b1D8a0860F8B80318f84402284A211","data":"0x06fdde03"},"latest"],"id":1}'
# Expected: Returns "Fanatico Publication" encoded
```

---

## Remove Multi-Chain Support

Fanatico L1 is a single-chain deployment. Remove:

- Polygon configuration
- Ethereum mainnet configuration
- BSC configuration
- Arbitrum configuration
- Chain switching logic
- Bridge functionality

---

## Known Issues

### Write Operations

Some contract write operations may not persist state correctly on L1. This is a known EVM compatibility issue being investigated. Read operations work correctly.

**Affected**:
- FCO supplyAccount()
- NFT transfers via Marketplace

**Workaround**: Monitor for L1 RPC updates

---

## Contact

- **L1 Team**: For contract issues
- **Backend Team**: dev@fanati.co
- **Jira**: [FAN-2302](https://fanatico.atlassian.net/browse/FAN-2302)

---

**Document Version**: 1.0
**Last Updated**: 2026-02-04
