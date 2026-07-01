# Publish current package to PyPI via uv (loads token from local .env).
#
# Usage (from any GenesisAeon package repo):
#   pwsh D:\mandala\genesis-os\scripts\publish_pypi.ps1
#   pwsh D:\mandala\genesis-os\scripts\publish_pypi.ps1 -RepoPath D:\mandala\amoc-utac
#   pwsh D:\mandala\genesis-os\scripts\publish_pypi.ps1 -DryRun
#
# Token lookup order:
#   1. Already set: UV_PUBLISH_TOKEN or PYPI_API_TOKEN
#   2. <RepoPath>\.env
#   3. D:\mandala\genesis-os\.env  (or $env:GENESISAEON_SECRETS)
#   4. D:\mandala\.env

param(
    [string]$RepoPath = (Get-Location).Path,
    [switch]$DryRun,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

function Import-DotEnvFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }
    Get-Content $Path -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $eq = $line.IndexOf("=")
        if ($eq -lt 1) { return }
        $key = $line.Substring(0, $eq).Trim()
        $val = $line.Substring($eq + 1).Trim()
        if ($val.StartsWith('"') -and $val.EndsWith('"')) { $val = $val.Substring(1, $val.Length - 2) }
        [Environment]::SetEnvironmentVariable($key, $val, "Process")
    }
    return $true
}

function Resolve-SecretsEnvFile {
    param([string]$StartDir)
    $candidates = @(
        (Join-Path $StartDir ".env")
    )
    $genesisOs = $env:GENESISAEON_SECRETS
    if (-not $genesisOs) {
        $scriptRoot = Split-Path -Parent $PSScriptRoot
        $genesisOs = Join-Path $scriptRoot ".env"
    }
    $candidates += $genesisOs
    $mandalaRoot = $env:GENESISAEON_DIR
    if (-not $mandalaRoot) { $mandalaRoot = "D:\mandala" }
    $candidates += (Join-Path $mandalaRoot ".env")

    foreach ($path in $candidates) {
        if (Import-DotEnvFile -Path $path) {
            Write-Host "Loaded secrets from $path"
            return $path
        }
    }
    return $null
}

if (-not $env:UV_PUBLISH_TOKEN -and -not $env:PYPI_API_TOKEN) {
    $loaded = Resolve-SecretsEnvFile -StartDir $RepoPath
    if (-not $loaded) {
        Write-Error @"
No PyPI token found. Set UV_PUBLISH_TOKEN / PYPI_API_TOKEN or create:
  $RepoPath\.env
  D:\mandala\genesis-os\.env   (copy from .env.example)
"@
    }
}

if ($env:PYPI_API_TOKEN -and -not $env:UV_PUBLISH_TOKEN) {
    $env:UV_PUBLISH_TOKEN = $env:PYPI_API_TOKEN
}

if (-not $env:UV_PUBLISH_TOKEN -or $env:UV_PUBLISH_TOKEN -match '^\s*$|^pypi-\.\.\.$') {
    Write-Error "UV_PUBLISH_TOKEN is empty or still a placeholder — edit your .env file."
}

$RepoPath = (Resolve-Path $RepoPath).Path
if (-not (Test-Path (Join-Path $RepoPath "pyproject.toml"))) {
    Write-Error "No pyproject.toml in $RepoPath — run from a Python package root or pass -RepoPath."
}

Push-Location $RepoPath
try {
    if (-not $SkipBuild) {
        $distDir = Join-Path $RepoPath "dist"
        if (Test-Path $distDir) {
            Write-Host "Cleaning $distDir ..."
            if ($DryRun) {
                Write-Host "[dry-run] remove dist/*"
            } else {
                Remove-Item (Join-Path $distDir "*") -Force -ErrorAction SilentlyContinue
            }
        }
        Write-Host "Building in $RepoPath ..."
        if ($DryRun) {
            Write-Host "[dry-run] uv build"
        } else {
            uv build
        }
        if (-not $DryRun -and (Test-Path $distDir)) {
            $artifacts = Get-ChildItem $distDir -File | Where-Object { $_.Name -ne ".gitignore" }
            Write-Host "Artifacts: $($artifacts.Name -join ', ')"
        }
    }

    Write-Host "Publishing to PyPI ..."
    $distDir = Join-Path $RepoPath "dist"
    $files = @(Get-ChildItem $distDir -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in ".whl", ".gz" })
    if ($files.Count -eq 0) {
        Write-Error "No .whl or .tar.gz in $distDir — run build first."
    }
    if ($DryRun) {
        Write-Host "[dry-run] uv publish $($files.Name -join ' ') (token $($env:UV_PUBLISH_TOKEN.Length) chars)"
    } else {
        # Explicit file list avoids stale dist/* and makes missing-wheel obvious
        uv publish @($files.FullName)
    }
} finally {
    Pop-Location
}