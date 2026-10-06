@echo off
chcp 65001 > nul
title Instalador de MCP — Engineering Handbook
color 0A
cls
echo ===================================================================
echo   INSTALADOR DE MCP SERVIDOR PARA CLAUDE, CURSOR, ANTIGRAVITY Y ROO
echo ===================================================================
echo.
echo Ejecutando instalador automatico en Node.js...
echo.

node "%~dp0mcp-server\installer.mjs"

echo.
echo ===================================================================
echo Presiona cualquier tecla para salir...
pause > nul
