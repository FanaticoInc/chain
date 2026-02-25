#!/bin/bash
# Script to check Oasis Node connectivity and sync status

echo "=== Oasis Node Connectivity Check ==="
echo "Date: $(date)"
echo

# Check service status
echo "1. Service Status:"
echo "=================="
systemctl status oasis-node --no-pager -l
echo

# Check if internal socket exists
echo "2. Internal Socket Check:"
echo "========================"
if [ -S /node/data/internal.sock ]; then
    echo "✅ Internal socket exists: /node/data/internal.sock"
else
    echo "❌ Internal socket not found: /node/data/internal.sock"
    echo "   Node may not be fully started yet"
fi
echo

# Check node status and sync progress
echo "3. Node Status and Sync Progress:"
echo "================================="
if [ -S /node/data/internal.sock ]; then
    echo "Checking node status..."
    sudo -u claude /node/bin/oasis-node control status -a unix:/node/data/internal.sock
    echo
    
    echo "Checking sync status..."
    sudo -u claude /node/bin/oasis-node control status -a unix:/node/data/internal.sock | grep -A5 -B5 "consensus"
else
    echo "❌ Cannot check node status - internal socket not available"
fi
echo

# Verify ParaTime registration
echo "4. ParaTime Registration:"
echo "========================"
if [ -S /node/data/internal.sock ]; then
    echo "Checking runtime list..."
    sudo -u claude /node/bin/oasis-node control runtime list -a unix:/node/data/internal.sock
else
    echo "❌ Cannot check runtime list - internal socket not available"
fi
echo

# Check peer connections
echo "5. Peer Connections:"
echo "==================="
if [ -S /node/data/internal.sock ]; then
    echo "Checking peer connections..."
    sudo -u claude /node/bin/oasis-node control net peers -a unix:/node/data/internal.sock
else
    echo "❌ Cannot check peers - internal socket not available"
fi
echo

# Check recent logs
echo "6. Recent Logs:"
echo "==============="
echo "Last 20 lines of oasis-node logs:"
journalctl -u oasis-node -n 20 --no-pager
echo

echo "=== Check Complete ==="
echo "If the node is not fully started, wait a few minutes and run this script again."