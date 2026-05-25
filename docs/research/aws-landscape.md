---
agent-notes: { ctx: "AWS service landscape for cloud specialists", deps: [.claude/agents/cloud-architect.md, .claude/agents/cloud-costguard.md, .claude/agents/cloud-netdiag.md], state: active, last: "cloud-architect@2026-02-12" }
---

# AWS Service Landscape

> **Last updated:** 2026-02-12
> **Updated by:** Initial seed from template
>
> Run `/cloud-update AWS` to refresh this file with current information.

This file is read by the cloud specialist agents (`cloud-architect`, `cloud-costguard`, `cloud-netdiag`) to supplement their built-in knowledge when operating in AWS mode. It captures the current state of AWS services, pricing, and gotchas that may change over time.

## Compute Options

| Service | Best for | Key limits/gotchas |
|---------|----------|-------------------|
| Lambda | Event-driven, short-lived tasks (<15min) | 10GB memory max, 15min timeout, cold starts with VPC |
| ECS Fargate | Containers without managing servers | No SSH (use ECS Exec), higher cost than EC2 for steady-state |
| ECS on EC2 | Containers with instance-level control | You manage the instances, patching, scaling |
| EKS (Fargate) | Kubernetes without nodes | $0.10/hr control plane + Fargate pricing |
| EKS (managed nodes) | Full Kubernetes | $0.10/hr control plane + EC2 costs |
| App Runner | Simple container/source deployments | Limited config, no VPC by default (opt-in), fewer regions |
| Elastic Beanstalk | PaaS-style deployment | Abstracts too much for complex setups, harder to debug |
| EC2 | Full control, GPU, special hardware | You manage everything |

## Database Options

| Service | Best for | Key limits/gotchas |
|---------|----------|-------------------|
| RDS (PostgreSQL/MySQL) | Relational, managed | Multi-AZ doubles cost, storage costs on stopped instances |
| Aurora | High-performance relational | Min cost higher than RDS, Aurora Serverless v2 scales to zero |
| DynamoDB | Key-value, document, serverless | On-demand vs provisioned pricing, hot partition limits |
| ElastiCache | Redis/Memcached caching | No Savings Plans, use reserved nodes |
| DocumentDB | MongoDB-compatible | Not actually MongoDB, some compatibility gaps |
| Neptune | Graph databases | Expensive for small workloads |

## Networking Pricing Traps

| Item | Cost | Mitigation |
|------|------|------------|
| NAT Gateway | $0.045/hr + $0.045/GB processed | VPC Endpoints for AWS services (Gateway endpoints are free for S3/DynamoDB) |
| Cross-AZ transfer | $0.01/GB each way | Keep chatty services in same AZ for dev; accept cost for prod HA |
| Data transfer out | $0.09/GB after 100GB/month free | CloudFront is often cheaper for serving |
| VPC Interface Endpoints | $0.01/hr per AZ + $0.01/GB | Cheaper than NAT for high-volume AWS API calls |
| Elastic IP (idle) | $0.005/hr (~$3.60/month) | Clean up unused |

## Recent Changes and New Services

<!-- Update this section when running /cloud-update AWS -->
<!-- Include: new service launches, significant pricing changes, deprecated services, new regions -->

*No updates recorded yet. Run `/cloud-update AWS` to populate.*

## Known Enterprise Patterns

- **AWS Control Tower** landing zones are standard for enterprise multi-account setups
- **SCPs** at the OU level are the most common constraint mechanism
- **AWS Config** conformance packs enforce compliance rules
- **Centralized networking** via Transit Gateway is common; shared VPC is less common than on GCP
- **IAM Identity Center (SSO)** is replacing direct IAM user access
