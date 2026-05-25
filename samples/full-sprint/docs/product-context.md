---
agent-notes: { ctx: "product context for URL shortener project", deps: [], state: active, last: "pat@2026-03-10" }
---

# Product Context -- linkr

## What We Are Building

A personal URL shortener. Self-hosted, single-user, runs on a Raspberry Pi or a VPS. Shortens long URLs to `https://yourdomain.tld/abc123` and redirects visitors to the original URL.

## Why

The user wants to share clean, short links in presentations, printed materials, and social media bios without depending on bit.ly or similar third-party services. Self-hosted means no tracking, no rate limits, and no risk of the service shutting down.

## Target Users

One user: the person who deployed it. Visitors who click shortened links are "users" only in the sense that they need a fast, reliable redirect.

## Success Criteria

- **Redirect latency under 50ms** (p99, measured at the application layer). Visitors should not perceive any delay.
- **Short codes are 6 characters** by default (base62, ~56 billion possible codes). Collision probability is negligible at the expected volume.
- **Zero-downtime deployment.** The service should survive `systemctl restart` without dropping in-flight redirects.
- **Works behind a reverse proxy.** Must correctly handle `X-Forwarded-For` and `X-Forwarded-Proto` headers.

## Non-Negotiables

- **No analytics or tracking.** The shortener does not log visitor IP addresses, referrers, or user agents. This is a privacy constraint, not a missing feature.
- **No JavaScript on the redirect page.** Visitors get a 301 redirect, not a page that executes JavaScript before redirecting.
- **SQLite storage.** No external database server. The entire application state is one file.

## Scope for v1

In scope: create short link, redirect to original URL, list all links, delete a link.
Out of scope: custom short codes, link expiration, click counting, bulk import.

## Decision Style

Ship the smallest thing that works. Prefer boring technology. When in doubt, leave it out -- features are easier to add than to remove.
