# YunMom repository instructions

## Mandatory visual routing

- Any task that creates, edits, implements, evaluates, or extends YunMom UI, Widget, character/Baby art, iconography, illustration, visual copy presentation, motion/Rive, ambient/weather visuals, screenshots, visual QA, accessibility presentation, Safety, or Gentle Closure visuals must use `$yunmom-art-director`.
- Pure review/critique/audit is read-only. Do not initialize state, save briefs, edit files, or record review data unless the user also asks for changes.
- For modifying visual work, use the Skill-relative scripts and explicitly pass the project root. Never assume the current working directory contains `scripts/`.

## Authority and durable memory

- Signed change orders and `docs/YunMom_Engineering_Contracts_V1.0.0/` outrank user taste, older baseline text, Goldens, code, screenshots, and inspiration references.
- Current user direction controls unlocked creative choices only. Aesthetic approval cannot waive Medical Safety, privacy, accessibility, deletion, platform parity, Token governance, Gentle Closure, or professional release gates.
- Read `visual/state/DESIGN_STATE.json`, `visual/state/APPROVED_INVARIANTS.md`, `visual/decisions/DECISION_LOG.md`, and `visual/manifests/asset_registry.json` as durable visual memory. Use only the current approved `implementation_ready` semantic Tokens as production constants; provisional Tokens are governed scaffolding, never a production-completion claim.
- Never overwrite a Golden. Contract change, professional-review failure, invalidated evidence, or parent replacement may mark it and its dependents stale even without new taste feedback.

## Working relationship

- The user is the creative approver, not the production designer. Decide pixels, radii, blur, shader parameters, animation timings, export formats, layer slicing, and implementation details yourself.
- Ask only for genuine brand forks, clear finalist preference, missing required external evidence, or a proposed change to a frozen contract.
- For S/A work, use independent read-only reviewers before presenting finalists. Reviewer scores never compensate for a hard-gate failure.

## Hard boundaries

- Baby production claims require versioned medical sources, declared gestational scope, structured comparison, and qualified independent review. Otherwise remain `unverified`.
- Persisted screenshots/prompts/contact sheets use synthetic or irreversibly de-identified data. Real sensitive health content never enters repository evidence or filenames. External egress requires both an approved exact Provider/model/modality/region/retention path and explicit per-send confirmation; either missing gate fails closed.
- Dynamic text, health data, controls, semantics, and navigation stay real Flutter/native UI; generated full-screen mockups are composition references only.
- Android is the current implementation/test focus, but the iOS/Android contract is unified. Android evidence never satisfies the public-release iOS/device matrix.
- User approval promotes only an aesthetic Golden. Until same-build professional evidence and joint signatures exist, keep `RELEASE_NOT_APPROVED`.

## Quality bar

Produce original, premium, warm, calm, low-pressure YunMom work—not a generic Flutter demo or generic mother-and-baby template. Never call work perfect, medically verified, accessible, production-ready, or release-ready without matching evidence.

## Machine storage safety

- Do not install, upgrade, move, delete, or clean machine-level software, SDKs, emulators, caches, registry entries, environment variables, junctions, or user-profile data without explicit approval for the exact paths and expected disk impact.
- New reusable development software belongs under `D:/DevTools`; never add a new SDK, IDE, emulator image, or toolchain to `C:`.
- YunMom-specific dependencies, build caches, Android user data, AVD data, temporary files, diagnostics, and generated artifacts must use the project-local `.local/` boundary or another explicitly approved non-`C:` path.
- Run Flutter/Dart verification and Android builds through the guarded scripts in `tool/`. Do not run `flutter upgrade`, `sdkmanager --install`, IDE auto-installers, or equivalent download commands as part of ordinary development.
- Before and after a guarded operation, measure `C:` free space. More than 100 MiB of unexplained growth is a hard stop and must be reported; never auto-delete data to compensate.
- Read-only disk inspection is allowed. Any machine mutation requires a path list, expected size, rollback plan, and user confirmation first.
