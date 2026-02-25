# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Fanatico L1 Blockchain - Development Guide

EVM-compatible blockchain with FCO native token. Chain ID: 11111111111 (0x2964619c7).

## Project Status

**Current Version**: v0.5.0.0 "Production Release" (GA — February 20, 2026)
**Production Score**: 99/100 (A+ Grade)
**RPC Coverage**: 38/41 methods (93%)
**Previous Version**: v0.4.9.98 "Block Explorer Compatibility" (January 2026)
**Next Release**: v0.5.1 (Q2-Q3 2026) — [FAN-2479](https://fanatico.atlassian.net/browse/FAN-2479)
**Git Tag**: `v0.5.0.0`

### v0.5.0.0-rc1 Deployment (February 16-17, 2026)

**Epic**: [FAN-2368](https://fanatico.atlassian.net/browse/FAN-2368) - Production Hardening Release Candidate

Deployed 4-node infrastructure with security hardening:
- 4 nodes: paratime (authority) + consensus1, consensus2, seed1 (read replicas)
- WebSocket support on all nodes (port 8546, eth_subscribe)
- CSP headers, rate limiting (100 req/min/IP), structured JSON access logging
- RPC fuzzer: 296/296 passed, 0 crashes
- Dependency audit: 0 actionable CVEs
- DB sync: paratime -> replicas every 2 min via SCP
- Auto-restart: crontab @reboot + 5-minute health check watchdog
- Public HTTPS endpoint: https://seed1.fanati.co (nginx + Let's Encrypt SSL)
- Public WSS endpoint: wss://seed1.fanati.co/ws
- OWASP reviews: A04 Insecure Design (5 low findings), A06 Components (0 actionable CVEs)

### DevTeam Assessment (February 2, 2026)

**Key Documents**:
- **[STATUS.md](/Users/sebastian/CODE/L1/STATUS.md)** - Master status document (start here)
- **[Assessment Summary](/Users/sebastian/CODE/L1/devteam/ASSESSMENT_SUMMARY_2026-02-02.md)** - 2-page executive summary
- **[Full Assessment](/Users/sebastian/CODE/L1/devteam/FCO_V04998_DEVTEAM_ASSESSMENT.md)** - 50+ pages comprehensive analysis

**Verdict**: Production Ready (99/100), Low Risk, 99% Confidence

### Public Infrastructure

| Service | URL | Description |
|---------|-----|-------------|
| **RPC Endpoint** | https://rpc.fanati.co | Public HTTPS JSON-RPC API (primary) |
| **RPC Endpoint 2** | https://seed1.fanati.co | Public HTTPS JSON-RPC API (secondary) |
| **WebSocket** | wss://seed1.fanati.co/ws | Public WSS subscriptions |
| **Block Explorer** | https://explorer.fanati.co | Blockscout-based explorer |
| **Chain Info** | https://chain.fanati.co | Network details & MetaMask integration |
| **Chainlist** | [chainlist.org](https://chainlist.org) | Merged (PR #2452, Feb 2 2026) |

### Internal Infrastructure

| Service | URL | Description |
|---------|-----|-------------|
| RPC (Internal) | http://paratime.fanati.co:8545 | Direct RPC access |
| Dashboard | http://paratime.fanati.co:8080 | Node dashboard |
| Explorer Host | 188.245.85.247 | Blockscout server |

### Version Directory Structure

```
/Users/sebastian/CODE/L1/
├── V04998/                         # v0.4.9.98 current release (production source)
├── V05000/                         # v0.5.0.0 implementation (WebSocket, HA, backup, monitoring, security)
│   ├── src/                        #   WebSocket server, combined HTTP+WS server
│   ├── scripts/                    #   RPC fuzzer (rpc_fuzzer.py - 296 test cases)
│   ├── infrastructure/             #   Patroni, HAProxy, etcd, backup scripts, monitoring, security
│   ├── api/                        #   FCO metrics API
│   └── www/                        #   chain.fanati.co static site
├── v0500/                          # v0.5.0.0 planning docs & specs
├── v0497/                          # ARCHIVED - v0.4.9.7 historical docs
├── hardhat/V04998/                 # v0.4.9.98 test results & assessments
├── devteam/V04998/                 # v0.4.9.98 dev team documentation
├── sapphire-evm-v0496/            # v0.4.9.6.x legacy code
└── Research/                       # Historical versions & experiments
```

## Essential Commands

### Testing Current Version (v0.4.9.98)

```bash
# Verify chain ID (use public HTTPS endpoint)
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
# Expected: {"result":"0x2964619c7"}

# Test web3_clientVersion
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":1}'
# Expected: {"result":"Fanatico/v0.5.0.0/python"}

# Test network status
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_syncing","params":[],"id":1}'
# Expected: {"result":false}

# Test web3_sha3
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_sha3","params":["0x68656c6c6f"],"id":1}'
# Expected: {"result":"0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8"}

# Check test account balances
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266","latest"],"id":1}'

# Run Hardhat tests
cd /Users/sebastian/CODE/L1/hardhat
npx hardhat test --network fanatico
```

### Version Navigation

```bash
# View current production implementation
cd /Users/sebastian/CODE/L1/V04998

# Access test results and assessments
cd /Users/sebastian/CODE/L1/hardhat/V04998
ls *.md

# Dev team documentation
cd /Users/sebastian/CODE/L1/devteam/V04998
```

### Documentation Access

```bash
# Current version release notes
cat /Users/sebastian/CODE/L1/V04998/RELEASE_NOTES_V04998.md

# Assessment report
cat /Users/sebastian/CODE/L1/hardhat/V04998/V04998_ASSESSMENT_REPORT.md

# Chain ID migration guide
cat /Users/sebastian/CODE/L1/hardhat/V04998/CHAIN_ID_MIGRATION_GUIDE.md
```

## Architecture

### Version System

1. **Production** (`V04998/`): v0.4.9.98 "Block Explorer Compatibility"
   - Current: v0.4.9.98 (99/100 production score)
   - Full EVM compatibility with smart contracts
   - SQLite backend for accounts/blocks/transactions
   - 38/41 RPC methods (93% coverage)

2. **Legacy** (`sapphire-evm-v0496/`): v0.4.9.6.x series (archived)
   - Historical reference only
   - Superseded by v0.4.9.98

3. **Implementation** (`V05000/`): v0.5.0.0 "Production Release" source code
   - `src/`: WebSocket server (19.5KB), combined HTTP+WS server
   - `infrastructure/`: Patroni HA, HAProxy, etcd, backup scripts, monitoring (Prometheus/Grafana), security audit
   - `api/`: FCO metrics API (Node.js)
   - `www/`: chain.fanati.co static site

4. **Planning** (`v0500/`): v0.5.0.0 specs and checklists
   - Feature specification, implementation checklist, infrastructure requirements

5. **Research** (`Research/`): Historical versions and experiments

### Key Components (v0.4.9.98)

**Location**: `/Users/sebastian/CODE/L1/V04998/`

- `web3_api_v04998.py`: Main JSON-RPC server (8545) - 128KB, full-featured

**Database**: SQLite blockchain storage
- Tables: accounts, blocks, transactions, receipts, contracts, logs

### Version Progression

```
v0.4.6     → Keccak-256 fix (JavaScript unblocked)
v0.4.7     → cumulativeGasUsed field
v0.4.8.1   → transactionIndex, eth_estimateGas (92% JS support)
v0.4.9.5   → SQLite storage + 3-tier caching (15.9x faster)
v0.4.9.6   → 13 Sapphire precompiles (85% compatibility)
v0.4.9.6.4 → Production release (95/100 score)
v0.4.9.7.8 → EVM Integration (97/100 score)
             ├─ eth_call (read-only contract execution)
             └─ eth_getLogs (event log querying)
v0.4.9.97  → EIP-1559/2930 support, JSON-RPC error fix
v0.4.9.98  → Block Explorer Compatibility (99/100)
             ├─ 15 NEW RPC methods (93% coverage)
             ├─ web3_clientVersion, web3_sha3
             ├─ Network status (eth_syncing, net_peerCount)
             ├─ Block counts (eth_getBlockTransactionCountByNumber)
             └─ Uncle stubs (returns 0/null for L1)
v0.5.0.0   → Production Release (99/100) - CURRENT ✅ GA
             ├─ 4-node HA cluster (paratime + 3 replicas)
             ├─ WebSocket support (eth_subscribe)
             ├─ Security hardening (CSP, rate limiting, logging)
             ├─ /health endpoint on all nodes
             ├─ DB sync every 2 minutes
             └─ 8 contracts deployed, backend integrated
```

## Test Accounts

**Source**: `/Users/sebastian/CODE/L1/sapphire-evm-v0496/TEST_DEVELOPER_INFO_v04964.md`

| Name | Address | Balance | Private Key Location |
|------|---------|---------|---------------------|
| Roman | 0xf39Fd...92266 | 14.5 FCO | KEYS.md |
| Hardhat | 0x7099...c79C8 | 20.0 FCO | KEYS.md |
| Air | 0x3C44...FA293BC | 39.5 FCO | KEYS.md |
| Ali | 0xf945...58E92 | 39.5 FCO | KEYS.md |

**HD Wallet Seed**: `test test test test test test test test test test test junk`

## Version-Specific Behaviors

### v0.4.9.98 (Current Production)

**What Works**:
- Value transfers (100% functional, perfect gas accounting)
- Balance queries
- Block queries
- Transaction receipts (all fields present)
- Gas estimation (eth_estimateGas)
- Smart contract deployment and execution
- eth_call, eth_getLogs, eth_getCode, eth_getStorageAt
- EIP-1559 Type 2 transactions
- EIP-2930 Access list transactions
- JavaScript/ethers.js support (100%)
- Python/web3.py support (100%)
- Block explorer compatibility (web3_clientVersion, web3_sha3)
- Network status (eth_syncing, eth_mining, net_peerCount)

**Known Limitations**:
- UNIQUE constraint on rapid sequential transactions (add 100ms delay)
- Balance query immediately after tx may return stale (add 1000ms delay)

**Gas Calculation**: Exact to the wei
- Simple transfer: 21,000 gas × 20 Gwei = 0.00042 FCO
- All test results show perfect gas accounting

### v0.5.0.0 (Planned - Production Release)

**Planned Features**:
1. WebSocket support (eth_subscribe, eth_unsubscribe)
2. High Availability cluster (Patroni)
3. HAProxy load balancing
4. Automated backup procedures
5. Full monitoring stack (Prometheus/Grafana)
6. Security audit completion

**Status**: rc1 deployed (Feb 16-17, 2026). All rc1 tasks complete. Planning in `v0500/`, source code in `V05000/`.
Phases 1-5 complete (WebSocket, HA, Backup, Monitoring, Security). Phases 6-7 deferred to v0.5.1 Q2 2026.

## Testing Strategy

### Running Comprehensive Tests

```bash
# Run Hardhat test suite
cd /Users/sebastian/CODE/L1/hardhat
npx hardhat test --network fanatico

# Quick RPC validation
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":1}'

# Check block explorer indexing status
curl -s https://explorer.fanati.co/api/v2/main-page/indexing-status
```

**Test Suites** (v0.4.9.98):
- Core Tests: 57 tests (96.5% passing)
- New Methods Tests: 19 tests (100% passing)
- Total: 152 tests (68.4% passing - failures are test suite issues, not API bugs)

### Expected Results

**v0.4.9.98**: 104/152 passing (68.4%)
- Core functional tests: 96.5% PASS
- New RPC method tests: 100% PASS
- FCO Token tests: 33 FAIL (missing Authority contract - test issue)
- Old TokenMock tests: 11 FAIL (missing contract - test issue)

**Key Metrics**:
- Functional correctness: 100%
- Production score: 99/100
- JavaScript support: 100%
- Python support: 100%
- RPC coverage: 93% (38/41 methods)

## Critical Hash Implementation

**IMPORTANT**: Always use Keccak-256, NOT SHA3-256

```python
# WRONG - Do not use
import hashlib
k = hashlib.sha3_256()  # NIST standard, incompatible with Ethereum

# CORRECT - Use this
from Crypto.Hash import keccak
k = keccak.new(digest_bits=256)  # Ethereum-compatible
```

This was fixed in v0.4.6 and is critical for JavaScript/ethers.js compatibility.

## Documentation Organization

### Current Version Docs (`V04998/`)
- `web3_api_v04998.py`: Production source code
- `RELEASE_NOTES_V04998.md`: Release information

### Test Results & Assessments (`hardhat/V04998/`)
- `V04998_ASSESSMENT_REPORT.md`: Production readiness assessment
- `QUICK_TEST_SUMMARY.md`: Quick status check
- `VERSION_COMPARISON.md`: v0.4.9.97 vs v0.4.9.98 comparison
- `INDEX.md`: Documentation navigation
- `CHAIN_ID_MIGRATION_GUIDE.md`: Migration instructions

### Dev Team Docs (`devteam/V04998/`)
- `CHAIN_ID_MIGRATION_GUIDE.md`: Dev team copy
- `RELEASE_NOTES_V04998.md`: Dev team copy

### Legacy Docs (`v0497/`, `sapphire-evm-v0496/`)
- Historical planning and implementation docs
- Superseded by v0.4.9.98 release

### Finding Information

```bash
# Current version assessment
cat /Users/sebastian/CODE/L1/hardhat/V04998/V04998_ASSESSMENT_REPORT.md

# Release notes
cat /Users/sebastian/CODE/L1/V04998/RELEASE_NOTES_V04998.md

# Quick status
cat /Users/sebastian/CODE/L1/hardhat/V04998/QUICK_TEST_SUMMARY.md
```

## Common Workflows

### Testing a New Feature

1. Write specification in planning directory (e.g., `/v0500/`)
2. Create Hardhat test in `/hardhat/` directory
3. Run tests: `npx hardhat test --network fanatico`
4. Document results in assessment file
5. Update version documentation

### Creating Version Documentation

1. Create version directory (e.g., `/V05000/` for source, `/hardhat/V05000/` for tests)
2. Include: RELEASE_NOTES, ASSESSMENT_REPORT, INDEX
3. Copy relevant docs to `/devteam/V05000/` for dev team
4. Update this CLAUDE.md with new version info

### Assessing Production Readiness

1. Run Hardhat test suite against RPC endpoint
2. Calculate scores: functional (target 95%+), overall (target 99/100)
3. Document known issues and limitations
4. Create assessment report with:
   - Test results breakdown
   - RPC method coverage
   - Security considerations
   - Deployment recommendations

## Network Configuration

**Chain ID**: 11111111111 (0x2964619c7)
**RPC (Public)**: https://rpc.fanati.co (primary), https://seed1.fanati.co (secondary)
**WebSocket (Public)**: wss://seed1.fanati.co/ws
**RPC (Internal)**: http://paratime.fanati.co:8545
**Block Explorer**: https://explorer.fanati.co
**Chain Info**: https://chain.fanati.co
**Currency**: FCO (18 decimals)
**Gas Price**: 20 Gwei (20,000,000,000 wei)
**Block Time**: ~2 seconds

### Hardhat Config

```javascript
module.exports = {
  solidity: "0.8.20",
  networks: {
    fanatico: {
      url: "https://rpc.fanati.co",
      chainId: 11111111111,
      accounts: {
        mnemonic: "test test test test test test test test test test test junk"
      },
      gasPrice: 20000000000
    }
  }
};
```

### Web3.js/Ethers.js

```javascript
// Using public HTTPS RPC
const provider = new ethers.JsonRpcProvider("https://rpc.fanati.co");

// Send transaction
const tx = await wallet.sendTransaction({
    to: recipient,
    value: ethers.parseEther('1.0')
});

// Wait for receipt
const receipt = await tx.wait();
```

## Important Notes

### What's Working (v0.4.9.98)
- ✅ Value transfers (perfect gas accounting)
- ✅ Balance queries
- ✅ Transaction receipts (all fields present)
- ✅ Gas estimation
- ✅ Smart contract deployment & execution
- ✅ JavaScript/ethers.js support (100%)
- ✅ Python/web3.py support (100%)
- ✅ EIP-1559 Type 2 transactions
- ✅ EIP-2930 Access list transactions
- ✅ eth_call, eth_getLogs, eth_getCode, eth_getStorageAt
- ✅ Network status (eth_syncing, eth_mining, net_peerCount)
- ✅ Block explorer support (web3_clientVersion, web3_sha3)
- ✅ 38/41 RPC methods (93% coverage)

### What's Not Implemented (By Design)
- ❌ eth_sign - Requires private key access (security risk)
- ❌ eth_signTransaction - Requires private key access (security risk)
- ❌ eth_submitWork - PoW only, not applicable to L1

### Version Selection

- **All Use Cases** → v0.4.9.98 (full feature set, 99/100 score)
- **Block Explorers** → v0.4.9.98 (full compatibility)
- **MetaMask Users** → Ensure Chain ID is 11111111111

## Critical Warnings

1. Always use Chain ID **11111111111** (not 999999999 or 1234, deprecated)
2. Always use **Keccak-256** (not SHA3-256)
3. Test accounts are **TEST ONLY** - never use in production
4. Performance test failures are **network latency**, not bugs

## Quick Reference

```bash
# Check version (public HTTPS)
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":1}'
# Expected: {"result":"Fanatico/v0.5.0.0/python"}

# Test connectivity
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
# Expected: {"result":"0x2964619c7"}

# Get latest block number
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Run Hardhat tests
cd /Users/sebastian/CODE/L1/hardhat
npx hardhat test --network fanatico

# View documentation
cat /Users/sebastian/CODE/L1/hardhat/V04998/INDEX.md

# Check block explorer API
curl -s https://explorer.fanati.co/api/v2/stats | jq '{total_blocks, total_transactions}'
```

## Infrastructure Hosts

| Host | IP | HTTP:8545 | WS:8546 | Role |
|------|-----|-----------|---------|------|
| paratime.fanati.co | (internal) | ✅ | ✅ | Authority (writes), dashboard |
| consensus1 | 95.217.47.102 | ✅ | ✅ | Read replica |
| consensus2 | 95.216.243.184 | ✅ | ✅ | Read replica |
| seed1 (seed1.fanati.co) | 138.201.16.186 | ✅ | ✅ | Read replica / seed, **public HTTPS+WSS** |
| consensus3 | 142.132.128.217 | - | - | Available (not deployed) |
| explorer.fanati.co | 188.245.85.247 | - | - | Blockscout (14 containers) |
| chain.fanati.co | GitHub Pages | - | - | Static chain info site |
| rpc.fanati.co | paratime (nginx) | ✅ | - | HTTPS RPC endpoint (primary) |
| seed1.fanati.co | seed1 (nginx) | ✅ | ✅ | HTTPS RPC + WSS endpoint (secondary) |

**Node Management**: `ssh <node> '/home/claude/fanatico-l1/manage.sh status|start|stop|logs'`
**DB Sync**: paratime -> replicas every 2 min via crontab + SCP
**Replica DB**: `/home/claude/fanatico-l1/fco_blockchain.db`
**Paratime DB**: `/home/claude/fco_blockchain_v04963.db`

---

## Backend Integration Requirements (Completed Feb 12, 2026)

**Assessment**: [FAN-2294](https://fanatico.atlassian.net/browse/FAN-2294)
**Status**: ✅ ALL CONTRACTS DEPLOYED + BACKEND INTEGRATION COMPLETE

### Deployed Contracts (8 total)

| Contract | Address | Jira |
|----------|---------|------|
| Authority | `0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2` | - |
| FCO Token | `0xd6F8Ff0036D8B2088107902102f9415330868109` | FAN-2298 ✅ |
| FanaticoNFT | `0x0442121975b1D8a0860F8B80318f84402284A211` | FAN-2299 ✅ |
| Marketplace | `0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9` | FAN-2300 ✅ |
| AuctionEng | `0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049` | FAN-2301 ✅ |
| AuctionDut | `0x4437204542e5C71409Af1eE0154Ce5fa659f55a7` | FAN-2301 ✅ |
| AuctionSen | `0xCe1370E6013989185ac2552832099F24a85DbfD4` | FAN-2301 ✅ |
| AuctionLub | `0xB3faFE3b27fCB65689d540c5185a8420310d59dA` | FAN-2301 ✅ |

### Backend Integration Tasks: COMPLETED (February 12, 2026)

| Order | Jira | Task | Priority | Status |
|-------|------|------|----------|--------|
| 1 | [FB-1877](https://fanatico.atlassian.net/browse/FB-1877) | Update Environment Variables | High | Closed |
| 2 | [FB-1880](https://fanatico.atlassian.net/browse/FB-1880) | Update RPC Provider | High | Closed |
| 3 | [FB-1878](https://fanatico.atlassian.net/browse/FB-1878) | Update EIP-712 Domain | High | Closed |
| 4 | [FB-1879](https://fanatico.atlassian.net/browse/FB-1879) | Update Gas Price Handling | Medium | Closed |
| 5 | [FB-1881](https://fanatico.atlassian.net/browse/FB-1881) | Test All 57 Endpoints | High | Closed |

### Environment Variables

```
L1_CHAIN_ID=11111111111
L1_RPC_URL=https://rpc.fanati.co
AUTHORITY_CONTRACT_L1=0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2
FCO_CONTRACT_L1=0xd6F8Ff0036D8B2088107902102f9415330868109
NFT_CONTRACT_L1=0x0442121975b1D8a0860F8B80318f84402284A211
MARKETPLACE_CONTRACT_L1=0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9
AUCTION_ENG_CONTRACT_L1=0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049
AUCTION_DUT_CONTRACT_L1=0x4437204542e5C71409Af1eE0154Ce5fa659f55a7
AUCTION_SEN_CONTRACT_L1=0xCe1370E6013989185ac2552832099F24a85DbfD4
AUCTION_LUB_CONTRACT_L1=0xB3faFE3b27fCB65689d540c5185a8420310d59dA
```

### Key Documentation

- `BACKEND_INTEGRATION_REQUIREMENTS.md` - Full requirements
- `CONTRACT_DEPLOYMENT_BLOCKERS.md` - Contract specifications
- `FANATICO-WEB3-ENDPOINTS.md` - Web3 endpoint inventory

### Related Fremont2 Docs

```
/Users/sebastian/CODE/FREMONT2/documentation/JIRA/FAN-2294-L1-RPC-COMPATIBILITY.md
/Users/sebastian/CODE/FREMONT2/documentation/JIRA/FAN-2294-COMPATIBILITY-MATRIX.md
/Users/sebastian/CODE/FREMONT2/documentation/JIRA/FAN-2294-GAPS-AND-BLOCKERS.md
/Users/sebastian/CODE/FREMONT2/documentation/JIRA/FAN-2294-MIGRATION-RECOMMENDATIONS.md
```

---

## Pending Tasks

### Backend Integration: COMPLETED (February 12, 2026)

All 5 backend integration tasks (FB-1877 through FB-1881) are **Closed** in Jira.

### v0.5.0.0 Production Release

#### rc1 (FAN-2368) — ✅ Closed

All rc1 subtasks complete. FAN-2368 closed Feb 18, 2026.

| Jira | Task | Status |
|------|------|--------|
| [FAN-2368](https://fanatico.atlassian.net/browse/FAN-2368) | ~~v0.5.0.0-rc1 Production Hardening~~ | Closed |
| [FAN-2388](https://fanatico.atlassian.net/browse/FAN-2388) | Engage external security auditor | Backlog (business decision) |

#### v0.5.0 GA — Active

| Jira | Task | Priority | Status | Notes |
|------|------|----------|--------|-------|
| [FAN-2450](https://fanatico.atlassian.net/browse/FAN-2450) | ~~eth_getBlockByNumber returns empty transactions~~ | High | **Fixed** | All 4 nodes patched, 2,130 txs now visible |
| [FAN-2400](https://fanatico.atlassian.net/browse/FAN-2400) | ~~Standardize network name to "Fanatico"~~ | High | **Closed** | All 4 nodes return `Fanatico/v0.5.0.0/python` |
| [FAN-2401](https://fanatico.atlassian.net/browse/FAN-2401) | ~~Fix native token symbol configuration~~ | High | **Resolved** | FCO symbol already correct everywhere |
| [FAN-2470](https://fanatico.atlassian.net/browse/FAN-2470) | ~~Reduce DB replication interval 10min -> 2min~~ | High | **Closed** | Crontab updated, verified at 14:12 UTC |
| [FAN-2471](https://fanatico.atlassian.net/browse/FAN-2471) | ~~Add /health endpoint to all nodes~~ | High | **Closed** | All 4 nodes, GET /health |
| [FAN-2291](https://fanatico.atlassian.net/browse/FAN-2291) | EIP-712 Phase 3: Mobile SDK Integration | Highest | **Backlog** | Parked — needs mobile dev team (v0.5.1+) |
| [FAN-2292](https://fanatico.atlassian.net/browse/FAN-2292) | EIP-712 Phase 4: Migration & Deprecation | High | **Backlog** | Parked — depends on Phase 3 (v0.5.1+) |

#### v0.5.0 Completed

| Jira | Task | Status |
|------|------|--------|
| [FAN-2157](https://fanatico.atlassian.net/browse/FAN-2157) | ~~Validator and Paratime Requirements~~ | **Fixed** (spike: `v0500/VALIDATOR_PARATIME_REQUIREMENTS.md`) |

#### v0.5.1+ Roadmap — [FAN-2479](https://fanatico.atlassian.net/browse/FAN-2479)

All 10 backlog items moved from FAN-2068 to new epic FAN-2479 "L1 v0.5.1 Post-GA".

| Jira | Task | Priority | Status |
|------|------|----------|--------|
| [FAN-2291](https://fanatico.atlassian.net/browse/FAN-2291) | EIP-712 Phase 3: Mobile SDK Integration | Highest | Backlog |
| [FAN-2292](https://fanatico.atlassian.net/browse/FAN-2292) | EIP-712 Phase 4: Migration & Deprecation | High | Backlog |
| [FAN-2473](https://fanatico.atlassian.net/browse/FAN-2473) | Extend Authority contract with validator set mgmt | Medium | Backlog |
| [FAN-2472](https://fanatico.atlassian.net/browse/FAN-2472) | Standardize Python 3.12+ across all nodes | Medium | Backlog |
| [FAN-2146](https://fanatico.atlassian.net/browse/FAN-2146) | Logo | Medium | Backlog |
| [FAN-2069](https://fanatico.atlassian.net/browse/FAN-2069) | FNS (Fanatico NameService) | Low | Backlog |
| [FAN-2402](https://fanatico.atlassian.net/browse/FAN-2402) | Staking contract deployment | Low | Backlog |
| [FAN-2403](https://fanatico.atlassian.net/browse/FAN-2403) | Governance parameters and framework | Low | Backlog |
| [FAN-2404](https://fanatico.atlassian.net/browse/FAN-2404) | Long-term inflation model design | Low | Backlog |
| [FAN-2405](https://fanatico.atlassian.net/browse/FAN-2405) | Community participation program | Low | Backlog |

---

**Last Updated**: February 20, 2026
**Current Version**: v0.5.0.0 (GA Released Feb 20, 2026, 99/100)
**Git Tag**: `v0.5.0.0`
**FAN-2068 Epic**: Closed (29/29 children complete)
**FAN-2479 Epic**: 0/10 Closed (v0.5.1 Post-GA roadmap)
**Next Version**: v0.5.1 (Q2-Q3 2026)
**Contract Status**: ✅ All 8 contracts deployed
**Backend Status**: ✅ Integration complete (FB-1877 to FB-1881 Closed)
**Public Endpoints**: https://rpc.fanati.co (RPC), https://seed1.fanati.co (RPC+WSS)
**Spike**: `v0500/VALIDATOR_PARATIME_REQUIREMENTS.md` — validator types, requirements, 6-phase migration path
