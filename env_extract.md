## Windows
### PowerShell
`pipdeptree --warn silence | ForEach-Object { if ($_ -match "^[a-zA-Z]") { $_ } } > requirements.txt`