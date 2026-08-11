# Design System Extraction

The user does not need to pre-design token values. A valid semantic Token Schema and priority cascade exist before production UI begins; Codex proposes versioned aesthetic values from approved Goldens without bypassing Token governance.

## Trigger
Run after:
- G1 YunMom Master approval → derive character/material identity
- G3 HOME Canonical approval → derive screen/UI system

## Automatically create/update
Under `visual/system/`:
- `design_tokens.json`
- `typography.md`
- `material_light.md`
- `layout_grammar.md`
- `component_primitives.md`
- `icon_language.md`
- `motion_tokens.json`
- `STYLE_LOCK_REQUIREMENTS.md` / rendered Style Lock Sheet

## Extraction rules
1. Derive aesthetic proposals from valid Goldens, not arbitrary conventions. Goldens never directly rewrite the active Token Bundle.
2. Convert visual relationships into reusable ranges, not brittle one-screen pixel tracing.
3. Preserve hierarchy across screen sizes.
4. Mark each token family as `provisional` or `locked`.
5. Do not ask the user to approve token values individually.
6. If a later aesthetic Golden suggests a better token, create a proposed version, run required review/regression, and mark affected screens stale only when the governed version is accepted.
7. Treat the versioned machine-readable semantic Token repository as the sole implementation Token source; generate Flutter, Rive, iOS Widget, and Android Widget mappings from it.
8. Reject production code containing unapproved raw color, typography, spacing, radius, elevation, opacity, motion, or z-order values.
9. Apply priority: system accessibility/high contrast → Medical Safety/Crisis → error/permission/destructive confirmation → interaction → Mood/Ambient → Task → decoration.
10. Require design, both platform owners, and QA approval for Token changes; add MD for Safety/accessibility semantics and use CHG-001 for Breaking changes. Bind accepted Token output to its generator version and regression evidence.
11. Compute `content_sha256` only from the frozen content payload defined in `visual/system/README.md`. Bind generators, outputs, approvals, and regressions to that hash so adding attestations does not change the values already generated.
12. `implementation_ready` permits governed code generation/consumption only. Same-build public-release signatures remain in the external release evidence package and never become self-referential Token input.

## Token philosophy
Goldens and decisions are art-direction evidence used to derive or change Tokens. The Token repository is the only implementation value source and must never compete with scattered code constants. No Golden or theme may override Safety or accessibility semantics.
