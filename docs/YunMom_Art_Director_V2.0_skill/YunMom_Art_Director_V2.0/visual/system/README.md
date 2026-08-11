# Governed Visual System

The semantic Token Schema, priority cascade, versioning, and platform mapping contract are active from the first visual implementation. A `bootstrap_provisional`/`proposed` Bundle or `implementation_ready: false` is concept/development scaffolding only: it must not be represented as approved brand values or completed production UI. Production code consumes only a reviewed, generated, `implementation_ready: true` Bundle and never scattered raw constants.

After G1/G3, Codex proposes and, after required review, maintains:
- design_tokens.json
- typography.md
- material_light.md
- layout_grammar.md
- component_primitives.md
- icon_language.md
- motion_tokens.json

The user is not expected to author these files or approve micro-values. Goldens are design inputs; they cannot directly bypass Token review, SemVer, regression, or rollback governance.

`content_sha256` is the SHA-256 of canonical UTF-8 JSON (sorted keys, no insignificant whitespace) containing exactly `token_version`, `contract_decisions`, `source_golden_ids`, `semantic_priority`, `primitive`, and `semantic`. Generators, approval records, and regression evidence bind to that immutable content hash. They live outside the hashed payload so adding attestations cannot silently change the values that generated code consumed. Same-build public-release attestation remains in the external release evidence package; `implementation_ready` means approved for governed generation/consumption, not public `Go`.
