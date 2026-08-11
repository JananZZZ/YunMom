# Visual state tool reference

`visual/manifests/visual_program.json` is the only mutable visual-program source of truth. `DESIGN_STATE.json`, registries, and `DECISION_LOG.md` are generated projections. Never hand-edit them during ordinary work.

## Invocation contract

Resolve both roots first, then invoke the Skill-relative script from any working directory:

```text
python -B <SKILL_DIR>/scripts/visual_ops.py --project-root <PROJECT_ROOT> <command> ...
```

Pass a stable `--operation-id OP-...` to every command that writes the canonical operation journal. Retrying the same ID with the same payload returns the committed result; reusing it with a different payload fails. `repair-projections` is the deliberate exception: it rebuilds disposable projections without changing canonical state and therefore has no operation ID. Run `<command> --help` before constructing an unfamiliar mutation.

## Lifecycle commands

- `status`: read canonical lifecycle, freshness, evidence tier, slots, drift, and errors.
- `validate`: fail on canonical, file, Token, evidence, migration, or projection invalidity. `--no-fail` is diagnostic only and never grants acceptance.
- `init`: only for a genuinely fresh project with no legacy visual state.
- `migrate`: explicitly back up and migrate supported legacy v2 projections. It never doubles as `init`.
- `repair-migration-hashes`: narrow, journaled compatibility repair for the known legacy backup-manifest hash bug; never use it for general corruption.
- `repair-projections`: rebuild disposable projections from a valid canonical program. It never repairs canonical data.

## Asset and decision commands

- `register-asset`: registers an immutable source file under `visual/candidates/`, `visual/derived/`, or `visual/production/`. Classification and content origin must be explicit and repository-safe. `confirmed_per_send` requires a receipt. Rights default to unverified and therefore block Golden promotion. Every local prompt or reference must have a sibling `<stem>.provenance.json` bound to its exact path/hash, privacy, egress, and rights; start from `assets/templates/provenance_sidecar.json`.
- `record-decision`: records feedback, rejection, change, or an exact user aesthetic approval. Approval must name a finalist/provisional asset; it is not a release signature.
- `record-review`: records one hash/version-bound independent review. A `PASS` must include every applicable hard gate with repeated `--gate`; an empty or partial gate set fails.
- `mark-stale`: records a structured reason without destroying lifecycle history. Select source, dependents, or both explicitly.
- `promote-golden`: creates an immutable content-addressed aesthetic Golden after the exact decision, review, medical, privacy, rights, and type gates pass. Use a named slot only for canonical Master pointers or `baby_anchor:<stage>`; omit `--slot` (or use `none`) for governed content Goldens such as Safety, Gentle Closure, Widget, motion, or components. A slotless Golden is still fully reviewed and immutable, but it neither replaces a Master pointer nor stales that pointer's dependents. Golden promotion cannot create production or release approval.

Base PASS gate names are machine-enforced:

- brand: `BRAND_DISTINCTIVENESS`, `BRAND_CONSISTENCY`
- visual: `VISUAL_HIERARCHY`, `VISUAL_COHERENCE`, `NON_TEMPLATE_QUALITY`
- production: `IMPLEMENTATION_FEASIBILITY`, `TOKEN_COMPLIANCE`, `PERFORMANCE_RISK`
- medical: `MEDICAL_SCOPE_ACCURACY`, `SAFETY_SEVERITY_PRESERVED`, `NO_DIAGNOSIS_TREATMENT`
- accessibility-safety: `WCAG_2_2_AA`, `SCREEN_READER`, `TEXT_SCALE_200`, `REDUCE_MOTION`, `NON_COLOR_SAFETY`

Type-specific gates are additional. Ask the command to validate the exact record; do not invent substitutes.

## Medical evidence commands

- `add-medical-source`: binds an asset to dated jurisdiction/population/gestational scope and content-addressed source evidence. A URL or figure locator without a source checksum or archived-document hash is insufficient. Every archived local source needs the sibling provenance sidecar; its rights/authorization must permit the use, and a public-domain claim needs an immutable `PUBLIC-CLINICAL-SOURCE:` evidence reference.
- `verify-medical`: requires a qualified independent human/external specialist, exact source IDs, scope, credential reference, and a local hash-bound attestation. The attestation also needs a sibling privacy-safe provenance sidecar. A custom agent or subagent can review adversarially but can never issue `VERIFIED`.

`baby`, `safety`, and `gentle_closure` assets are automatically medical-applicable; a caller cannot evade this by omitting a flag.

## Implementation and release evidence

- `record-evidence`: records one independent, artifact-hash-bound result with source Tag, Build hash, platform, OS, device, test suite, verifier identity/role, credential or attestation, and repository-safe privacy metadata.
- `advance-evidence`: advances only `integrated` → `matrix_accepted` → `release_signed` for the exact same source Tag and Build hash.

Matrix acceptance requires current integration, production, accessibility, and matrix evidence, distinct qualified verification, and both Android and iOS for dual-platform visual types. Release signing requires distinct, same-build `PO`, `TECH`, `QA`, `MD`, `LEGAL`, `SEC`, and `ETHICS` attestations. Distinctness is checked by signed/credential artifact hash, not filename, so byte-identical copies and hard links cannot impersonate independent evidence. The tool must also reject one-person self-signing, a changed Build, or unsafe evidence.

## Contact sheets

Use:

```text
python -B <SKILL_DIR>/scripts/build_contact_sheet.py --project-root <PROJECT_ROOT> --out visual/reviews/<new-name>.png <registered-image> [...]
```

Inputs must be current registered assets whose on-disk hashes and privacy policy still match canonical state. Output stays under `visual/reviews/`, never overwrites, and includes a provenance sidecar bound to the canonical program hash. A pure review request does not authorize creating a contact sheet.

## Completion rule

After every authorized mutation, run `validate` and `status`. Report the exact evidence stage and remaining blockers. `release_status: not_approved` is the correct state until same-build professional signatures genuinely exist.
