# YunMom Art Director 3.0.0 hardening audit

The historical V2 audit is superseded by this implementation and verification pass dated 2026-08-11.

## Corrected mechanisms

- Codex discovery uses project-root `.agents/skills/yunmom-art-director`, root `AGENTS.md`, Skill `agents/openai.yaml`, and read-only project reviewers under `.codex/agents`.
- Review/critique/audit remains read-only; create/edit/implement is scoped mutation; user promotion creates only an immutable aesthetic Golden.
- Frozen engineering contracts outrank baseline prose, taste, Goldens, Tokens, code, screenshots, and inspiration references.
- One canonical `visual_program.json` drives generated projections, operation-id replay, explicit migration/repair, lifecycle/freshness separation, dependency invalidation, and content-addressed Golden storage.
- Assets, prompts, references, medical sources, attestations, and QA evidence are path/hash bound with explicit privacy, egress, provenance, and rights gates. Real-sensitive, unknown, or unclassified repository evidence fails closed.
- Managed paths reject escape, NTFS alternate streams, symlink/reparse traversal, and hard links. Contact Sheet applies the same rules, bounded resources, ICC-to-sRGB handling, deterministic sidecar evidence, and atomic no-overwrite output.
- Migration backups validate their manifest plus every declared file, size, hash, missing/extra entry, and path boundary.
- Medical-applicable Baby, Safety, and Gentle Closure art requires content-addressed sources and a qualified independent human attestation; a model review cannot self-certify.
- Safety/Gentle Closure/Widget/motion/component assets can become fully governed slotless content Goldens; canonical Master slots remain strict pointers with explicit replacement semantics.
- Integration, matrix, and release evidence bind one source Tag/Build. Byte-identical copied attestations cannot impersonate independent signers. Dual-platform visual types require Android and iOS matrix evidence, and release evidence requires the seven frozen roles.
- Token readiness cross-checks actual current Goldens, evidence, generator mappings, regression artifacts, approvals, and content hashes. Provisional Tokens remain development scaffolding.

## Executed verification

- System Python 3.14 self-test: PASS, including the friendly no-Pillow branch.
- Bundled Python 3.12.13 with Pillow 12.2.0 self-test: PASS, including Contact Sheet positive and negative paths.
- Full self-test covers fresh init, legacy migration, idempotent replay, projection repair, path/ADS/link rejection, review hard gates, privacy and rights failures, medical-source/attestation provenance, Safety and Gentle Closure slotless Golden flows, same-build matrix/release gates, duplicate-attestation rejection, backup tamper/extra/path failures, and Token fail-closed behavior.
- All four Python scripts parse; every `visual_ops.py` subcommand help path loads.
- Source canonical validation: PASS at revision 2 with no projection drift; current Gate is `G1_YUNMOM_MASTER` and release remains `not_approved`.
- Markdown links, JSON, TOML, Skill frontmatter, and Skill metadata are validated again before packaging.

## Distribution gate

`MANIFEST.json` v2 is the immutable package inventory. A handoff is invalid unless both commands succeed after every final edit:

```text
python -B <SKILL_DIR>/scripts/verify_package_manifest.py --package-root <PACKAGE_ROOT>
python -B <SKILL_DIR>/scripts/verify_package_manifest.py --package-root <PACKAGE_ROOT> --include-seeds
```

The installed project intentionally copies only `AGENTS.md`, `.agents/`, `.codex/`, and `visual/`; the distribution manifest and fallback baseline remain in the source package.

## Honest boundary

This system makes visual work convergent, auditable, and fail-closed, but no Skill can mathematically guarantee taste, clinical correctness, accessibility, or public-release readiness. Human MD/LEGAL/SEC/TECH/QA/ETHICS/PO evidence remains authoritative. Android-first development is allowed; iOS and multi-device evidence are still required before public Go/No-Go. Until that same-build package exists, preserve `RELEASE_NOT_APPROVED`.
