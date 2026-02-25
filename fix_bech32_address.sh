#!/bin/bash

echo "=== Oasis Node Bech32 Address Fix Script ==="
echo "This script fixes the invalid bech32 address in the genesis file"
echo "Invalid:  oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qvz"
echo "Valid:    oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qn0zn68"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

# Stop the service
echo "1. Stopping oasis-node service..."
systemctl stop oasis-node
sleep 2

# Backup current genesis file
echo "2. Creating backup of current genesis file..."
cp /node/etc/genesis.json /node/etc/genesis.json.backup.$(date +%Y%m%d_%H%M%S)

# Apply the fix
echo "3. Applying bech32 address fix..."
sed -i 's/oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qvz/oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qn0zn68/g' /node/etc/genesis.json

# Verify the fix was applied
echo "4. Verifying fix was applied..."
if grep -q "oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qn0zn68" /node/etc/genesis.json; then
    echo "   ✓ Fix applied successfully - valid address found in genesis.json"
else
    echo "   ✗ Fix failed - valid address not found in genesis.json"
    exit 1
fi

if grep -q "oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qvz" /node/etc/genesis.json; then
    echo "   ✗ Invalid address still present in genesis.json"
    exit 1
else
    echo "   ✓ Invalid address removed from genesis.json"
fi

# Ensure proper ownership
echo "5. Setting proper file ownership..."
chown oasis:oasis /node/etc/genesis.json

# Start the service
echo "6. Starting oasis-node service..."
systemctl start oasis-node
sleep 3

# Check service status
echo "7. Checking service status..."
systemctl status oasis-node --no-pager

# Show recent logs
echo
echo "8. Recent logs:"
journalctl -u oasis-node -n 20 --no-pager

echo
echo "=== Fix Complete ==="
echo "The bech32 address has been corrected in the genesis file and the service has been restarted."
echo "Monitor the logs to ensure the node is functioning properly."