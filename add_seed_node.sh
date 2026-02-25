#!/bin/bash

echo "Adding seed node to oasis-node configuration..."

# Create updated config with seed node
cat > /tmp/config_with_seeds.yml << 'EOF'
mode: client
common:
  data_dir: /node/data
  log:
    format: JSON
    level:
      default: info
      cometbft: info
      cometbft/context: error

p2p:
  port: 26657
  seeds:
    - "0BDzJnkREvNWRJ65I/TpamPzt2y/5/8duvZBjMd8acY=@95.217.47.102:26656"

genesis:
  file: /node/etc/genesis.json
EOF

# Stop the service
echo "Stopping oasis-node service..."
sudo systemctl stop oasis-node

# Backup current config
echo "Creating backup of current config..."
sudo cp /node/etc/config.yml /node/etc/config.yml.backup.$(date +%Y%m%d_%H%M%S)

# Apply new config
echo "Applying configuration with seed node..."
sudo cp /tmp/config_with_seeds.yml /node/etc/config.yml
sudo chown oasis:oasis /node/etc/config.yml

# Start the service
echo "Starting oasis-node service..."
sudo systemctl start oasis-node

# Check status
echo "Checking service status..."
sudo systemctl status oasis-node --no-pager

echo "Seed node configuration applied!"
echo "Monitor logs with: journalctl -u oasis-node -f"