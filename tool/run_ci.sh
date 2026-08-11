#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

local_root="$project_root/.local"
mkdir -p "$local_root/gradle" "$local_root/pub" "$local_root/android/user" \
  "$local_root/android/avd" "$local_root/tmp" "$local_root/audit"
export GRADLE_USER_HOME="$local_root/gradle"
export PUB_CACHE="$local_root/pub"
export ANDROID_USER_HOME="$local_root/android/user"
export ANDROID_AVD_HOME="$local_root/android/avd"
export TMPDIR="$local_root/tmp"
export DART_SUPPRESS_ANALYTICS=true
export FLUTTER_SUPPRESS_ANALYTICS=true

if [[ -n "${FLUTTER_ROOT:-}" ]]; then
  flutter_cmd="$FLUTTER_ROOT/bin/flutter"
  dart_cmd="$FLUTTER_ROOT/bin/dart"
else
  flutter_cmd="$(command -v flutter)"
  dart_cmd="$(command -v dart)"
fi

"$flutter_cmd" --no-version-check pub get
"$dart_cmd" format --output=none --set-exit-if-changed apps packages
"$dart_cmd" analyze --fatal-warnings --fatal-infos
"$dart_cmd" test packages/yunmom_contracts
"$dart_cmd" test packages/yunmom_domain
"$flutter_cmd" --no-version-check test packages/yunmom_design_system
"$flutter_cmd" --no-version-check test apps/yunmom_app
