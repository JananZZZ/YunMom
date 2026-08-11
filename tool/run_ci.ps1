param(
    [switch]$SkipPubGet
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$toolchainFile = Join-Path $projectRoot 'toolchains\toolchain.json'

function Resolve-FlutterRoot {
    if ($env:FLUTTER_ROOT) {
        return $env:FLUTTER_ROOT
    }

    $flutterOnPath = Get-Command flutter -ErrorAction SilentlyContinue
    if ($flutterOnPath) {
        return Split-Path -Parent (Split-Path -Parent $flutterOnPath.Source)
    }

    if (Test-Path -LiteralPath $toolchainFile) {
        $toolchain = Get-Content -LiteralPath $toolchainFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($toolchain.flutter.root) {
            return ($toolchain.flutter.root -replace '/', '\')
        }
    }

    throw 'Flutter was not found via FLUTTER_ROOT, PATH, or toolchains/toolchain.json.'
}

$flutterRoot = Resolve-FlutterRoot
$flutter = Join-Path $flutterRoot 'bin\flutter.bat'
$dart = Join-Path $flutterRoot 'bin\dart.bat'
if (-not (Test-Path -LiteralPath $flutter) -or -not (Test-Path -LiteralPath $dart)) {
    throw "Invalid Flutter root: $flutterRoot"
}

Push-Location $projectRoot
try {
    if (-not $SkipPubGet) {
        & $flutter pub get
        if ($LASTEXITCODE -ne 0) { throw "flutter pub get failed: $LASTEXITCODE" }
    }

    & $dart format --output=none --set-exit-if-changed apps packages
    if ($LASTEXITCODE -ne 0) { throw "dart format check failed: $LASTEXITCODE" }

    & $dart analyze --fatal-warnings --fatal-infos
    if ($LASTEXITCODE -ne 0) { throw "dart analyze failed: $LASTEXITCODE" }

    & $dart test packages/yunmom_contracts
    if ($LASTEXITCODE -ne 0) { throw "yunmom_contracts tests failed: $LASTEXITCODE" }

    & $dart test packages/yunmom_domain
    if ($LASTEXITCODE -ne 0) { throw "yunmom_domain tests failed: $LASTEXITCODE" }

    & $flutter test packages/yunmom_design_system
    if ($LASTEXITCODE -ne 0) { throw "yunmom_design_system tests failed: $LASTEXITCODE" }

    & $flutter test apps/yunmom_app
    if ($LASTEXITCODE -ne 0) { throw "yunmom_app tests failed: $LASTEXITCODE" }
} finally {
    Pop-Location
}
