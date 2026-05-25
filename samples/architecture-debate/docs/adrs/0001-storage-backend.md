---
agent-notes: { ctx: "ADR for SQLite storage in personal notes app", deps: [], state: active, last: "archie@2026-03-15", key: ["Wei debate caused migration-path addition"] }
---

# ADR-0001: Storage Backend for Personal Notes

## Status

Accepted

## Context

We are building a personal note-taking app (single user, local-first, desktop). The app needs to store notes with titles, body text (Markdown), tags, and timestamps. Expected volume is hundreds to low thousands of notes over several years of use.

We need to choose a storage backend. The main candidates are:

1. **SQLite** -- embedded relational database, single-file storage
2. **PostgreSQL** -- full client-server relational database
3. **Plain files** -- one Markdown file per note, metadata in frontmatter

## Decision

**Use SQLite.**

SQLite is the right fit for a single-user, local-first desktop app with modest data volume:

- **Zero deployment complexity.** No server process, no connection string, no credentials management. The database is a single file in the user's data directory.
- **Full SQL.** Tag filtering, full-text search (via FTS5), and date-range queries are straightforward. Plain files would require building a custom indexing layer.
- **Battle-tested at this scale.** SQLite handles millions of rows comfortably. Our hundreds-to-thousands of notes are well within its sweet spot.
- **Backup is file copy.** Users can back up their data by copying one file. No `pg_dump`, no export step.

PostgreSQL was rejected because it introduces operational overhead (running a server, managing connections, handling credentials) that provides no benefit for a single-user desktop app. The features PostgreSQL offers over SQLite (concurrent writes, network access, row-level security) are irrelevant here.

Plain files were rejected because they require building query infrastructure from scratch. Searching by tag across 1,000 Markdown files is a linear scan unless we build and maintain a secondary index -- which is just building a worse SQLite.

## Consequences

### Positive

- No external dependencies at deployment time. The app is fully self-contained.
- The SQLite file can be inspected with standard tools (`sqlite3` CLI, DB Browser for SQLite) -- useful for debugging and user data portability.
- FTS5 gives us full-text search without adding Elasticsearch or similar.

### Negative

- **No multi-device sync out of the box.** SQLite does not support concurrent access from multiple machines. If multi-device sync becomes a requirement, we will need either a sync layer (e.g., cr-sqlite for CRDTs) or a migration to a client-server database.
- **Schema migrations require care.** SQLite's `ALTER TABLE` is limited compared to PostgreSQL. Complex migrations may need the "copy table" pattern.

### Neutral

- **Migration path to PostgreSQL exists.** If requirements change (multi-user, network access, concurrent writes), the SQL is standard enough that migration to PostgreSQL is feasible. The application should use a repository pattern so the storage backend can be swapped without rewriting business logic. _(Added after Wei's challenge -- see Debate Summary.)_

## Debate Summary

Wei challenged this ADR on 2026-03-15. Two rounds of debate were conducted per the Adversarial Debate Protocol. Key outcomes:

1. **Multi-device sync concern (Wei).** Wei argued that single-device is a temporary constraint -- users will eventually want their notes on their phone. Archie acknowledged this as a real risk but maintained that designing for multi-device now (via PostgreSQL or a sync layer) adds complexity with no current user demand. Compromise: document the migration path explicitly and use a repository pattern to keep the door open. _(This consequence was added to the ADR.)_

2. **FTS5 portability concern (Wei).** Wei noted that FTS5 is SQLite-specific and would not carry over to PostgreSQL. Archie responded that full-text search implementation is backend-specific regardless -- PostgreSQL's `tsvector` is equally non-portable. The repository pattern would abstract this. _(No ADR change -- concern was addressed.)_

3. **Backup corruption risk (Wei).** Wei pointed out that "backup is file copy" is only safe if the copy is made while no writes are in progress. Archie agreed and noted that SQLite's backup API (`sqlite3_backup`) handles this correctly. The app should use the backup API rather than raw file copy for programmatic backups. _(Acknowledged as implementation detail, not an ADR-level concern.)_

Full debate transcript: `docs/tracking/2026-03-15-notes-app-debate.md`
