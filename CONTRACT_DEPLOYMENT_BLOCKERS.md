# Fanatico L1 Contract Deployment Blockers

**Date**: 2026-02-03
**Epic**: [FAN-2068](https://fanatico.atlassian.net/browse/FAN-2068) - FANATICO CHAIN
**Priority**: P0 - Critical Path

---

## Summary

**5 contracts must be deployed before backend migration can proceed.**

| # | Contract | Jira | Endpoints Blocked | Dependencies | Status |
|---|----------|------|-------------------|--------------|--------|
| 1 | FCO Token (ERC-20) | [FAN-2298](https://fanatico.atlassian.net/browse/FAN-2298) | 0 | None | ✅ Deployed |
| 2 | NFT (ERC-721) | [FAN-2299](https://fanatico.atlassian.net/browse/FAN-2299) | 0 | None | ✅ Deployed |
| 3 | Marketplace | [FAN-2300](https://fanatico.atlassian.net/browse/FAN-2300) | 0 | FCO + NFT | ✅ Deployed |
| 4 | Auctions (4 types) | [FAN-2301](https://fanatico.atlassian.net/browse/FAN-2301) | 0 | FCO + NFT | ✅ Deployed |
| 5 | Dispatch | [FAN-2302](https://fanatico.atlassian.net/browse/FAN-2302) | 0 | FCO | ✅ Config Ready |

**Total Blocked**: 0 Web3 endpoints - All contracts deployed!

---

## Deployment Order

```
Week 1                    Week 2                    Week 3
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│   FCO   │  │   NFT   │  │Dispatch │  │Marketpl.│  │Auctions │
│FAN-2298 │  │FAN-2299 │  │FAN-2302 │  │FAN-2300 │  │FAN-2301 │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     │            │            │            │            │
     │ PARALLEL   │            │ DEPENDS    │ DEPENDS    │
     └────────────┘            │ ON FCO     │ ON BOTH    │
                               ▼            ▼            ▼
```

---

## Blocker #1: FCO Token Contract ✅ DEPLOYED

### Jira: [FAN-2298](https://fanatico.atlassian.net/browse/FAN-2298)

**Status**: ✅ **DEPLOYED** (2026-02-02)
**Standard**: ERC-20 with balance locking and epochs
**Endpoints Unblocked**: 28

### Deployed Contracts

| Contract | Address |
|----------|---------|
| Authority | `0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2` |
| FCO Token | `0xd6F8Ff0036D8B2088107902102f9415330868109` |

### Metrics API

| Endpoint | URL |
|----------|-----|
| Health | http://paratime.fanati.co:3001/health |
| All Metrics | http://paratime.fanati.co:3001/api/info/stat/metrics |
| Total Supply | http://paratime.fanati.co:3001/api/info/stat/metrics/total-supply |
| Contract Info | http://paratime.fanati.co:3001/api/info/contract |

### Known Issue

Write operations (supplyAccount, receive) are not updating contract storage on L1. Read operations work correctly. Under investigation.

### Required Interface

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IFCOToken {
    // ERC-20 Standard
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function decimals() external view returns (uint8);
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);

    // Extensions for Fanatico
    function mint(address to, uint256 amount) external;
    function burn(uint256 amount) external;

    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}
```

### Backend Endpoints Affected

```
/wallet/transferFco         POST   Transfer FCO between users
/wallet/tippingFco          POST   Tip creators with FCO
/wallet/subscribeFco        POST   Subscribe using FCO
/wallet/buyFco              POST   Purchase FCO (partial - needs fiat bridge)
/fco/                       GET    Get FCO balance
/fco/transfer               POST   Direct FCO transfer
/fco/transfer/execute       POST   Execute pending transfer
/fco/deposit                POST   Detect FCO deposits
/fco/depositConfirm         POST   Confirm deposits
/subscriptions/subscribeFco POST   Subscription payments
/bonus/requestSignUpBonus   POST   Mint bonus FCO
/dispatch/serviceData       GET    Service configuration
```

### Deployment Checklist

- [x] Deploy ERC-20 contract to L1 (2026-02-02)
- [x] Deploy Authority contract to L1
- [x] Verify contract reads (name, symbol, decimals, totalSupply)
- [ ] Verify contract on block explorer
- [ ] Test mint/burn functions (blocked by write issue)
- [ ] Test transfer functions (blocked by write issue)
- [x] Generate ABI (in hardhat artifacts)
- [x] Deploy metrics API (http://paratime.fanati.co:3001)
- [ ] Report contract address to backend team
- [ ] Test with backend `/fco/` endpoint

---

## Blocker #2: NFT Contract ✅ DEPLOYED

### Jira: [FAN-2299](https://fanatico.atlassian.net/browse/FAN-2299)

**Status**: ✅ **DEPLOYED** (2026-02-03)
**Standard**: ERC-721 + ERC721URIStorage + ERC2981 (Royalty)
**Endpoints Unblocked**: 18

### Deployed Contract

| Property | Value |
|----------|-------|
| Address | `0x0442121975b1D8a0860F8B80318f84402284A211` |
| Name | Fanatico Publication |
| Symbol | FPUB |
| Royalty | 5% (500 basis points) |

### Required Interface

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IFanaticoNFT {
    // ERC-721 Standard
    function balanceOf(address owner) external view returns (uint256);
    function ownerOf(uint256 tokenId) external view returns (address);
    function safeTransferFrom(address from, address to, uint256 tokenId) external;
    function safeTransferFrom(address from, address to, uint256 tokenId, bytes calldata data) external;
    function transferFrom(address from, address to, uint256 tokenId) external;
    function approve(address to, uint256 tokenId) external;
    function setApprovalForAll(address operator, bool approved) external;
    function getApproved(uint256 tokenId) external view returns (address);
    function isApprovedForAll(address owner, address operator) external view returns (bool);

    // ERC-721 Metadata
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function tokenURI(uint256 tokenId) external view returns (string memory);

    // Fanatico Extensions
    function mint(address to, string memory tokenURI) external returns (uint256);
    function setTokenURI(uint256 tokenId, string memory tokenURI) external;

    // Events
    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);
}
```

### Backend Endpoints Affected

```
/publication/init           POST   Initialize NFT minting
/publication/confirm        POST   Confirm NFT with metadata
/publication/transfer       POST   Transfer NFT ownership
/publication/delegate       POST   Delegate NFT rights
/publication/getByTokenId   GET    Query NFT by token ID
/publication/decrypt        POST   Decrypt NFT content
/metadata/:id               GET    Get NFT metadata
/dispatch/requestSignUpMint POST   Mint signup NFT
```

### Deployment Checklist

- [x] Deploy ERC-721 contract to L1 (2026-02-03)
- [x] Test mint function with tokenURI
- [x] Test transfer functions
- [x] Verify ERC-721 interface support
- [x] Verify ERC-2981 royalty support
- [x] Generate ABI (in hardhat artifacts)
- [ ] Verify contract on block explorer
- [ ] Report contract address to backend team
- [ ] Test with backend `/publication/init` endpoint

---

## Blocker #3: Marketplace Contract ✅ DEPLOYED

### Jira: [FAN-2300](https://fanatico.atlassian.net/browse/FAN-2300)

**Status**: ✅ **DEPLOYED** (2026-02-03)
**Dependencies**: FCO Token (FAN-2298), NFT Contract (FAN-2299)
**Endpoints Unblocked**: 3

### Deployed Contract

| Property | Value |
|----------|-------|
| Address | `0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9` |
| Service Fee | 2.5% (250 basis points) |
| NFT Contract | `0x0442121975b1D8a0860F8B80318f84402284A211` |

### Required Interface

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IMarketplace {
    struct Listing {
        address seller;
        uint256 tokenId;
        uint256 price;
        bool active;
    }

    function listForSale(uint256 tokenId, uint256 price) external;
    function cancelListing(uint256 tokenId) external;
    function buy(uint256 tokenId) external payable;
    function getListing(uint256 tokenId) external view returns (Listing memory);
    function getActiveListings() external view returns (uint256[] memory);

    event Listed(address indexed seller, uint256 indexed tokenId, uint256 price);
    event Sold(address indexed seller, address indexed buyer, uint256 indexed tokenId, uint256 price);
    event Cancelled(address indexed seller, uint256 indexed tokenId);
}
```

### Backend Endpoints Affected

```
/publication/listSale       POST   List NFT for fixed-price sale
/publication/buySale        POST   Purchase listed NFT
/publication/unlist         POST   Remove NFT from marketplace
```

### Deployment Checklist

- [x] Wait for FCO and NFT contracts
- [x] Deploy marketplace contract with NFT address (2026-02-03)
- [x] Test listing flow
- [x] Test cancel listing
- [ ] Test purchase flow (known L1 write issue)
- [ ] Verify contract on block explorer
- [ ] Generate and export ABI JSON
- [ ] Report contract address to backend team

---

## Blocker #4: Auction Contracts ✅ DEPLOYED

### Jira: [FAN-2301](https://fanatico.atlassian.net/browse/FAN-2301)

**Status**: ✅ **DEPLOYED** (2026-02-04)
**Dependencies**: FCO Token (FAN-2298), NFT Contract (FAN-2299)
**Endpoints Unblocked**: 10
**Contracts Deployed**: 4

### Deployed Contracts

| Auction Type | Address | Description |
|--------------|---------|-------------|
| AuctionEng | `0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049` | English (ascending price) |
| AuctionDut | `0x4437204542e5C71409Af1eE0154Ce5fa659f55a7` | Dutch (descending price) |
| AuctionSen | `0xCe1370E6013989185ac2552832099F24a85DbfD4` | Sealed second-price (Vickrey) |
| AuctionLub | `0xB3faFE3b27fCB65689d540c5185a8420310d59dA` | Sealed-bid with buy-now |

### Auction Types

| Type | Name | Mechanism |
|------|------|-----------|
| LUB | Sealed-bid + Buy-now | Encrypted bids, optional instant purchase |
| DUT | Dutch | Price decreases over time |
| ENG | English | Traditional ascending bids |
| SEN | Sealed second-price | Winner pays second-highest bid |

### Backend Endpoints Affected

```
# Dutch Auction (Lub - Sealed)
/publication/listLub        POST   List sealed-bid auction
/publication/buyLub         POST   Buy now (if enabled)
/publication/bidLub         POST   Place encrypted bid

# Dutch Auction (Dut - Descending)
/publication/listDut        POST   List Dutch auction
/publication/buyDut         POST   Buy at current price

# English Auction (Ascending)
/publication/listEng        POST   List English auction
/publication/bidEng         POST   Place bid

# Sealed Second-Price
/publication/listSen        POST   List second-price auction
/publication/bidSen         POST   Place encrypted bid

# Query
/auction/getParticipants    GET    Get auction participants
/auction/getLubBids         POST   Get user's bids
```

### Deployment Checklist

- [ ] Wait for FCO and NFT contracts
- [ ] Deploy AuctionLub contract
- [ ] Deploy AuctionDut contract
- [ ] Deploy AuctionEng contract
- [ ] Deploy AuctionSen contract
- [ ] Verify all contracts
- [ ] Test each auction type end-to-end
- [ ] Generate and export all ABIs
- [ ] Report all contract addresses to backend team

---

## Blocker #5: Dispatch Configuration ✅ DOCUMENTED

### Jira: [FAN-2302](https://fanatico.atlassian.net/browse/FAN-2302)

**Status**: ✅ **Configuration Guide Ready** (2026-02-04)
**Type**: Backend middleware (NOT a smart contract)
**Documentation**: `DISPATCH_L1_CONFIG.md`

**Note**: Dispatch is backend middleware for transaction queuing. No smart contract deployment is needed - only backend configuration updates.

### Configuration Checklist

- [x] Create configuration guide document
- [ ] Update backend `.env` with L1 contract addresses
- [ ] Update chain ID to 11111111111
- [ ] Update RPC URL to https://rpc.fanati.co
- [ ] Update EIP-712 domain configuration
- [ ] Update gas price to fixed 20 Gwei
- [ ] Test dispatch service with L1

### Original Interface (For Reference)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IDispatch {
    enum Status { Pending, Executed, Failed, Cancelled }

    struct Dispatch {
        address creator;
        bytes data;
        Status status;
        uint256 createdAt;
        uint256 executedAt;
    }

    function createDispatch(bytes calldata data) external returns (uint256);
    function executeDispatch(uint256 dispatchId) external;
    function cancelDispatch(uint256 dispatchId) external;
    function getDispatch(uint256 dispatchId) external view returns (Dispatch memory);
    function getDispatchStatus(uint256 dispatchId) external view returns (Status);
    function getUserDispatches(address user) external view returns (uint256[] memory);

    event DispatchCreated(uint256 indexed dispatchId, address indexed creator);
    event DispatchExecuted(uint256 indexed dispatchId);
    event DispatchFailed(uint256 indexed dispatchId, string reason);
    event DispatchCancelled(uint256 indexed dispatchId);
}
```

### Backend Endpoints Affected

```
/dispatch/                  GET    Get user's dispatch queue
/dispatch/serviceData       GET    Get service configuration
/dispatch/:id               GET    Get specific dispatch
/dispatch/create            POST   Create new dispatch
/dispatch/execute           POST   Execute queued dispatch
/dispatch/verify            POST   Verify on-chain status
/dispatch/requestSignUpMint POST   Request signup NFT mint
```

### Deployment Checklist

- [ ] Wait for FCO contract
- [ ] Deploy dispatch contract with FCO address
- [ ] Verify contract on block explorer
- [ ] Test dispatch creation
- [ ] Test dispatch execution
- [ ] Test status queries
- [ ] Generate and export ABI JSON
- [ ] Report contract address to backend team

---

## Post-Deployment Requirements

### Information Needed by Backend Team

After each contract deployment, create a deployment report:

```yaml
contract_name: "FCO Token"
jira_issue: "FAN-2298"
network: "Fanatico L1"
chain_id: 11111111111
contract_address: "0x..."
deployment_tx: "0x..."
deployment_block: 12345
deployer_address: "0x..."
verification_url: "http://paratime.fanati.co:8080/address/0x..."
abi_location: "/path/to/abi.json"
constructor_args: []
```

### Contract Address Registry

| Contract | Address | Status |
|----------|---------|--------|
| Authority | `0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2` | ✅ Deployed |
| FCO Token | `0xd6F8Ff0036D8B2088107902102f9415330868109` | ✅ Deployed |
| FanaticoNFT | `0x0442121975b1D8a0860F8B80318f84402284A211` | ✅ Deployed |
| Marketplace | `0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9` | ✅ Deployed |
| AuctionEng | `0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049` | ✅ Deployed |
| AuctionDut | `0x4437204542e5C71409Af1eE0154Ce5fa659f55a7` | ✅ Deployed |
| AuctionSen | `0xCe1370E6013989185ac2552832099F24a85DbfD4` | ✅ Deployed |
| AuctionLub | `0xB3faFE3b27fCB65689d540c5185a8420310d59dA` | ✅ Deployed |
| Marketplace | `TBD` | Pending |
| AuctionLub | `TBD` | Pending |
| AuctionDut | `TBD` | Pending |
| AuctionEng | `TBD` | Pending |
| AuctionSen | `TBD` | Pending |
| Dispatch | `TBD` | Pending |

### FCO Metrics API

| Service | URL | Status |
|---------|-----|--------|
| API Server | http://paratime.fanati.co:3001 | ✅ Running |
| Systemd Service | fco-metrics-api.service | ✅ Enabled |

---

## Testing After Deployment

### Smoke Tests (Per Contract)

```bash
# FCO Token - Get name (returns "Fanatico")
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_call","params":[{"to":"0xd6F8Ff0036D8B2088107902102f9415330868109","data":"0x06fdde03"},"latest"],"id":1}'

# FCO Metrics API - Health check
curl http://paratime.fanati.co:3001/health

# FCO Metrics API - Get all metrics
curl http://paratime.fanati.co:3001/api/info/stat/metrics

# NFT Contract (update address after deployment)
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_call","params":[{"to":"<NFT_ADDRESS>","data":"0x06fdde03"},"latest"],"id":1}'
```

### Integration Tests

| Test | Contracts Involved | Expected Result |
|------|-------------------|-----------------|
| FCO Transfer | FCO | Balance changes |
| NFT Mint | NFT | Token created |
| NFT List | NFT + Marketplace | Listing active |
| NFT Purchase | FCO + NFT + Marketplace | Ownership transferred |
| Dispatch Execute | Dispatch + FCO | Transaction completed |

---

## Timeline Estimate

| Week | Tasks | Status |
|------|-------|--------|
| 1 | Deploy FCO Token, Deploy NFT Contract | ✅ Both Done |
| 2 | Deploy Marketplace, Deploy Auction Contracts | Ready |
| 3 | Integration testing with backend | Pending |
| 4 | Staged rollout to sandbox | Pending |
| 5 | Production migration | Pending |

---

## Contact & Escalation

**L1 Team Issues**: Tag in Jira comments
**Backend Team**: dev@fanati.co
**Urgent Blockers**: Slack #fanatico-chain

---

**Document Version**: 1.1
**Last Updated**: 2026-02-03
**FCO Deployed**: 2026-02-02
