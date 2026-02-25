# Oasis Sapphire Testnet Node Requirements

## Target: seed2.fanati.co (188.245.85.247)

**Network:** Oasis Sapphire Testnet
**Chain ID:** 23295 (0x5aff)
**Currency:** TEST

---

## Hardware Requirements

### For Sapphire ParaTime Node (Testnet)

| Resource | Minimum | Recommended | seed2.fanati.co |
|----------|---------|-------------|-----------------|
| CPU | 2.0 GHz x86-64 with AES + SGX | 2.0 GHz x86-64, 2+ cores, AES, SGX, AVX2 | 8 vCPUs ✅ |
| RAM | 12 GB ECC | 20 GB ECC | 15 GB ⚠️ |
| Storage | 200 GB SSD/NVMe | 300 GB SSD/NVMe | 143 GB ❌ |
| Network | 200 Mbps low latency | 1 Gbps low latency | TBD |

### Critical Hardware Note
**Intel SGX Required:** Sapphire ParaTime requires Intel SGX support for compute nodes. Need to verify if seed2.fanati.co has SGX-capable CPU.

---

## Software Requirements

### Operating System
- x86_64 Linux (Ubuntu recommended)
- UEFI boot mode required for SGX provisioning

### Required Packages
- `bubblewrap` >= 0.3.3 (sandboxing)
- `oasis-node` binary (v25.9 for Testnet)
- `oasis-core-runtime-loader` (for SGX ParaTimes)

### Oasis Testnet Versions
- Oasis Core: 25.9
- Web3 Gateway: 5.3.4
- Sapphire Runtime: 1.2.0-testnet
- Runtime ID: `000000000000000000000000000000000000000000000000a6d1e3ebf60dff6c`

---

## Network Configuration

### Required Ports (TCP + UDP)
| Port | Purpose |
|------|---------|
| 26656 | Consensus P2P |
| 9200 | ParaTime P2P |
| 8545 | Web3 RPC (optional, for JSON-RPC access) |
| 8546 | Web3 WebSocket (optional) |

### Testnet Seed Nodes
```
HcDFrTp/MqRHtju5bCx6TIhIMd6X/0ZQ3lUG73q5898=@35.247.24.212:26656
kqsc8ETIgG9LCmW5HhSEUW80WIpwKhS7hRQd8FrnkJ0=@34.140.116.202:26656
```

---

## System Configuration

### 1. Create Dedicated User
```bash
adduser --system oasis --shell /usr/sbin/nologin
```

### 2. File Descriptor Limits
Minimum: 102,400

```bash
# /etc/security/limits.d/99-oasis-node.conf
*  soft  nofile  102400
*  hard  nofile  1048576
```

Or via systemd:
```ini
[Service]
LimitNOFILE=102400
```

### 3. Directory Structure
```
/node/
├── bin/
│   ├── oasis-node
│   └── oasis-core-runtime-loader
├── etc/
│   ├── config.yml
│   └── genesis.json
├── data/
└── runtimes/
    └── sapphire-paratime.orc
```

### 4. SGX Configuration (if available)
- Enable SGX in BIOS
- Set "SGX Auto MP Registration" to enabled
- Configure quote provider for attestation

---

## Testnet Genesis

**Genesis File SHA256:** `02ce385c050b2a5c7cf0e5e34f5e4930f7804bb21efba2d1d3aa8215123aab68`

Download from: https://github.com/oasisprotocol/testnet-artifacts

---

## Installation Steps

1. **Verify Hardware**
   - Check SGX support: `cpuid | grep -i sgx`
   - Verify CPU features: `lscpu | grep -E 'aes|avx2'`

2. **Install Dependencies**
   ```bash
   apt update && apt install -y bubblewrap
   ```

3. **Download Oasis Node**
   ```bash
   wget https://github.com/oasisprotocol/oasis-core/releases/download/v25.9/oasis_core_25.9_linux_amd64.tar.gz
   tar xvf oasis_core_25.9_linux_amd64.tar.gz
   cp oasis-core-25.9/oasis-node /node/bin/
   cp oasis-core-25.9/oasis-core-runtime-loader /node/bin/
   ```

4. **Download Genesis**
   ```bash
   wget -O /node/etc/genesis.json https://github.com/oasisprotocol/testnet-artifacts/releases/download/2023-10-12/genesis.json
   sha256sum /node/etc/genesis.json
   # Should match: 02ce385c050b2a5c7cf0e5e34f5e4930f7804bb21efba2d1d3aa8215123aab68
   ```

5. **Configure Node**
   Create `/node/etc/config.yml` (see Configuration section below)

6. **Start Node**
   ```bash
   oasis-node --config /node/etc/config.yml
   ```

---

## Configuration Template

```yaml
# /node/etc/config.yml
datadir: /node/data

log:
  level:
    default: info
    tendermint: warn
    tendermint/context: error
  format: JSON

genesis:
  file: /node/etc/genesis.json

consensus:
  tendermint:
    p2p:
      seed:
        - "HcDFrTp/MqRHtju5bCx6TIhIMd6X/0ZQ3lUG73q5898=@35.247.24.212:26656"
        - "kqsc8ETIgG9LCmW5HhSEUW80WIpwKhS7hRQd8FrnkJ0=@34.140.116.202:26656"

runtime:
  mode: client
  paths:
    - /node/runtimes/sapphire-paratime.orc

  # For SGX-enabled nodes:
  # sgx:
  #   loader: /node/bin/oasis-core-runtime-loader
```

---

## Blockers & Concerns

### 1. Storage Insufficient ❌
- Required: 200-300 GB SSD
- Available: 143 GB
- **Action:** Expand disk or use separate volume

### 2. RAM Marginal ⚠️
- Required: 12-20 GB
- Available: 15 GB
- **Status:** Within range but at minimum for production

### 3. SGX Support Unknown ❓
- Sapphire requires Intel SGX for compute nodes
- Need to verify: `cpuid | grep -i sgx`
- **Alternative:** Run as client node (no SGX required)

### 4. Coexistence with Blockscout ⚠️
- Blockscout already running on seed2.fanati.co
- May compete for resources
- Consider port conflicts (both use 8545 for RPC)

---

## References

- [Oasis Testnet Documentation](https://docs.oasis.io/node/network/testnet/)
- [Hardware Requirements](https://docs.oasis.io/node/run-your-node/prerequisites/hardware-recommendations/)
- [ParaTime Node Setup](https://docs.oasis.io/node/run-your-node/paratime-node/)
- [TEE Setup](https://docs.oasis.io/node/run-your-node/prerequisites/set-up-trusted-execution-environment-tee/)

---

## Deployment Status

### Current State: SYNCING ✅

**Deployed:** January 31, 2026

| Component | Status |
|-----------|--------|
| Oasis Node | Running (systemd service) |
| Consensus Sync | In Progress |
| Web3 Gateway | Pending (after sync) |
| DNS | sapphire-testnet.fanati.co |
| SSL | Configured (Let's Encrypt) |

### Sync Progress (as of January 31, 2026)

| Metric | Value |
|--------|-------|
| Current Height | 17,839,635 |
| Genesis Height | 17,751,681 |
| Blocks Synced | 87,954 |
| Sync Position | October 18, 2023 |
| Peers Connected | 20 |
| Estimated Completion | ~15-20 days |

### Resource Usage

| Resource | Usage | Status |
|----------|-------|--------|
| Disk | 28 GB / 150 GB (20%) | ✅ OK |
| RAM | 2.8 GB / 15 GB (19%) | ✅ OK |
| CPU | ~44% (8 vCPUs) | ✅ OK |

### Hardware Findings

- **CPU:** AMD EPYC (no Intel SGX support)
- **Mode:** Client node (observer only, no SGX required)
- **Storage:** 150 GB available (exceeded original 143 GB estimate)

### Resolved Concerns

1. ✅ **Storage:** 150 GB available, currently using 28 GB
2. ✅ **RAM:** 15 GB sufficient, using ~3 GB
3. ✅ **SGX:** Running as client node (no SGX required)
4. ✅ **Port Conflict:** Blockscout on 8000, Oasis Web3 Gateway will use 8545

### Configuration Files

| File | Location |
|------|----------|
| Node Config | `/node/etc/config.yml` |
| Genesis | `/node/etc/genesis.json` |
| Gateway Config | `/node/etc/gateway.yml` |
| Systemd Service | `/etc/systemd/system/oasis-node.service` |
| nginx Config | `/etc/nginx/sites-available/sapphire-testnet.fanati.co` |

### Management Commands

```bash
# Check service status
systemctl status oasis-node

# View logs
journalctl -u oasis-node -f

# Check sync progress
oasis-node control status -a unix:/node/data/internal.sock

# Restart node
systemctl restart oasis-node
```

### Next Steps

1. Monitor sync progress (check back in 7 days)
2. Start Web3 Gateway after consensus sync completes
3. Enable nginx proxy for sapphire-testnet.fanati.co
4. Test JSON-RPC connectivity

---

**Last Updated:** January 31, 2026
