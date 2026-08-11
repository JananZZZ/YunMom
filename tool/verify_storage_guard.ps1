$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'project_env.ps1')
. (Join-Path $PSScriptRoot 'storage_guard.ps1')

$expectedRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot '.local'))
$checks = [ordered]@{
    GRADLE_USER_HOME = $env:GRADLE_USER_HOME
    PUB_CACHE = $env:PUB_CACHE
    ANDROID_USER_HOME = $env:ANDROID_USER_HOME
    ANDROID_AVD_HOME = $env:ANDROID_AVD_HOME
    TEMP = $env:TEMP
    TMP = $env:TMP
}

foreach ($entry in $checks.GetEnumerator()) {
    $candidate = [System.IO.Path]::GetFullPath($entry.Value)
    $prefix = $expectedRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $isApprovedWindowsTemp =
        $entry.Key -in @('TEMP', 'TMP') -and
        $candidate.StartsWith('D:\DevCaches\YunMom\', [System.StringComparison]::OrdinalIgnoreCase)
    if (-not $candidate.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase) -and
        -not $isApprovedWindowsTemp) {
        throw "$($entry.Key) escaped project-local storage: $candidate"
    }
    if (-not (Test-Path -LiteralPath $candidate -PathType Container)) {
        throw "$($entry.Key) directory was not created: $candidate"
    }
}

$forbidden = rg -n --glob '*.ps1' --glob '*.sh' 'flutter\s+upgrade|sdkmanager(.bat)?\s+.*--install' $PSScriptRoot
if ($LASTEXITCODE -eq 0 -and $forbidden) {
    throw "Forbidden automatic installer command found:`n$forbidden"
}
if ($LASTEXITCODE -gt 1) {
    throw "rg storage-policy scan failed: $LASTEXITCODE"
}

Invoke-YunMomDiskGuard -Operation 'storage-guard-self-test' -ScriptBlock {
    $probe = Join-Path $env:YUNMOM_PROJECT_LOCAL_ROOT 'tmp\storage-guard-probe.txt'
    [System.IO.File]::WriteAllText($probe, 'project-local-only')
    Remove-Item -LiteralPath $probe -Force
}

Write-Output 'YunMom storage guard: OK'
$checks.GetEnumerator() | ForEach-Object {
    Write-Output ("{0}={1}" -f $_.Key, $_.Value)
}
