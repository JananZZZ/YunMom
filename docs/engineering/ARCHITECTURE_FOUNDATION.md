# Architecture Foundation

## Dependency direction

```text
apps/yunmom_app
  ├─ packages/yunmom_design_system
  ├─ packages/yunmom_domain
  │    └─ packages/yunmom_contracts
  └─ packages/yunmom_contracts
```

- `yunmom_contracts` is pure Dart and owns shared version identifiers and future generated Schema APIs.
- `yunmom_domain` is pure Dart and must not import Flutter, Android, iOS, network, storage, or Provider SDKs.
- `yunmom_design_system` may depend on Flutter but only consumes generated output from the governed Token SSOT.
- `cloud_mom` composes adapters and UI; platform differences remain under adapter/native boundaries.

## Non-negotiable boundaries

- Pregnancy Event Store is the only health-domain fact source.
- Commands are typed, revision-checked, idempotent, and atomically produce Events and Receipts.
- Projections, Widget state, indexes, caches, and snapshots are rebuildable.
- Local app behavior and deterministic Safety never depend on login, Gateway, Provider, or entitlement.
- Health正文、Prompt、Response、附件和完整 Context 不进入 backend persistence or logs.
- Tests and repository evidence use synthetic or irreversibly de-identified data only.

## Foundation decisions still pending implementation

Storage engine, exact Crypto Profile, Schema generator, Event envelope codegen, and CI provider
remain implementation tasks governed by ENG-03 through ENG-06. Their interfaces should be frozen
before selecting libraries; a convenient Android implementation cannot become the cross-platform contract.
