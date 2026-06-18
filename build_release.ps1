$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$BuildName = "SplashlineShowdown"
$DistDir = Join-Path $Root "dist\$BuildName"
$ZipPath = Join-Path $Root "dist\$BuildName.zip"
$CompileCache = Join-Path $env:TEMP "splashline_compile_cache"

function Invoke-Native {
    param(
        [string]$Executable,
        [string[]]$Arguments
    )

    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Executable $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Compress-WithRetry {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )

    for ($attempt = 1; $attempt -le 5; $attempt += 1) {
        try {
            Compress-Archive -Path $SourcePath -DestinationPath $DestinationPath -ErrorAction Stop
            return
        }
        catch {
            if ($attempt -eq 5) {
                throw
            }
            Start-Sleep -Seconds 2
        }
    }
}

Write-Host "Running unit tests..."
Invoke-Native "python" @("-m", "unittest", "discover", "-s", "tests")

Write-Host "Running compile check..."
$env:PYTHONPYCACHEPREFIX = $CompileCache
Invoke-Native "python" @("-m", "compileall", "engine", "demos", "game", "main.py", "media_capture.py", "tests", "splashline_release.py")

Write-Host "Cleaning old build output..."
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path $DistDir) {
    Remove-Item -Recurse -Force $DistDir
}
if (Test-Path $ZipPath) {
    Remove-Item -Force $ZipPath
}

Write-Host "Building Splashline Showdown..."
Invoke-Native "python" @("-m", "PyInstaller", "--noconfirm", "--clean", "--name", $BuildName, "splashline_release.py")

$ExePath = Join-Path $DistDir "$BuildName.exe"
if (-not (Test-Path $ExePath)) {
    throw "Expected executable was not created: $ExePath"
}

Write-Host "Copying player README..."
New-Item -ItemType Directory -Force -Path (Join-Path $DistDir "release") | Out-Null
Copy-Item -Force "release\README_PLAYER.txt" (Join-Path $DistDir "release\README_PLAYER.txt")

Write-Host "Creating release zip..."
Compress-WithRetry -SourcePath (Join-Path $DistDir "*") -DestinationPath $ZipPath

Write-Host "Release build ready: $ZipPath"
