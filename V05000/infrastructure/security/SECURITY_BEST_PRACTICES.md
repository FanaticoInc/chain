# Fanatico L1 Security Best Practices

## Overview

This document provides practical security best practices for developing, deploying, and operating the Fanatico L1 blockchain infrastructure.

**Target Audience:** Developers, DevOps, System Administrators
**Last Updated:** January 31, 2026

---

## Table of Contents

1. [Key Management](#key-management)
2. [Credential Handling](#credential-handling)
3. [Network Security](#network-security)
4. [OWASP Considerations](#owasp-considerations)
5. [Incident Response](#incident-response)
6. [Smart Contract Security](#smart-contract-security)
7. [Infrastructure Security](#infrastructure-security)
8. [Operational Security](#operational-security)

---

## Key Management

### Private Key Storage

**DO:**
- Store private keys in hardware security modules (HSMs) for production
- Use encrypted keystores with strong passwords
- Implement key derivation from HD wallets (BIP-32/39/44)
- Keep cold storage backups in geographically separate locations
- Use multisig wallets for high-value operations

**DON'T:**
- Store private keys in plain text files
- Commit private keys to version control
- Share private keys via email, Slack, or other messaging
- Store keys on shared or multi-tenant systems
- Use the same key for multiple environments

### Key Rotation

```bash
# Key rotation schedule
Production keys:      Every 90 days
Development keys:     Every 30 days
Service account keys: Every 60 days
SSL/TLS certificates: Before expiration (monitor with 30-day warning)
```

### Test Account Security

The Fanatico L1 test accounts use a well-known mnemonic:
```
test test test test test test test test test test test junk
```

**CRITICAL:** These accounts are for testing ONLY. Never:
- Fund these addresses with real assets on mainnet
- Use these keys for production deployments
- Assume these accounts are secure

---

## Credential Handling

### Environment Variables

**Best Practice:** Use environment variables or secrets managers, never hardcode credentials.

```bash
# .env file (NEVER commit this file)
DATABASE_URL=postgresql://user:password@host:5432/db
RPC_API_KEY=your-api-key-here
PRIVATE_KEY=0x...  # For dev only, use HSM in production
```

**.gitignore must include:**
```gitignore
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
```

### Secrets Management

**Recommended Tools:**
| Tool | Use Case |
|------|----------|
| HashiCorp Vault | Production secrets management |
| AWS Secrets Manager | AWS-hosted infrastructure |
| Docker Secrets | Container deployments |
| 1Password/Bitwarden | Team credential sharing |

### Database Credentials

```yaml
# PostgreSQL security settings
postgresql:
  # Require SSL for all connections
  ssl: require
  ssl_mode: verify-full

  # Use strong passwords (20+ chars, mixed case, numbers, symbols)
  password_min_length: 20

  # Rotate credentials quarterly
  credential_rotation: 90d

  # Limit connection sources
  pg_hba:
    - "hostssl all all 10.0.0.0/8 scram-sha-256"
```

### API Keys

```python
# Good: Load from environment
import os
api_key = os.environ.get('API_KEY')
if not api_key:
    raise ValueError("API_KEY environment variable not set")

# Bad: Hardcoded
api_key = "sk-1234567890abcdef"  # NEVER DO THIS
```

---

## Network Security

### Firewall Configuration

```bash
# Default deny policy
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow only essential ports
sudo ufw allow 22/tcp    # SSH (consider changing port)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8545/tcp  # RPC (restrict to trusted IPs)

# Restrict RPC to specific IPs
sudo ufw allow from 10.0.0.0/8 to any port 8545

# Enable firewall
sudo ufw enable
```

### TLS/SSL Requirements

**Minimum Requirements:**
- TLS 1.2 or higher (disable TLS 1.0, 1.1)
- Strong cipher suites only
- Valid certificates from trusted CA
- HSTS enabled for web services

```nginx
# nginx SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_stapling on;
ssl_stapling_verify on;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### RPC Endpoint Security

```yaml
# RPC security configuration
rpc:
  # Rate limiting
  rate_limit:
    requests_per_second: 100
    burst: 200

  # Disable dangerous methods
  disabled_methods:
    - personal_*
    - admin_*
    - debug_*
    - miner_*
    - eth_sign
    - eth_signTransaction

  # Input validation
  max_request_size: 1MB
  max_batch_size: 100
  timeout: 30s

  # Access control
  cors_origins:
    - "https://explorer.fanati.co"
    - "https://app.fanati.co"
```

### DDoS Protection

- Use CDN (CloudFlare, AWS CloudFront) for public endpoints
- Implement connection rate limiting at network level
- Configure SYN flood protection
- Set up geographic blocking for high-risk regions if needed

---

## OWASP Considerations

### OWASP Top 10 for Blockchain APIs

| # | Risk | Mitigation |
|---|------|------------|
| A01 | Broken Access Control | Implement proper authentication, disable dangerous RPC methods |
| A02 | Cryptographic Failures | Use TLS 1.2+, proper key management, secure random generation |
| A03 | Injection | Validate all RPC inputs, use parameterized queries |
| A04 | Insecure Design | Follow secure development lifecycle, threat modeling |
| A05 | Security Misconfiguration | Harden servers, disable unnecessary features |
| A06 | Vulnerable Components | Keep dependencies updated, run `npm audit` regularly |
| A07 | Authentication Failures | Strong passwords, rate limit login attempts, MFA |
| A08 | Data Integrity Failures | Verify signatures, use checksums, validate transactions |
| A09 | Logging Failures | Comprehensive logging, secure log storage, monitoring |
| A10 | SSRF | Validate URLs, restrict internal network access |

### Input Validation

```python
# RPC input validation example
def validate_rpc_request(request):
    # Check JSON structure
    if not isinstance(request, dict):
        raise InvalidRequest("Request must be JSON object")

    # Validate required fields
    required = ['jsonrpc', 'method', 'id']
    for field in required:
        if field not in request:
            raise InvalidRequest(f"Missing required field: {field}")

    # Validate method name (alphanumeric and underscore only)
    method = request.get('method', '')
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', method):
        raise InvalidRequest("Invalid method name")

    # Check method is allowed
    if method in DISABLED_METHODS:
        raise MethodNotAllowed(f"Method {method} is disabled")

    # Validate params size
    params = request.get('params', [])
    if len(str(params)) > MAX_PARAMS_SIZE:
        raise InvalidRequest("Params too large")

    return True
```

### SQL Injection Prevention

```python
# Good: Parameterized query
cursor.execute(
    "SELECT * FROM transactions WHERE hash = %s",
    (tx_hash,)
)

# Bad: String concatenation
cursor.execute(
    f"SELECT * FROM transactions WHERE hash = '{tx_hash}'"  # VULNERABLE
)
```

---

## Incident Response

### Quick Reference

**Incident Hotline:** [Define your contact method]
**On-Call Rotation:** [Define schedule]
**Escalation Path:** Developer -> Lead -> CTO -> CEO

### Severity Classification

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| P1 Critical | Active exploit, funds at risk | < 15 min | Private key leak, active attack |
| P2 High | Security vulnerability found | < 1 hour | RCE, authentication bypass |
| P3 Medium | Potential security issue | < 4 hours | Suspicious activity, failed logins |
| P4 Low | Minor security concern | < 24 hours | Outdated dependency, config issue |

### Immediate Response Checklist

**For P1 Critical Incidents:**

```markdown
[ ] 1. Alert on-call engineer (< 5 min)
[ ] 2. Assess scope and impact (< 10 min)
[ ] 3. Isolate affected systems if needed
[ ] 4. Preserve logs and evidence
[ ] 5. Begin containment actions
[ ] 6. Notify stakeholders
[ ] 7. Document all actions taken
```

### Key Compromise Response

If private keys are compromised:

1. **Immediate (0-15 min):**
   - Revoke compromised keys
   - Transfer funds to secure wallet
   - Block compromised addresses

2. **Short-term (15-60 min):**
   - Generate new keys using secure process
   - Update all systems with new keys
   - Audit for unauthorized transactions

3. **Follow-up (1-24 hours):**
   - Full security audit
   - Identify breach source
   - Implement additional controls

---

## Smart Contract Security

### Development Best Practices

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SecureContract is ReentrancyGuard, Pausable, Ownable {
    // Use checks-effects-interactions pattern
    function withdraw(uint256 amount) external nonReentrant whenNotPaused {
        // Checks
        require(balances[msg.sender] >= amount, "Insufficient balance");

        // Effects
        balances[msg.sender] -= amount;

        // Interactions
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }

    // Emergency pause function
    function pause() external onlyOwner {
        _pause();
    }
}
```

### Security Checklist

- [ ] Use latest Solidity version (0.8.x for overflow protection)
- [ ] Implement reentrancy guards
- [ ] Add emergency pause functionality
- [ ] Use OpenZeppelin audited contracts
- [ ] Run static analysis (Slither, Mythril)
- [ ] Get professional audit before mainnet deployment
- [ ] Test with fuzzing tools (Echidna)

---

## Infrastructure Security

### Server Hardening Checklist

```bash
# 1. Update system
apt update && apt upgrade -y

# 2. Configure automatic security updates
apt install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

# 3. Harden SSH
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#PermitRootLogin yes/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
systemctl restart sshd

# 4. Install and configure fail2ban
apt install fail2ban
systemctl enable fail2ban

# 5. Set up audit logging
apt install auditd
systemctl enable auditd
```

### Container Security

```dockerfile
# Use specific version, not 'latest'
FROM python:3.12-slim

# Run as non-root user
RUN useradd -m -s /bin/bash appuser
USER appuser

# Don't store secrets in image
# Use environment variables or mounted secrets

# Scan image for vulnerabilities
# docker scan myimage:tag
```

### Monitoring Requirements

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| Failed SSH logins | > 10/5min | Block IP, investigate |
| RPC error rate | > 5% | Check service health |
| CPU usage | > 90% for 5min | Scale or investigate |
| Disk usage | > 85% | Clean up or expand |
| Certificate expiry | < 30 days | Renew certificate |

---

## Operational Security

### Access Control

**Principle of Least Privilege:**
- Grant minimum permissions needed
- Use role-based access control (RBAC)
- Review access quarterly
- Revoke access immediately when roles change

### Change Management

```markdown
## Change Request Template

**Change ID:** CHG-2026-001
**Requestor:** [Name]
**Date:** [Date]
**Environment:** Production / Staging / Development

**Description:**
[What is being changed]

**Risk Assessment:**
- Impact: High / Medium / Low
- Likelihood of issues: High / Medium / Low

**Rollback Plan:**
[How to revert if issues occur]

**Approvals:**
- [ ] Security review
- [ ] Technical lead
- [ ] Operations
```

### Backup Security

- Encrypt all backups (AES-256)
- Store backup encryption keys separately from backups
- Test backup restoration monthly
- Keep backups in geographically separate location
- Verify backup integrity with checksums

```bash
# Encrypted backup example
tar czf - /data | gpg --symmetric --cipher-algo AES256 > backup.tar.gz.gpg

# Verify backup
gpg --decrypt backup.tar.gz.gpg | tar tzf -
```

---

## Quick Reference Card

### Security Contacts

| Role | Contact |
|------|---------|
| Security Lead | [TBD] |
| On-Call Engineer | [TBD] |
| Infrastructure | [TBD] |

### Critical Commands

```bash
# Emergency: Stop RPC service
systemctl stop fanatico-rpc

# Emergency: Block IP
ufw deny from <IP_ADDRESS>

# View security logs
journalctl -u fail2ban -f
tail -f /var/log/auth.log

# Check for unauthorized changes
aide --check
```

### Important URLs

| Service | URL |
|---------|-----|
| RPC Endpoint | https://rpc.fanati.co |
| Block Explorer | https://explorer.fanati.co |
| Monitoring | http://paratime.fanati.co:8080 |

---

## Related Documentation

- [Security README](./README.md) - Overview and tooling
- [Security Audit Checklist](./audit/SECURITY_AUDIT_CHECKLIST.md) - Detailed audit procedures
- [Incident Response Plan](./audit/INCIDENT_RESPONSE_PLAN.md) - Full IR procedures
- [Server Hardening Script](./scripts/harden-server.sh) - Automated hardening

---

**Document Version:** 1.0
**Classification:** Internal
**Review Schedule:** Quarterly
**Next Review:** April 30, 2026
