---
agent-notes: { ctx: "debate transcript for SQLite storage decision", deps: [samples/architecture-debate/docs/adrs/0001-storage-backend.md], state: active, last: "archie@2026-03-15" }
---

# Debate: Storage Backend for Personal Notes

**ADR:** docs/adrs/0001-storage-backend.md
**Date:** 2026-03-15
**Participants:** Archie (author) vs Wei (challenger)

## Round 1 -- Wei's Challenges

1. **Multi-device is not optional for long.** Every note-taking app that starts as "single device, local-first" eventually faces the "I want my notes on my phone" request. SQLite fundamentally cannot serve concurrent clients across a network. By choosing SQLite, you are building a migration into the product roadmap whether you acknowledge it or not. Why not start with PostgreSQL and avoid the migration entirely?

2. **FTS5 is a vendor lock-in trap.** You cite FTS5 as an advantage, but it is an SQLite extension with no equivalent in other databases. If you ever migrate to PostgreSQL, you rewrite your entire search layer. You are trading deployment simplicity now for migration complexity later.

3. **"Backup is file copy" is a lie.** Copying a SQLite file while the application is writing to it can produce a corrupted backup. This is a well-documented footgun. Your ADR presents it as an advantage without mentioning the risk.

## Round 2 -- Archie's Responses

1. **On multi-device sync:**
   Fair point -- "users will want sync" is a near-certainty for a notes app. But the question is *when*, not *if*. Starting with PostgreSQL means every user runs a database server on day one to solve a problem that does not exist yet. That is a poor trade-off for a v1 personal tool.

   What I will concede: the ADR should explicitly document the migration path. The application should use a repository pattern so the storage backend is a swappable implementation detail. If sync becomes a priority, we evaluate cr-sqlite (CRDT-based SQLite sync) before jumping to PostgreSQL -- it may solve multi-device without changing the storage engine at all.

   **ADR change:** Adding a "Migration path to PostgreSQL exists" consequence and noting the repository pattern requirement.

2. **On FTS5 portability:**
   Full-text search is inherently backend-specific. PostgreSQL uses `tsvector`/`tsquery` with its own syntax. Elasticsearch has its own DSL. There is no portable full-text search abstraction. The repository pattern would abstract the search interface -- the implementation behind it will be rewritten regardless of which database we start with. FTS5 vs. `tsvector` is not a lock-in argument; it is a "search is always custom" observation.

   **No ADR change.** The concern is real but does not change the decision.

3. **On backup corruption:**
   You are correct. A raw file copy during an active write can produce a corrupt backup. The mitigation is straightforward: use SQLite's backup API (`sqlite3_backup_init` / `sqlite3_backup_step` / `sqlite3_backup_finish`), which safely copies the database while handling in-progress transactions. The app's backup feature should use this API, not `shutil.copy`.

   This is an implementation detail rather than an architectural decision, so I will not add it to the ADR consequences. But it is a valid concern that the implementation team (Sato) should be aware of.

   **No ADR change.** Noted for implementation.

## Resolution

- **Resolved:**
  - Multi-device sync: acknowledged as a future concern. ADR updated with migration path consequence and repository pattern requirement.
  - FTS5 portability: not a meaningful lock-in beyond what any search backend introduces. No ADR change.
  - Backup safety: valid implementation concern. SQLite backup API is the correct approach. No ADR change; flagged for implementation.

- **Accepted risks:**
  - Multi-device sync will require either cr-sqlite or a storage migration. This is deferred complexity, accepted as a conscious trade-off.
  - Schema migrations in SQLite are more limited than PostgreSQL. The "copy table" pattern is a known workaround.

- **ADR changes:**
  - Added "Migration path to PostgreSQL exists" to Neutral consequences.
  - Added repository pattern recommendation.
  - Expanded the multi-device sync negative consequence with more detail.
  - Added Debate Summary section referencing this transcript.
