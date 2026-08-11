Set-StrictMode -Version Latest

$script:YunMomProjectRoot = Split-Path -Parent $PSScriptRoot
$script:YunMomStoragePolicyPath = Join-Path $PSScriptRoot 'storage_policy.json'

if (-not (Test-Path -LiteralPath $script:YunMomStoragePolicyPath -PathType Leaf)) {
    throw "Missing storage policy: $script:YunMomStoragePolicyPath"
}

$script:YunMomStoragePolicy =
    Get-Content -LiteralPath $script:YunMomStoragePolicyPath -Raw -Encoding UTF8 |
    ConvertFrom-Json

function Resolve-YunMomLocalPath {
    param([Parameter(Mandatory)][string]$RelativePath)

    if ([System.IO.Path]::IsPathRooted($RelativePath)) {
        throw "Project-local path must be relative: $RelativePath"
    }

    $localRoot = [System.IO.Path]::GetFullPath(
        (Join-Path $script:YunMomProjectRoot $script:YunMomStoragePolicy.project_local_root)
    )
    $candidate = [System.IO.Path]::GetFullPath((Join-Path $localRoot $RelativePath))
    $prefix = $localRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $candidate.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Project-local path escaped .local: $candidate"
    }
    return $candidate
}

$localRoot = [System.IO.Path]::GetFullPath(
    (Join-Path $script:YunMomProjectRoot $script:YunMomStoragePolicy.project_local_root)
)
$gradleHome = Resolve-YunMomLocalPath $script:YunMomStoragePolicy.paths.gradle
$pubCache = Resolve-YunMomLocalPath $script:YunMomStoragePolicy.paths.pub
$androidUserHome = Resolve-YunMomLocalPath $script:YunMomStoragePolicy.paths.android_user
$androidAvdHome = Resolve-YunMomLocalPath $script:YunMomStoragePolicy.paths.android_avd
$isWindows = [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT
if ($isWindows) {
    $temporaryHome = [System.IO.Path]::GetFullPath(
        ($script:YunMomStoragePolicy.windows_compatibility_paths.temporary -replace '/', '\')
    )
    if (-not $temporaryHome.StartsWith('D:\DevCaches\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Windows compatibility temp must stay under D:\DevCaches: $temporaryHome"
    }
} else {
    $temporaryHome = Resolve-YunMomLocalPath $script:YunMomStoragePolicy.paths.temporary
}
$auditHome = Resolve-YunMomLocalPath $script:YunMomStoragePolicy.paths.audit

foreach ($directory in @(
    $localRoot,
    $gradleHome,
    $pubCache,
    $androidUserHome,
    $androidAvdHome,
    $temporaryHome,
    $auditHome
)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}

$env:YUNMOM_PROJECT_ROOT = $script:YunMomProjectRoot
$env:YUNMOM_PROJECT_LOCAL_ROOT = $localRoot
$env:YUNMOM_STORAGE_POLICY = $script:YunMomStoragePolicyPath
$env:GRADLE_USER_HOME = $gradleHome
$env:PUB_CACHE = $pubCache
$env:ANDROID_USER_HOME = $androidUserHome
$env:ANDROID_AVD_HOME = $androidAvdHome
$env:TEMP = $temporaryHome
$env:TMP = $temporaryHome
$env:DART_SUPPRESS_ANALYTICS = 'true'
$env:FLUTTER_SUPPRESS_ANALYTICS = 'true'
