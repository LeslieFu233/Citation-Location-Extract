## Windows
### PowerShell
```bash
pipdeptree --warn silence | ForEach-Object { if ($_ -match "^[a-zA-Z]") { $_ } } > requirements.txt
```
## Unix
### MacOS?
### Linux



## install
when you want to install this env please run:
```bash
pip install -r requirements.txt
```