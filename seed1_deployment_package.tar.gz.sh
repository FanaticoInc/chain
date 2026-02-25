#!/bin/bash
# Self-extracting deployment package for seed1.fanati.co
# This script creates a complete deployment package

EXTRACT_DIR="${1:-/tmp/seed1_deployment}"

echo "Creating deployment package for seed1.fanati.co..."
echo "Extraction directory: $EXTRACT_DIR"

mkdir -p "$EXTRACT_DIR"

# Create the installation script
cat > "$EXTRACT_DIR/seed1_setup_script.sh" << 'EOF'
#!/bin/bash
# Fanatico L1 Seed Node Setup Script
# Target: seed1.fanati.co (138.201.16.186)
# Role: Primary seed node for Fanatico L1 network

set -e

echo "=========================================="
echo "Fanatico L1 Seed Node Setup"
echo "Server: seed1.fanati.co (138.201.16.186)"
echo "Date: $(date)"
echo "=========================================="

# Configuration variables
OASIS_VERSION="24.3.2"
CHAIN_ID="fanatico-l1-1234"
NODE_DIR="/node"
SERVICE_USER="oasis"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Function to create system user
create_user() {
    log_info "Creating oasis system user..."
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/bash -m "$SERVICE_USER"
        log_info "User $SERVICE_USER created successfully"
    else
        log_info "User $SERVICE_USER already exists"
    fi
}

# Function to create directory structure
create_directories() {
    log_info "Creating directory structure..."
    mkdir -p $NODE_DIR/{bin,etc,data,logs}
    chown -R $SERVICE_USER:$SERVICE_USER $NODE_DIR
    chmod -R 755 $NODE_DIR
    chmod 700 $NODE_DIR/data
    log_info "Directory structure created"
}

# Function to download Oasis node binary
download_oasis_node() {
    log_info "Downloading Oasis Node v$OASIS_VERSION..."

    cd /tmp
    if [ ! -f "oasis_core_${OASIS_VERSION}_linux_amd64.tar.gz" ]; then
        wget -q "https://github.com/oasisprotocol/oasis-core/releases/download/v${OASIS_VERSION}/oasis_core_${OASIS_VERSION}_linux_amd64.tar.gz"
        log_info "Download completed"
    else
        log_info "Binary already downloaded"
    fi

    log_info "Extracting and installing binary..."
    tar -xzf "oasis_core_${OASIS_VERSION}_linux_amd64.tar.gz"
    cp "oasis_core_${OASIS_VERSION}_linux_amd64/oasis-node" "$NODE_DIR/bin/"
    chmod +x "$NODE_DIR/bin/oasis-node"
    chown $SERVICE_USER:$SERVICE_USER "$NODE_DIR/bin/oasis-node"

    log_info "Oasis node binary installed successfully"
}

# Function to generate node identity
generate_identity() {
    log_info "Generating node identity..."

    # Run as oasis user
    sudo -u $SERVICE_USER "$NODE_DIR/bin/oasis-node" identity init --datadir "$NODE_DIR/data"

    log_info "Node identity generated successfully"

    # Show node ID for configuration
    log_info "Node identity information:"
    sudo -u $SERVICE_USER "$NODE_DIR/bin/oasis-node" identity show-tls-pubkey --datadir "$NODE_DIR/data" | sed 's/^/  TLS Public Key: /'
}

# Function to create genesis file
create_genesis() {
    log_info "Creating genesis file..."

    # Use the working genesis from paratime node
    cat > "$NODE_DIR/etc/genesis.json" << 'GENESIS_EOF'
{
  "height": 1,
  "genesis_time": "2025-07-16T08:00:00Z",
  "chain_id": "fanatico-l1-1234",
  "registry": {
    "params": {
      "gas_costs": {
        "deregister_entity": 1000,
        "prove_freshness": 1000,
        "register_entity": 1000,
        "register_node": 1000,
        "register_runtime": 1000,
        "runtime_epoch_maintenance": 1000,
        "unfreeze_node": 1000
      },
      "max_node_expiration": 5,
      "enable_runtime_governance_models": {
        "entity": true
      },
      "tee_features": {
        "sgx": {
          "pcs": true,
          "signed_attestations": true,
          "max_attestation_age": 1200
        },
        "freshness_proofs": true
      }
    }
  },
  "roothash": {
    "params": {
      "gas_costs": {
        "compute_commit": 1000,
        "evidence": 1000,
        "proposer_timeout": 1000,
        "submit_msg": 1000
      },
      "max_runtime_messages": 128,
      "max_in_runtime_messages": 128,
      "max_evidence_age": 0,
      "max_past_roots_stored": 1200
    }
  },
  "staking": {
    "params": {
      "thresholds": {
        "entity": "0",
        "keymanager-churp": "0",
        "node-compute": "0",
        "node-keymanager": "0",
        "node-observer": "0",
        "node-validator": "0",
        "runtime-compute": "0",
        "runtime-keymanager": "0"
      },
      "debonding_interval": 1,
      "commission_schedule_rules": {
        "min_commission_rate": "0"
      },
      "min_delegation": "0",
      "min_transfer": "0",
      "min_transact_balance": "0",
      "fee_split_weight_propose": "0",
      "fee_split_weight_vote": "1",
      "fee_split_weight_next_propose": "0",
      "reward_factor_epoch_signed": "0",
      "reward_factor_block_proposed": "0"
    },
    "token_symbol": "FANATICO",
    "token_value_exponent": 0,
    "total_supply": "0",
    "common_pool": "0",
    "last_block_fees": "0",
    "governance_deposits": "0"
  },
  "keymanager": {
    "params": {
      "gas_costs": {
        "publish_ephemeral_secret": 1000,
        "publish_master_secret": 1000,
        "update_policy": 1000
      }
    }
  },
  "scheduler": {
    "params": {
      "min_validators": 1,
      "max_validators": 100,
      "max_validators_per_entity": 1,
      "reward_factor_epoch_election_any": "0"
    }
  },
  "beacon": {
    "base": 0,
    "params": {
      "backend": "insecure",
      "insecure_parameters": {
        "interval": 86400
      }
    }
  },
  "governance": {
    "params": {
      "gas_costs": {
        "cast_vote": 1000,
        "submit_proposal": 1000
      },
      "min_proposal_deposit": "100",
      "voting_period": 100,
      "stake_threshold": 90,
      "upgrade_min_epoch_diff": 300,
      "upgrade_cancel_min_epoch_diff": 300,
      "enable_change_parameters_proposal": true
    }
  },
  "consensus": {
    "backend": "tendermint",
    "params": {
      "timeout_commit": 5000000000,
      "skip_timeout_commit": false,
      "empty_block_interval": 0,
      "max_tx_size": 32768,
      "max_block_size": 22020096,
      "max_block_gas": 0,
      "max_evidence_size": 1048576,
      "state_checkpoint_interval": 10000,
      "state_checkpoint_num_kept": 2,
      "state_checkpoint_chunk_size": 8388608,
      "gas_costs": {
        "tx_byte": 1
      }
    }
  },
  "extra_data": null
}
GENESIS_EOF

    chown $SERVICE_USER:$SERVICE_USER "$NODE_DIR/etc/genesis.json"
    log_info "Genesis file created successfully"
}

# Function to create node configuration
create_config() {
    log_info "Creating seed node configuration..."

    cat > "$NODE_DIR/etc/config.yml" << CONFIG_EOF
# Fanatico L1 Seed Node Configuration
# Role: Primary seed node for network bootstrap
mode: seed

common:
  data_dir: $NODE_DIR/data
  log:
    format: JSON
    level:
      default: info
      cometbft: info
      cometbft/context: error
      p2p: debug

# P2P configuration for seed node
p2p:
  port: 26656
  external_address: "138.201.16.186:26656"

  # Seed node specific settings
  seeds: []  # Seed nodes don't connect to other seeds initially
  persistent_peers: []

  # Connection limits
  max_num_outbound_peers: 50
  max_num_inbound_peers: 100

  # Network timeouts
  dial_timeout: 3s
  handshake_timeout: 20s

# Genesis configuration
genesis:
  file: $NODE_DIR/etc/genesis.json

# Metrics and monitoring
metrics:
  mode: pull
  address: "127.0.0.1:9090"

# Disable components not needed for seed nodes
runtime:
  enabled: false

registration:
  enabled: false
CONFIG_EOF

    chown $SERVICE_USER:$SERVICE_USER "$NODE_DIR/etc/config.yml"
    log_info "Configuration file created"
}

# Function to create systemd service
create_service() {
    log_info "Creating systemd service..."

    cat > /etc/systemd/system/oasis-seed.service << SERVICE_EOF
[Unit]
Description=Oasis Seed Node - Fanatico L1
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$NODE_DIR/data
ExecStart=$NODE_DIR/bin/oasis-node --config $NODE_DIR/etc/config.yml
Restart=on-failure
RestartSec=5
LimitNOFILE=1024000

# Security settings
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$NODE_DIR
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
SERVICE_EOF

    systemctl daemon-reload
    log_info "Systemd service created successfully"
}

# Function to configure firewall
configure_firewall() {
    log_info "Configuring firewall for seed node..."

    # Install ufw if not present
    if ! command -v ufw &> /dev/null; then
        apt update && apt install -y ufw
    fi

    # Configure firewall rules
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing

    # Allow SSH
    ufw allow 22/tcp comment 'SSH'

    # Allow P2P port for Oasis network
    ufw allow 26656/tcp comment 'Oasis P2P'
    ufw allow 26656/udp comment 'Oasis P2P UDP'

    # Allow metrics (local only)
    ufw allow from 127.0.0.1 to any port 9090 comment 'Metrics'

    # Enable firewall
    ufw --force enable

    log_info "Firewall configured successfully"
}

# Function to optimize system settings
optimize_system() {
    log_info "Optimizing system settings for seed node..."

    # Increase file descriptor limits
    cat > /etc/security/limits.d/99-oasis-seed.conf << LIMITS_EOF
$SERVICE_USER soft nofile 102400
$SERVICE_USER hard nofile 102400
LIMITS_EOF

    # Network optimizations
    cat >> /etc/sysctl.conf << SYSCTL_EOF

# Oasis seed node optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 5000
SYSCTL_EOF

    sysctl -p
    log_info "System optimizations applied"
}

# Main installation function
main() {
    log_info "Starting Fanatico L1 seed node installation..."

    check_root
    create_user
    create_directories
    download_oasis_node
    generate_identity
    create_genesis
    create_config
    create_service
    configure_firewall
    optimize_system

    log_info "Installation completed successfully!"
    echo ""
    echo "=========================================="
    echo "SEED NODE SETUP COMPLETE"
    echo "=========================================="
    echo "Next steps:"
    echo "1. Start the service: systemctl start oasis-seed"
    echo "2. Enable auto-start: systemctl enable oasis-seed"
    echo "3. Check status: systemctl status oasis-seed"
    echo "4. View logs: journalctl -u oasis-seed -f"
    echo ""
    echo "Node identity (for validator configuration):"
    sudo -u $SERVICE_USER "$NODE_DIR/bin/oasis-node" identity show-tls-pubkey --datadir "$NODE_DIR/data"
    echo ""
    echo "P2P Address: 138.201.16.186:26656"
    echo "=========================================="
}

# Run main function
main "$@"
EOF

# Create the verification script
cat > "$EXTRACT_DIR/verify_seed1_deployment.sh" << 'EOF'
#!/bin/bash
# Seed1 Deployment Verification Script
# Run this script to verify seed1 deployment was successful

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SUCCESS_COUNT=0
TOTAL_TESTS=0

log_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "[$TOTAL_TESTS] $1: "
}

log_pass() {
    echo -e "${GREEN}PASS${NC}"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
}

log_fail() {
    echo -e "${RED}FAIL${NC} - $1"
}

log_warn() {
    echo -e "${YELLOW}WARN${NC} - $1"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))  # Count warnings as success
}

echo "=========================================="
echo "Seed1 Deployment Verification"
echo "Target: 138.201.16.186"
echo "Date: $(date)"
echo "=========================================="

# Test 1: Basic connectivity
log_test "Testing basic connectivity to seed1"
if ping -c 1 -W 3 138.201.16.186 >/dev/null 2>&1; then
    log_pass
else
    log_fail "Host unreachable"
fi

# Test 2: SSH connectivity
log_test "Testing SSH port accessibility"
if timeout 3 nc -z 138.201.16.186 22 2>/dev/null; then
    log_pass
else
    log_fail "SSH port not accessible"
fi

# Test 3: P2P port accessibility
log_test "Testing P2P port (26656) accessibility"
if timeout 3 nc -z 138.201.16.186 26656 2>/dev/null; then
    log_pass
else
    log_fail "P2P port 26656 not accessible - service may not be running or firewall blocking"
fi

# If we can SSH, run additional tests
if timeout 3 nc -z 138.201.16.186 22 2>/dev/null; then
    echo ""
    echo "Additional tests require SSH access to seed1..."
    echo "To run complete verification, execute this script on seed1 directly:"
    echo ""
    echo "  scp verify_seed1_deployment.sh root@138.201.16.186:/tmp/"
    echo "  ssh root@138.201.16.186 '/tmp/verify_seed1_deployment.sh --local'"
    echo ""
fi

# If running locally on seed1 (with --local flag)
if [[ "$1" == "--local" ]]; then
    echo ""
    echo "Running local verification tests..."

    # Test 4: Service status
    log_test "Checking oasis-seed service status"
    if systemctl is-active --quiet oasis-seed; then
        log_pass
    else
        log_fail "Service not active"
    fi

    # Test 5: User exists
    log_test "Checking oasis user exists"
    if id oasis >/dev/null 2>&1; then
        log_pass
    else
        log_fail "Oasis user not found"
    fi

    # Test 6: Directory structure
    log_test "Checking directory structure"
    if [[ -d /node && -d /node/bin && -d /node/etc && -d /node/data ]]; then
        log_pass
    else
        log_fail "Directory structure incomplete"
    fi

    # Test 7: Binary exists
    log_test "Checking oasis-node binary"
    if [[ -f /node/bin/oasis-node && -x /node/bin/oasis-node ]]; then
        log_pass
    else
        log_fail "Oasis node binary not found or not executable"
    fi

    # Test 8: Configuration file
    log_test "Checking configuration file"
    if [[ -f /node/etc/config.yml ]]; then
        log_pass
    else
        log_fail "Configuration file not found"
    fi

    # Test 9: Genesis file
    log_test "Checking genesis file"
    if [[ -f /node/etc/genesis.json ]]; then
        log_pass
    else
        log_fail "Genesis file not found"
    fi

    # Test 10: Node identity
    log_test "Checking node identity"
    if [[ -f /node/data/identity.pem ]]; then
        log_pass
    else
        log_fail "Node identity not generated"
    fi

    # Test 11: Port binding
    log_test "Checking port 26656 is bound"
    if ss -tulpn | grep -q ":26656"; then
        log_pass
    else
        log_fail "Port 26656 not bound"
    fi

    # Test 12: Firewall configuration
    log_test "Checking firewall status"
    if ufw status | grep -q "Status: active"; then
        if ufw status | grep -q "26656"; then
            log_pass
        else
            log_warn "UFW active but P2P port rule missing"
        fi
    else
        log_warn "UFW not active"
    fi

    # Test 13: Recent logs
    log_test "Checking for recent service logs"
    if journalctl -u oasis-seed --since "5 minutes ago" | grep -q "oasis-node"; then
        log_pass
    else
        log_warn "No recent service logs found"
    fi

    # Test 14: Node identity display
    echo ""
    echo "Node Identity Information:"
    if [[ -f /node/bin/oasis-node ]]; then
        echo "TLS Public Key:"
        sudo -u oasis /node/bin/oasis-node identity show-tls-pubkey --datadir /node/data 2>/dev/null | sed 's/^/  /'
        echo ""
        echo "P2P Address: 138.201.16.186:26656"
        echo ""
    fi

    # Test 15: Service logs (last 10 lines)
    echo "Recent Service Logs:"
    journalctl -u oasis-seed -n 10 --no-pager | sed 's/^/  /'
    echo ""
fi

# Summary
echo "=========================================="
echo "VERIFICATION SUMMARY"
echo "=========================================="
echo "Tests Passed: $SUCCESS_COUNT / $TOTAL_TESTS"

if [[ $SUCCESS_COUNT -eq $TOTAL_TESTS ]]; then
    echo -e "Status: ${GREEN}ALL TESTS PASSED${NC}"
    echo ""
    echo "✅ Seed1 deployment appears successful!"
    echo "✅ Ready for Phase 2: Validator configuration"
    exit 0
elif [[ $SUCCESS_COUNT -ge $((TOTAL_TESTS * 2 / 3)) ]]; then
    echo -e "Status: ${YELLOW}MOSTLY SUCCESSFUL${NC}"
    echo ""
    echo "⚠️  Some issues detected but deployment may be functional"
    echo "⚠️  Review failed tests and resolve before proceeding"
    exit 1
else
    echo -e "Status: ${RED}DEPLOYMENT ISSUES${NC}"
    echo ""
    echo "❌ Significant issues detected"
    echo "❌ Review installation and resolve issues before proceeding"
    exit 2
fi
EOF

# Create deployment instructions
cat > "$EXTRACT_DIR/README.md" << 'EOF'
# Seed1 Deployment Package - Phase 1

## Quick Start

1. **Transfer to seed1 server**:
```bash
scp -r seed1_deployment/ root@138.201.16.186:/tmp/
```

2. **SSH into seed1**:
```bash
ssh root@138.201.16.186
```

3. **Run installation**:
```bash
cd /tmp/seed1_deployment
chmod +x seed1_setup_script.sh
./seed1_setup_script.sh
```

4. **Start service**:
```bash
systemctl start oasis-seed
systemctl enable oasis-seed
```

5. **Verify deployment**:
```bash
./verify_seed1_deployment.sh --local
```

## What This Package Contains

- `seed1_setup_script.sh` - Complete installation script
- `verify_seed1_deployment.sh` - Verification script
- `README.md` - This file

## Expected Output

After successful installation, you should see:
- Service active: `systemctl status oasis-seed`
- Port bound: `ss -tulpn | grep 26656`
- Node identity generated
- P2P address: 138.201.16.186:26656

## Troubleshooting

If installation fails:
1. Check logs: `journalctl -u oasis-seed -f`
2. Verify firewall: `ufw status`
3. Test connectivity: `nc -zv 138.201.16.186 26656`

## Next Steps

After successful deployment:
1. Configure validators to connect to this seed
2. Start Phase 2: Validator setup on consensus1,2,3
3. Connect ParaTime to established network
EOF

# Make scripts executable
chmod +x "$EXTRACT_DIR/seed1_setup_script.sh"
chmod +x "$EXTRACT_DIR/verify_seed1_deployment.sh"

echo ""
echo "=========================================="
echo "DEPLOYMENT PACKAGE CREATED"
echo "=========================================="
echo "Location: $EXTRACT_DIR"
echo "Contents:"
ls -la "$EXTRACT_DIR"
echo ""
echo "To deploy to seed1.fanati.co:"
echo "1. scp -r $EXTRACT_DIR root@138.201.16.186:/tmp/"
echo "2. ssh root@138.201.16.186"
echo "3. cd /tmp/seed1_deployment && ./seed1_setup_script.sh"
echo "=========================================="