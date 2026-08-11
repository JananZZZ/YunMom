# Legacy migration notes

Current hardened package version: 3.0.0.

Key corrections from earlier packages:

1. Repo Skill uses `.agents/skills/`; `.codex/agents/` is reserved for project custom agents.
2. Package contents must be merged into the actual project root; Codex does not discover a Skill nested below `docs/`.
3. Frozen engineering contracts outrank baseline, Goldens, implementation and creative approval.
4. Review-only tasks remain read-only.
5. User approval creates an aesthetic Golden, not production or release approval.
6. Visual state uses a canonical, idempotent store with generated projections, migration backup and immutable Golden files.
7. Lifecycle and freshness are separate; contract changes can stale prior Goldens without destroying their history.
8. Baby verification requires structured sources, declared scope and qualified independent review.
9. P0 accessibility, R0–R3 Safety, Widget privacy, Gentle Closure, Token governance and visual-evidence privacy are non-compensable gates.
10. Android-first work does not waive iOS/multi-device public-release evidence.

After installation, run `validate` when the canonical program is present, `init` only for a genuinely fresh project, or the explicit `migrate` command when legacy projections exist. Migration first creates and verifies a backup; `init` never silently overwrites legacy state. Unsupported future schemas remain read-only and require an explicit tool upgrade.
