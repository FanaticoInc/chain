#!/bin/bash

# FEN Network Health Check Script
# Quick health status of the Fanatico L1 network

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

RPC_URL="http://localhost:8545"
EXTERNAL_RPC="http://paratime.fanati.co:8545"

echo "=== FEN Network Health Check ==="
echo "Timestamp: $(date)"
echo ""

HEALTH_SCORE=0
MAX_SCORE=10

# 1. Check local service
echo -n "1. Local Node Service: "
STATUS=$(systemctl is-active oasis-node 2>/dev/null || echo "unknown")
if [ "$STATUS" == "active" ]; then
    echo -e "${GREEN}✓ Active${NC}"
    ((HEALTH_SCORE++))
elif [ "$STATUS" == "activating" ]; then
    echo -e "${YELLOW}🔄 Starting${NC}"
else
    echo -e "${RED}✗ $STATUS${NC}"
fi

# 2. Check RPC connectivity (local)
echo -n "2. Local RPC (8545): "
if curl -s -X POST $RPC_URL \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' 2>/dev/null | grep -q "0x4d2"; then
    echo -e "${GREEN}✓ Responding${NC}"
    ((HEALTH_SCORE++))
else
    echo -e "${RED}✗ Not responding${NC}"
fi

# 3. Check external RPC
echo -n "3. External RPC: "
if timeout 2 curl -s -X POST $EXTERNAL_RPC \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' 2>/dev/null | grep -q "0x4d2"; then
    echo -e "${GREEN}✓ Accessible${NC}"
    ((HEALTH_SCORE++))
else
    echo -e "${YELLOW}⚠ Not accessible externally${NC}"
fi

# 4. Check genesis configuration
echo -n "4. Genesis Config: "
if [ -f /node/etc/genesis.json ]; then
    TOKEN=$(grep '"token_symbol"' /node/etc/genesis.json | cut -d'"' -f4)
    if [ "$TOKEN" == "FEN" ]; then
        echo -e "${GREEN}✓ FEN configured${NC}"
        ((HEALTH_SCORE++))
    else
        echo -e "${RED}✗ Token is $TOKEN, expected FEN${NC}"
    fi
else
    echo -e "${RED}✗ Genesis file missing${NC}"
fi

# 5. Check block production
echo -n "5. Block Production: "
BLOCK_HEX=$(curl -s -X POST $RPC_URL \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>/dev/null | \
    grep -o '"result":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$BLOCK_HEX" ]; then
    BLOCK_NUM=$((16#${BLOCK_HEX#0x}))
    if [ $BLOCK_NUM -gt 0 ]; then
        echo -e "${GREEN}✓ Block #$BLOCK_NUM${NC}"
        ((HEALTH_SCORE+=2))
    else
        echo -e "${YELLOW}⏳ At genesis (block 0)${NC}"
        ((HEALTH_SCORE++))
    fi
else
    echo -e "${RED}✗ Cannot determine${NC}"
fi

# 6. Check consensus nodes
echo -n "6. Consensus Nodes: "
REACHABLE=0
for node in consensus1.fanati.co consensus2.fanati.co; do
    if ping -c 1 -W 1 $node > /dev/null 2>&1; then
        ((REACHABLE++))
    fi
done
if [ $REACHABLE -eq 2 ]; then
    echo -e "${GREEN}✓ 2/2 reachable${NC}"
    ((HEALTH_SCORE++))
elif [ $REACHABLE -eq 1 ]; then
    echo -e "${YELLOW}⚠ 1/2 reachable${NC}"
else
    echo -e "${RED}✗ 0/2 reachable${NC}"
fi

# 7. Check recent errors
echo -n "7. Recent Errors: "
ERROR_COUNT=$(journalctl -u oasis-node --since "10 minutes ago" 2>/dev/null | grep -c ERROR || echo 0)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ None${NC}"
    ((HEALTH_SCORE++))
elif [ "$ERROR_COUNT" -lt 5 ]; then
    echo -e "${YELLOW}⚠ $ERROR_COUNT errors${NC}"
else
    echo -e "${RED}✗ $ERROR_COUNT errors${NC}"
fi

# 8. Check disk space
echo -n "8. Disk Space: "
if [ -d /node ]; then
    DISK_USAGE=$(df /node | awk 'NR==2 {print int($5)}')
    if [ $DISK_USAGE -lt 80 ]; then
        echo -e "${GREEN}✓ $DISK_USAGE% used${NC}"
        ((HEALTH_SCORE++))
    elif [ $DISK_USAGE -lt 90 ]; then
        echo -e "${YELLOW}⚠ $DISK_USAGE% used${NC}"
    else
        echo -e "${RED}✗ $DISK_USAGE% used${NC}"
    fi
else
    echo -e "${RED}✗ /node not found${NC}"
fi

# Calculate health percentage
echo ""
echo "════════════════════════════════"
HEALTH_PERCENT=$((HEALTH_SCORE * 100 / MAX_SCORE))

echo -n "Overall Health: "
if [ $HEALTH_PERCENT -ge 80 ]; then
    echo -e "${GREEN}$HEALTH_PERCENT% - Healthy${NC}"
elif [ $HEALTH_PERCENT -ge 60 ]; then
    echo -e "${YELLOW}$HEALTH_PERCENT% - Degraded${NC}"
else
    echo -e "${RED}$HEALTH_PERCENT% - Critical${NC}"
fi

echo "Score: $HEALTH_SCORE/$MAX_SCORE"
echo ""

# Recommendations
if [ $HEALTH_PERCENT -lt 100 ]; then
    echo "Recommendations:"

    if [ "$STATUS" != "active" ]; then
        echo "  • Start the oasis-node service: sudo systemctl start oasis-node"
    fi

    if [ $BLOCK_NUM -eq 0 ] 2>/dev/null; then
        echo "  • Network at genesis block - wait for consensus formation"
    fi

    if [ $ERROR_COUNT -gt 0 ]; then
        echo "  • Check logs for errors: sudo journalctl -u oasis-node -n 100"
    fi

    if [ $DISK_USAGE -gt 80 ] 2>/dev/null; then
        echo "  • Disk usage high - consider cleanup"
    fi
fi

# Quick status for scripts
exit $((100 - HEALTH_PERCENT))