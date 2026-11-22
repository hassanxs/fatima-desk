# Fatima Desk - Windows build
#
# Builds fatimadesk.exe the same way RustDesk's CI does (flutter-build.yml,
# x86_64 job). Run from this folder in PowerShell:
#
#   .\build-windows.ps1              # app folder only (fast, for development)
#   .\build-windows.ps1 -Installer   # also the files to hand out
#
# Output: dist\FatimaDesk\fatimadesk.exe (run it from that folder; it needs
# the DLLs and data folder next to it). With -Installer also:
#   dist\fatimadesk-<version>-install.exe      single file: runs portable, can install
#   dist\fatimadesk-<version>-windows-portable.zip   the app folder, zipped
#
# Toolchain (installed once): VS 2022 Build Tools (C++), Rust 1.75,
# LLVM 15.0.6, Flutter 3.24.5 in D:\dev\flutter, vcpkg in D:\dev\vcpkg,
# flutter_rust_bridge_codegen 1.80.1, cargo-expand 1.0.95.

param([switch]$Installer)

# 'Continue', not 'Stop': cargo and flutter print normal progress to stderr,
# which Windows PowerShell 5.1 would turn into a terminating error. Failures
# are caught by Run's exit-code check and -ErrorAction Stop on cmdlets.
$ErrorActionPreference = 'Continue'
$Repo = $PSScriptRoot
$FlutterRoot = 'D:\dev\flutter'

$env:VCPKG_ROOT = 'D:\dev\vcpkg'
$env:LIBCLANG_PATH = 'C:\Program Files\LLVM\bin'
$env:Path = "$env:USERPROFILE\.cargo\bin;C:\Program Files\LLVM\bin;$FlutterRoot\bin;$env:Path"

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Run($exe) {
    & $exe @args
    if ($LASTEXITCODE -ne 0) { throw "$exe $args failed with exit code $LASTEXITCODE" }
}

Set-Location $Repo

Step 'Checking tools'
Run rustc --version
Run flutter --version

# ---- One-time Flutter setup (skipped once done) ------------------------
$engineDir = "$FlutterRoot\bin\cache\artifacts\engine\windows-x64-release"
$engineMarker = "$engineDir\.fatimadesk-custom-engine"
if (-not (Test-Path $engineMarker)) {
    Step 'Installing RustDesk custom Flutter engine (one time)'
    Run flutter precache --windows
    $zip = Join-Path $env:TEMP 'windows-x64-release.zip'
    $out = Join-Path $env:TEMP 'windows-x64-release'
    Invoke-WebRequest -Uri 'https://github.com/rustdesk/engine/releases/download/main/windows-x64-release.zip' -OutFile $zip
    if (Test-Path $out) { Remove-Item -Recurse -Force $out }
    Expand-Archive -Path $zip -DestinationPath $out
    Copy-Item -Force -Recurse "$out\*" $engineDir
    New-Item -ItemType File $engineMarker | Out-Null
}

$patch = 'flutter_3.24.4_dropdown_menu_enableFilter.diff'
git -C $FlutterRoot apply --check --reverse "$Repo\.github\patches\$patch" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Step 'Patching Flutter dropdown menu (one time)'
    Run git -C $FlutterRoot apply "$Repo\.github\patches\$patch"
}

if (-not (Test-Path "$env:VCPKG_ROOT\installed\x64-windows-static\include\libavcodec\avcodec.h")) {
    Step 'Building native libraries with vcpkg (one time, 30-60 min)'
    # ffmpeg is a "host" dependency in vcpkg.json; CI builds host deps into
    # the same static triplet, and hwcodec links against it from there.
    $env:VCPKG_DEFAULT_HOST_TRIPLET = 'x64-windows-static'
    Run "$env:VCPKG_ROOT\vcpkg.exe" install --triplet x64-windows-static "--x-install-root=$env:VCPKG_ROOT\installed"
}

if (-not (Test-Path "$env:USERPROFILE\.rustup\toolchains\1.75-x86_64-pc-windows-msvc\bin\rustfmt.exe")) {
    Step 'Installing rustfmt (one time, needed by the bridge generator)'
    Run rustup component add rustfmt --toolchain 1.75
}

if (-not (Get-Command cargo-expand -ErrorAction SilentlyContinue)) {
    Step 'Installing cargo-expand (one time)'
    Run cargo install cargo-expand --version 1.0.95 --locked
}

# ---- Build -------------------------------------------------------------
Step 'Fetching Flutter packages'
Push-Location flutter
Run flutter pub get
Pop-Location

Step 'Generating Flutter <-> Rust bridge'
Run flutter_rust_bridge_codegen --rust-input ./src/flutter_ffi.rs --dart-output ./flutter/lib/generated_bridge.dart

Step 'Building Fatima Desk (Rust core + Flutter UI)'
if ($Installer) {
    # build.py calls "python3", which on Windows is often only the Microsoft
    # Store shortcut. Put a shim for the real Python first on PATH for this
    # build only.
    $shim = Join-Path $env:TEMP 'fatimadesk-python3-shim'
    New-Item -ItemType Directory -Force $shim | Out-Null
    $py = (Get-Command python -ErrorAction Stop).Source
    Set-Content -Path "$shim\python3.cmd" -Value "@`"$py`" %*" -Encoding ascii
    $env:Path = "$shim;$env:Path"
    Run python build.py --portable --flutter --hwcodec --vram
} else {
    Run python build.py --portable --flutter --skip-portable-pack --hwcodec --vram
}

Step 'Copying to dist\FatimaDesk'
$release = 'flutter\build\windows\x64\runner\Release'
if (Test-Path dist\FatimaDesk) { Remove-Item -Recurse -Force dist\FatimaDesk -ErrorAction Stop }
New-Item -ItemType Directory -Force dist -ErrorAction Stop | Out-Null
Copy-Item -Recurse $release dist\FatimaDesk -ErrorAction Stop
Write-Host "`nDone: $Repo\dist\FatimaDesk\fatimadesk.exe" -ForegroundColor Green

if ($Installer) {
    $version = (Select-String -Path Cargo.toml -Pattern '^version = "([^"]+)"' | Select-Object -First 1).Matches[0].Groups[1].Value
    Step 'Collecting the files to hand out'
    $exe = "fatimadesk-$version-install.exe"
    if (-not (Test-Path $exe)) { throw "$exe was not produced by the portable packer" }
    Move-Item -Force $exe "dist\$exe" -ErrorAction Stop
    $zip = "dist\fatimadesk-$version-windows-portable.zip"
    if (Test-Path $zip) { Remove-Item -Force $zip }
    Compress-Archive -Path dist\FatimaDesk -DestinationPath $zip -ErrorAction Stop
    Write-Host "Done: $Repo\dist\$exe" -ForegroundColor Green
    Write-Host "Done: $Repo\$zip" -ForegroundColor Green
}
