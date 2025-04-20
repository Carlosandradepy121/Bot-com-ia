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

REM Verificar e instalar pip se necessário
echo Verificando pip...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Pip nao encontrado. Instalando...
    %PYTHON_CMD% -m ensurepip --default-pip
    %PYTHON_CMD% -m pip install --upgrade pip
)

REM Atualizar pip
echo Atualizando pip...
%PYTHON_CMD% -m pip install --upgrade pip

REM Instalar numpy primeiro
echo Instalando numpy...
%PYTHON_CMD% -m pip install numpy==1.26.4
if %ERRORLEVEL% NEQ 0 (
    echo Tentando instalar numpy com --user...
    %PYTHON_CMD% -m pip install --user numpy==1.26.4
)

REM Verificar se o numpy foi instalado corretamente
%PYTHON_CMD% -c "import numpy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha na instalacao do numpy. Tentando instalacao alternativa...
    %PYTHON_CMD% -m pip uninstall -y numpy
    %PYTHON_CMD% -m pip install --no-cache-dir numpy==1.26.4
)

REM Instalar PyQt6 e suas dependências
echo Instalando PyQt6 e dependencias...
%PYTHON_CMD% -m pip install PyQt6==6.6.1
%PYTHON_CMD% -m pip install PyQt6-Qt6==6.6.1
%PYTHON_CMD% -m pip install PyQt6-sip==13.6.0

REM Verificar se o PyQt6 foi instalado corretamente
%PYTHON_CMD% -c "from PyQt6.QtCore import QCoreApplication" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha na instalacao do PyQt6. Tentando instalacao alternativa...
    %PYTHON_CMD% -m pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip
    %PYTHON_CMD% -m pip install --no-cache-dir PyQt6==6.6.1
    %PYTHON_CMD% -m pip install --no-cache-dir PyQt6-Qt6==6.6.1
    %PYTHON_CMD% -m pip install --no-cache-dir PyQt6-sip==13.6.0
)

REM Instalar torch e outras dependências ML/AI
echo Instalando torch e dependencias ML/AI...
%PYTHON_CMD% -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
%PYTHON_CMD% -m pip install transformers==4.38.2
%PYTHON_CMD% -m pip install scikit-learn==1.4.0
%PYTHON_CMD% -m pip install tensorboard==2.15.2

REM Verificar e instalar outras dependências principais
echo Verificando outras dependencias principais...
for %%m in (
    "qt-material==2.14"
    "selenium>=4.17.2"
    "webdriver-manager>=4.0.1"
    "beautifulsoup4>=4.12.3"
    "requests>=2.31.0"
) do (
    echo Verificando %%m...
    %PYTHON_CMD% -m pip install %%m
    if !ERRORLEVEL! NEQ 0 (
        echo Tentando instalar %%m com --user...
        %PYTHON_CMD% -m pip install --user %%m
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