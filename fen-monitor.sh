#!/bin/bash

# FEN Network Monitoring Dashboard
# Real-time monitoring of Fanatico L1 with FEN token

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

RPC_URL="http://localhost:8545"

# Clear screen and show header
clear_and_header() {
    clear
    echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║           FEN NETWORK MONITORING DASHBOARD                ║${NC}"
    echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${BLUE}Timestamp: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo ""
}

# Get chain data via RPC
get_chain_data() {
    # Get chain ID
    CHAIN_ID=$(curl -s -X POST $RPC_URL \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' 2>/dev/null | \
        grep -o '"result":"[^"]*"' | cut -d'"' -f4)

    # Get block number
    BLOCK_HEX=$(curl -s -X POST $RPC_URL \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>/dev/null | \
        grep -o '"result":"[^"]*"' | cut -d'"' -f4)

    # Convert hex to decimal
    if [ ! -z "$BLOCK_HEX" ]; then
        BLOCK_NUM=$((16#${BLOCK_HEX#0x}))
    else
        BLOCK_NUM="N/A"
    fi

    # Get gas price
    GAS_PRICE_HEX=$(curl -s -X POST $RPC_URL \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}' 2>/dev/null | \
        grep -o '"result":"[^"]*"' | cut -d'"' -f4)

    if [ ! -z "$GAS_PRICE_HEX" ] && [ "$GAS_PRICE_HEX" != "0x0" ]; then
        GAS_PRICE=$((16#${GAS_PRICE_HEX#0x}))
        GAS_PRICE_GWEI=$(echo "scale=2; $GAS_PRICE / 1000000000" | bc 2>/dev/null || echo "0")
    else
        GAS_PRICE_GWEI="0"
    fi
}

# Check service status
check_services() {
    # Local node status
    LOCAL_STATUS=$(systemctl is-active oasis-node 2>/dev/null || echo "unknown")

    # Check if RPC is responding
    if curl -s -X POST $RPC_URL \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' 2>/dev/null | grep -q result; then
        RPC_STATUS="online"
    else
        RPC_STATUS="offline"
    fi
}

# Get genesis info
get_genesis_info() {
    if [ -f /node/etc/genesis.json ]; then
        TOKEN=$(grep '"token_symbol"' /node/etc/genesis.json | cut -d'"' -f4)
        DECIMALS=$(grep '"token_value_exponent"' /node/etc/genesis.json | grep -o '[0-9]*')
        SUPPLY=$(grep '"total_supply"' /node/etc/genesis.json | cut -d'"' -f4)

        # Calculate FCO supply
        if [ ! -z "$SUPPLY" ]; then
            FCO_SUPPLY=$(echo "scale=0; $SUPPLY / 1000000000000000000" | bc 2>/dev/null || echo "100000000")
        else
            FCO_SUPPLY="N/A"
        fi
    else
        TOKEN="N/A"
        DECIMALS="N/A"
        FCO_SUPPLY="N/A"
    fi
}

# Display dashboard
display_dashboard() {
    clear_and_header

    # Network Information
    echo -e "${YELLOW}${BOLD}═══ Network Information ═══${NC}"
    echo -e "  Token Symbol:    ${GREEN}$TOKEN${NC}"
    echo -e "  Token Decimals:  ${GREEN}$DECIMALS${NC}"
    echo -e "  Total Supply:    ${GREEN}$FCO_SUPPLY FCO${NC}"
    echo -e "  Chain ID:        ${GREEN}$CHAIN_ID${NC} ($(printf "%d" $CHAIN_ID 2>/dev/null || echo "1234"))"
    echo ""

    # Blockchain Status
    echo -e "${YELLOW}${BOLD}═══ Blockchain Status ═══${NC}"
    echo -e "  Current Block:   ${BLUE}#$BLOCK_NUM${NC}"
    echo -e "  Gas Price:       ${BLUE}$GAS_PRICE_GWEI Gwei${NC}"

    # Block production status
    if [ "$BLOCK_NUM" == "0" ]; then
        echo -e "  Block Production: ${YELLOW}⏳ Waiting for consensus${NC}"
    elif [ "$BLOCK_NUM" == "N/A" ]; then
        echo -e "  Block Production: ${RED}✗ Unable to determine${NC}"
    else
        echo -e "  Block Production: ${GREEN}✓ Active${NC}"
    fi
    echo ""

    # Service Status
    echo -e "${YELLOW}${BOLD}═══ Service Status ═══${NC}"

    # Local node
    if [ "$LOCAL_STATUS" == "active" ]; then
        echo -e "  Oasis Node:      ${GREEN}✓ Active${NC}"
    elif [ "$LOCAL_STATUS" == "activating" ]; then
        echo -e "  Oasis Node:      ${YELLOW}🔄 Starting${NC}"
    elif [ "$LOCAL_STATUS" == "inactive" ]; then
        echo -e "  Oasis Node:      ${RED}✗ Inactive${NC}"
    else
        echo -e "  Oasis Node:      ${YELLOW}? Unknown${NC}"
    fi

    # RPC status
    if [ "$RPC_STATUS" == "online" ]; then
        echo -e "  Web3 RPC:        ${GREEN}✓ Online${NC} (port 8545)"
    else
        echo -e "  Web3 RPC:        ${RED}✗ Offline${NC}"
    fi
    echo ""

    # Node Connections
    echo -e "${YELLOW}${BOLD}═══ Node Connections ═══${NC}"

    # Check connectivity to other nodes
    for node in consensus1.fanati.co consensus2.fanati.co; do
        if ping -c 1 -W 1 $node > /dev/null 2>&1; then
            echo -e "  $node: ${GREEN}✓ Reachable${NC}"
        else
            echo -e "  $node: ${RED}✗ Unreachable${NC}"
        fi
    done
    echo ""

    # Performance Metrics
    echo -e "${YELLOW}${BOLD}═══ Performance Metrics ═══${NC}"

    # Memory usage
    if [ -f /proc/meminfo ]; then
        TOTAL_MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        FREE_MEM=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
        USED_MEM=$((($TOTAL_MEM - $FREE_MEM) * 100 / $TOTAL_MEM))
        echo -e "  Memory Usage:    ${BLUE}$USED_MEM%${NC}"
    fi

    # CPU load
    LOAD=$(uptime | awk -F'load average:' '{print $2}')
    echo -e "  Load Average:   ${BLUE}$LOAD${NC}"

    # Disk usage for /node
    if [ -d /node ]; then
        DISK_USAGE=$(df -h /node | awk 'NR==2 {print $5}')
        echo -e "  Disk Usage:      ${BLUE}$DISK_USAGE${NC} (/node)"
    fi
    echo ""

    # Recent Activity
    echo -e "${YELLOW}${BOLD}═══ Recent Activity ═══${NC}"

    # Check for recent errors
    ERROR_COUNT=$(journalctl -u oasis-node --since "5 minutes ago" 2>/dev/null | grep -c ERROR || echo 0)
    if [ "$ERROR_COUNT" -eq 0 ]; then
        echo -e "  Recent Errors:   ${GREEN}✓ None${NC}"
    else
        echo -e "  Recent Errors:   ${YELLOW}⚠ $ERROR_COUNT errors in last 5 min${NC}"
    fi

    # Check last log entry time
    LAST_LOG=$(journalctl -u oasis-node -n 1 --no-pager 2>/dev/null | grep -o '[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}' | head -1)
    if [ ! -z "$LAST_LOG" ]; then
        echo -e "  Last Log Entry:  ${BLUE}$LAST_LOG${NC}"
    fi
}

# Main monitoring loop
main() {
    echo -e "${GREEN}Starting FEN Network Monitor...${NC}"
    echo "Press Ctrl+C to exit"
    sleep 2

    while true; do
        get_genesis_info
        get_chain_data
        check_services
        display_dashboard

        # Status bar at bottom
        echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}Auto-refresh: 5 seconds | Press Ctrl+C to exit${NC}"

        sleep 5
    done
}

# Trap Ctrl+C
trap 'echo -e "\n${YELLOW}Monitor stopped.${NC}"; exit 0' INT

# Run main function
main