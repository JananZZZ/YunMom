# YunMom engineering program control

`ENGINEERING_PLAN.json` is the only hand-edited source of engineering-plan state. `PROJECT_MAP.md`
and `TRACEABILITY_MATRIX.md` are generated projections and must never be edited directly.

## Authority

```text
Signed Change Order
  > frozen engineering contracts and Final Readback
  > ENGINEERING_PLAN.json
  > accepted ADR / engineering specifications
  > implementation and tests
  > evidence
  > generated map and traceability views
```

The plan references contract IDs; it does not copy or reinterpret their text. The root
`visual/manifests/visual_program.json` is the only visual-program input. Historical copies inside the
Art Director source package and migration backups are never planning inputs.

## Session start

1. Read `AGENTS.md` and the frozen engineering contracts.
2. Run `dart run tool/plan_ops.dart check` through the guarded project environment.
3. Inspect `git status` and the current `in_progress` or `ready` work item.
4. Claim only the paths listed by that work item. Do not overlap an active path claim.
5. Use the work-item ID in every implementation and evidence commit.

## State transitions

```text
planned -> ready -> in_progress -> verification_pending -> done
```

- `blocked` requires a blocker type, Owner and release condition.
- `deferred` is legal only for `future_explicitly_excluded`; V1 Required work cannot be deferred.
- `superseded` requires both a successor and an ADR or `CHG-001` reference.
- `done` requires source-bound evidence with a SHA-256 digest.
- engineering completion never grants release approval. `RELEASE_NOT_APPROVED` remains until the
  seven required roles sign the same Release Manifest under `SIGN-001`.

## Commands

```powershell
dart run tool/plan_ops.dart validate
dart run tool/plan_ops.dart render
dart run tool/plan_ops.dart check
dart run tool/plan_ops.dart self-test
```

`render` is the only command allowed to update generated planning views. CI uses `check`, which
renders in memory and fails if tracked projections drift. Commands require no network access.

## ADR and contract changes

Implementation choices that remain inside the frozen contract use `docs/engineering/adr/`. A change
to scope, medical meaning, privacy, security, deletion, platform parity or release gates is not an ADR;
it must stop and follow `CHG-001` with the required professional signatures.
