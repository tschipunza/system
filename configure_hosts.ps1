# PowerShell script to add Fleet Manager SaaS hosts entries
# Run as Administrator

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$entries = @(
    "127.0.0.1  fleetmanager.local",
    "127.0.0.1  acme.fleetmanager.local",
    "127.0.0.1  demo.fleetmanager.local",
    "127.0.0.1  company1.fleetmanager.local",
    "127.0.0.1  company2.fleetmanager.local"
)

Write-Host "Fleet Manager SaaS - Hosts File Configuration" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Read current hosts file
$currentHosts = Get-Content $hostsPath

Write-Host "Checking current hosts file..." -ForegroundColor Yellow
Write-Host ""

$entriesToAdd = @()
foreach ($entry in $entries) {
    $found = $false
    foreach ($line in $currentHosts) {
        if ($line -match [regex]::Escape($entry)) {
            $found = $true
            break
        }
    }
    
    if ($found) {
        Write-Host "[✓] Already exists: $entry" -ForegroundColor Green
    } else {
        Write-Host "[+] Will add: $entry" -ForegroundColor Yellow
        $entriesToAdd += $entry
    }
}

Write-Host ""

if ($entriesToAdd.Count -eq 0) {
    Write-Host "All entries already exist in hosts file!" -ForegroundColor Green
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host "Ready to add $($entriesToAdd.Count) entries to hosts file." -ForegroundColor Cyan
$confirm = Read-Host "Continue? (Y/N)"

if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

# Backup hosts file
$backupPath = "$hostsPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item $hostsPath $backupPath
Write-Host ""
Write-Host "Backed up hosts file to: $backupPath" -ForegroundColor Green

# Add entries
try {
    Add-Content -Path $hostsPath -Value ""
    Add-Content -Path $hostsPath -Value "# Fleet Manager SaaS - Added $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    foreach ($entry in $entriesToAdd) {
        Add-Content -Path $hostsPath -Value $entry
        Write-Host "[✓] Added: $entry" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host "✓ Hosts file updated successfully!" -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now access:" -ForegroundColor Yellow
    Write-Host "  - Main site: http://fleetmanager.local:5000" -ForegroundColor White
    Write-Host "  - Company signup: http://fleetmanager.local:5000/tenant/signup" -ForegroundColor White
    Write-Host "  - Test company: http://acme.fleetmanager.local:5000" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "ERROR: Failed to update hosts file!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Read-Host "Press Enter to exit"
