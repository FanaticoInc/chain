# Fanatico L1 v0.5.0.0-rc1 Deployment Runbook

**Version**: v0.5.0.0-rc1
**Date**: February 17, 2026
**Author**: Claude (automated deployment)

## Architecture

```
                    ┌─────────────────┐
                    │   rpc.fanati.co │  (HTTPS, nginx reverse proxy)
                    │   paratime      │
                    │   :8545 + :8546 │  Authority node (writes)
                    └────────┬────────┘
                             │ SCP every 10 min
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────┴──────┐ ┌────┴──────────┐ ┌─┴──────────────────┐
    │  consensus1    │ │  consensus2   │ │     seed1           │
    │ 95.217.47.102  │ │ 95.216.243.184│ │ 138.201.16.186      │
    │ :8545 + :8546  │ │ :8545 + :8546 │ │ :8545 + :8546       │
    └────────────────┘ └───────────────┘ │ seed1.fanati.co     │
                                         │ HTTPS:443 + WSS /ws │
                                         └─────────────────────┘
         Read replica       Read replica      Read replica (public)
```

## Prerequisites

- SSH access as `claude` user to target node
- Python 3.10+ on target
- `pip3 install flask pycryptodome web3 websockets` on target

## Deploy a New Replica Node

### 1. Install dependencies

```bash
ssh <node> "pip3 install flask pycryptodome web3 websockets"
```

### 2. Create directory and copy files

```bash
ssh <node> "mkdir -p /home/claude/fanatico-l1"
scp /Users/sebastian/CODE/L1/V04998/web3_api_v04998.py <node>:/home/claude/fanatico-l1/
scp /tmp/fanatico_ws_server.py <node>:/home/claude/fanatico-l1/websocket_server.py
```

### 3. Copy database from paratime

```bash
ssh paratime "scp /home/claude/fco_blockchain_v04963.db <node>:/home/claude/fanatico-l1/fco_blockchain.db"
```

### 4. Create management script

Deploy `manage.sh` to `/home/claude/fanatico-l1/manage.sh` (see existing nodes for reference):

```bash
scp consensus1:/home/claude/fanatico-l1/manage.sh <node>:/home/claude/fanatico-l1/
ssh <node> "chmod +x /home/claude/fanatico-l1/manage.sh"
```

### 5. Start services

```bash
ssh <node> "/home/claude/fanatico-l1/manage.sh start"
```

### 6. Verify

```bash
# HTTP RPC
curl -s http://<node-ip>:8545 -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":1}'

# WebSocket
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://<node-ip>:8546') as ws:
        await ws.send(json.dumps({'jsonrpc':'2.0','method':'eth_subscribe','params':['newHeads'],'id':1}))
        print(await ws.recv())
asyncio.run(test())
"
```

### 7. Add to paratime DB sync

On paratime, add to crontab:
```bash
*/10 * * * * scp /home/claude/fco_blockchain_v04963.db <node>:/home/claude/fanatico-l1/fco_blockchain.db 2>/dev/null
```

### 8. Set up auto-restart

On the new node, add to crontab:
```bash
@reboot cd /home/claude/fanatico-l1 && /home/claude/fanatico-l1/manage.sh start
*/5 * * * * /home/claude/fanatico-l1/manage.sh start 2>/dev/null
```

## Operations

### Check status (all nodes)

```bash
for node in paratime consensus1 consensus2 seed1; do
  echo "=== $node ==="
  ssh $node "/home/claude/fanatico-l1/manage.sh status" 2>/dev/null || \
  ssh $node "curl -s http://localhost:8545 -X POST -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"method\":\"eth_blockNumber\",\"params\":[],\"id\":1}' 2>/dev/null | python3 -c 'import sys,json; print(\"Block:\", int(json.load(sys.stdin)[\"result\"],16))' 2>/dev/null || echo 'UNREACHABLE'"
done
```

### Restart a node

```bash
ssh <node> "/home/claude/fanatico-l1/manage.sh stop && sleep 2 && /home/claude/fanatico-l1/manage.sh start"
```

### View logs

```bash
ssh <node> "/home/claude/fanatico-l1/manage.sh logs"
```

### Rolling restart (zero downtime)

Restart replicas one at a time, waiting for each to come back:
```bash
for node in consensus1 consensus2 seed1; do
  echo "Restarting $node..."
  ssh $node "/home/claude/fanatico-l1/manage.sh stop"
  sleep 5
  ssh $node "/home/claude/fanatico-l1/manage.sh start"
  sleep 10
  # Verify
  ssh $node "curl -s http://localhost:8545 -X POST -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"method\":\"eth_blockNumber\",\"params\":[],\"id\":1}'" | python3 -c "import sys,json; print('OK - Block:', int(json.load(sys.stdin)['result'],16))"
  echo "---"
done
```

## File Locations

| File | Paratime | Replicas |
|------|----------|----------|
| API source | `/opt/web3-evm-v030/web3_api_v04998.py` | `/home/claude/fanatico-l1/web3_api_v04998.py` |
| WebSocket | `/home/claude/websocket_server.py` | `/home/claude/fanatico-l1/websocket_server.py` |
| Database | `/home/claude/fco_blockchain_v04963.db` | `/home/claude/fanatico-l1/fco_blockchain.db` |
| Management | N/A (systemd) | `/home/claude/fanatico-l1/manage.sh` |
| Logs | journalctl | `nohup.out` in working directory |

## Security

- Rate limiting: 100 requests/minute per IP (HTTP 429 on exceed)
- CSP headers: `default-src 'none'; frame-ancestors 'none'`
- Structured JSON access logging on all nodes
- Ports bound to localhost (8545) or firewalled (8546) on replicas
- Public HTTPS access via:
  - **rpc.fanati.co** (nginx + SSL on paratime) — HTTP RPC only
  - **seed1.fanati.co** (nginx + Let's Encrypt on seed1) — HTTP RPC + WSS
- SSL auto-renewal: certbot timer on seed1 (cert expires 2026-05-18)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API not responding | `manage.sh stop && manage.sh start` |
| Stale block data | Check paratime SCP crontab, verify DB file timestamp |
| WebSocket not connecting | Check port 8546 is open, verify process running |
| Rate limit hit | Wait 60s or check from different IP |
| DB locked | Stop all processes, restart. Single-writer SQLite limitation |
