# Fanatico L1 Backend Migration - Documentation Index

**Date**: 2026-02-05
**Status**: ✅ ALL CONTRACTS DEPLOYED - Ready for Backend Integration

---

## Quick Summary

| Metric | Value |
|--------|-------|
| Web3 Endpoints | 57 total |
| Fully Compatible | 38 (67%) |
| Need Changes | 12 (21%) |
| Partial | 5 (9%) |
| Not Compatible | 2 (3%) |
| P0 Blockers | 0 contracts - ALL DEPLOYED ✅ |

---

## Documentation Map

### In This Directory (`/Users/sebastian/CODE/L1/`)

| Document | Purpose |
|----------|---------|
| `CLAUDE.md` | AI assistant reference guide (updated) |
| `BACKEND_INTEGRATION_REQUIREMENTS.md` | **Full backend integration requirements** |
| `CONTRACT_DEPLOYMENT_BLOCKERS.md` | **Contract deployment specifications** |
| `DISPATCH_L1_CONFIG.md` | **Dispatch service configuration for L1** |
| `BACKEND_MIGRATION_INDEX.md` | This index file |
| `FANATICO-WEB3-ENDPOINTS.md` | Web3 endpoint inventory |
| `README.md` | Main L1 documentation |

### Assessment Reports (`/Users/sebastian/CODE/FREMONT2/documentation/JIRA/`)

| Document | Purpose |
|----------|---------|
| `FAN-2294-L1-RPC-COMPATIBILITY.md` | RPC method compatibility (18/22) |
| `FAN-2294-COMPATIBILITY-MATRIX.md` | Endpoint vs L1 mapping (57 endpoints) |
| `FAN-2294-GAPS-AND-BLOCKERS.md` | P0/P1/P2 issues analysis |
| `FAN-2294-MIGRATION-RECOMMENDATIONS.md` | Migration plan and risk assessment |

---

## Jira Issues

### Epic
- **[FAN-2068](https://fanatico.atlassian.net/browse/FAN-2068)** - FANATICO CHAIN

### Assessment
- **[FAN-2294](https://fanatico.atlassian.net/browse/FAN-2294)** - L1 Compatibility Assessment

### P0 Contract Deployments

| Jira | Contract | Status | Blocks |
|------|----------|--------|--------|
| **[FAN-2298](https://fanatico.atlassian.net/browse/FAN-2298)** | FCO Token (ERC-20) | ✅ Deployed | 0 (unblocked) |
| **[FAN-2299](https://fanatico.atlassian.net/browse/FAN-2299)** | NFT (ERC-721) | ✅ Deployed | 0 (unblocked) |
| **[FAN-2300](https://fanatico.atlassian.net/browse/FAN-2300)** | Marketplace | ✅ Deployed | 0 (unblocked) |
| **[FAN-2301](https://fanatico.atlassian.net/browse/FAN-2301)** | Auctions | ✅ Deployed | 0 (unblocked) |

### Backend Configuration (No Contract Needed)

| Jira | Task | Status |
|------|------|--------|
| **[FAN-2302](https://fanatico.atlassian.net/browse/FAN-2302)** | Dispatch config + EIP-712 domain | ✅ Config Ready |

**Configuration Guide**: `DISPATCH_L1_CONFIG.md`

### Deployed Contracts

| Contract | Address |
|----------|---------|
| Authority | `0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2` |
| FCO Token | `0xd6F8Ff0036D8B2088107902102f9415330868109` |
| FanaticoNFT | `0x0442121975b1D8a0860F8B80318f84402284A211` |
| Marketplace | `0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9` |
| AuctionEng | `0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049` |
| AuctionDut | `0x4437204542e5C71409Af1eE0154Ce5fa659f55a7` |
| AuctionSen | `0xCe1370E6013989185ac2552832099F24a85DbfD4` |
| AuctionLub | `0xB3faFE3b27fCB65689d540c5185a8420310d59dA` |

### FCO Metrics API

- **Health**: http://paratime.fanati.co:3001/health
- **Metrics**: http://paratime.fanati.co:3001/api/info/stat/metrics

---

## Network Configuration

| Parameter | Value |
|-----------|-------|
| Chain ID | 11111111111 |
| RPC (Public) | https://rpc.fanati.co |
| RPC (Internal) | http://paratime.fanati.co:8545 |
| Gas Price | Fixed 20 Gwei |
| Currency | FCO |

---

## Action Items

### For L1 Team (Contract Development) ✅ COMPLETE

1. ~~**Deploy FCO Token** (FAN-2298)~~ - ✅ Deployed
2. ~~**Deploy NFT Contract** (FAN-2299)~~ - ✅ Deployed
3. ~~**Deploy Marketplace** (FAN-2300)~~ - ✅ Deployed
4. ~~**Deploy Auctions** (FAN-2301)~~ - ✅ Deployed (4 contracts)

### For Backend Team (Jira Tasks Created)

| Order | Jira | Task | Priority |
|-------|------|------|----------|
| 1 | [FB-1877](https://fanatico.atlassian.net/browse/FB-1877) | Update Backend Environment Variables | High |
| 2 | [FB-1880](https://fanatico.atlassian.net/browse/FB-1880) | Update RPC Provider Configuration | High |
| 3 | [FB-1878](https://fanatico.atlassian.net/browse/FB-1878) | Update EIP-712 Domain Configuration | High |
| 4 | [FB-1879](https://fanatico.atlassian.net/browse/FB-1879) | Update Gas Price Handling | Medium |
| 5 | [FB-1881](https://fanatico.atlassian.net/browse/FB-1881) | Test All 57 Web3 Endpoints | High |

---

## Reading Order

1. **Start here**: `BACKEND_MIGRATION_INDEX.md` (this file)
2. **Overview**: `BACKEND_INTEGRATION_REQUIREMENTS.md`
3. **Contract specs**: `CONTRACT_DEPLOYMENT_BLOCKERS.md`
4. **Endpoint list**: `FANATICO-WEB3-ENDPOINTS.md`
5. **Detailed analysis**: FREMONT2 JIRA documents

---

## Contact

- **L1 Team**: Roman (roman@fanati.co)
- **Backend Team**: dev@fanati.co
- **Jira**: https://fanatico.atlassian.net/browse/FAN

---

**Document Version**: 2.0
**Last Updated**: 2026-02-05
**All Contracts Deployed**: 2026-02-03
**Backend Tasks Created**: FB-1877 through FB-1881
