#!/bin/bash

echo "Testing eth_estimateGas endpoint"
echo "================================"
echo ""

curl -s -X POST http://paratime.fanati.co:8545 \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_estimateGas\",\"params\":[{\"from\":\"0x70997970C51812dc3A010C7d01b50e0d17dc79C8\",\"to\":\"0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC\",\"value\":\"0xde0b6b3a7640000\"}],\"id\":1}" | jq .
