# Fanatico L1 Monitoring Stack
## v0.5.0.0 - January 29, 2026

Production-grade monitoring infrastructure for Fanatico L1 blockchain using Prometheus, Grafana, and AlertManager.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Monitoring Infrastructure                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐                 │
│  │   Grafana   │◄───│ Prometheus  │◄───│ AlertManager    │                 │
│  │   :3000     │    │   :9090     │    │     :9093       │                 │
│  └─────────────┘    └──────┬──────┘    └────────┬────────┘                 │
│                            │                     │                          │
│        ┌───────────────────┼───────────────────┬─┘                          │
│        ▼                   ▼                   ▼                            │
│  ┌───────────┐      ┌───────────┐      ┌─────────────────┐                 │
│  │ Slack     │      │ PagerDuty │      │ Email           │                 │
│  │ Channels  │      │ Incidents │      │ Notifications   │                 │
│  └───────────┘      └───────────┘      └─────────────────┘                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              Scrape Targets                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  RPC Nodes      │  │  PostgreSQL     │  │  etcd Cluster   │             │
│  │  :9545          │  │  :9187          │  │  :2381          │             │
│  │  (x3)           │  │  (x3)           │  │  (x3)           │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  Patroni        │  │  HAProxy        │  │  Node Exporter  │             │
│  │  :8008          │  │  :8404          │  │  :9100          │             │
│  │  (x3)           │  │  (x2)           │  │  (all hosts)    │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                                   │
│  │  Fanatico       │  │  Blackbox       │                                   │
│  │  Exporter :9546 │  │  Exporter :9115 │                                   │
│  └─────────────────┘  └─────────────────┘                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Prometheus (`prometheus/`)

Central metrics collection and storage.

**Configuration**: `prometheus/prometheus.yml`
- Scrape interval: 15s
- Evaluation interval: 15s
- External labels: cluster=fanatico-l1, env=production

**Scrape Jobs**:
| Job | Targets | Port | Description |
|-----|---------|------|-------------|
| fanatico-rpc | rpc1-3.internal | 9545 | RPC node metrics |
| fanatico-rpc-health | rpc1-3.internal | 8545 | HTTP health probes |
| patroni | db1-3.internal | 8008 | Patroni cluster metrics |
| postgres | db1-3.internal | 9187 | PostgreSQL metrics |
| etcd | etcd1-3.internal | 2381 | etcd cluster metrics |
| haproxy | haproxy1-2.internal | 8404 | Load balancer metrics |
| node | all hosts | 9100 | System metrics |
| redis | redis.internal | 9121 | Redis metrics |
| blackbox-http | external URLs | 9115 | External probes |
| fanatico-exporter | fanatico-exporter | 9546 | Custom blockchain metrics |

### 2. Alert Rules (`prometheus/rules/`)

**File**: `prometheus/rules/fanatico-alerts.yml`

**Alert Groups**:

| Group | Alerts | Description |
|-------|--------|-------------|
| fanatico-rpc | 4 | RPC node health, latency, errors, rate limits |
| fanatico-blockchain | 4 | Block production, block time, pending txs, reorgs |
| fanatico-database | 5 | Patroni cluster, PostgreSQL, replication, connections |
| fanatico-etcd | 3 | etcd cluster, fsync duration, commit duration |
| fanatico-haproxy | 3 | Backend/server health, connection rate |
| fanatico-system | 6 | Host down, CPU, memory, disk, network errors |
| fanatico-security | 3 | Failed logins, SSL certificate expiry |

**Severity Levels**:
- `critical`: Immediate action required (PagerDuty + Slack)
- `high`: Urgent attention needed (Slack critical channel)
- `warning`: Needs investigation (Slack warnings channel)

### 3. AlertManager (`alertmanager/`)

**Configuration**: `alertmanager/alertmanager.yml`

**Routing**:
```
Default → slack-notifications (#fanatico-alerts)
    ├── severity: critical → pagerduty-critical + slack-critical
    ├── severity: high → slack-critical
    ├── severity: warning → slack-warnings
    ├── service: database → slack-dba
    └── service: security → slack-security + email-security
```

**Receivers**:
| Receiver | Channel/Target | Icon |
|----------|---------------|------|
| slack-notifications | #fanatico-alerts | 🔔 |
| slack-critical | #fanatico-critical | 🚨 |
| slack-warnings | #fanatico-warnings | ⚠️ |
| slack-dba | #fanatico-dba | 🗄️ |
| slack-security | #fanatico-security | 🔒 |
| pagerduty-critical | PagerDuty service | - |
| email-security | security@fanati.co | - |

**Inhibition Rules**:
- HostDown inhibits all alerts for that instance
- PatroniClusterUnhealthy inhibits database alerts
- RPCNodeDown inhibits RPCHighLatency

### 4. Custom Exporter (`exporters/`)

**File**: `exporters/fanatico_exporter.py`

Python-based Prometheus exporter for blockchain-specific metrics.

**Metrics Exported**:
| Metric | Type | Description |
|--------|------|-------------|
| fanatico_up | gauge | Node availability (0/1) |
| fanatico_chain_id | gauge | Chain ID (11111111111) |
| fanatico_block_number | gauge | Current block height |
| fanatico_block_timestamp | gauge | Latest block timestamp |
| fanatico_block_gas_used | gauge | Gas used in latest block |
| fanatico_block_gas_limit | gauge | Gas limit of latest block |
| fanatico_block_transaction_count | gauge | Transactions in latest block |
| fanatico_gas_price_wei | gauge | Current gas price (wei) |
| fanatico_gas_price_gwei | gauge | Current gas price (gwei) |
| fanatico_syncing | gauge | Sync status (0=synced, 1=syncing) |
| fanatico_peer_count | gauge | Connected peers |
| fanatico_mining | gauge | Mining status |
| fanatico_client_info | info | Client version information |

**Endpoints**:
- `/metrics` - Prometheus metrics
- `/health` - Health check (JSON)

**Usage**:
```bash
python3 fanatico_exporter.py \
    --rpc-url http://localhost:8545 \
    --port 9546 \
    --interval 15
```

### 5. Grafana Dashboards (`grafana/dashboards/`)

**File**: `grafana/dashboards/fanatico-overview.json`

**Panels**:

| Row | Panels |
|-----|--------|
| Node Status | Node Up/Down, Block Height, Gas Price, Peer Count |
| Blockchain | Transactions/Block, Sync Status, Block Time |
| System Resources | CPU Usage, Memory Usage, Disk Usage |
| Database | PostgreSQL Connections, Replication Lag |
| Network | RPC Requests/sec, Error Rate |

## Deployment

### Prerequisites

```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-*/prometheus /usr/local/bin/

# Install AlertManager
wget https://github.com/prometheus/alertmanager/releases/download/v0.26.0/alertmanager-0.26.0.linux-amd64.tar.gz
tar xvfz alertmanager-*.tar.gz
sudo mv alertmanager-*/alertmanager /usr/local/bin/

# Install Grafana
sudo apt-get install -y apt-transport-https software-properties-common
wget -q -O - https://apt.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update && sudo apt-get install grafana
```

### Configuration

1. **Set Environment Variables**:
```bash
export SMTP_USERNAME="alerts@fanati.co"
export SMTP_PASSWORD="<smtp-password>"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export PAGERDUTY_SERVICE_KEY="<pagerduty-key>"
```

2. **Deploy Prometheus**:
```bash
sudo mkdir -p /etc/prometheus/rules
sudo cp prometheus/prometheus.yml /etc/prometheus/
sudo cp prometheus/rules/*.yml /etc/prometheus/rules/

# Start Prometheus
prometheus --config.file=/etc/prometheus/prometheus.yml \
           --storage.tsdb.path=/var/lib/prometheus \
           --web.enable-lifecycle
```

3. **Deploy AlertManager**:
```bash
sudo mkdir -p /etc/alertmanager/templates
sudo cp alertmanager/alertmanager.yml /etc/alertmanager/
envsubst < /etc/alertmanager/alertmanager.yml > /tmp/alertmanager.yml
sudo mv /tmp/alertmanager.yml /etc/alertmanager/alertmanager.yml

# Start AlertManager
alertmanager --config.file=/etc/alertmanager/alertmanager.yml
```

4. **Deploy Fanatico Exporter**:
```bash
pip install requests
python3 exporters/fanatico_exporter.py &
```

5. **Configure Grafana**:
```bash
sudo systemctl start grafana-server
# Access at http://localhost:3000
# Add Prometheus data source: http://localhost:9090
# Import dashboard from grafana/dashboards/fanatico-overview.json
```

### Docker Deployment

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.48.0
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"

  alertmanager:
    image: prom/alertmanager:v0.26.0
    volumes:
      - ./alertmanager:/etc/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
    ports:
      - "9093:9093"
    environment:
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
      - PAGERDUTY_SERVICE_KEY=${PAGERDUTY_SERVICE_KEY}

  grafana:
    image: grafana/grafana:10.2.0
    volumes:
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

  fanatico-exporter:
    build:
      context: ./exporters
      dockerfile: Dockerfile
    ports:
      - "9546:9546"
    environment:
      - RPC_URL=http://rpc1.internal:8545

volumes:
  prometheus_data:
  grafana_data:
```

## Alert Runbook

### Critical Alerts

#### RPCNodeDown
**Severity**: Critical
**Impact**: RPC endpoint unavailable

**Investigation**:
1. Check node status: `systemctl status fanatico-rpc`
2. Check logs: `journalctl -u fanatico-rpc -n 100`
3. Verify network connectivity: `curl http://node:8545`

**Resolution**:
1. Restart service: `systemctl restart fanatico-rpc`
2. If persistent, check disk space and memory
3. Escalate if node won't start

#### BlockProductionStopped
**Severity**: Critical
**Impact**: No new blocks being produced

**Investigation**:
1. Check block number: `curl -X POST http://rpc:8545 -d '{"method":"eth_blockNumber"}'`
2. Check consensus node status
3. Verify network connectivity between validators

**Resolution**:
1. Check validator node logs
2. Verify consensus mechanism is running
3. Escalate to blockchain team

#### PatroniClusterUnhealthy
**Severity**: Critical
**Impact**: Database HA compromised

**Investigation**:
1. Check Patroni status: `patronictl list`
2. Check etcd: `etcdctl cluster-health`
3. Review Patroni logs

**Resolution**:
1. Identify failed node
2. Reinitialize if necessary: `patronictl reinit fanatico-l1 <node>`
3. Verify replication is working

### Warning Alerts

#### HostDiskSpaceLow
**Severity**: Warning
**Impact**: Service may fail if disk fills

**Investigation**:
1. Check disk usage: `df -h`
2. Identify large files: `du -sh /* | sort -h`

**Resolution**:
1. Clean up logs: `journalctl --vacuum-time=7d`
2. Archive old data
3. Expand disk if necessary

#### PostgreSQLReplicationLag
**Severity**: Warning
**Impact**: Replica data is stale

**Investigation**:
1. Check lag: `SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) FROM pg_stat_replication;`
2. Check network between primary and replica
3. Check replica resources (CPU, I/O)

**Resolution**:
1. If network issue, fix connectivity
2. If I/O bound, optimize queries or add resources
3. If severe, reinitialize replica

## Metrics Reference

### RPC Metrics
```promql
# Request rate
rate(rpc_requests_total[5m])

# Error rate
rate(rpc_requests_total{status="error"}[5m]) / rate(rpc_requests_total[5m])

# Latency P95
histogram_quantile(0.95, rate(rpc_request_duration_seconds_bucket[5m]))
```

### Blockchain Metrics
```promql
# Block production rate
rate(fanatico_block_number[5m]) * 60

# Block time
fanatico_block_time_seconds

# Pending transactions
fanatico_pending_transactions
```

### Database Metrics
```promql
# Connection usage
pg_stat_activity_count / pg_settings_max_connections

# Replication lag (seconds)
pg_replication_lag_seconds

# Transaction rate
rate(pg_stat_database_xact_commit[5m])
```

### System Metrics
```promql
# CPU usage
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

## Maintenance

### Prometheus

**Retention**: Default 15 days
```bash
# Increase retention
prometheus --storage.tsdb.retention.time=30d
```

**Reload Configuration**:
```bash
curl -X POST http://localhost:9090/-/reload
```

### AlertManager

**Reload Configuration**:
```bash
curl -X POST http://localhost:9093/-/reload
```

**Silence Alerts**:
```bash
amtool silence add alertname=HostHighCPU instance=rpc1.internal \
    --comment="Planned maintenance" \
    --duration=2h
```

### Grafana

**Backup Dashboards**:
```bash
curl -H "Authorization: Bearer $GRAFANA_API_KEY" \
     http://localhost:3000/api/dashboards/uid/fanatico-overview \
     > dashboard-backup.json
```

## Troubleshooting

### Prometheus Not Scraping

1. Check target status: http://localhost:9090/targets
2. Verify network connectivity to targets
3. Check firewall rules for metrics ports

### Alerts Not Firing

1. Check rule evaluation: http://localhost:9090/rules
2. Verify AlertManager is reachable
3. Check AlertManager logs for routing issues

### Grafana Dashboard Empty

1. Verify Prometheus data source is configured
2. Check time range selection
3. Test query in Prometheus UI first

## Security Considerations

1. **Network**: Prometheus/AlertManager/Grafana should be on internal network
2. **Authentication**: Enable Grafana authentication (default: admin/admin)
3. **TLS**: Use TLS for all external-facing endpoints
4. **Secrets**: Store credentials in environment variables or secret manager
5. **RBAC**: Configure Grafana organizations and permissions

## Related Documentation

- [Backup Documentation](../backup/README.md)
- [Security Audit Framework](../security/audit/SECURITY_AUDIT_CHECKLIST.md)
- [High Availability Setup](../haproxy/README.md)
- [Incident Response Plan](../security/audit/INCIDENT_RESPONSE_PLAN.md)
