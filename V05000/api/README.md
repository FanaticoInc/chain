# FCO Token Metrics API

REST API service for Fanatico L1 FCO token metrics. Provides endpoints compatible with secret-token.com.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /api/info/prices` | Price aggregation from CEX/DEX |
| `GET /api/info/stat/metrics` | All token metrics |
| `GET /api/info/stat/metrics/total-supply` | Current total supply |
| `GET /api/info/stat/metrics/max-supply` | Maximum supply (20B) |
| `GET /api/info/stat/metrics/total-circulation` | Circulating supply |
| `GET /api/info/stat/metrics/total-mint` | Total minted tokens |
| `GET /api/info/stat/metrics/total-burn` | Total burned tokens |
| `GET /api/info/contract` | Contract addresses |

## Contract Addresses

| Contract | Address |
|----------|---------|
| Authority | `0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2` |
| FCO Token | `0xd6F8Ff0036D8B2088107902102f9415330868109` |

## Quick Start

### Local Development

```bash
npm install
npm start
```

### Docker

```bash
docker-compose up -d
```

### Test Endpoints

```bash
# Health check
curl http://localhost:3001/health

# Get all metrics
curl http://localhost:3001/api/info/stat/metrics

# Get total supply
curl http://localhost:3001/api/info/stat/metrics/total-supply

# Get prices
curl http://localhost:3001/api/info/prices
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3001 | API server port |
| `RPC_URL` | http://paratime.fanati.co:8545 | Fanatico L1 RPC endpoint |
| `AUTHORITY_ADDRESS` | 0xed4E... | Authority contract address |
| `FCO_ADDRESS` | 0xd6F8... | FCO token contract address |

## Response Examples

### GET /api/info/stat/metrics

```json
{
  "token": {
    "name": "Fanatico",
    "symbol": "sFCO",
    "decimals": 2,
    "address": "0xd6F8Ff0036D8B2088107902102f9415330868109"
  },
  "supply": {
    "total": 0,
    "max": 20000000000,
    "circulation": 0,
    "burned": 0
  },
  "epoch": {
    "current": 1769990400,
    "duration": 86400,
    "lockDuration": 2592000
  },
  "chain": {
    "id": 11111111111,
    "rpc": "http://paratime.fanati.co:8545",
    "ethReserve": "0"
  },
  "timestamp": "2026-02-02T12:00:00.000Z"
}
```

### GET /api/info/prices

```json
{
  "usd_fco_l1": 0,
  "usd_fco_cex_lbank": 0.0627,
  "usdt_fco_dex_uniswap": 0.28,
  "timestamp": "2026-02-02T12:00:00.000Z"
}
```

## Deployment

### On paratime.fanati.co

```bash
# Copy files
scp -r /Users/sebastian/CODE/L1/V05000/api claude@paratime.fanati.co:/home/claude/fco-metrics-api/

# SSH and start
ssh claude@paratime.fanati.co
cd /home/claude/fco-metrics-api
docker-compose up -d
```

## Related

- [FCO Token Contract](../hardhat/contracts/devteam/FCO.sol)
- [Authority Contract](../hardhat/contracts/devteam/AccessControl.sol)
- [CLAUDE.md](../../CLAUDE.md)

---

**Version:** 1.0.0
**Chain ID:** 11111111111
**Last Updated:** February 2026
