Get-ChildItem -Path . -Recurse -Filter *.py | ForEach-Object {
    Write-Host "Converting: $($_.Name)"
     = Get-Content $_.FullName -Raw
     =  -replace 'PyQt6', 'PySide6'
    Set-Content $_.FullName -Value  -NoNewline
}
Write-Host "Import conversion complete!"
