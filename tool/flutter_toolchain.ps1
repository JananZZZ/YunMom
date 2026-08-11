Set-StrictMode -Version Latest

function Resolve-YunMomFlutterRoot {
    param([Parameter(Mandatory)][string]$ProjectRoot)

    if ($env:FLUTTER_ROOT) {
        return $env:FLUTTER_ROOT
    }

    $flutterOnPath = Get-Command flutter -ErrorAction SilentlyContinue
    if ($flutterOnPath) {
        return Split-Path -Parent (Split-Path -Parent $flutterOnPath.Source)
    }

    $toolchainFile = Join-Path $ProjectRoot 'toolchains\toolchain.json'
    if (Test-Path -LiteralPath $toolchainFile -PathType Leaf) {
        $toolchain = Get-Content -LiteralPath $toolchainFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($toolchain.flutter.root) {
            return ($toolchain.flutter.root -replace '/', '\')
        }
    }

    throw 'Flutter was not found via FLUTTER_ROOT, PATH, or toolchains/toolchain.json.'
}

function Get-YunMomFlutterCommands {
    param([Parameter(Mandatory)][string]$ProjectRoot)

    $flutterRoot = Resolve-YunMomFlutterRoot -ProjectRoot $ProjectRoot
    $flutter = Join-Path $flutterRoot 'bin\flutter.bat'
    $dart = Join-Path $flutterRoot 'bin\dart.bat'
    if (-not (Test-Path -LiteralPath $flutter -PathType Leaf) -or
        -not (Test-Path -LiteralPath $dart -PathType Leaf)) {
        throw "Invalid Flutter root: $flutterRoot"
    }

    return [pscustomobject]@{
        Root = $flutterRoot
        Flutter = $flutter
        Dart = $dart
    }
}
