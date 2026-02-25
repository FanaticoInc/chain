#!/bin/bash
# Seed1 Deployment Verification Script
# Run this script to verify seed1 deployment was successful

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SUCCESS_COUNT=0
TOTAL_TESTS=0

log_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "[$TOTAL_TESTS] $1: "
}

log_pass() {
    echo -e "${GREEN}PASS${NC}"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
}

log_fail() {
    echo -e "${RED}FAIL${NC} - $1"
}

log_warn() {
    echo -e "${YELLOW}WARN${NC} - $1"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))  # Count warnings as success
}

echo "=========================================="
echo "Seed1 Deployment Verification"
echo "Target: 138.201.16.186"
echo "Date: $(date)"
echo "=========================================="

# Test 1: Basic connectivity
log_test "Testing basic connectivity to seed1"
if ping -c 1 -W 3 138.201.16.186 >/dev/null 2>&1; then
    log_pass
else
    log_fail "Host unreachable"
fi

# Test 2: SSH connectivity
log_test "Testing SSH port accessibility"
if timeout 3 nc -z 138.201.16.186 22 2>/dev/null; then
    log_pass
else
    log_fail "SSH port not accessible"
fi

# Test 3: P2P port accessibility
log_test "Testing P2P port (26656) accessibility"
if timeout 3 nc -z 138.201.16.186 26656 2>/dev/null; then
    log_pass
else
    log_fail "P2P port 26656 not accessible - service may not be running or firewall blocking"
fi

# If we can SSH, run additional tests
if timeout 3 nc -z 138.201.16.186 22 2>/dev/null; then
    echo ""
    echo "Additional tests require SSH access to seed1..."
    echo "To run complete verification, execute this script on seed1 directly:"
    echo ""
    echo "  scp verify_seed1_deployment.sh root@138.201.16.186:/tmp/"
    echo "  ssh root@138.201.16.186 '/tmp/verify_seed1_deployment.sh --local'"
    echo ""
fi

# If running locally on seed1 (with --local flag)
if [[ "$1" == "--local" ]]; then
    echo ""
    echo "Running local verification tests..."

    # Test 4: Service status
    log_test "Checking oasis-seed service status"
    if systemctl is-active --quiet oasis-seed; then
        log_pass
    else
        log_fail "Service not active"
    fi

    # Test 5: User exists
    log_test "Checking oasis user exists"
    if id oasis >/dev/null 2>&1; then
        log_pass
    else
        log_fail "Oasis user not found"
    fi

    # Test 6: Directory structure
    log_test "Checking directory structure"
    if [[ -d /node && -d /node/bin && -d /node/etc && -d /node/data ]]; then
        log_pass
    else
        log_fail "Directory structure incomplete"
    fi

    # Test 7: Binary exists
    log_test "Checking oasis-node binary"
    if [[ -f /node/bin/oasis-node && -x /node/bin/oasis-node ]]; then
        log_pass
    else
        log_fail "Oasis node binary not found or not executable"
    fi

    # Test 8: Configuration file
    log_test "Checking configuration file"
    if [[ -f /node/etc/config.yml ]]; then
        log_pass
    else
        log_fail "Configuration file not found"
    fi

    # Test 9: Genesis file
    log_test "Checking genesis file"
    if [[ -f /node/etc/genesis.json ]]; then
        log_pass
    else
        log_fail "Genesis file not found"
    fi

    # Test 10: Node identity
    log_test "Checking node identity"
    if [[ -f /node/data/identity.pem ]]; then
        log_pass
    else
        log_fail "Node identity not generated"
    fi

    # Test 11: Port binding
    log_test "Checking port 26656 is bound"
    if ss -tulpn | grep -q ":26656"; then
        log_pass
    else
        log_fail "Port 26656 not bound"
    fi

    # Test 12: Firewall configuration
    log_test "Checking firewall status"
    if ufw status | grep -q "Status: active"; then
        if ufw status | grep -q "26656"; then
            log_pass
        else
            log_warn "UFW active but P2P port rule missing"
        fi
    else
        log_warn "UFW not active"
    fi

    # Test 13: Recent logs
    log_test "Checking for recent service logs"
    if journalctl -u oasis-seed --since "5 minutes ago" | grep -q "oasis-node"; then
        log_pass
    else
        log_warn "No recent service logs found"
    fi

    # Test 14: Node identity display
    echo ""
    echo "Node Identity Information:"
    if [[ -f /node/bin/oasis-node ]]; then
        echo "TLS Public Key:"
        sudo -u oasis /node/bin/oasis-node identity show-tls-pubkey --datadir /node/data 2>/dev/null | sed 's/^/  /'
        echo ""
        echo "P2P Address: 138.201.16.186:26656"
        echo ""
    fi

    # Test 15: Service logs (last 10 lines)
    echo "Recent Service Logs:"
    journalctl -u oasis-seed -n 10 --no-pager | sed 's/^/  /'
    echo ""
fi

# Summary
echo "=========================================="
echo "VERIFICATION SUMMARY"
echo "=========================================="
echo "Tests Passed: $SUCCESS_COUNT / $TOTAL_TESTS"

if [[ $SUCCESS_COUNT -eq $TOTAL_TESTS ]]; then
    echo -e "Status: ${GREEN}ALL TESTS PASSED${NC}"
    echo ""
    echo "✅ Seed1 deployment appears successful!"
    echo "✅ Ready for Phase 2: Validator configuration"
    exit 0
elif [[ $SUCCESS_COUNT -ge $((TOTAL_TESTS * 2 / 3)) ]]; then
    echo -e "Status: ${YELLOW}MOSTLY SUCCESSFUL${NC}"
    echo ""
    echo "⚠️  Some issues detected but deployment may be functional"
    echo "⚠️  Review failed tests and resolve before proceeding"
    exit 1
else
    echo -e "Status: ${RED}DEPLOYMENT ISSUES${NC}"
    echo ""
    echo "❌ Significant issues detected"
    echo "❌ Review installation and resolve issues before proceeding"
    exit 2
fi