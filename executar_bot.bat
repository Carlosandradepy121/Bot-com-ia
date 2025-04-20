@echo off
setlocal EnableDelayedExpansion
title Self-Evolving Bot
color 0A

echo ===================================================================
echo                      SELF-EVOLVING BOT
echo ===================================================================
echo.

REM ===== DETECÇÃO DO PYTHON =====
echo Procurando Python...
SET PYTHON_CMD=

REM Verificar comandos Python comuns
for %%x in (python python3 py) do (
    %%x --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        SET PYTHON_CMD=%%x
        echo Python encontrado: %%x
        goto :PYTHON_FOUND
    )
)

REM Verificar caminhos comuns
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python*\python.exe"
    "C:\Python*\python.exe"
    "%PROGRAMFILES%\Python*\python.exe"
    "%PROGRAMFILES(x86)%\Python*\python.exe"
) do (
    for /f "delims=" %%i in ('dir /b /s %%p 2^>nul') do (
        "%%i" --version >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            SET PYTHON_CMD="%%i"
            echo Python encontrado: %%i
            goto :PYTHON_FOUND
        )
    )
)

REM Python não encontrado
echo ERRO: Python nao foi encontrado no sistema.
echo Para executar este bot, voce precisa instalar o Python:
echo 1. Baixe o Python em https://www.python.org/downloads/
echo 2. Durante a instalacao, marque a opcao "Add Python to PATH"
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit /b 1

:PYTHON_FOUND
echo Verificando versao do Python:
%PYTHON_CMD% --version

echo.
echo ===== VERIFICANDO DEPENDENCIAS =====

echo Verificando PyQt6 (interface grafica)...
%PYTHON_CMD% -c "import PyQt6" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo PyQt6 nao encontrado. Instalando...
    %PYTHON_CMD% -m pip install PyQt6
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Falha ao instalar PyQt6.
        echo Tentando instalar manualmente...
        %PYTHON_CMD% -m pip install --user --upgrade pip
        %PYTHON_CMD% -m pip install --user PyQt6
    )
)

echo Verificando outras dependencias...
for %%m in (requests selenium bs4 webdriver_manager) do (
    echo Verificando %%m...
    %PYTHON_CMD% -c "import %%m" 2>nul
    if !ERRORLEVEL! NEQ 0 (
        echo Instalando %%m...
        %PYTHON_CMD% -m pip install %%m
        if !ERRORLEVEL! NEQ 0 (
            echo Tentando instalar %%m com --user...
            %PYTHON_CMD% -m pip install --user %%m
        )
    )
)

echo.
echo ===== CONFIGURANDO WEBDRIVER =====
if exist setup_webdriver.py (
    echo Configurando WebDriver...
    %PYTHON_CMD% setup_webdriver.py
) else (
    echo Arquivo setup_webdriver.py nao encontrado.
)

echo.
echo ===== INICIANDO O BOT =====
if not exist gui_interface.py (
    echo ERRO: Arquivo gui_interface.py nao encontrado!
    echo Verifique se voce esta no diretorio correto.
    pause >nul
    exit /b 1
)

echo Iniciando o Self-Evolving Bot...
%PYTHON_CMD% gui_interface.py

echo.
echo O Self-Evolving Bot foi encerrado.
echo Pressione qualquer tecla para sair...
pause >nul 