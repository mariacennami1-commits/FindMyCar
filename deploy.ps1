param(
    [switch]$SkipDownload,
    [string]$CustomUrl
)

$Repo = "mariacennami1-commits/FindMyCar"
$ApkName = "findmycar-1.0.0-arm64-v8a-debug.apk"

if ($CustomUrl) {
    Write-Host "Downloading from custom URL: $CustomUrl"
    Invoke-WebRequest -Uri $CustomUrl -OutFile "$env:TEMP\$ApkName" -UseBasicParsing
} elseif (-not $SkipDownload) {
    Write-Host "Fetching latest release from $Repo..."
    try {
        $release = Invoke-RestMethod "https://api.github.com/repos/$Repo/releases/latest" -UseBasicParsing
        $apk = $release.assets | Where-Object { $_.name -like "*.apk" } | Select-Object -First 1
        if (-not $apk) {
            Write-Host "ERROR: No APK found in latest release"
            exit 1
        }
        Write-Host "Downloading $($apk.name) (build $($release.tag_name))..."
        Invoke-WebRequest -Uri $apk.browser_download_url -OutFile "$env:TEMP\$ApkName" -UseBasicParsing
        Write-Host "Downloaded to $env:TEMP\$ApkName"
    } catch {
        Write-Host "ERROR: Failed to download: $_"
        exit 1
    }
} else {
    Write-Host "Skipping download, using cached APK from $env:TEMP\$ApkName"
}

Write-Host "Installing APK via ADB..."
adb install -r "$env:TEMP\$ApkName"
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: APK installed!"
    Write-Host "Launching app via monkey..."
    adb shell monkey -p com.findmycar.findmycar 1
} else {
    Write-Host "ERROR: ADB install failed"
}
