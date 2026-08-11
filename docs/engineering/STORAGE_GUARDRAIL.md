# Development storage guardrail

Status: `ENFORCED_FOR_PROJECT_SCRIPTS`

## Boundary

YunMom development must not silently grow `C:`. Existing toolchains remain untouched, but ordinary
project dependency resolution, tests, Android user state, AVD state, temporary files and build caches
are redirected to the ignored project-local `.local/` directory.

Windows Flutter test subprocesses use the ASCII compatibility path `D:/DevCaches/YunMom/tmp` because
the repository path contains non-ASCII characters. This is the only current project-cache exception;
it remains off `C:` and contains only disposable temporary data.

The machine-readable policy is `tool/storage_policy.json`. It currently enforces:

- no new tool or SDK installation on `C:`;
- future reusable tools under `D:/DevTools` and reusable cross-project caches under `D:/DevCaches`;
- YunMom project caches under `.local/`;
- at least 40 GiB free on `C:` before a guarded operation;
- at least 20 GiB free on the project drive;
- a hard stop when a guarded operation observes more than 100 MiB of `C:` growth.

The guard records the first observed result. If it exceeds the limit, it samples for another ten seconds
and fails only when growth remains above the limit; this avoids treating a short unrelated Windows
allocation as a persistent Codex write. It cannot roll back unrelated writes. When persistent growth
exceeds the limit, stop, inspect and report. Never auto-delete data to compensate.

## Approved entry points

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tool\verify_storage_guard.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\tool\run_ci.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\tool\run_ci.ps1 -Offline
powershell -NoProfile -ExecutionPolicy Bypass -File .\tool\build_android_debug.ps1
```

Use `-Offline` when the project-local Pub cache has already been seeded. Flutter tests use `--no-pub`
after the root workspace resolution so they cannot start a second implicit dependency download.

Direct `flutter upgrade`, `sdkmanager --install`, Android Studio auto-installers and unreviewed build
commands are outside the project contract. Machine-level installation, migration and cleanup always
require an exact path list, size estimate, rollback plan and explicit user approval.
