Set-StrictMode -Version Latest

function Get-YunMomDriveInfo {
    param([Parameter(Mandatory)][string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $root = [System.IO.Path]::GetPathRoot($fullPath)
    $drive = [System.IO.DriveInfo]::new($root)
    if (-not $drive.IsReady) {
        throw "Drive is not ready: $root"
    }
    return $drive
}

function Assert-YunMomStoragePreflight {
    $policy = Get-Content -LiteralPath $env:YUNMOM_STORAGE_POLICY -Raw -Encoding UTF8 | ConvertFrom-Json
    $cDrive = [System.IO.DriveInfo]::new('C:\')
    $projectDrive = Get-YunMomDriveInfo -Path $env:YUNMOM_PROJECT_ROOT

    $minimumC = [int64]$policy.limits.minimum_c_drive_free_gib * 1GB
    $minimumProject = [int64]$policy.limits.minimum_project_drive_free_gib * 1GB
    if ($cDrive.AvailableFreeSpace -lt $minimumC) {
        throw "C: free space is below the policy floor of $($policy.limits.minimum_c_drive_free_gib) GiB."
    }
    if ($projectDrive.AvailableFreeSpace -lt $minimumProject) {
        throw "Project drive free space is below the policy floor of $($policy.limits.minimum_project_drive_free_gib) GiB."
    }
}

function Invoke-YunMomDiskGuard {
    param(
        [Parameter(Mandatory)][string]$Operation,
        [Parameter(Mandatory)][scriptblock]$ScriptBlock
    )

    Assert-YunMomStoragePreflight
    $policy = Get-Content -LiteralPath $env:YUNMOM_STORAGE_POLICY -Raw -Encoding UTF8 | ConvertFrom-Json
    $cDrive = [System.IO.DriveInfo]::new('C:\')
    $beforeC = $cDrive.AvailableFreeSpace
    $projectDrive = Get-YunMomDriveInfo -Path $env:YUNMOM_PROJECT_ROOT
    $beforeProject = $projectDrive.AvailableFreeSpace
    $startedAt = [DateTimeOffset]::Now
    $commandError = $null

    try {
        & $ScriptBlock
    } catch {
        $commandError = $_
    } finally {
        $cDrive = [System.IO.DriveInfo]::new('C:\')
        $projectDrive = Get-YunMomDriveInfo -Path $env:YUNMOM_PROJECT_ROOT
        $afterC = $cDrive.AvailableFreeSpace
        $observedGrowthBytes = [int64]($beforeC - $afterC)
        $persistentGrowthBytes = $observedGrowthBytes
        $limitMiB = [int64]$policy.limits.max_c_drive_growth_mib
        if ($observedGrowthBytes -gt ($limitMiB * 1MB)) {
            foreach ($sample in 1..5) {
                Start-Sleep -Seconds 2
                $sampleFree = [System.IO.DriveInfo]::new('C:\').AvailableFreeSpace
                $sampleGrowth = [int64]($beforeC - $sampleFree)
                if ($sampleGrowth -lt $persistentGrowthBytes) {
                    $persistentGrowthBytes = $sampleGrowth
                }
            }
        }
        $afterProject = $projectDrive.AvailableFreeSpace
        $observedGrowthMiB = [math]::Round($observedGrowthBytes / 1MB, 2)
        $persistentGrowthMiB = [math]::Round($persistentGrowthBytes / 1MB, 2)
        $projectGrowthMiB = [math]::Round(($beforeProject - $afterProject) / 1MB, 2)
        $record = [ordered]@{
            schema_version = 1
            operation = $Operation
            started_at = $startedAt.ToString('o')
            completed_at = [DateTimeOffset]::Now.ToString('o')
            c_drive_observed_growth_mib = $observedGrowthMiB
            c_drive_persistent_growth_mib = $persistentGrowthMiB
            project_drive_growth_mib = $projectGrowthMiB
            c_drive_limit_mib = $limitMiB
            command_succeeded = ($null -eq $commandError)
            within_policy = ($persistentGrowthBytes -le ($limitMiB * 1MB))
        }
        $auditPath = Join-Path $env:YUNMOM_PROJECT_LOCAL_ROOT 'audit\storage-guard.jsonl'
        ($record | ConvertTo-Json -Compress) | Add-Content -LiteralPath $auditPath -Encoding UTF8
        Write-Host ("Storage guard: C: observed {0} MiB, persistent {1} MiB; project drive: {2} MiB; limit: {3} MiB" -f
            $observedGrowthMiB, $persistentGrowthMiB, $projectGrowthMiB, $limitMiB)
    }

    if ($null -ne $commandError) {
        throw $commandError
    }
    if ($persistentGrowthBytes -gt ($limitMiB * 1MB)) {
        throw "C: persistently grew by $persistentGrowthMiB MiB during '$Operation', above the $limitMiB MiB hard limit. Stop and investigate; do not auto-clean."
    }
}
