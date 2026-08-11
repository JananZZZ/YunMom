#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if [[ -n "${FLUTTER_ROOT:-}" ]]; then
  flutter_cmd="$FLUTTER_ROOT/bin/flutter"
  dart_cmd="$FLUTTER_ROOT/bin/dart"
else
  flutter_cmd="$(command -v flutter)"
  dart_cmd="$(command -v dart)"
fi

"$flutter_cmd" pub get
"$dart_cmd" format --output=none --set-exit-if-changed apps packages
"$dart_cmd" analyze --fatal-warnings --fatal-infos
"$dart_cmd" test packages/yunmom_contracts
"$dart_cmd" test packages/yunmom_domain
"$flutter_cmd" test packages/yunmom_design_system
"$flutter_cmd" test apps/yunmom_app
