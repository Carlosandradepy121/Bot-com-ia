@echo off
title Instalação de Dependências - Self-Evolving Bot
color 0A

echo ===================================================================
echo            INSTALAÇÃO DE DEPENDÊNCIAS - SELF-EVOLVING BOT
echo ===================================================================
echo.

REM Encontrar o Python
SET PYTHON_CMD=python

echo Verificando instalação do Python...
%PYTHON_CMD% --version 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Tentando com 'py'...
    SET PYTHON_CMD=py
    py --version 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Python não encontrado! Verifique se está instalado e adicionado ao PATH.
        echo.
        echo 1. Baixe o Python em https://www.python.org/downloads/
        echo 2. Durante a instalação, marque a opção "Add Python to PATH"
        echo.
        echo Pressione qualquer tecla para sair...
        pause >nul
        exit /b 1
    )
)

echo Python encontrado: %PYTHON_CMD% 
echo.

echo Atualizando pip...
%PYTHON_CMD% -m pip install --upgrade pip
echo.

echo Instalando dependências principais...
%PYTHON_CMD% -m pip install PyQt6
echo.

echo Instalando dependências para web...
%PYTHON_CMD% -m pip install requests
%PYTHON_CMD% -m pip install selenium
%PYTHON_CMD% -m pip install beautifulsoup4
%PYTHON_CMD% -m pip install webdriver-manager
echo.

echo Verificando requirements.txt...
if exist requirements.txt (
    echo Instalando dependências adicionais de requirements.txt...
    %PYTHON_CMD% -m pip install -r requirements.txt
) else (
    echo Arquivo requirements.txt não encontrado.
)

echo.
echo ===================================================================
echo                    INSTALAÇÃO CONCLUÍDA
echo ===================================================================
echo.
echo Todas as dependências foram instaladas.
echo Agora você pode executar o Self-Evolving Bot com o arquivo executar_bot.bat
echo.
echo Pressione qualquer tecla para sair...
pause >nul 