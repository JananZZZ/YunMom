# M1-WP01 V1 scope-control evidence

- Source commit: `3d03e3cb6bde4c426cb160c1f6a96f666d8d4b12`
- Captured: `2026-08-11T19:00:51+08:00`
- Data class: `no_health_content`
- Review roles: `PO`, `TECH`, `QA`

Result: `pass` for the engineering scope-control mechanism.

- four machine-readable Scope/Allowlist registers contain `111` entries;
- all Phase 1–6 feature groups are present;
- the frozen Skill registry contains exactly `30` named entries;
- the formal Field Type registry contains exactly `22` entries, retaining `boolean`/`tristate` and
  `multienum`/`tag` separately;
- Rule Pack, Provider/model, Widget, export/Archive and Android/iOS platform paths are explicit;
- ten future capabilities are explicitly excluded and bound to `CHG-001`;
- `required_present_disabled` entries require a named gate and remain release blockers;
- negative tests reject duplicates, unknown contracts, missing Skills, malformed exclusions, disabled
  items without gates and a false `RELEASE_APPROVED` transition;
- complete offline Strict CI passed with `6.06 MiB` persistent C-drive growth, below the `100 MiB`
  hard stop.

The working allowlist is version `0.1.0` and unsigned. This evidence validates structure and contract
coverage only; it does not provide the MD, LEGAL, SEC, ETHICS or same-build release signatures needed
to enable currently gated capabilities or approve public release.
