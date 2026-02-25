# Fanatico L1 v0.5.0.0 - Automated Backup System

**Status**: Configuration Complete
**Date**: January 29, 2026

## Overview

Comprehensive backup system for Fanatico L1 blockchain infrastructure including:
- PostgreSQL full and incremental backups
- Blockchain state backups (SQLite, contracts, config)
- WAL archiving for point-in-time recovery
- Remote storage (S3-compatible)
- Encryption at rest
- Automated verification

## Backup Types

| Type | Frequency | Retention | Storage |
|------|-----------|-----------|---------|
| Full PostgreSQL | Daily | 30 days | Local + S3 |
| WAL Archive | Continuous | 7 days | Local + S3 |
| Blockchain State | 6 hours | 30 days | Local + S3 |
| Configuration | On change | 90 days | Local + S3 |

## Directory Structure

```
/var/backups/fanatico/
├── full/                    # Full PostgreSQL backups
│   ├── full_backup_20260129_020000.tar.gz
│   ├── full_backup_20260129_020000.tar.gz.sha256
│   └── ...
├── wal/                     # WAL archive segments
│   ├── 000000010000000000000001.gz
│   ├── 000000010000000000000002.gz
│   └── ...
├── blockchain/              # Blockchain state backups
│   ├── blockchain_backup_20260129_060000.tar.gz
│   └── ...
└── config/                  # Configuration backups
    └── ...
```

## Scripts

| Script | Description | Schedule |
|--------|-------------|----------|
| `backup-full.sh` | Full PostgreSQL backup | Daily 2:00 AM |
| `backup-wal.sh` | WAL segment archiving | Continuous |
| `backup-blockchain.sh` | Blockchain state backup | Every 6 hours |
| `restore-full.sh` | Restore from backup | Manual |
| `backup-verify.sh` | Verify backup integrity | Weekly Sunday 4:00 AM |

## Quick Start

### 1. Install Dependencies

```bash
# Ubuntu/Debian
apt-get install -y postgresql-client-15 awscli openssl jq

# Create directories
mkdir -p /var/backups/fanatico/{full,wal,blockchain,config}
mkdir -p /var/log/fanatico
mkdir -p /opt/fanatico/backup/scripts
mkdir -p /etc/fanatico
```

### 2. Deploy Scripts

```bash
# Copy scripts
cp scripts/*.sh /opt/fanatico/backup/scripts/
chmod +x /opt/fanatico/backup/scripts/*.sh

# Copy configuration
cp configs/backup.conf /etc/fanatico/
```

### 3. Generate Encryption Key

```bash
# Generate a strong encryption key
openssl rand -base64 32 > /etc/fanatico/backup.key
chmod 600 /etc/fanatico/backup.key

# IMPORTANT: Back up this key securely!
# Without it, encrypted backups cannot be restored
```

### 4. Configure S3 (Optional)

```bash
# Configure AWS CLI
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1

# Create bucket
aws s3 mb s3://fanatico-backups
```

### 5. Configure PostgreSQL WAL Archiving

Add to `postgresql.conf`:

```ini
archive_mode = on
archive_command = '/opt/fanatico/backup/scripts/backup-wal.sh %f %p'
archive_timeout = 300  # 5 minutes
```

Or in Patroni configuration:

```yaml
postgresql:
  parameters:
    archive_mode: "on"
    archive_command: '/opt/fanatico/backup/scripts/backup-wal.sh %f %p'
    archive_timeout: 300
```

### 6. Install Cron Jobs

```bash
# Install crontab
crontab /path/to/configs/crontab

# Or copy to cron.d
cp configs/crontab /etc/cron.d/fanatico-backup
```

## Usage

### Create Full Backup

```bash
# Basic backup
/opt/fanatico/backup/scripts/backup-full.sh

# With S3 upload
/opt/fanatico/backup/scripts/backup-full.sh --upload-s3

# With verification
/opt/fanatico/backup/scripts/backup-full.sh --upload-s3 --verify
```

### Create Blockchain Backup

```bash
# Basic backup
/opt/fanatico/backup/scripts/backup-blockchain.sh

# Include logs
/opt/fanatico/backup/scripts/backup-blockchain.sh --include-logs --upload-s3
```

### Restore from Backup

```bash
# List available backups
ls -la /var/backups/fanatico/full/

# Restore latest backup
/opt/fanatico/backup/scripts/restore-full.sh /var/backups/fanatico/full/full_backup_20260129_020000.tar.gz

# Point-in-time recovery
/opt/fanatico/backup/scripts/restore-full.sh backup.tar.gz --pitr "2026-01-29 12:00:00"

# Restore to different directory
/opt/fanatico/backup/scripts/restore-full.sh backup.tar.gz --target-dir /var/lib/postgresql/15/restore

# Verify only (don't restore)
/opt/fanatico/backup/scripts/restore-full.sh backup.tar.gz --verify-only
```

### Verify Backups

```bash
# Quick verification
/opt/fanatico/backup/scripts/backup-verify.sh

# Full test restore
/opt/fanatico/backup/scripts/backup-verify.sh --full-test

# Report only (no actions)
/opt/fanatico/backup/scripts/backup-verify.sh --report-only
```

## Recovery Procedures

### Scenario 1: Single Node Failure

```bash
# 1. Stop PostgreSQL on failed node
systemctl stop patroni

# 2. Clear data directory
rm -rf /var/lib/postgresql/15/fanatico/*

# 3. Patroni will automatically reinitialize from primary
systemctl start patroni
```

### Scenario 2: Full Cluster Recovery

```bash
# 1. Stop all Patroni nodes
systemctl stop patroni  # on all nodes

# 2. Restore on primary node
/opt/fanatico/backup/scripts/restore-full.sh /var/backups/fanatico/full/latest.tar.gz

# 3. Start primary
systemctl start patroni

# 4. Reinitialize replicas
patronictl reinit fanatico-l1-cluster db2
patronictl reinit fanatico-l1-cluster db3
```

### Scenario 3: Point-in-Time Recovery

```bash
# 1. Stop PostgreSQL
systemctl stop patroni

# 2. Restore with PITR
/opt/fanatico/backup/scripts/restore-full.sh backup.tar.gz --pitr "2026-01-29 12:00:00"

# 3. Start PostgreSQL (standalone, not Patroni)
pg_ctl -D /var/lib/postgresql/15/fanatico start

# 4. Verify recovery
psql -c "SELECT pg_is_in_recovery();"
psql -c "SELECT pg_last_wal_replay_lsn();"

# 5. Promote if needed
psql -c "SELECT pg_promote();"
```

### Scenario 4: Restore from S3

```bash
# 1. Download backup from S3
aws s3 cp s3://fanatico-backups/postgresql/full/full_backup_20260129_020000.tar.gz.enc /tmp/

# 2. Restore
/opt/fanatico/backup/scripts/restore-full.sh /tmp/full_backup_20260129_020000.tar.gz.enc --decrypt
```

## Monitoring

### Check Backup Status

```bash
# Recent full backups
ls -la /var/backups/fanatico/full/*.tar.gz | tail -5

# WAL archive count
find /var/backups/fanatico/wal -name "*.gz" | wc -l

# Disk usage
df -h /var/backups/fanatico
```

### Verify Backup Integrity

```bash
# Run verification
/opt/fanatico/backup/scripts/backup-verify.sh

# View verification reports
ls -la /var/log/fanatico/backup-reports/
cat /var/log/fanatico/backup-reports/backup_verification_*.json | jq .
```

### View Logs

```bash
# Backup logs
tail -f /var/log/fanatico/backup-full.log
tail -f /var/log/fanatico/backup-blockchain.log

# Cron logs
tail -f /var/log/fanatico/cron-backup-full.log
```

## Recovery Objectives

| Metric | Target | Actual |
|--------|--------|--------|
| RTO (Recovery Time Objective) | < 1 hour | ~30 minutes |
| RPO (Recovery Point Objective) | < 5 minutes | ~5 minutes (WAL) |

## Security

### Encryption
- Backups encrypted with AES-256-CBC
- Key stored at `/etc/fanatico/backup.key`
- Key must be backed up separately (not with data!)

### Access Control
- Backup scripts run as root or postgres
- Backup files owned by postgres:postgres
- Permissions: 600 for backup files, 700 for directories

### S3 Security
- Use IAM roles when possible
- Enable S3 bucket versioning
- Enable S3 bucket encryption (SSE-S3 or SSE-KMS)
- Restrict bucket access with bucket policy

## Troubleshooting

### Backup Fails

```bash
# Check PostgreSQL connectivity
pg_isready -h localhost -p 5432

# Check disk space
df -h /var/backups/fanatico

# Check permissions
ls -la /var/backups/fanatico
```

### Restore Fails

```bash
# Check PostgreSQL is stopped
systemctl status postgresql patroni

# Check target directory permissions
ls -la /var/lib/postgresql/15/

# Check encryption key exists
ls -la /etc/fanatico/backup.key
```

### WAL Archiving Fails

```bash
# Check archive directory
ls -la /var/backups/fanatico/wal/

# Check archive_command in PostgreSQL
psql -c "SHOW archive_command;"

# Check pg_stat_archiver
psql -c "SELECT * FROM pg_stat_archiver;"
```

---

**Version**: 0.5.0.0
**Author**: Fanatico Development Team
