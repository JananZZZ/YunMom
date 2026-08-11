$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'project_env.ps1')
. (Join-Path $PSScriptRoot 'flutter_toolchain.ps1')
. (Join-Path $PSScriptRoot 'storage_guard.ps1')
$commands = Get-YunMomFlutterCommands -ProjectRoot $projectRoot

Push-Location $projectRoot
try {
    Invoke-YunMomDiskGuard -Operation 'android-debug-build' -ScriptBlock {
        & $commands.Flutter --no-version-check build apk --debug
        if ($LASTEXITCODE -ne 0) { throw "Android debug build failed: $LASTEXITCODE" }
    }
} finally {
    Pop-Location
}
