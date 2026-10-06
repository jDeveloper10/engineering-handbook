@echo off
title Visualizador Neuronal del Engineering Handbook
cd /d "%~dp0"
python tools/visualize_handbook_network.py
if errorlevel 1 (
    echo.
    echo Ocurrio un error al ejecutar el visualizador.
    pause
)
