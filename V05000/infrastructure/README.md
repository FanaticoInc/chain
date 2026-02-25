# Fanatico L1 v0.5.0.0 - High Availability Infrastructure

**Status**: Configuration Complete
**Date**: January 29, 2026

## Overview

This directory contains all configuration files and deployment scripts for setting up a highly available Fanatico L1 infrastructure.

## Architecture

```
                         Internet
                            │
                    ┌───────┴───────┐
                    │   CloudFlare  │
                    │     (DDoS)    │
                    └───────┬───────┘
                            │
               ┌────────────┴────────────┐
               │                         │
        ┌──────┴──────┐           ┌──────┴──────┐
        │  HAProxy 1  │◄─────────▶│  HAProxy 2  │
        │  (Primary)  │ Keepalive │  (Standby)  │
        │  VIP: .100  │           │             │
        └──────┬──────┘           └──────┬──────┘
               │                         │
    ┌──────────┼──────────┬──────────────┼──────────┐
    │          │          │              │          │
┌───┴───┐  ┌───┴───┐  ┌───┴───┐    ┌─────┴─────┐   │
│ RPC 1 │  │ RPC 2 │  │ RPC 3 │    │ WebSocket │   │
│ :8545 │  │ :8545 │  │ :8545 │    │   :8546   │   │
└───┬───┘  └───┬───┘  └───┬───┘    └─────┬─────┘   │
    │          │          │              │         │
    └──────────┴──────────┴──────────────┘         │
               │                                    │
        ┌──────┴──────┐                            │
        │   Patroni   │                            │
        │   Cluster   │                            │
        └──────┬──────┘                            │
               │                                    │
    ┌──────────┼──────────┐                        │
    │          │          │                        │
┌───┴───┐  ┌───┴───┐  ┌───┴───┐              ┌────┴────┐
│ DB 1  │  │ DB 2  │  │ DB 3  │              │  etcd   │
│Primary│  │Replica│  │Replica│              │ Cluster │
└───────┘  └───────┘  └───────┘              └─────────┘
```

## Components

### 1. HAProxy (Load Balancer)
- **Purpose**: Load balancing for RPC, WebSocket, and PostgreSQL
- **Nodes**: 2 (active/standby with Keepalived)
- **Ports**: 8545 (HTTP), 8546 (WebSocket), 5432 (PostgreSQL primary), 5433 (PostgreSQL read replicas)

### 2. Keepalived (VRRP Failover)
- **Purpose**: Virtual IP failover for HAProxy
- **Virtual IP**: 10.0.0.100
- **Failover Time**: < 3 seconds

### 3. Patroni (PostgreSQL HA)
- **Purpose**: PostgreSQL high availability and automatic failover
- **Nodes**: 3 (1 primary, 2 replicas)
- **Failover Time**: < 30 seconds

### 4. etcd (Distributed Configuration)
- **Purpose**: Configuration store for Patroni cluster
- **Nodes**: 3 (quorum-based)

## Directory Structure

```
infrastructure/
├── README.md                    # This file
├── patroni/
│   └── patroni.yml             # Patroni configuration template
├── haproxy/
│   └── haproxy.cfg             # HAProxy configuration
├── etcd/
│   └── etcd.conf.yml           # etcd configuration template
├── keepalived/
│   └── keepalived.conf         # Keepalived configuration
└── scripts/
    ├── setup-etcd-node.sh      # etcd node setup
    ├── setup-patroni-node.sh   # Patroni node setup
    └── setup-haproxy-node.sh   # HAProxy + Keepalived setup
```

## Deployment Order

### Phase 1: etcd Cluster (3 nodes)

```bash
# On each etcd node (10.0.3.10, 10.0.3.11, 10.0.3.12)
./scripts/setup-etcd-node.sh etcd1 10.0.3.10
./scripts/setup-etcd-node.sh etcd2 10.0.3.11
./scripts/setup-etcd-node.sh etcd3 10.0.3.12

# Start all nodes simultaneously
systemctl start etcd

# Verify cluster
etcdctl endpoint health --cluster
etcdctl member list
```

### Phase 2: Patroni Cluster (3 nodes)

```bash
# Copy template to nodes
scp patroni/patroni.yml db1:/etc/patroni/patroni.yml.template
scp patroni/patroni.yml db2:/etc/patroni/patroni.yml.template
scp patroni/patroni.yml db3:/etc/patroni/patroni.yml.template

# On each Patroni node (10.0.2.10, 10.0.2.11, 10.0.2.12)
./scripts/setup-patroni-node.sh db1 10.0.2.10
./scripts/setup-patroni-node.sh db2 10.0.2.11
./scripts/setup-patroni-node.sh db3 10.0.2.12

# Start first node (becomes primary)
systemctl start patroni

# Start other nodes (become replicas)
systemctl start patroni

# Verify cluster
patronictl -c /etc/patroni/patroni.yml list
```

### Phase 3: HAProxy + Keepalived (2 nodes)

```bash
# On primary HAProxy node (10.0.0.10)
./scripts/setup-haproxy-node.sh primary 10.0.0.10 10.0.0.11

# On backup HAProxy node (10.0.0.11)
./scripts/setup-haproxy-node.sh backup 10.0.0.11 10.0.0.10

# Update haproxy.cfg with actual backend IPs
# Start services
systemctl start haproxy
systemctl start keepalived

# Verify
ip addr show eth0  # Check for VIP
curl http://10.0.0.100:8545/health
```

## Configuration Templates

### Environment Variables

Set these before running setup scripts:

```bash
# etcd
export CLUSTER_TOKEN="fanatico-etcd-cluster-2026"

# Patroni
export PATRONI_REST_PASSWORD="secure-password"
export POSTGRES_ADMIN_PASSWORD="secure-password"
export POSTGRES_REPLICATOR_PASSWORD="secure-password"
export POSTGRES_FANATICO_PASSWORD="secure-password"
export POSTGRES_SUPERUSER_PASSWORD="secure-password"
export POSTGRES_REWIND_PASSWORD="secure-password"
export ETCD_HOSTS="10.0.3.10:2379,10.0.3.11:2379,10.0.3.12:2379"

# HAProxy + Keepalived
export HAPROXY_STATS_PASSWORD="secure-password"
export KEEPALIVED_AUTH_PASS="secure-password"
```

## IP Address Plan

| Component | Node | IP Address |
|-----------|------|------------|
| HAProxy Primary | haproxy1 | 10.0.0.10 |
| HAProxy Backup | haproxy2 | 10.0.0.11 |
| Virtual IP (VIP) | - | 10.0.0.100 |
| RPC Node 1 | rpc1 | 10.0.1.10 |
| RPC Node 2 | rpc2 | 10.0.1.11 |
| RPC Node 3 | rpc3 | 10.0.1.12 |
| PostgreSQL 1 | db1 | 10.0.2.10 |
| PostgreSQL 2 | db2 | 10.0.2.11 |
| PostgreSQL 3 | db3 | 10.0.2.12 |
| etcd 1 | etcd1 | 10.0.3.10 |
| etcd 2 | etcd2 | 10.0.3.11 |
| etcd 3 | etcd3 | 10.0.3.12 |

## Ports

| Service | Port | Protocol | Access |
|---------|------|----------|--------|
| RPC HTTP | 8545 | TCP | Public (via VIP) |
| RPC WebSocket | 8546 | TCP | Public (via VIP) |
| HAProxy Stats | 8404 | TCP | Internal |
| PostgreSQL Primary | 5432 | TCP | Internal (via VIP) |
| PostgreSQL Read | 5433 | TCP | Internal (via VIP) |
| Patroni REST API | 8008 | TCP | Internal |
| etcd Client | 2379 | TCP | Internal |
| etcd Peer | 2380 | TCP | Internal |
| etcd Metrics | 2381 | TCP | Internal |

## Health Checks

### HAProxy
```bash
# Stats page
curl http://10.0.0.100:8404/stats

# RPC health
curl http://10.0.0.100:8545/health
```

### Patroni
```bash
# Cluster status
patronictl -c /etc/patroni/patroni.yml list

# Node status
curl http://10.0.2.10:8008/
curl http://10.0.2.10:8008/primary
curl http://10.0.2.10:8008/replica
```

### etcd
```bash
# Cluster health
etcdctl endpoint health --cluster

# Member list
etcdctl member list

# Cluster status
etcdctl endpoint status --cluster -w table
```

## Failover Testing

### HAProxy Failover
```bash
# On primary HAProxy
systemctl stop haproxy

# Watch VIP move to backup
# On backup node
ip addr show eth0

# Verify RPC still works
curl http://10.0.0.100:8545/health
```

### PostgreSQL Failover
```bash
# Check current primary
patronictl -c /etc/patroni/patroni.yml list

# Force failover
patronictl -c /etc/patroni/patroni.yml switchover

# Verify new primary
patronictl -c /etc/patroni/patroni.yml list
```

## Monitoring Integration

Metrics endpoints for Prometheus:
- HAProxy: `http://haproxy:8404/metrics`
- Patroni: `http://patroni:8008/metrics`
- etcd: `http://etcd:2381/metrics`

## Troubleshooting

### HAProxy not starting
```bash
haproxy -c -f /etc/haproxy/haproxy.cfg  # Config check
journalctl -u haproxy -f                 # View logs
```

### Patroni not connecting to etcd
```bash
etcdctl endpoint health --cluster        # Check etcd
journalctl -u patroni -f                 # View logs
```

### VIP not floating
```bash
journalctl -u keepalived -f              # View logs
ip addr show                             # Check interfaces
tcpdump -i eth0 vrrp                     # Check VRRP traffic
```

## Recovery Procedures

### Recover from total etcd failure
1. Stop all Patroni nodes
2. Restore etcd from backup or reinitialize
3. Start etcd cluster
4. Start Patroni nodes (primary first)

### Recover PostgreSQL from backup
```bash
# On new primary node
patronictl -c /etc/patroni/patroni.yml reinit <node-name>
```

---

**Version**: 0.5.0.0
**Author**: Fanatico Development Team
