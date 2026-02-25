# Fanatico L1 v0.5.0.0 Release Notes

**Version**: 0.5.0.0
**Codename**: Production Release
**Release Date**: February 20, 2026
**Status**: GA DEPLOYED
**Production Score**: 99/100 (A+ Grade)
**RPC Coverage**: 38/41 methods (93%)

| Parameter | Value |
|-----------|-------|
| Chain ID | 11111111111 (`0x2964619c7`) |
| RPC Endpoint (Primary) | https://rpc.fanati.co |
| RPC Endpoint (Secondary) | https://seed1.fanati.co |
| WebSocket | wss://seed1.fanati.co/ws |
| Block Explorer | https://explorer.fanati.co |
| Chain Info | https://chain.fanati.co |
| Gas Price | 20 Gwei |
| Currency | FCO (18 decimals) |
| Client Version | `Fanatico/v0.5.0.0/python` |

---

## Executive Summary

v0.5.0.0 is the **first production-grade release** of the Fanatico L1 blockchain. Building on the v0.4.9.98 codebase (99/100 score), this release adds production infrastructure: 4-node high availability, WebSocket subscriptions, security hardening, automated monitoring, and operational tooling.

**Key Achievements**:
- 4-node HA cluster: 1 authority + 3 read replicas
- WebSocket support (eth_subscribe) on all nodes
- Security hardening: CSP headers, rate limiting, structured logging
- RPC fuzzer: 296/296 test cases passed, 0 crashes
- Dependency audit: 0 actionable CVEs
- 2-minute DB replication across all replicas
- /health endpoint on all nodes for monitoring
- 8 smart contracts deployed
- Backend integration complete (57 web3 endpoints)
- Public HTTPS + WSS endpoints with Let's Encrypt SSL

---

## What's New in v0.5.0.0

### Infrastructure (rc1 — February 16-17, 2026)

| Feature | Details |
|---------|---------|
| **4-Node Cluster** | paratime (authority/writer), consensus1, consensus2, seed1 (read replicas) |
| **WebSocket Support** | Port 8546 on all nodes. eth_subscribe: newHeads, logs, newPendingTransactions, syncing |
| **Public HTTPS** | rpc.fanati.co (primary), seed1.fanati.co (secondary) via nginx + Let's Encrypt |
| **Public WSS** | wss://seed1.fanati.co/ws |
| **Auto-Restart** | crontab @reboot + 5-minute health check watchdog on all nodes |
| **DB Replication** | SCP-based, every 2 minutes from paratime to all replicas |

### Security Hardening (rc1)

| Feature | Details |
|---------|---------|
| **CSP Headers** | `default-src 'none'; frame-ancestors 'none'` on all nodes |
| **Rate Limiting** | 100 requests/minute per IP with JSON-RPC error responses |
| **Structured Logging** | JSON access logs (OWASP A09) on all replicas |
| **RPC Fuzzing** | 296 test cases across 39 methods, 0 crashes, 0 hangs |
| **Dependency Audit** | 10 CVEs found, 0 actionable (Windows-only or unused packages) |
| **OWASP Reviews** | A04 Insecure Design (5 low findings), A05 Security Misconfiguration (clear), A06 Components (0 actionable) |

### Bug Fixes (GA — February 20, 2026)

| Issue | Fix |
|-------|-----|
| **FAN-2450** | `eth_getBlockByNumber`/`eth_getBlockByHash` now return transaction data instead of empty arrays. Supports both full transaction objects and hash-only mode. |
| **FAN-2400** | Network name standardized to "Fanatico" across all 4 nodes (was "FanaticoL1") |
| **FAN-2401** | Native token symbol confirmed as FCO everywhere (no change needed) |

### Operational Improvements (GA — February 20, 2026)

| Feature | Details |
|---------|---------|
| **Health Endpoint** | `GET /health` on all nodes — returns status, version, blockNumber, blockAge, totalBlocks, totalTransactions |
| **DB Sync Interval** | Reduced from 10 minutes to 2 minutes (FAN-2470) |
| **Node Management** | `manage.sh` script on all nodes: start, stop, status, logs |

---

## Deployed Contracts (8 total)

| Contract | Address | Purpose |
|----------|---------|---------|
| Authority | `0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2` | Network authority |
| FCO Token | `0xd6F8Ff0036D8B2088107902102f9415330868109` | ERC-20 native token |
| FanaticoNFT | `0x0442121975b1D8a0860F8B80318f84402284A211` | ERC-721 NFT |
| Marketplace | `0xb5d4D4a87Cb07f33b5FAd6736D8F1EE7D255d9E9` | NFT marketplace |
| AuctionEng | `0x83EbbF9Ea0515629bcAcD135f2c7eD65c7dB3049` | English auction |
| AuctionDut | `0x4437204542e5C71409Af1eE0154Ce5fa659f55a7` | Dutch auction |
| AuctionSen | `0xCe1370E6013989185ac2552832099F24a85DbfD4` | Sealed-bid auction |
| AuctionLub | `0xB3faFE3b27fCB65689d540c5185a8420310d59dA` | Lubinski auction |

---

## Node Infrastructure

| Node | IP | Role | HTTP | WS | Public |
|------|-----|------|------|----|--------|
| paratime | paratime.fanati.co | Authority (writes) | :8545 | :8546 | https://rpc.fanati.co |
| consensus1 | 95.217.47.102 | Read replica | :8545 | :8546 | Internal |
| consensus2 | 95.216.243.184 | Read replica | :8545 | :8546 | Internal |
| seed1 | 138.201.16.186 | Read replica / seed | :8545 | :8546 | https://seed1.fanati.co |

**Management**: `ssh <node> '/home/claude/fanatico-l1/manage.sh status'`

---

## Chain Statistics (at release)

| Metric | Value |
|--------|-------|
| Total Blocks | 2,308 |
| Total Transactions | 2,130 |
| Block Height | 2,307 |
| Block Time | ~2 seconds (on demand) |
| Gas Price | 20 Gwei (fixed) |

---

## RPC Method Coverage: 38/41 (93%)

### Implemented Methods

**Core (15/15 — 100%)**:
eth_chainId, eth_blockNumber, eth_getBalance, eth_getTransactionCount,
eth_sendRawTransaction, eth_getTransactionByHash, eth_getTransactionReceipt,
eth_getBlockByNumber, eth_getBlockByHash, eth_gasPrice, eth_estimateGas,
eth_call, eth_getCode, eth_getStorageAt, eth_accounts

**Extended (23/26 — 88%)**:
eth_getLogs, eth_newFilter, eth_newBlockFilter, eth_newPendingTransactionFilter,
eth_getFilterChanges, eth_getFilterLogs, eth_uninstallFilter,
eth_getBlockTransactionCountByNumber, eth_getBlockTransactionCountByHash,
web3_clientVersion, web3_sha3, net_version, net_listening, net_peerCount,
eth_syncing, eth_mining, eth_hashrate, eth_protocolVersion, eth_coinbase,
eth_getUncleCountByBlockNumber, eth_getUncleCountByBlockHash,
eth_getUncleByBlockNumberAndIndex, eth_getUncleByBlockHashAndIndex

### Not Implemented (by design)
- eth_sign — Requires private key access (security risk)
- eth_signTransaction — Requires private key access (security risk)
- eth_submitWork — PoW only, not applicable

---

## Upgrade Path

### From v0.4.9.98
- No breaking changes
- Version string updated automatically
- All existing transactions, blocks, and contracts preserved

### Known Limitations
- UNIQUE constraint on rapid sequential transactions (add 100ms delay)
- Balance query immediately after tx may return stale (add 1000ms delay)
- Single-authority consensus (paratime produces all blocks)

---

## Verification

```bash
# Check version
curl -s -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":1}'
# Expected: {"result":"Fanatico/v0.5.0.0/python"}

# Health check
curl -s https://rpc.fanati.co/health | python3 -m json.tool

# Chain ID
curl -s -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
# Expected: {"result":"0x2964619c7"}
```

---

## Jira References

| Epic | Description | Status |
|------|-------------|--------|
| [FAN-2068](https://fanatico.atlassian.net/browse/FAN-2068) | FANATICO CHAIN | Closed (29/29 children) |
| [FAN-2368](https://fanatico.atlassian.net/browse/FAN-2368) | v0.5.0.0-rc1 Production Hardening | Closed |
| [FAN-2480](https://fanatico.atlassian.net/browse/FAN-2480) | v0.5.0.0 GA Release | Closed |

## Next Release

**v0.5.1** — [FAN-2479](https://fanatico.atlassian.net/browse/FAN-2479) "Post-GA Roadmap"
- EIP-712 Mobile SDK (Phases 3-4)
- Validator set management
- Python 3.12+ standardization
- Governance framework
- Staking contracts
- FNS (Fanatico NameService)

---

**Released**: February 20, 2026
**Tag**: `v0.5.0.0`
**Git**: https://github.com/FanaticoInc/CODE
