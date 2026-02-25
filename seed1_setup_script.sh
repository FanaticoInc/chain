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
    cat > "$NODE_DIR/etc/genesis.json" << 'EOF'
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
EOF

    chown $SERVICE_USER:$SERVICE_USER "$NODE_DIR/etc/genesis.json"
    log_info "Genesis file created successfully"
}

# Function to create node configuration
create_config() {
    log_info "Creating seed node configuration..."

    cat > "$NODE_DIR/etc/config.yml" << EOF
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
EOF

    chown $SERVICE_USER:$SERVICE_USER "$NODE_DIR/etc/config.yml"
    log_info "Configuration file created"
}

# Function to create systemd service
create_service() {
    log_info "Creating systemd service..."

    cat > /etc/systemd/system/oasis-seed.service << EOF
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
EOF

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
    cat > /etc/security/limits.d/99-oasis-seed.conf << EOF
$SERVICE_USER soft nofile 102400
$SERVICE_USER hard nofile 102400
EOF

    # Network optimizations
    cat >> /etc/sysctl.conf << EOF

# Oasis seed node optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 5000
EOF

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