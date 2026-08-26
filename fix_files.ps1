Write-Host "Fixing corrupted Python files..." -ForegroundColor Yellow

# List all Python files
 = Get-ChildItem -Path . -Recurse -Filter *.py

foreach ( in ) {
    Write-Host "Checking: $(.Name)"
     = Get-Content .FullName -Raw
    
    # Remove the corrupted -NoNewline that got added
    if ( -match '-NoNewline') {
        Write-Host "  Fixing: $(.Name)"
         =  -replace '-NoNewline', ''
         =  -replace 'NoNewline', ''
        Set-Content .FullName -Value  -NoNewline
    }
}

Write-Host "Fix complete!" -ForegroundColor Green
