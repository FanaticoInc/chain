#!/bin/bash

echo "=== Deploying Entity Registration Files ==="

# Backup existing files
echo "Creating backups..."
cp /node/etc/config.yml /node/etc/config.yml.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
cp /node/etc/genesis.json /node/etc/genesis.json.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# Deploy updated configuration
echo "Deploying configuration file..."
cp /home/claude/config_with_entity_registration.yml /node/etc/config.yml
chown oasis:oasis /node/etc/config.yml

# Deploy updated genesis file with validators
echo "Deploying genesis file with validators..."
cp /home/claude/genesis_with_validators.json /node/etc/genesis.json
chown oasis:oasis /node/etc/genesis.json

# Verify the entity descriptor file exists in the data directory
if [ ! -f "/node/data/entity_descriptor.json" ]; then
    echo "Error: Entity descriptor file not found at /node/data/entity_descriptor.json"
    exit 1
fi

echo "=== Deployment Complete ==="
echo ""
echo "Entity ID: HGhLI8jeV3R7Dp5nsSHW0bFyvw3a0Sq3Qdd0tzQpnGs="
echo "Node ID: m9igeaTpDmMWj2r7I5tO2JZKSQ3XI7mNLLC/AasVjkM="
echo "Consensus Key: NLStRPXrQuF4eWwIuUqw+gJdEYEHqjGw29HowSDRJxs="
echo ""
echo "Files updated:"
echo "- /node/etc/config.yml (with entity registration)"
echo "- /node/etc/genesis.json (with validator set)"
echo "- Entity keys are available at /node/data/"
echo ""
echo "To restart the node with the new configuration:"
echo "systemctl restart oasis-node"