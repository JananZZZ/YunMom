# Sprint 0 verification

Captured: `2026-08-11`  
Status: `FOUNDATION_READY_FOR_FIRST_VERTICAL_SLICE`  
Release status: `RELEASE_NOT_APPROVED`

## Verified host toolchain

- Flutter `3.44.9` stable and Dart `3.12.2`.
- Android Studio `Quail 3 | 2026.1.3 Patch 1` at `C:/dev/android-studio`.
- Android SDK platform/build-tools `36`, platform-tools `37.0.1`, command-line tools `22.0`.
- Flutter uses Android Studio JBR `25.0.2`; the general user `JAVA_HOME` remains JDK `22.0.2`.
- Android SDK licenses are accepted.
- User-level environment variables and PATH are installed for future projects, not vendored into YunMom.

`flutter doctor -v` recognizes Flutter, Android Studio, the Android toolchain and licenses. Its only
network finding was a timeout probing `https://maven.google.com/`; the actual Android build completed
through the current local development proxy.

## Verified repository gates

- Root Pub workspace dependency resolution: pass.
- `dart format --output=none --set-exit-if-changed`: pass.
- `flutter analyze --fatal-warnings --fatal-infos`: pass.
- Contract, domain, design-system and app tests: pass.
- YunMom visual canonical state validation: pass, canonical revision `2`.
- Visual release state remains correctly fail-closed at `G1_YUNMOM_MASTER` / `not_approved`.
- Raw local RAG material is ignored; only its policy README is eligible for Git.

## Storage-guard re-verification

The storage guard implementation is bound to source commit
`aedd217fd9f899bc9e0fdb0961c8704ab87ef2a1` (`M0-WP01`). It supersedes the earlier failed
strict-CI observation without deleting that local audit record.

Commands executed on `2026-08-11`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tool\verify_storage_guard.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\tool\run_ci.ps1 -Offline
```

Results:

- storage-guard self-test: pass; observed and persistent `C:` growth `0 MiB`;
- offline Strict CI: pass; format, analysis and all four test suites passed;
- Strict CI observed and persistent `C:` growth: `3.46 MiB`, below the `100 MiB` hard limit;
- project dependency, Gradle, Android user/AVD and audit paths resolved under `.local/`;
- Windows compatibility temp resolved to `D:/DevCaches/YunMom/tmp`;
- no SDK, IDE, emulator image or toolchain installation/upgrade was performed.

The ignored `.local/audit/storage-guard.jsonl` is operational evidence only. Durable evidence is this
source-bound readback plus the repository scripts and policy in the referenced commit.

## Engineering planning control-plane verification

The planning control-plane implementation is bound to source commit
`a0b75e8651ff28b4f4b3d3027128a06ead67d537` (`M0-WP02`). The verification was executed after that
commit, with no engineering-source changes present; concurrent visual-line changes were outside the
CI input and were not included in the commit.

Command executed on `2026-08-11`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tool\run_ci.ps1 -Offline
```

Results:

- machine plan validation and generated-view drift check: pass;
- planning negative self-tests: pass for duplicate IDs, unknown contract IDs, dependency cycles,
  Required deferral, missing done evidence, authority hash drift, visual revision drift and active path
  overlap;
- repository format and fatal analysis gates: pass;
- contract, domain, design-system and app tests: pass;
- Strict CI observed and persistent `C:` growth: `2.44 MiB`, below the `100 MiB` hard limit;
- no SDK, IDE, emulator image or toolchain installation/upgrade was performed.

This evidence approves only the local engineering planning controls. It does not approve product
release or satisfy any MD, LEGAL, SEC, ETHICS or public-device evidence gate.

Run the repository gate from PowerShell without changing the machine-wide execution policy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tool\run_ci.ps1
```

## Android build proof

Command:

```powershell
flutter build apk --debug
```

Result:

- Path: `apps/yunmom_app/build/app/outputs/flutter-apk/app-debug.apk`
- Bytes: `146084310`
- SHA-256: `cf5b81f6e11ed719d21634a44e2aa1d6b4bcfc4478a094febd6865e37f7c0f75`

This is a development artifact, not a signed release candidate. It is intentionally ignored by Git.

## One-time host action still required

The AVD `YunMom_Android_36` exists, but acceleration is unavailable until the Android Emulator
Hypervisor Driver is installed once from an Administrator terminal:

```powershell
& 'C:\dev\android-sdk\extras\google\Android_Emulator_Hypervisor_Driver\silent_install_safe.bat'
```

After Windows accepts the driver, verify it with:

```powershell
& 'C:\dev\android-sdk\emulator\emulator-check.exe' accel
```

This does not block source work, analysis, unit tests, or Android APK builds.

## Evidence boundary

This verification proves only the current Windows/Android development foundation. It is not the R10
device/OS matrix, iOS evidence, clinical validation, privacy/security sign-off, accessibility acceptance,
store readiness, or public-release approval.
