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
