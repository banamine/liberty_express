Get-ChildItem -Path . -Recurse -Include *.py | ForEach-Object {
    \ = Get-Content \.FullName -Raw
    if (\ -match '-NoNewline') {
        Write-Host "Fixing: \"
        \ = \ -replace '-NoNewline', ''
        \ = \ -replace 'NoNewline', ''
        # Remove any lines that are just empty or garbage
        \ = \ -replace '(?m)^\s*$', ''
        Set-Content \.FullName -Value \ -NoNewline
    }
}
Write-Host "All files cleaned."
