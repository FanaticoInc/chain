#!/bin/bash

echo "=== Deploying Entity Registration Files ==="

# Create backup directory in /tmp
BACKUP_DIR="/tmp/oasis_backups_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup existing files
echo "Creating backups..."
cp /node/etc/config.yml "$BACKUP_DIR/config.yml.backup" 2>/dev/null || true
cp /node/etc/genesis.json "$BACKUP_DIR/genesis.json.backup" 2>/dev/null || true

# Copy files to /tmp for deployment
echo "Preparing files for deployment..."
cp /home/claude/config_with_entity_registration.yml /tmp/config_new.yml
cp /home/claude/genesis_with_validators.json /tmp/genesis_new.json

# Change ownership to oasis user
echo "Changing ownership to oasis user..."
chown oasis:oasis /tmp/config_new.yml /tmp/genesis_new.json

# Verify the entity descriptor file exists in the data directory
if [ ! -f "/node/data/entity_descriptor.json" ]; then
    echo "Error: Entity descriptor file not found at /node/data/entity_descriptor.json"
    exit 1
fi

echo "=== Files prepared for deployment ==="
echo ""
echo "Entity ID: HGhLI8jeV3R7Dp5nsSHW0bFyvw3a0Sq3Qdd0tzQpnGs="
echo "Node ID: m9igeaTpDmMWj2r7I5tO2JZKSQ3XI7mNLLC/AasVjkM="
echo "Consensus Key: NLStRPXrQuF4eWwIuUqw+gJdEYEHqjGw29HowSDRJxs="
echo ""
echo "Files prepared in /tmp/:"
echo "- config_new.yml (with entity registration)"
echo "- genesis_new.json (with validator set)"
echo "- Backups saved to: $BACKUP_DIR"
echo ""
echo "To complete deployment, run as oasis user:"
echo "sudo -u oasis cp /tmp/config_new.yml /node/etc/config.yml"
echo "sudo -u oasis cp /tmp/genesis_new.json /node/etc/genesis.json"
echo "sudo systemctl restart oasis-node"