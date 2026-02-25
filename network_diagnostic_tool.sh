#!/bin/bash
# Fanatico L1 Network Diagnostic Tool
# Tests connectivity to all network nodes and provides status report

set -e

echo "=========================================="
echo "Fanatico L1 Network Diagnostic Tool"
echo "=========================================="
echo "Timestamp: $(date)"
echo ""

# Network nodes configuration
declare -A NODES=(
    ["paratime-km"]="178.162.202.84"
    ["consensus1"]="95.217.47.102"
    ["consensus2"]="95.216.243.184"
    ["consensus3"]="142.132.128.217"
    ["seed1"]="138.201.16.186"
)

declare -A ROLES=(
    ["paratime-km"]="ParaTime/Key Manager"
    ["consensus1"]="Seed Node (Primary)"
    ["consensus2"]="Validator Node"
    ["consensus3"]="Validator Node"
    ["seed1"]="Seed Node (Designated)"
)

echo "=== NETWORK CONNECTIVITY TESTS ==="
echo ""

# Test basic connectivity
for node in "${!NODES[@]}"; do
    ip="${NODES[$node]}"
    role="${ROLES[$node]}"
    echo "Testing $node ($role) - $ip:"

    # Ping test
    if ping -c 2 -W 3 "$ip" >/dev/null 2>&1; then
        echo "  ✅ Ping: Reachable"

        # P2P port test (26656)
        if timeout 3 nc -z "$ip" 26656 2>/dev/null; then
            echo "  ✅ P2P Port (26656): OPEN"
        else
            echo "  ❌ P2P Port (26656): CLOSED/FILTERED"
        fi

        # Alternative port test (26657)
        if timeout 3 nc -z "$ip" 26657 2>/dev/null; then
            echo "  ℹ️  Alt Port (26657): OPEN"
        else
            echo "  ℹ️  Alt Port (26657): CLOSED"
        fi
    else
        echo "  ❌ Ping: UNREACHABLE"
        echo "  ❌ P2P Port: N/A (Host unreachable)"
    fi
    echo ""
done

echo "=== OASIS NODE STATUS ==="
echo ""

# Check oasis-node service
echo "Local Oasis Node Service Status:"
if systemctl is-active --quiet oasis-node 2>/dev/null; then
    echo "  ✅ Service: Active"
else
    echo "  ❌ Service: Inactive/Failed"
fi

# Check recent logs for connectivity
echo ""
echo "Recent Network Bootstrap Attempts:"
if journalctl -u oasis-node -n 20 --no-pager 2>/dev/null | grep -E "(bootstrap|seed|dial|connect)" | tail -3; then
    echo "  (See above for recent connection attempts)"
else
    echo "  ℹ️  No recent bootstrap attempts found in logs"
fi

echo ""
echo "=== CONNECTIVITY SUMMARY ==="
echo ""

reachable_count=0
total_nodes=${#NODES[@]}

for node in "${!NODES[@]}"; do
    ip="${NODES[$node]}"
    if ping -c 1 -W 2 "$ip" >/dev/null 2>&1; then
        ((reachable_count++))
    fi
done

echo "Reachable nodes: $reachable_count/$total_nodes"

# Recommendations
echo ""
echo "=== RECOMMENDATIONS ==="
echo ""

if [ $reachable_count -eq 0 ]; then
    echo "❌ CRITICAL: No network nodes reachable"
    echo "   • Check internet connectivity"
    echo "   • Verify network configuration"
elif [ $reachable_count -lt $total_nodes ]; then
    echo "⚠️  WARNING: Some network nodes unreachable"
    echo "   • Some nodes may be offline for maintenance"
    echo "   • Network may still function with available nodes"
else
    echo "✅ Good: All network nodes reachable"
    echo "   • Check P2P port accessibility"
    echo "   • Verify node software is running on external hosts"
fi

echo ""
echo "For P2P connectivity issues:"
echo "  • Contact Fanatico network administrator"
echo "  • Verify firewall settings on external nodes"
echo "  • Check if network is in maintenance mode"
echo ""
echo "=========================================="