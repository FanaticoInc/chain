# Blockscout Block Explorer Deployment Guide

## Overview

Blockscout is an open-source block explorer for EVM-compatible blockchains. This guide documents the deployment of Blockscout for the Fanatico L1 blockchain.

**Production URL:** https://explorer.fanati.co
**Server:** seed2.fanati.co (188.245.85.247)
**Chain ID:** 11111111111 (0x2964619c7)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     seed2.fanati.co                         │
│                                                             │
│  ┌─────────────┐     ┌─────────────────────────────────┐   │
│  │   nginx     │────▶│     Blockscout Docker Stack     │   │
│  │  (SSL/443)  │     │                                 │   │
│  └─────────────┘     │  ┌─────────┐  ┌─────────────┐  │   │
│        │             │  │ frontend│  │   backend   │  │   │
│        │             │  │  :3000  │  │    :4000    │  │   │
│        ▼             │  └─────────┘  └─────────────┘  │   │
│  ┌─────────────┐     │       │              │         │   │
│  │ Let's       │     │       ▼              ▼         │   │
│  │ Encrypt     │     │  ┌─────────────────────────┐   │   │
│  │ Certs       │     │  │      PostgreSQL         │   │   │
│  └─────────────┘     │  │        :5432            │   │   │
│                      │  └─────────────────────────┘   │   │
│                      └─────────────────────────────────┘   │
│                                    │                       │
│                                    ▼                       │
│                      ┌─────────────────────────┐           │
│                      │   Fanatico L1 RPC       │           │
│                      │  https://rpc.fanati.co  │           │
│                      └─────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- Docker and Docker Compose installed
- Domain with DNS pointing to server
- SSL certificates (Let's Encrypt via certbot)
- Access to Fanatico L1 RPC endpoint

---

## Directory Structure

```
/opt/blockscout/
├── docker-compose/
│   ├── docker-compose.yml          # Main compose file
│   ├── envs/
│   │   └── common-blockscout.env   # Environment variables
│   └── services/
│       ├── nginx.yml               # nginx proxy service
│       └── ...
└── data/
    └── postgres/                   # PostgreSQL data
```

---

## Installation

### 1. Clone Blockscout Repository

```bash
cd /opt
git clone https://github.com/blockscout/blockscout.git
cd blockscout/docker-compose
```

### 2. Configure Environment Variables

Edit `/opt/blockscout/docker-compose/envs/common-blockscout.env`:

```bash
# Chain Configuration
ETHEREUM_JSONRPC_HTTP_URL=https://rpc.fanati.co
ETHEREUM_JSONRPC_TRACE_URL=https://rpc.fanati.co
ETHEREUM_JSONRPC_WS_URL=wss://rpc.fanati.co
CHAIN_ID=11111111111

# Network Display
CHAIN_TYPE=ethereum
SUBNETWORK=Fanatico
NETWORK=Fanatico L1
NETWORK_ICON=_network_icon.html

# Coin Configuration
COIN=FCO
COIN_NAME=Fanatico

# Database
DATABASE_URL=postgresql://blockscout:blockscout@db:5432/blockscout

# API Configuration
API_V2_ENABLED=true
DISABLE_EXCHANGE_RATES=true

# Block Configuration
BLOCK_TRANSFORMER=base
FIRST_BLOCK=0
TRACE_FIRST_BLOCK=0

# Indexer Settings
INDEXER_DISABLE_INTERNAL_TRANSACTIONS_FETCHER=true
INDEXER_DISABLE_PENDING_TRANSACTIONS_FETCHER=true
```

### 3. Configure Docker Compose

Edit `/opt/blockscout/docker-compose/docker-compose.yml`:

```yaml
version: '3.9'

services:
  db:
    image: postgres:14
    restart: always
    environment:
      POSTGRES_PASSWORD: blockscout
      POSTGRES_USER: blockscout
      POSTGRES_DB: blockscout
    volumes:
      - /opt/blockscout/data/postgres:/var/lib/postgresql/data

  backend:
    image: blockscout/blockscout:latest
    restart: always
    depends_on:
      - db
    env_file:
      - ./envs/common-blockscout.env
    environment:
      ETHEREUM_JSONRPC_HTTP_URL: https://rpc.fanati.co
      ETHEREUM_JSONRPC_TRACE_URL: https://rpc.fanati.co
      ETHEREUM_JSONRPC_WS_URL: wss://rpc.fanati.co
      CHAIN_ID: '11111111111'

  frontend:
    image: ghcr.io/blockscout/frontend:latest
    restart: always
    depends_on:
      - backend
    environment:
      NEXT_PUBLIC_API_HOST: localhost
      NEXT_PUBLIC_API_BASE_PATH: /
      NEXT_PUBLIC_NETWORK_NAME: Fanatico
      NEXT_PUBLIC_NETWORK_SHORT_NAME: FCO
      NEXT_PUBLIC_NETWORK_ID: 11111111111

  proxy:
    extends:
      file: ./services/nginx.yml
      service: proxy
    depends_on:
      - frontend
      - backend
```

### 4. Configure nginx Proxy Service

Edit `/opt/blockscout/docker-compose/services/nginx.yml`:

```yaml
version: '3.9'

services:
  proxy:
    image: nginx:alpine
    restart: always
    ports:
      - "8000:80"    # Changed from 80 to allow host nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

**Note:** Port 8000 is used because host nginx handles SSL on port 443.

---

## Host nginx Configuration

### SSL Configuration

Create `/etc/nginx/sites-available/explorer.fanati.co`:

```nginx
server {
    listen 80;
    server_name explorer.fanati.co;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name explorer.fanati.co;

    ssl_certificate /etc/letsencrypt/live/explorer.fanati.co/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/explorer.fanati.co/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 90;
    }
}
```

### Enable Site

```bash
ln -s /etc/nginx/sites-available/explorer.fanati.co /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Obtain SSL Certificate

```bash
certbot --nginx -d explorer.fanati.co
```

---

## Starting the Explorer

### Start All Services

```bash
cd /opt/blockscout/docker-compose
docker compose up -d
```

### Check Status

```bash
docker compose ps
docker compose logs -f backend
```

### Restart After Configuration Changes

```bash
docker compose down
docker compose up -d
```

---

## Troubleshooting

### 502 Bad Gateway

**Cause:** Backend or proxy container not running or DNS cache stale.

**Solution:**
```bash
# Check container status
docker compose ps

# Restart proxy to clear DNS cache
docker compose restart proxy

# Check backend logs
docker compose logs backend
```

### Blocks Not Syncing

**Cause:** Incorrect RPC URL or Chain ID in docker-compose.yml.

**Solution:**
1. Verify environment variables in docker-compose.yml (not just .env file)
2. Ensure RPC endpoint is accessible:
   ```bash
   curl -X POST https://rpc.fanati.co \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
   ```
3. Restart backend:
   ```bash
   docker compose restart backend
   ```

### Database Connection Issues

**Cause:** PostgreSQL container not ready or data corruption.

**Solution:**
```bash
# Check database container
docker compose logs db

# Reset database (WARNING: loses indexed data)
docker compose down
rm -rf /opt/blockscout/data/postgres/*
docker compose up -d
```

### Frontend Not Loading

**Cause:** Frontend container crashed or API misconfiguration.

**Solution:**
```bash
# Check frontend logs
docker compose logs frontend

# Verify API connection
curl http://localhost:4000/api/v2/blocks

# Restart frontend
docker compose restart frontend
```

---

## Maintenance

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

### Update Blockscout

```bash
cd /opt/blockscout/docker-compose
docker compose pull
docker compose down
docker compose up -d
```

### Backup Database

```bash
docker compose exec db pg_dump -U blockscout blockscout > blockscout_backup.sql
```

### Restore Database

```bash
cat blockscout_backup.sql | docker compose exec -T db psql -U blockscout blockscout
```

---

## Configuration Reference

### Required Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| ETHEREUM_JSONRPC_HTTP_URL | https://rpc.fanati.co | L1 RPC endpoint |
| ETHEREUM_JSONRPC_TRACE_URL | https://rpc.fanati.co | Trace RPC endpoint |
| CHAIN_ID | 11111111111 | Fanatico L1 Chain ID |
| COIN | FCO | Native token symbol |
| NETWORK | Fanatico L1 | Network display name |

### Port Mapping

| Service | Internal Port | External Port | Purpose |
|---------|---------------|---------------|---------|
| frontend | 3000 | - | Web UI |
| backend | 4000 | - | API |
| proxy | 80 | 8000 | nginx reverse proxy |
| db | 5432 | - | PostgreSQL |

---

## Verification

### Check Explorer Status

```bash
# Via browser
open https://explorer.fanati.co

# Via API
curl https://explorer.fanati.co/api/v2/stats
```

### Verify Block Indexing

```bash
curl https://explorer.fanati.co/api/v2/blocks | jq '.items[0]'
```

### Check RPC Connectivity

```bash
curl -X POST https://rpc.fanati.co \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
# Expected: {"result":"0x2964619c7"}
```

---

## Related Documentation

- [Fanatico L1 CLAUDE.md](../CLAUDE.md) - Main L1 project documentation
- [Oasis Sapphire Testnet](./OASIS_SAPPHIRE_TESTNET_REQUIREMENTS.md) - Testnet setup
- [Blockscout Official Docs](https://docs.blockscout.com/)

---

**Last Updated:** January 31, 2026
**Deployed On:** seed2.fanati.co (188.245.85.247)
