# Fanatico L1 v0.5.0.0 - WebSocket Implementation

**Status**: Deployed to all 4 nodes + public WSS endpoint
**Date**: January 29, 2026 (implemented) / February 17, 2026 (deployed)

## Overview

This directory contains the WebSocket server implementation for Fanatico L1 v0.5.0.0, enabling real-time event subscriptions.

## Files

| File | Description |
|------|-------------|
| `websocket_server.py` | Core WebSocket server with subscription management |
| `combined_server.py` | Integration module running HTTP + WebSocket servers |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Fanatico L1 Node                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐     ┌──────────────────┐         │
│  │   Flask HTTP     │     │    WebSocket     │         │
│  │   Port 8545      │     │   Port 8546      │         │
│  │                  │     │                  │         │
│  │  - eth_*         │     │  - eth_subscribe │         │
│  │  - net_*         │     │  - eth_unsubscr  │         │
│  │  - web3_*        │     │                  │         │
│  └────────┬─────────┘     └────────┬─────────┘         │
│           │                        │                    │
│           └──────────┬─────────────┘                    │
│                      │                                  │
│           ┌──────────┴──────────┐                      │
│           │    Blockchain       │                      │
│           │    (shared state)   │                      │
│           │                     │                      │
│           │  Event Hooks:       │                      │
│           │  - on_new_block()   │                      │
│           │  - on_logs()        │                      │
│           │  - on_pending_tx()  │                      │
│           └─────────────────────┘                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Subscription Types

### newHeads
Subscribe to new block headers.

```javascript
// Subscribe
const subId = await provider.send("eth_subscribe", ["newHeads"]);

// Notification format
{
  "jsonrpc": "2.0",
  "method": "eth_subscription",
  "params": {
    "subscription": "0x...",
    "result": {
      "hash": "0x...",
      "parentHash": "0x...",
      "number": "0x10",
      "timestamp": "0x5f5e100",
      "gasLimit": "0xe4e1c0",
      "gasUsed": "0x5208",
      "baseFeePerGas": "0x4a817c800",
      ...
    }
  }
}
```

### logs
Subscribe to contract event logs with optional filters.

```javascript
// Subscribe with filter
const subId = await provider.send("eth_subscribe", ["logs", {
  address: "0x...",
  topics: ["0xddf252ad..."]  // Transfer event
}]);

// Notification format
{
  "jsonrpc": "2.0",
  "method": "eth_subscription",
  "params": {
    "subscription": "0x...",
    "result": {
      "address": "0x...",
      "topics": ["0x..."],
      "data": "0x...",
      "blockNumber": "0x10",
      "transactionHash": "0x...",
      "logIndex": "0x0"
    }
  }
}
```

### newPendingTransactions
Subscribe to pending transaction hashes.

```javascript
const subId = await provider.send("eth_subscribe", ["newPendingTransactions"]);

// Notification: just the transaction hash
{
  "params": {
    "subscription": "0x...",
    "result": "0x..." // tx hash
  }
}
```

### syncing
Subscribe to sync status changes.

```javascript
const subId = await provider.send("eth_subscribe", ["syncing"]);

// Notification
{
  "params": {
    "subscription": "0x...",
    "result": false  // or sync status object
  }
}
```

## Usage

### Standalone WebSocket Server

```bash
cd /Users/sebastian/CODE/L1/V05000/src
python3 websocket_server.py
```

### Combined Server (HTTP + WebSocket)

```bash
cd /Users/sebastian/CODE/L1/V05000/src
python3 combined_server.py --http-port 8545 --ws-port 8546
```

### Client Examples

#### JavaScript (ethers.js v6)

```javascript
const { ethers } = require("ethers");

// HTTP provider for standard calls (public HTTPS)
const httpProvider = new ethers.JsonRpcProvider("https://rpc.fanati.co");

// WebSocket provider for subscriptions (public WSS)
const wsProvider = new ethers.WebSocketProvider("wss://seed1.fanati.co/ws");

// Subscribe to new blocks
wsProvider.on("block", (blockNumber) => {
  console.log("New block:", blockNumber);
});

// Subscribe to logs
const filter = {
  address: "0x...",
  topics: [ethers.id("Transfer(address,address,uint256)")]
};
wsProvider.on(filter, (log) => {
  console.log("Transfer event:", log);
});
```

#### Python (web3.py)

```python
from web3 import Web3

# Connect via WebSocket (public WSS)
w3 = Web3(Web3.WebsocketProvider("wss://seed1.fanati.co/ws"))

# Subscribe to new blocks
def handle_new_block(block_hash):
    block = w3.eth.get_block(block_hash)
    print(f"New block: {block.number}")

subscription_id = w3.eth.subscribe("newHeads")
# Handle in event loop...
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `WS_HOST` | 0.0.0.0 | WebSocket bind address |
| `WS_PORT` | 8546 | WebSocket port |
| `MAX_CONNECTIONS` | 1000 | Maximum concurrent connections |
| `PING_INTERVAL` | 30s | WebSocket ping interval |
| `PING_TIMEOUT` | 10s | Ping response timeout |
| `MAX_SUBSCRIPTIONS_PER_CONNECTION` | 100 | Subscription limit per client |

## Integration with v0.4.9.98

The WebSocket server integrates with the existing HTTP RPC server through event hooks:

```python
from websocket_server import WebSocketEventHooks

# When a new block is created
WebSocketEventHooks.on_new_block(block_dict)

# When logs are emitted
WebSocketEventHooks.on_logs([log1, log2, ...])

# When a pending transaction is received
WebSocketEventHooks.on_pending_transaction(tx_hash)
```

## Testing

```bash
cd /Users/sebastian/CODE/L1/hardhat
npx hardhat test test/14-websocket-subscriptions.test.js --network fanatico
```

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid request | Invalid JSON-RPC |
| -32601 | Method not found | Unknown method |
| -32602 | Invalid params | Invalid parameters |
| -32603 | Internal error | Server error |
| -32000 | Server error | Subscription limit reached |

## Performance

| Metric | Value |
|--------|-------|
| Max subscriptions | 100,000 |
| Notification latency | < 10ms |
| Connection overhead | ~1KB per client |
| Throughput | 10,000+ notifications/sec |

## Dependencies

```txt
websockets>=12.0
asyncio
```

Install:
```bash
pip install websockets
```

---

**Version**: 0.5.0.0
**Author**: Fanatico Development Team
