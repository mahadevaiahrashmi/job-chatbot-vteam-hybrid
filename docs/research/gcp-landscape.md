---
agent-notes: { ctx: "GCP service landscape for cloud specialists", deps: [.claude/agents/cloud-architect.md, .claude/agents/cloud-costguard.md, .claude/agents/cloud-netdiag.md], state: active, last: "cloud-architect@2026-02-12" }
---

# GCP Service Landscape

> **Last updated:** 2026-02-12
> **Updated by:** Initial seed from template
>
> Run `/cloud-update GCP` to refresh this file with current information.

This file is read by the cloud specialist agents (`cloud-architect`, `cloud-costguard`, `cloud-netdiag`) to supplement their built-in knowledge when operating in GCP mode. It captures the current state of GCP services, pricing, and gotchas that may change over time.

## Compute Options

| Service | Best for | Key limits/gotchas |
|---------|----------|-------------------|
| Cloud Functions (2nd gen) | Event-driven, short-lived tasks | Built on Cloud Run, 60min max timeout, 32GB memory max |
| Cloud Run | Containers with scale-to-zero | Cold starts on min-instances=0, custom domains need verification |
| GKE Autopilot | Kubernetes without node management | $0.10/vCPU/hr + $0.01/GB/hr for pods, no node-level access |
| GKE Standard | Full Kubernetes with node control | Free control plane for one zonal cluster, $0.10/hr for regional |
| App Engine | PaaS (legacy feel, still supported) | Standard env has limited runtimes, Flexible env is just containers |
| Compute Engine | Full control, GPU, TPU | You manage everything; sustained use discounts on N1/N2/C2 (NOT E2) |

## Database Options

| Service | Best for | Key limits/gotchas |
|---------|----------|-------------------|
| Cloud SQL | PostgreSQL/MySQL/SQL Server, managed | HA doubles cost, storage charged on stopped instances |
| AlloyDB | High-performance PostgreSQL | Expensive, columnar engine is powerful for analytics |
| Firestore | Document/NoSQL, serverless | Free tier generous (1GB, 50K reads/day), pricing per operation |
| Cloud Spanner | Global relational, strong consistency | Minimum ~$65/month for smallest instance, powerful but expensive |
| Memorystore | Redis/Memcached caching | No free tier, basic tier lacks replication |
| Bigtable | Wide-column, high throughput | Minimum 1 node (~$468/month), not for small workloads |

## Networking Pricing Traps

| Item | Cost | Mitigation |
|------|------|------------|
| Cloud NAT | $0.045/hr per gateway + $0.045/GB | Similar to AWS NAT Gateway; use Private Google Access for Google APIs |
| Egress (internet) | $0.12/GB (premium tier) or $0.085/GB (standard tier) | Use standard tier if latency isn't critical; Cloud CDN for serving |
| Egress (cross-region) | $0.01/GB within continent, more across | Keep resources in same region |
| Cloud Load Balancer | ~$18/month minimum (forwarding rule) | Expensive for dev; skip LB and use Cloud Run URLs directly for dev |
| Static external IP (idle) | $0.01/hr (~$7.20/month) | Clean up unused |

## Recent Changes and New Services

<!-- Update this section when running /cloud-update GCP -->
<!-- Include: new service launches, significant pricing changes, deprecated services, new regions -->

*No updates recorded yet. Run `/cloud-update GCP` to populate.*

## Known Enterprise Patterns

- **Organization, Folders, Projects** hierarchy determines policy inheritance
- **Shared VPC** is the dominant enterprise networking pattern (host project owns VPC)
- **VPC Service Controls** perimeters protect API access (often the most confusing security layer)
- **Organization Policies** at org/folder level are the primary constraint mechanism
- **Workload Identity Federation** replacing service account key export
- **BeyondCorp Enterprise** for zero-trust access
