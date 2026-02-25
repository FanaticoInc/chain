#!/bin/bash
echo "======================================================================"
echo "RPC ENDPOINT DIAGNOSTIC"
echo "======================================================================"
echo ""

RPC_URL="http://paratime.fanati.co:8545"

echo "Testing basic methods on $RPC_URL"
echo ""

# Test 1: Chain ID
echo "1. eth_chainId:"
curl -s -X POST $RPC_URL -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' | jq .
echo ""

# Test 2: Block Number  
echo "2. eth_blockNumber:"
curl -s -X POST $RPC_URL -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' | jq .
echo ""

# Test 3: Get Balance (known to be broken)
echo "3. eth_getBalance:"
curl -s -X POST $RPC_URL -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x70997970C51812dc3A010C7d01b50e0d17dc79C8","latest"],"id":1}' | jq .
echo ""

# Test 4: Get Transaction Count (known to be broken)
echo "4. eth_getTransactionCount:"
curl -s -X POST $RPC_URL -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getTransactionCount","params":["0x70997970C51812dc3A010C7d01b50e0d17dc79C8","latest"],"id":1}' | jq .
echo ""

# Test 5: Get Block By Number (known to not exist)
echo "5. eth_getBlockByNumber:"
curl -s -X POST $RPC_URL -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",false],"id":1}' | jq .
echo ""

echo "======================================================================"
echo "SUMMARY"
echo "======================================================================"
echo "Based on these results:"
echo "- If methods return errors: Server is broken/partially deployed"
echo "- If methods work: Need to test transaction receipt structure"
