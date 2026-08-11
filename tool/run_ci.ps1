param(
    [switch]$SkipPubGet,
    [switch]$Offline
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'project_env.ps1')
. (Join-Path $PSScriptRoot 'flutter_toolchain.ps1')
. (Join-Path $PSScriptRoot 'storage_guard.ps1')
$commands = Get-YunMomFlutterCommands -ProjectRoot $projectRoot

Push-Location $projectRoot
try {
    Invoke-YunMomDiskGuard -Operation 'strict-ci' -ScriptBlock {
        if (-not $SkipPubGet) {
            $pubArguments = @('--no-version-check', 'pub', 'get')
            if ($Offline) { $pubArguments += '--offline' }
            & $commands.Flutter @pubArguments
            if ($LASTEXITCODE -ne 0) { throw "flutter pub get failed: $LASTEXITCODE" }
        }

        & $commands.Dart format --output=none --set-exit-if-changed apps packages tool
        if ($LASTEXITCODE -ne 0) { throw "dart format check failed: $LASTEXITCODE" }

        & $commands.Dart analyze --fatal-warnings --fatal-infos
        if ($LASTEXITCODE -ne 0) { throw "dart analyze failed: $LASTEXITCODE" }

        & $commands.Dart run tool/plan_ops.dart check
        if ($LASTEXITCODE -ne 0) { throw "engineering plan check failed: $LASTEXITCODE" }

        & $commands.Dart run tool/plan_ops.dart self-test
        if ($LASTEXITCODE -ne 0) { throw "engineering plan self-test failed: $LASTEXITCODE" }

        & $commands.Dart test packages/yunmom_contracts
        if ($LASTEXITCODE -ne 0) { throw "yunmom_contracts tests failed: $LASTEXITCODE" }

        & $commands.Dart test packages/yunmom_domain
        if ($LASTEXITCODE -ne 0) { throw "yunmom_domain tests failed: $LASTEXITCODE" }

        & $commands.Flutter --no-version-check test --no-pub packages/yunmom_design_system
        if ($LASTEXITCODE -ne 0) { throw "yunmom_design_system tests failed: $LASTEXITCODE" }

        & $commands.Flutter --no-version-check test --no-pub apps/yunmom_app
        if ($LASTEXITCODE -ne 0) { throw "yunmom_app tests failed: $LASTEXITCODE" }
    }
} finally {
    Pop-Location
}
