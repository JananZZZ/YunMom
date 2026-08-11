# Contract precedence

## Scope-aware authority

There is no single “latest sentence wins” rule. Resolve each claim by its authority and scope:

1. A signed change order that follows the `CHG-001` process may supersede only the contract clauses it names and only after all required domain re-signatures.
2. `docs/YunMom_Engineering_Contracts_V1.0.0/00_DECISION_LEDGER.md` and `01_FINAL_READBACK.md` are the frozen engineering contract. Missing external signatures keep `RELEASE_NOT_APPROVED`; they do not reopen the decision.
3. Current user direction controls unlocked creative choices. A request touching a frozen item is a proposed change, not an override.
4. The product baseline controls only semantics not superseded by the engineering contract.
5. Visual decisions and aesthetic Goldens control identity and taste only. They cannot waive product, medical, privacy, accessibility, deletion, platform, Token, or release rules.
6. For production implementation constants, the current approved `implementation_ready` semantic Token Bundle is the sole source. A provisional Bundle is development scaffolding only. Baseline or Golden colors, sizes, and timings are extraction inputs, not code authority.
7. Existing code and screenshots are evidence of current behavior, not permission to preserve a violation.
8. Inspiration references are mood, material, or composition input only.

If canonical engineering contracts are missing from a standalone package, `product_baseline_reference/` is a dated fallback snapshot. Restrict work to read-only review or explicitly labelled concept exploration and keep all production/release claims blocked.

## Known baseline supersessions

Apply these without reopening them as aesthetic choices:

| Topic | Main decision IDs | Frozen rule that supersedes older baseline language |
|---|---|---|
| Platforms | `BND-003`, `MAT-001` | Android is the first implementation/test focus; iOS and Android share one semantic contract. Both require named real-device evidence before public release. |
| Episode | `EPI-003`, `EPI-004`, `DEL-001` | Use `active`, `delivery_completed`, `closure_confirmation_pending`, `quiet_archive`, and `archived`; permanent deletion is a command. AI/OCR cannot trigger outcome transition. |
| Subjects | `EPI-002`, `FLD-002`, `CFL-001` | An Episode contains `1..N BabySubject`. Mother data belongs to Episode; fetus-specific data belongs to Subject; unknown attribution stays explicit. |
| Risk | `MED-002`, `MED-003`, `MED-008`, `SAFEOPS-001` | R0–R3 and the local deterministic Rule Pack are authoritative. `dismiss != resolve`. AI, Mood, character state, animation, and Widget cannot lower or clear risk. |
| Risk UI | `MED-003`, `A11Y-003`, `ACCU-001` | A compact `!` may be a HOME entry affordance, but symbol, size, and position are not the complete contract. The controlled Safety surface needs explicit severity, what happened, what to do, action, and accessibility semantics. |
| Motion | `A11Y-003`, `TOK-002` | System Reduce Motion is mandatory now. Remove floating, breathing, parallax, flashing, particles, and unnecessary scaling without removing state, confirmation, error, or Safety meaning. |
| Widget | `WGT-001`, `WGT-002`, `WGT-003` | Default off; per-field opt-in; pregnancy week/EDD are sensitive. Read-only local projection, unlocked-App deep link only, no Risk or “safe/no risk,” and no report/medication/mood/diary/AI/Gentle Closure detail. |
| Widget expiry/deletion | `WGT-004`, `DEL-002`, `DEL-003`, `BAK-001` | Hard expiry is at most 24 hours. Withdrawal, Episode switch/archive/delete, Gentle Closure, or delete-all clears projection, cache, preview, and extension key immediately. |
| Token authority | `TOK-001`, `TOK-002`, `TOK-003` | The versioned machine-readable semantic Token Bundle is the only implementation source. Safety/Accessibility priority cannot be themed away; Breaking changes require written governance. |
| Family | `FAM-001`, `FAM-002`, `FAM-003` | V1 family access is same-device controlled entry plus user-generated summary, not realtime cross-device health sharing. Sensitive categories are private by default. |
| AI/provider | `FILE-001`, `PROV-001`, `PROV-002`, `BYOK-001` | No automatic Provider fallback. File egress is foreground and reconfirmed. BYOK is direct from device. Failure states must not imply completion. |
| Queue | `QUE-001`–`QUE-004`, `RES-001` | Safety, medication urgency, and crisis never queue. Partial AI output is unverified and cannot persist a Command. |
| Deletion | `EVT-003`, `DEL-001`–`DEL-003`, `BAK-001` | Permanent deletion overrides normal Event retention and clears Widget, queue, index, attachment, projection, cache, notification, and keys. Do not promise flash-bit overwrite. |
| Accessibility | `A11Y-001`–`A11Y-003`, `ACCU-001` | WCAG 2.2 AA-equivalent mobile baseline, platform maximum text and at least 200%, screen readers, non-gesture alternatives, minimum targets, contrast, focus, and reflow are release gates. |
| Gentle Closure | `EPI-003`, `EPI-004`, `WGT-004`, `ACCM-001`, `ACCU-001` | Clear countdowns, growth/Baby progress, unsuitable Widget/notification content, and celebratory future motion after confirmed transition. Do not default to angel/heaven imagery or future-pregnancy promotion. |
| Evidence | `ACCM-001`, `ACCS-001`, `ACCU-001`, `ACCP-001`, `SIGN-001` | Golden-corpus 100% means that corpus passed, not real-world zero medical error. Visual similarity never substitutes for semantics, accessibility, privacy, or clinical evidence. |

## Conflict behavior

When a request conflicts with a frozen rule:

1. Stop only the conflicting branch.
2. Cite the relevant decision ID when available.
3. Offer the closest compliant direction.
4. Require a written change and the corresponding professional re-signatures before implementation.
5. Mark affected visual assets and transitive dependents `stale_contract_conflict` rather than treating their prior aesthetic approval as current.

Disclaimers, feature flags, prototype labels, creative approval, or a visually attractive result do not waive a red line.
