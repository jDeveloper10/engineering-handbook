@echo off
setlocal
set "SCRIPT=%~dp0desktop_mascots.py"
set "PYW=%LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe"

if exist "%PYW%" (
    start "" "%PYW%" "%SCRIPT%"
    goto :eof
)

where pyw.exe >nul 2>&1
if %errorlevel%==0 (
    start "" pyw.exe -3 "%SCRIPT%"
    goto :eof
)

echo No se encontro pythonw. Instala Python 3 desde python.org y vuelve a intentar.
pause
