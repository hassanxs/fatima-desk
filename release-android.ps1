<#
  Fatima Desk: ship an Android build that CI has already built and signed.

  The APKs are built by the "Fatima Desk Android" GitHub workflow (this PC has
  no Android Rust toolchain). This script:
    1. picks a finished run (the newest successful one, or -RunId),
    2. downloads its APKs to ..\releases\android\run-<id>\,
    3. uploads them to the GitHub release (-Tag), replacing older ones,
    4. sends the arm64-v8a APK to Firebase App Distribution testers.

  One-time setup on the PC:
    npm install -g firebase-tools
    firebase login      (the Google account that owns the Firebase project)
    gh auth login       (already done if gh works)

  Usage:
    .\release-android.ps1 "What changed"
    .\release-android.ps1 -Notes "..." -RunId 45146331618
    .\release-android.ps1 "..." -NoGitHub      # Firebase only
    .\release-android.ps1 "..." -NoFirebase    # GitHub release only
#>
param(
    [Parameter(Position = 0)]
    [string]$Notes = "",
    [string]$RunId = "",
    [string]$Tag = "v1.5.3-fd1",
    [string]$Groups = "private",
    [switch]$NoGitHub,
    [switch]$NoFirebase
)

# ---- Firebase values for Fatima Desk ----
$project = "fatima-desk"
$appId   = "1:803264935208:android:fa429031126b0b5e5c0c1d"
# -----------------------------------------
$repo     = "hassanxs/fatima-desk"
$workflow = "fatima-desk-android.yml"

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

if (-not $RunId) {
    $RunId = gh run list --repo $repo --workflow $workflow --branch fatima-desk `
        --status success --limit 1 --json databaseId --jq '.[0].databaseId'
    if (-not $RunId) { throw "No successful '$workflow' run found" }
}
$run = gh run view $RunId --repo $repo --json headSha,conclusion | ConvertFrom-Json
if ($run.conclusion -ne "success") { throw "Run $RunId has not succeeded ($($run.conclusion))" }
$sha = $run.headSha.Substring(0, 9)
Write-Host "Run $RunId (commit $sha)" -ForegroundColor Cyan

# 1. Download the APKs
$out = Join-Path (Split-Path $root -Parent) "releases\android\run-$RunId"
if (-not (Test-Path $out)) {
    gh run download $RunId --repo $repo --pattern "fatimadesk-*-android-*" --dir $out
    if ($LASTEXITCODE -ne 0) { throw "Download failed" }
}
$apks = Get-ChildItem $out -Recurse -Filter *.apk
if (-not $apks) { throw "No APKs in $out" }
$apks | ForEach-Object {
    $h = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()
    Write-Host ("  {0}  {1:N1} MB  sha256 {2}" -f $_.Name, ($_.Length / 1MB), $h)
}
$arm64 = $apks | Where-Object Name -like "*arm64-v8a.apk" | Select-Object -First 1
if (-not $Notes) { $Notes = "Fatima Desk build from commit $sha" }

# 2. GitHub release
if (-not $NoGitHub) {
    gh release upload $Tag --repo $repo --clobber @($apks.FullName)
    if ($LASTEXITCODE -ne 0) { throw "GitHub upload failed" }
    Write-Host "Uploaded to release $Tag" -ForegroundColor Green
}

# 3. Firebase App Distribution
if (-not $NoFirebase) {
    if ($appId.StartsWith("<")) { throw "Fill in `$project and `$appId at the top of this script" }
    if (-not $arm64) { throw "No arm64-v8a APK in $out" }
    firebase appdistribution:distribute $arm64.FullName `
        --app $appId `
        --project $project `
        --groups $Groups `
        --release-notes $Notes
    if ($LASTEXITCODE -ne 0) { throw "Firebase distribute failed" }
    Write-Host "Sent $($arm64.Name) to '$Groups'" -ForegroundColor Green
}
