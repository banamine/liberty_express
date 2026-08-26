# install_deps.ps1
Write-Host "Liberty Express Dependency Installer" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

$python_exe = "C:\Python314\python.exe"

# Check if Python exists
if (-not (Test-Path $python_exe)) {
    Write-Host "Python not found at $python_exe" -ForegroundColor Red
    Write-Host "Please install Python 3.11 or 3.12 from python.org" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using Python: $python_exe" -ForegroundColor Green
$version = & $python_exe --version
Write-Host "Version: $version" -ForegroundColor Green

# Try to install PyQt6
Write-Host "`nAttempting to install PyQt6..." -ForegroundColor Yellow
& $python_exe -m pip install PyQt6

if ($LASTEXITCODE -ne 0) {
    Write-Host "PyQt6 installation failed. Trying PySide6 instead..." -ForegroundColor Yellow
    
    # Install PySide6
    & $python_exe -m pip install PySide6 requests beautifulsoup4 lxml
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PySide6 installed successfully!" -ForegroundColor Green
        Write-Host "Converting imports from PyQt6 to PySide6..." -ForegroundColor Yellow
        
        # Convert imports
        Get-ChildItem -Path . -Recurse -Filter *.py | ForEach-Object {
            Write-Host "Converting: $($_.Name)"
            (Get-Content $_.FullName) -replace 'PyQt6', 'PySide6' | Set-Content $_.FullName
        }
        
        Write-Host "Import conversion complete!" -ForegroundColor Green
    }
} else {
    Write-Host "PyQt6 installed successfully!" -ForegroundColor Green
    
    # Install other dependencies
    Write-Host "Installing other dependencies..." -ForegroundColor Yellow
    & $python_exe -m pip install requests beautifulsoup4 lxml
}

Write-Host "`nSetup complete! Running application..." -ForegroundColor Green
& $python_exe main.py

Read-Host "`nPress Enter to exit"