---
agent-notes: { ctx: "Azure service landscape for cloud specialists", deps: [.claude/agents/cloud-architect.md, .claude/agents/cloud-costguard.md, .claude/agents/cloud-netdiag.md], state: active, last: "cloud-architect@2026-02-12" }
---

# Azure Service Landscape

> **Last updated:** 2026-02-12
> **Updated by:** Initial seed from template
>
> Run `/cloud-update Azure` to refresh this file with current information.

This file is read by the cloud specialist agents (`cloud-architect`, `cloud-costguard`, `cloud-netdiag`) to supplement their built-in knowledge when operating in Azure mode. It captures the current state of Azure services, pricing, and gotchas that may change over time.

## Compute Options

| Service | Best for | Key limits/gotchas |
|---------|----------|-------------------|
| Azure Functions | Event-driven, short-lived tasks | Consumption plan: 5min default timeout (10min max), cold starts |
| Container Apps | Containers with scale-to-zero | Consumption plan has cold starts, custom domains need verification |
| App Service | Web apps, APIs | VNet integration is outbound-only, no inbound private endpoint on Basic tier |
| AKS | Full Kubernetes | Free control plane (Standard tier: $0.10/hr), node pools cost extra |
| Azure Spring Apps | Java Spring Boot apps | Niche, expensive for non-Spring workloads |
| Virtual Machines | Full control, GPU, special hardware | You manage everything |

## Database Options

| Service | Best for | Key limits/gotchas |
|---------|----------|-------------------|
| Azure SQL | SQL Server, managed | DTU vs vCore pricing models, serverless tier scales to zero |
| PostgreSQL Flexible Server | PostgreSQL, managed | Burstable tier for dev, General Purpose for prod |
| Cosmos DB | Multi-model, global distribution | RU-based pricing is confusing, overshoot charges, serverless tier available |
| Azure Cache for Redis | Caching | No free tier, Basic tier lacks replication |
| Azure SQL Managed Instance | SQL Server lift-and-shift | Expensive, long provisioning times |

## Networking Pricing Traps

| Item | Cost | Mitigation |
|------|------|------------|
| Azure Firewall | ~$1.25/hr (~$912/month) + $0.016/GB | Expensive; consider NSGs + Private Endpoints instead for simple setups |
| Private DNS Zones | $0.50/zone/month + $0.40/million queries | Adds up in complex PE setups with many zones |
| Public IPs (Standard) | $0.005/hr idle (~$3.60/month) | Clean up unused |
| VNet peering (cross-region) | $0.01/GB each way | Keep peered resources in same region when possible |
| Bandwidth out | $0.087/GB after 100GB/month free | Azure CDN or Front Door for serving |

## Recent Changes and New Services

<!-- Update this section when running /cloud-update Azure -->
<!-- Include: new service launches, significant pricing changes, deprecated services, new regions -->

*No updates recorded yet. Run `/cloud-update Azure` to populate.*

## Known Enterprise Patterns

- **Azure Landing Zones** (CAF) are standard for enterprise subscriptions
- **Azure Policy** at management group level is the primary constraint mechanism
- **Hub-spoke VNet topology** with Azure Firewall or NVA is common
- **Entra ID (formerly Azure AD)** for identity, PIM for privileged access
- **Private Endpoints** are increasingly mandated by enterprise security policies
