## Windows
### PowerShell
```bash
pipdeptree --warn silence | ForEach-Object { if ($_ -match "^[a-zA-Z]") { $_ } } > requirements.txt
```
## Unix
### MacOS?
> you can fix here, I don't have a mac, but I think it's same as other unix-like system :-(
### Linux?



## install
when you want to install this env please run:
```bash
pip install -r requirements.txt
```