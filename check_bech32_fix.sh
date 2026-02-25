#!/bin/bash

echo "=== Checking Bech32 Address Fix Status ==="
echo

# Check in genesis.json
if [ -f "/node/etc/genesis.json" ]; then
    echo "Checking /node/etc/genesis.json:"
    if grep -q "oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qvz" /node/etc/genesis.json; then
        echo "  ✗ Invalid address found: oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qvz"
    else
        echo "  ✓ No invalid address found"
    fi
    
    if grep -q "oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qn0zn68" /node/etc/genesis.json; then
        echo "  ✓ Valid address found: oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qn0zn68"
    else
        echo "  ✗ Valid address not found"
    fi
else
    echo "  ✗ /node/etc/genesis.json not found"
fi

echo

# Check in script
if [ -f "/home/claude/create_working_node.sh" ]; then
    echo "Checking /home/claude/create_working_node.sh:"
    if grep -q "oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qvz" /home/claude/create_working_node.sh; then
        echo "  ✗ Invalid address found in script"
    else
        echo "  ✓ No invalid address found in script"
    fi
    
    if grep -q "oasis1qpllh99nhwzrd56px4txvl26atzgg4f0dpmx7qn0zn68" /home/claude/create_working_node.sh; then
        echo "  ✓ Valid address found in script"
    else
        echo "  ✗ Valid address not found in script"
    fi
else
    echo "  ✗ /home/claude/create_working_node.sh not found"
fi

echo

# Check service status
echo "Checking oasis-node service status:"
systemctl is-active oasis-node 2>/dev/null || echo "  Service not running or not accessible"