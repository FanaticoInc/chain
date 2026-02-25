# Fanatico L1 Backend Integration Requirements

**Date**: 2026-02-03
**Version**: 1.0
**Status**: P0 Blockers Identified
**Jira Epic**: [FAN-2068](https://fanatico.atlassian.net/browse/FAN-2068) (FANATICO CHAIN)

---

## Executive Summary

The Fanatico backend has **57 Web3 endpoints** that need to work with Fanatico L1. Assessment complete:

| Status | Count | Percentage |
|--------|-------|------------|
| Fully Compatible | 38 | 67% |
| Need Contract Address Updates | 12 | 21% |
| Partial Functionality | 5 | 9% |
| Not Compatible | 2 | 3% |

**Critical Finding**: Migration **CANNOT** proceed until 5 smart contracts are deployed on L1.

---

## P0 Blockers - Contract Deployments Required

These Jira issues block all backend Web3 functionality:

| Jira | Contract | Endpoints Blocked | Dependencies | Status |
|------|----------|-------------------|--------------|--------|
| [FAN-2298](https://fanatico.atlassian.net/browse/FAN-2298) | FCO Token (ERC-20) | 0 (unblocked) | None | ✅ Deployed |
| [FAN-2299](https://fanatico.atlassian.net/browse/FAN-2299) | NFT (ERC-721) | 0 (unblocked) | None | ✅ Deployed |
| [FAN-2300](https://fanatico.atlassian.net/browse/FAN-2300) | Marketplace | 0 (unblocked) | FCO, NFT | ✅ Deployed |
| [FAN-2301](https://fanatico.atlassian.net/browse/FAN-2301) | Auction Contracts | 0 (unblocked) | FCO, NFT | ✅ Deployed |
| [FAN-2302](https://fanatico.atlassian.net/browse/FAN-2302) | Dispatch | 0 (backend config) | FCO | ✅ Config Ready |

**Deployed Contracts**:
- Authority: `0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2`
- FCO Token: `0xd6F8Ff0036D8B2088107902102f9415330868109`
- FanaticoNFT: `0x0442121975b1D8a0860F8B80318f84402284A211`
- Marketplace: `0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9`
- AuctionEng: `0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049`
- AuctionDut: `0x4437204542e5C71409Af1eE0154Ce5fa659f55a7`
- AuctionSen: `0xCe1370E6013989185ac2552832099F24a85DbfD4`
- AuctionLub: `0xB3faFE3b27fCB65689d540c5185a8420310d59dA`
- Metrics API: http://paratime.fanati.co:3001

### Dependency Graph

```
┌─────────────────┐     ┌─────────────────┐
│   FCO Token     │     │   NFT Contract  │
│   (FAN-2298)    │     │   (FAN-2299)    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ├───────────┬───────────┤
         │           │           │
         ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Marketplace │ │  Auctions   │ │  Dispatch   │
│ (FAN-2300)  │ │ (FAN-2301)  │ │ (FAN-2302)  │
└─────────────┘ └─────────────┘ └─────────────┘
```

**Deployment Order**:
1. FCO Token + NFT Contract (parallel, no dependencies)
2. Dispatch Contract (needs FCO)
3. Marketplace (needs FCO + NFT)
4. Auction Contracts (needs FCO + NFT)

---

## L1 Network Configuration

### Production Network

| Parameter | Value |
|-----------|-------|
| **Network Name** | Fanatico L1 |
| **Chain ID** | 11111111111 (0x2964619c7) |
| **RPC URL** | https://rpc.fanati.co |
| **Internal RPC** | http://paratime.fanati.co:8545 |
| **WebSocket** | ws://paratime.fanati.co:8546 |
| **Currency Symbol** | FCO |
| **Gas Price** | Fixed 20 Gwei |
| **Block Explorer** | http://paratime.fanati.co:8080 |

### Current Chain (Ethereum/Polygon)

| Parameter | Ethereum | Polygon |
|-----------|----------|---------|
| Chain ID | 1 | 137 |
| RPC URL | Infura | Infura |
| Gas Price | Dynamic (EIP-1559) | Dynamic |
| FCO Contract | 0x... | 0x... |

---

## Contract Specifications

### 1. FCO Token Contract (FAN-2298)

**Standard**: ERC-20
**Blocking**: 28 endpoints

**Required Functions**:
```solidity
// Standard ERC-20
function balanceOf(address account) external view returns (uint256);
function transfer(address to, uint256 amount) external returns (bool);
function approve(address spender, uint256 amount) external returns (bool);
function transferFrom(address from, address to, uint256 amount) external returns (bool);
function allowance(address owner, address spender) external view returns (uint256);

// Extensions
function mint(address to, uint256 amount) external;  // Bonus system
function burn(uint256 amount) external;              // Token burns
```

**Events**:
```solidity
event Transfer(address indexed from, address indexed to, uint256 value);
event Approval(address indexed owner, address indexed spender, uint256 value);
```

**Backend Endpoints Using FCO**:
- `/wallet/transferFco` - Transfer FCO between users
- `/wallet/tippingFco` - Tip creators with FCO
- `/wallet/subscribeFco` - Subscribe using FCO
- `/fco/transfer` - Direct FCO transfer
- `/fco/transfer/execute` - Execute pending transfer
- `/fco/deposit` - Detect FCO deposits
- `/fco/depositConfirm` - Confirm deposits
- `/subscriptions/subscribeFco` - Subscription payments
- `/bonus/requestSignUpBonus` - Mint bonus FCO

---

### 2. NFT Contract (FAN-2299)

**Standard**: ERC-721
**Blocking**: 18 endpoints

**Required Functions**:
```solidity
// Standard ERC-721
function ownerOf(uint256 tokenId) external view returns (address);
function balanceOf(address owner) external view returns (uint256);
function transferFrom(address from, address to, uint256 tokenId) external;
function safeTransferFrom(address from, address to, uint256 tokenId) external;
function approve(address to, uint256 tokenId) external;
function setApprovalForAll(address operator, bool approved) external;
function getApproved(uint256 tokenId) external view returns (address);
function isApprovedForAll(address owner, address operator) external view returns (bool);

// Extensions
function mint(address to, string memory tokenURI) external returns (uint256);
function tokenURI(uint256 tokenId) external view returns (string memory);
```

**Events**:
```solidity
event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
```

**Backend Endpoints Using NFT**:
- `/publication/init` - Mint new NFT
- `/publication/confirm` - Confirm NFT with metadata
- `/publication/transfer` - Transfer NFT ownership
- `/publication/delegate` - Delegate NFT rights
- `/publication/getByTokenId` - Query NFT by ID
- `/publication/decrypt` - Decrypt NFT content
- `/metadata/:id` - Get NFT metadata

---

### 3. Marketplace Contract (FAN-2300)

**Dependencies**: FCO Token, NFT Contract
**Blocking**: 3 endpoints

**Required Functions**:
```solidity
function listForSale(uint256 tokenId, uint256 price) external;
function cancelListing(uint256 tokenId) external;
function buy(uint256 tokenId) external payable;
function getListing(uint256 tokenId) external view returns (Listing memory);
```

**Backend Endpoints**:
- `/publication/listSale` - List NFT for fixed price
- `/publication/buySale` - Purchase listed NFT
- `/publication/unlist` - Remove from marketplace

---

### 4. Auction Contracts (FAN-2301)

**Dependencies**: FCO Token, NFT Contract
**Blocking**: 10 endpoints

**Auction Types Required**:

| Type | Name | Description |
|------|------|-------------|
| Dutch (Lub) | Sealed-bid with buy-now | Encrypted bids, optional instant purchase |
| Dutch (Dut) | Price-descending | Price drops over time |
| English (Eng) | Price-ascending | Traditional bidding |
| Sealed (Sen) | Second-price | Winner pays second-highest bid |

**Backend Endpoints**:
- `/publication/listLub`, `/publication/buyLub`, `/publication/bidLub`
- `/publication/listDut`, `/publication/buyDut`
- `/publication/listEng`, `/publication/bidEng`
- `/publication/listSen`, `/publication/bidSen`
- `/auction/getParticipants`, `/auction/getLubBids`

---

### 5. Dispatch Contract (FAN-2302)

**Dependencies**: FCO Token
**Blocking**: 6 endpoints

**Purpose**: Queue and execute blockchain transactions

**Required Functions**:
```solidity
function createDispatch(bytes calldata data) external returns (uint256);
function executeDispatch(uint256 dispatchId) external;
function getDispatch(uint256 dispatchId) external view returns (Dispatch memory);
function getDispatchStatus(uint256 dispatchId) external view returns (uint8);
```

**Backend Endpoints**:
- `/dispatch/create` - Create new dispatch
- `/dispatch/execute` - Execute queued dispatch
- `/dispatch/verify` - Verify on-chain status
- `/dispatch/serviceData` - Get service config
- `/dispatch/requestSignUpMint` - Mint signup NFT

---

## RPC Method Compatibility

### Fully Compatible (18/22 tested)

| Method | Status | Usage |
|--------|--------|-------|
| `eth_chainId` | ✅ | Chain identification |
| `eth_blockNumber` | ✅ | Current block |
| `eth_gasPrice` | ✅ | Returns 20 Gwei |
| `eth_getBalance` | ✅ | Balance queries |
| `eth_getTransactionCount` | ✅ | Nonce queries |
| `eth_call` | ✅ | Contract reads |
| `eth_estimateGas` | ✅ | Gas estimation |
| `eth_sendRawTransaction` | ✅ | Transaction submission |
| `eth_getTransactionReceipt` | ✅ | TX confirmation |
| `eth_getTransactionByHash` | ✅ | TX lookup |
| `eth_getBlockByNumber` | ✅ | Block queries |
| `eth_getBlockByHash` | ✅ | Block queries |
| `eth_getLogs` | ✅ | Event queries |
| `eth_getCode` | ✅ | Contract bytecode |
| `net_version` | ✅ | Network ID |
| `eth_syncing` | ✅ | Sync status |
| `web3_clientVersion` | ✅ | Client info |
| `eth_accounts` | ✅ | Returns [] |

### Missing Methods (Workarounds Available)

| Method | Impact | Workaround |
|--------|--------|------------|
| `eth_feeHistory` | EIP-1559 fee estimation | Use fixed 20 Gwei |
| `eth_maxPriorityFeePerGas` | Priority fee | Use 0 |
| `personal_sign` | Message signing | Client-side signing |
| `eth_signTypedData_v4` | EIP-712 signing | Client-side signing |

### EIP-1559 Handling

L1 uses **fixed 20 Gwei** gas price. Backend code must use:

```javascript
// Instead of dynamic fee estimation
const maxFeePerGas = 20000000000n;       // 20 Gwei
const maxPriorityFeePerGas = 0n;          // No priority fee needed
```

---

## Web3 Endpoint Compatibility Matrix

### Wallet Operations (14 endpoints)

| Endpoint | L1 Status | Notes |
|----------|-----------|-------|
| `/wallet/setWallet` | ✅ | Database only |
| `/wallet/setWalletBackup` | ✅ | Database only |
| `/wallet/getWalletBackup` | ✅ | Database only |
| `/wallet/unsetWallets` | ✅ | Database only |
| `/wallet/getBcConfig` | ⚠️ | Needs L1 config |
| `/wallet/registerTx` | ⚠️ | Needs L1 RPC URL |
| `/wallet/transferFco` | ⚠️ | Needs L1 FCO contract |
| `/wallet/tippingFco` | ⚠️ | Needs L1 FCO contract |
| `/wallet/buyFco` | 🔶 | No fiat-to-L1 bridge |
| `/wallet/inAppPurchaseRequest` | 🔶 | App store → L1 bridge needed |
| `/wallet/subscribeFco` | ⚠️ | Needs L1 FCO contract |
| `/wallet/marketInfo` | ⚠️ | Needs L1 price feeds |

### FCO Token Operations (10 endpoints)

| Endpoint | L1 Status | Notes |
|----------|-----------|-------|
| `/fco/` | ⚠️ | Needs L1 FCO contract |
| `/fco/transfer` | ⚠️ | Needs L1 FCO contract |
| `/fco/transfer/request` | ✅ | Database only |
| `/fco/transfer/execute` | ⚠️ | Needs L1 FCO contract |
| `/fco/cash` | 🔶 | FCO→fiat requires exchange |
| `/fco/bank` | 🔶 | FCO→bank requires bridge |
| `/fco/bridge` | ❌ | L1 is single chain |
| `/fco/deposit` | ⚠️ | Needs L1 event monitoring |
| `/fco/depositConfirm` | ⚠️ | Needs L1 RPC |
| `/fco/lastDeposits` | ✅ | Database query |

### Publication/NFT Operations (18 endpoints)

| Endpoint | L1 Status | Notes |
|----------|-----------|-------|
| `/publication/getByTokenId` | ✅ | L1 compatible |
| `/publication/init` | ⚠️ | Needs L1 NFT contract |
| `/publication/confirm` | ⚠️ | Needs L1 RPC |
| `/publication/decrypt` | ✅ | L1 compatible (read) |
| `/publication/transfer` | ⚠️ | Needs L1 NFT contract |
| `/publication/delegate` | ⚠️ | Needs L1 contract |
| `/publication/listSale` | ⚠️ | Needs L1 marketplace |
| `/publication/buySale` | ⚠️ | Needs L1 marketplace |
| `/publication/unlist` | ⚠️ | Needs L1 marketplace |
| `/publication/list*` (auctions) | ⚠️ | Needs L1 auction contracts |
| `/publication/buy*` (auctions) | ⚠️ | Needs L1 auction contracts |
| `/publication/bid*` (auctions) | ⚠️ | Needs L1 auction contracts |

### Dispatch Operations (8 endpoints)

| Endpoint | L1 Status | Notes |
|----------|-----------|-------|
| `/dispatch/` | ✅ | Database query |
| `/dispatch/serviceData` | ⚠️ | Needs L1 RPC, fixed gas |
| `/dispatch/capabilities` | ⚠️ | Return L1 capabilities |
| `/dispatch/:id` | ✅ | Database query |
| `/dispatch/requestSignUpMint` | ⚠️ | Needs L1 NFT contract |
| `/dispatch/create` | ⚠️ | Needs L1 RPC |
| `/dispatch/execute` | ⚠️ | Needs L1 RPC |
| `/dispatch/verify` | ✅ | L1 compatible |

### Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fully compatible, no changes |
| ⚠️ | Compatible after config/contract updates |
| 🔶 | Partial functionality |
| ❌ | Not compatible |

---

## Backend Configuration Requirements

### Environment Variables

**Current (Ethereum)**:
```env
INFURA_API_KEY=fff61defcdfe45c6b238b1a7516be240
ETH_CHAIN_ID=1
POLYGON_CHAIN_ID=137
FCO_CONTRACT_ETH=0x...
FCO_CONTRACT_POLYGON=0x...
NFT_CONTRACT_ETH=0x...
```

**New (L1)**:
```env
L1_RPC_URL=https://rpc.fanati.co
L1_CHAIN_ID=11111111111
L1_GAS_PRICE=20000000000
AUTHORITY_CONTRACT_L1=0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2
FCO_CONTRACT_L1=0xd6F8Ff0036D8B2088107902102f9415330868109
NFT_CONTRACT_L1=0x0442121975b1D8a0860F8B80318f84402284A211
MARKETPLACE_CONTRACT_L1=0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9
AUCTION_ENG_CONTRACT_L1=0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049
AUCTION_DUT_CONTRACT_L1=0x4437204542e5C71409Af1eE0154Ce5fa659f55a7
AUCTION_SEN_CONTRACT_L1=0xCe1370E6013989185ac2552832099F24a85DbfD4
AUCTION_LUB_CONTRACT_L1=0xB3faFE3b27fCB65689d540c5185a8420310d59dA
DISPATCH_CONTRACT_L1=<TBD after FAN-2302>
FCO_METRICS_API=http://paratime.fanati.co:3001
```

### Files Requiring Updates

| File | Change | Priority |
|------|--------|----------|
| `controllers_ng/wallet_ng.controller.js` | L1 RPC URL, chain ID | P1 |
| `controllers/fco.controller.js` | FCO contract address | P1 |
| `controllers/dispatch.controller.js` | Dispatch contract, RPC | P1 |
| `controllers/publication_*.controller.js` | NFT/marketplace contracts | P1 |
| `config/blockchain.js` | New L1 configuration | P0 |
| `services/web3.service.js` | L1 provider setup | P1 |

---

## Features Lost on L1

| Feature | Current | L1 | Impact |
|---------|---------|-----|--------|
| Multi-chain | ETH, Polygon, BSC, Arbitrum | L1 only | HIGH |
| FCO Bridge | Cross-chain transfers | None | HIGH |
| Dynamic gas | EIP-1559 market | Fixed 20 Gwei | LOW |
| External DEX | Uniswap, etc. | None | MEDIUM |

---

## Testing Requirements

### Pre-Migration

| Test | Description | Status |
|------|-------------|--------|
| RPC connectivity | All methods work | ✅ Verified |
| Contract deployment | Contracts deploy correctly | ⏳ Pending |
| Transaction signing | EIP-1559 accepted | ✅ Verified |
| Event monitoring | eth_getLogs works | ✅ Verified |
| Gas estimation | Consistent 20 Gwei | ✅ Verified |

### Integration Testing

| Flow | Endpoints | Priority |
|------|-----------|----------|
| FCO Transfer | `/wallet/transferFco` → `/dispatch/execute` | P0 |
| NFT Mint | `/publication/init` → `/dispatch/execute` | P0 |
| NFT Sale | `/publication/listSale` → `/publication/buySale` | P1 |
| Auction | `/publication/listLub` → `/auction/getLubBids` | P1 |

---

## Action Items for L1 Team

### Immediate (Before Migration)

1. **Deploy FCO Token Contract** (FAN-2298)
   - ERC-20 with mint/burn extensions
   - Report contract address to backend team

2. **Deploy NFT Contract** (FAN-2299)
   - ERC-721 with tokenURI
   - Report contract address to backend team

3. **Deploy Dispatch Contract** (FAN-2302)
   - Transaction queueing system
   - Signup mint functionality

4. **Deploy Marketplace** (FAN-2300)
   - Fixed-price sales
   - List/buy/unlist functions

5. **Deploy Auction Contracts** (FAN-2301)
   - All 4 auction types
   - Dutch (Lub/Dut), English, Sealed

### Information Needed by Backend

After each contract deployment, provide:

| Item | Example |
|------|---------|
| Contract Address | `0x1234...abcd` |
| ABI JSON | `[{"type":"function",...}]` |
| Deployment TX | `0xabcd...1234` |
| Block Number | `12345` |
| Verification URL | Block explorer link |

---

## Related Documentation

| Document | Location |
|----------|----------|
| L1 README | `/Users/sebastian/CODE/L1/README.md` |
| Web3 Endpoints | `/Users/sebastian/CODE/L1/FANATICO-WEB3-ENDPOINTS.md` |
| RPC Compatibility | `/Users/sebastian/CODE/FREMONT2/documentation/JIRA/FAN-2294-L1-RPC-COMPATIBILITY.md` |
| Compatibility Matrix | `/Users/sebastian/CODE/FREMONT2/documentation/JIRA/FAN-2294-COMPATIBILITY-MATRIX.md` |
| Gaps Analysis | `/Users/sebastian/CODE/FREMONT2/documentation/JIRA/FAN-2294-GAPS-AND-BLOCKERS.md` |
| Migration Plan | `/Users/sebastian/CODE/FREMONT2/documentation/JIRA/FAN-2294-MIGRATION-RECOMMENDATIONS.md` |

---

## Contact

- **Backend Team**: dev@fanati.co
- **Jira Project**: [FAN](https://fanatico.atlassian.net/browse/FAN)
- **Epic**: [FAN-2068](https://fanatico.atlassian.net/browse/FAN-2068)
- **Assessment**: [FAN-2294](https://fanatico.atlassian.net/browse/FAN-2294)

---

**Document Version**: 1.1
**Last Updated**: 2026-02-03
**FCO Deployed**: 2026-02-02
**Next Review**: After NFT contract deployment
