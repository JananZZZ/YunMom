# V1 Scope / Allowlist

`V1_SCOPE_ALLOWLIST.json` is the machine-maintained scope register for the China-mainland public-store
V1. `SCOPE_FOUR_LISTS.md` is generated and must not be hand-edited.

The four registers are:

1. Phase 1–6 product capabilities and the frozen 30-Skill registry;
2. Rule Packs, Provider/model paths and the formal 22 Field Types;
3. Widget, export/Archive and Android/iOS delivery surfaces;
4. explicit V1 exclusions and `CHG-001` triggers.

Every item uses only the three `SCP-001` scope states. `scope_status` describes the signed V1 target;
`delivery_state` reports what exists now. In particular, `required_present_disabled` is a release
blocker unless the disabled state is the signed safety Kill Switch condition. It is never counted as
delivered merely because a placeholder or feature flag exists.

The allowlist is currently `0.1.0` and unsigned. It remains `RELEASE_NOT_APPROVED`; professional and
release evidence is intentionally absent. Clinical thresholds, Provider/model identities and release
hashes must not be invented to make the register appear complete.

Run through the guarded project environment:

```powershell
dart run tool/scope_ops.dart validate
dart run tool/scope_ops.dart render
dart run tool/scope_ops.dart check
dart run tool/scope_ops.dart self-test
```
