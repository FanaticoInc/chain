# Fanatico L1 Incident Response Plan

**Version**: 1.0
**Date**: January 29, 2026
**Classification**: Internal - Security Sensitive
**Owner**: Security Team

---

## 1. Overview

This document outlines the procedures for responding to security incidents affecting the Fanatico L1 blockchain infrastructure.

### 1.1 Scope

This plan covers:
- Security breaches
- Service disruptions
- Data loss or corruption
- Unauthorized access
- Smart contract vulnerabilities
- Key compromise

### 1.2 Objectives

1. Minimize damage and impact
2. Restore services quickly and safely
3. Preserve evidence for investigation
4. Prevent future incidents
5. Comply with notification requirements

---

## 2. Incident Classification

### 2.1 Severity Levels

| Level | Name | Description | Response Time | Examples |
|-------|------|-------------|---------------|----------|
| P1 | Critical | Service down, active exploit, key compromise | < 15 min | Private key leaked, active attack, total service outage |
| P2 | High | Significant impact, potential exploit | < 1 hour | Vulnerability discovered, partial outage, unauthorized access |
| P3 | Medium | Limited impact, contained issue | < 4 hours | Failed login attempts, minor service degradation |
| P4 | Low | Minimal impact, monitoring alert | < 24 hours | Unusual traffic patterns, config drift |

### 2.2 Incident Types

| Type | Description | Lead Team |
|------|-------------|-----------|
| Security Breach | Unauthorized system access | Security |
| Service Outage | Infrastructure failure | Operations |
| Smart Contract | Vulnerability or exploit | Development |
| Key Compromise | Private key exposure | Security |
| Data Incident | Data loss or corruption | Operations |
| DDoS Attack | Denial of service | Operations |

---

## 3. Response Team

### 3.1 Roles and Responsibilities

| Role | Responsibilities | Primary | Backup |
|------|------------------|---------|--------|
| Incident Commander | Overall coordination, decisions | [Name] | [Name] |
| Security Lead | Technical security response | [Name] | [Name] |
| Operations Lead | Infrastructure response | [Name] | [Name] |
| Communications Lead | Internal/external communications | [Name] | [Name] |
| Development Lead | Code-related issues | [Name] | [Name] |

### 3.2 Contact Information

```
INCIDENT HOTLINE: [Phone Number]
SECURITY EMAIL: security@fanati.co
SLACK CHANNEL: #incident-response
PAGERDUTY: [Service URL]
```

### 3.3 Escalation Matrix

| Severity | Initial Response | 15 min | 1 hour | 4 hours |
|----------|-----------------|--------|--------|---------|
| P1 | On-call engineer | Security Lead + Ops Lead | Incident Commander | Executive Team |
| P2 | On-call engineer | Team Lead | Security Lead | Incident Commander |
| P3 | On-call engineer | Team Lead | - | - |
| P4 | Assigned engineer | - | - | - |

---

## 4. Response Procedures

### 4.1 Phase 1: Detection & Triage (0-15 minutes)

**Objective**: Identify and classify the incident

1. **Acknowledge Alert**
   - Acknowledge in monitoring system
   - Join incident Slack channel
   - Update status page if needed

2. **Initial Assessment**
   - What is affected?
   - How many users/systems impacted?
   - Is it ongoing or contained?
   - What is the potential damage?

3. **Classify Incident**
   - Assign severity level (P1-P4)
   - Identify incident type
   - Determine response team

4. **Notify Stakeholders**
   - Alert appropriate team members
   - Create incident ticket
   - Start incident log

**Checklist**:
- [ ] Alert acknowledged
- [ ] Initial assessment complete
- [ ] Severity assigned
- [ ] Incident ticket created
- [ ] Stakeholders notified

### 4.2 Phase 2: Containment (15 min - 1 hour)

**Objective**: Stop the bleeding, prevent further damage

1. **Immediate Actions**
   - Isolate affected systems if needed
   - Block malicious IPs/users
   - Disable compromised accounts
   - Preserve evidence (logs, memory dumps)

2. **Short-term Containment**
   - Implement temporary fixes
   - Reroute traffic if needed
   - Enable additional monitoring
   - Communicate status to users

**For Specific Incident Types**:

**Key Compromise**:
```bash
# Immediately rotate compromised keys
# Revoke access from compromised accounts
# Check for unauthorized transactions
# Enable enhanced monitoring
```

**Active Attack**:
```bash
# Enable rate limiting
# Block attacking IPs
# Enable DDoS protection
# Scale up infrastructure
```

**Smart Contract Exploit**:
```bash
# Pause affected contracts if possible
# Disable affected functions
# Assess fund movement
# Prepare emergency response
```

**Checklist**:
- [ ] Affected systems isolated
- [ ] Attack vector blocked
- [ ] Evidence preserved
- [ ] Temporary fixes in place
- [ ] Status communicated

### 4.3 Phase 3: Eradication (1-4 hours)

**Objective**: Remove the threat completely

1. **Root Cause Analysis**
   - How did the incident occur?
   - What vulnerability was exploited?
   - What systems are affected?

2. **Remove Threat**
   - Patch vulnerabilities
   - Remove malware/backdoors
   - Reset compromised credentials
   - Update firewall rules

3. **Verify Eradication**
   - Scan for remaining threats
   - Verify patches applied
   - Check for persistence mechanisms

**Checklist**:
- [ ] Root cause identified
- [ ] Vulnerability patched
- [ ] Malicious artifacts removed
- [ ] Credentials rotated
- [ ] Verification complete

### 4.4 Phase 4: Recovery (4-24 hours)

**Objective**: Restore normal operations safely

1. **System Restoration**
   - Restore from clean backups if needed
   - Gradually bring systems online
   - Verify data integrity
   - Test functionality

2. **Monitoring**
   - Enhanced monitoring for recurrence
   - Watch for related indicators
   - Verify security controls effective

3. **Communication**
   - Update stakeholders on recovery
   - Prepare user communication
   - Update status page

**Recovery Procedures**:

```bash
# Verify backup integrity
/opt/fanatico/backup/scripts/backup-verify.sh --full-test

# Restore if needed
/opt/fanatico/backup/scripts/restore-full.sh <backup_file>

# Verify service health
curl http://localhost:8545/health

# Run security scan
python3 /opt/fanatico/security/scripts/rpc-security-audit.py
```

**Checklist**:
- [ ] Systems restored
- [ ] Data integrity verified
- [ ] Services functional
- [ ] Enhanced monitoring active
- [ ] Users notified of recovery

### 4.5 Phase 5: Post-Incident (24-72 hours)

**Objective**: Learn and improve

1. **Post-Incident Review**
   - Schedule review meeting
   - Document timeline
   - Identify what worked/didn't work
   - Determine root cause

2. **Documentation**
   - Complete incident report
   - Update runbooks
   - Document lessons learned
   - Update security controls

3. **Improvement Actions**
   - Create action items
   - Assign owners and deadlines
   - Track completion
   - Verify effectiveness

**Checklist**:
- [ ] Post-incident review held
- [ ] Incident report completed
- [ ] Lessons learned documented
- [ ] Action items created
- [ ] Controls updated

---

## 5. Communication Templates

### 5.1 Internal Alert (Slack)

```
🚨 SECURITY INCIDENT - [SEVERITY]

Type: [Incident Type]
Status: [Investigating/Contained/Resolved]
Impact: [Description of impact]
Lead: @[name]

Actions:
- [Current actions being taken]

Updates in this thread. Do not discuss outside this channel.
```

### 5.2 Status Page Update

```
[INCIDENT] Service Degradation

We are currently investigating an issue affecting [service].
Impact: [Description]
Status: [Investigating/Identified/Monitoring/Resolved]

Updates will be provided every [30 minutes/1 hour].

Last updated: [Timestamp]
```

### 5.3 User Notification

```
Subject: Important Security Notice - Action Required

Dear User,

We are writing to inform you of a security incident that may affect your account.

What happened:
[Brief description]

What we're doing:
[Actions taken]

What you should do:
[Required user actions]

We take security seriously and apologize for any inconvenience.

Fanatico Security Team
```

---

## 6. Specific Playbooks

### 6.1 Private Key Compromise

**Indicators**:
- Unauthorized transactions
- Key material found in logs/dumps
- Third-party breach notification

**Response**:
1. Immediately revoke/rotate compromised key
2. Freeze affected accounts if possible
3. Check transaction history for unauthorized activity
4. Generate new keys using secure process
5. Update all systems with new keys
6. Notify affected users
7. Report to relevant authorities if required

### 6.2 Smart Contract Vulnerability

**Indicators**:
- Security researcher report
- Unusual contract behavior
- Community alert

**Response**:
1. Verify the vulnerability
2. Assess exploitability and impact
3. Pause contract if critical (if pausable)
4. Prepare and test fix
5. Coordinate disclosure timing
6. Deploy fix
7. Publish post-mortem

### 6.3 DDoS Attack

**Indicators**:
- Spike in traffic
- Service degradation
- Monitoring alerts

**Response**:
1. Enable DDoS protection (CloudFlare)
2. Scale infrastructure if needed
3. Implement rate limiting
4. Block attacking IPs
5. Analyze attack patterns
6. Adjust defenses
7. Document attack details

### 6.4 Unauthorized Access

**Indicators**:
- Unusual login activity
- Privilege escalation
- Suspicious commands

**Response**:
1. Disable compromised accounts
2. Terminate active sessions
3. Check for persistence
4. Review access logs
5. Identify entry point
6. Patch vulnerability
7. Rotate credentials

---

## 7. Evidence Preservation

### 7.1 What to Preserve

- System logs (auth, application, security)
- Network traffic captures
- Memory dumps
- Disk images
- Configuration files
- Blockchain data/transactions
- Screenshots
- Communication records

### 7.2 Preservation Commands

```bash
# Capture system state
date > /evidence/timestamp.txt
hostname >> /evidence/timestamp.txt
uname -a >> /evidence/timestamp.txt

# Preserve logs
cp -r /var/log /evidence/logs/

# Memory dump (requires tools)
# dd if=/dev/mem of=/evidence/memory.dump

# Network connections
netstat -an > /evidence/netstat.txt
ss -tunapl > /evidence/ss.txt

# Process list
ps auxwww > /evidence/processes.txt

# Open files
lsof > /evidence/lsof.txt

# User activity
last > /evidence/last.txt
lastlog > /evidence/lastlog.txt

# Create disk image (if needed)
# dd if=/dev/sda of=/evidence/disk.img
```

### 7.3 Chain of Custody

Document for each piece of evidence:
- What was collected
- When it was collected
- Who collected it
- How it was preserved
- Where it is stored

---

## 8. Compliance and Reporting

### 8.1 Notification Requirements

| Stakeholder | Timeline | Method |
|-------------|----------|--------|
| Users (data breach) | 72 hours | Email |
| Regulators (if applicable) | As required | Official channel |
| Law enforcement | As needed | Official channel |
| Partners | 24 hours | Direct contact |

### 8.2 Required Documentation

- Incident report
- Timeline of events
- Impact assessment
- Remediation actions
- Lessons learned

---

## 9. Training and Testing

### 9.1 Training Requirements

- All team members: Annual incident response training
- On-call engineers: Quarterly tabletop exercises
- New hires: Incident response orientation

### 9.2 Testing Schedule

| Exercise | Frequency | Participants |
|----------|-----------|--------------|
| Tabletop | Quarterly | Response team |
| Simulation | Bi-annual | All technical staff |
| Full drill | Annual | Organization-wide |

---

## 10. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jan 29, 2026 | Security Team | Initial version |

**Next Review Date**: April 29, 2026

---

**REMEMBER**: In an incident, stay calm, follow the process, and document everything.
