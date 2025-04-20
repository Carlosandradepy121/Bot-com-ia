@echo off
setlocal EnableDelayedExpansion
title Compilar Executavel - Self-Evolving Bot
color 0A

echo ===================================================================
echo              COMPILACAO DO EXECUTAVEL - SELF-EVOLVING BOT
echo ===================================================================
echo.
echo Este script vai criar um ambiente virtual, instalar apenas as
echo dependencias necessarias e compilar o Self-Evolving Bot como
echo um arquivo executavel (.exe) com capacidade web e Chrome.
echo.

REM ===== DETECÇÃO DO PYTHON =====
SET PYTHON_CMD=

REM Método 1: Verificar comandos comuns
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    SET PYTHON_CMD=python
    goto :PYTHON_ENCONTRADO
)

py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    SET PYTHON_CMD=py
    goto :PYTHON_ENCONTRADO
)

python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    SET PYTHON_CMD=python3
    goto :PYTHON_ENCONTRADO
)

REM Método 2: Verificar locais comuns de instalação
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python*\python.exe"
    "C:\Python*\python.exe"
    "%PROGRAMFILES%\Python*\python.exe"
    "%PROGRAMFILES(x86)%\Python*\python.exe"
) do (
    for /f "delims=" %%i in ('dir /b /s %%p 2^>nul') do (
        SET PYTHON_CMD="%%i"
        goto :PYTHON_ENCONTRADO
    )
)

REM Método 3: Verificar no registro do Windows
for %%r in (
    "HKEY_CURRENT_USER\Software\Python\PythonCore"
    "HKEY_LOCAL_MACHINE\Software\Python\PythonCore"
) do (
    for /f "tokens=*" %%i in ('reg query %%r /s /f InstallPath /k 2^>nul ^| find "InstallPath"') do (
        for /f "tokens=3" %%j in ('reg query "%%i" /ve 2^>nul') do (
            if exist "%%j\python.exe" (
                SET PYTHON_CMD="%%j\python.exe"
                goto :PYTHON_ENCONTRADO
            )
        )
    )
)

echo ERRO: Python nao foi encontrado no sistema.
echo.
echo Para compilar o bot, voce precisa instalar o Python:
echo 1. Baixe o Python em https://www.python.org/downloads/
echo 2. Durante a instalacao, marque a opcao "Add Python to PATH"
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit /b 1

:PYTHON_ENCONTRADO
echo Python encontrado: %PYTHON_CMD%
%PYTHON_CMD% --version

REM ===== CRIAR E CONFIGURAR AMBIENTE VIRTUAL =====
echo.
echo [1/7] Criando ambiente virtual para compilacao...

REM Remover ambiente virtual antigo se existir
if exist venv_build (
    echo Removendo ambiente virtual antigo...
    rmdir /s /q venv_build
)

echo Criando novo ambiente virtual...
%PYTHON_CMD% -m venv venv_build

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO ao criar ambiente virtual. Tentando alternativa...
    %PYTHON_CMD% -m pip install virtualenv
    %PYTHON_CMD% -m virtualenv venv_build
    
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Falha ao criar ambiente virtual.
        echo Verifique sua instalacao do Python e tente novamente.
        pause
        exit /b 1
    )
)

echo Ativando ambiente virtual...
call venv_build\Scripts\activate.bat

REM ===== INSTALAR DEPENDÊNCIAS MÍNIMAS =====
echo.
echo [2/7] Instalando dependencias minimas...

REM Atualizar pip
python -m pip install --upgrade pip

REM Instalar numpy primeiro
echo Instalando numpy...
python -m pip install numpy==1.26.4
if %ERRORLEVEL% NEQ 0 (
    echo Tentando instalar numpy com --user...
    python -m pip install --user numpy==1.26.4
)

REM Verificar se o numpy foi instalado corretamente
python -c "import numpy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha na instalacao do numpy. Tentando instalacao alternativa...
    python -m pip uninstall -y numpy
    python -m pip install --no-cache-dir numpy==1.26.4
)

REM Instalar PyQt6 e suas dependências
echo Instalando PyQt6 e dependencias...
python -m pip install PyQt6==6.6.1
python -m pip install PyQt6-Qt6==6.6.1
python -m pip install PyQt6-sip==13.6.0

REM Verificar se o PyQt6 foi instalado corretamente
python -c "from PyQt6.QtCore import QCoreApplication" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha na instalacao do PyQt6. Tentando instalacao alternativa...
    python -m pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip
    python -m pip install --no-cache-dir PyQt6==6.6.1
    python -m pip install --no-cache-dir PyQt6-Qt6==6.6.1
    python -m pip install --no-cache-dir PyQt6-sip==13.6.0
)

REM Instalar torch e outras dependências ML/AI
echo Instalando torch e dependencias ML/AI...
python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install transformers==4.38.2
python -m pip install scikit-learn==1.4.0
python -m pip install tensorboard==2.15.2

REM Instalar dependências para web scraping e navegação
echo Instalando dependencias para navegacao web...
python -m pip install requests>=2.31.0
python -m pip install beautifulsoup4>=4.12.3
python -m pip install selenium>=4.17.2
python -m pip install webdriver-manager>=4.0.1

echo Instalando outras dependencias essenciais...
python -m pip install python-dotenv==1.0.1
python -m pip install jinja2>=3.1.3
python -m pip install pillow==10.2.0
python -m pip install pyqtdarktheme==2.1.0

REM Instalar qt_material por último para garantir que o PyQt já esteja instalado
echo Instalando qt_material (depois do PyQt)...
python -m pip install qt-material==2.14

REM Instalar PyInstaller
echo.
echo [3/7] Instalando PyInstaller...
python -m pip install pyinstaller>=6.3.0

REM ===== PREPARAR RECURSOS =====
echo.
echo [4/7] Preparando recursos para compilacao...

REM Criar pasta resources se não existir
if not exist resources (
    echo Criando pasta resources...
    mkdir resources
)

REM ===== CRIAR SCRIPT DE CONFIGURAÇÃO PARA WEBDRIVER =====
echo.
echo [5/7] Criando script de configuracao para webdriver...

echo import os > setup_webdriver.py
echo from webdriver_manager.chrome import ChromeDriverManager >> setup_webdriver.py
echo from selenium import webdriver >> setup_webdriver.py
echo from selenium.webdriver.chrome.service import Service >> setup_webdriver.py
echo from selenium.webdriver.chrome.options import Options >> setup_webdriver.py
echo. >> setup_webdriver.py
echo def setup_chrome_driver(): >> setup_webdriver.py
echo     chrome_options = Options() >> setup_webdriver.py
echo     chrome_options.add_argument("--headless") >> setup_webdriver.py
echo     chrome_options.add_argument("--disable-gpu") >> setup_webdriver.py
echo     chrome_options.add_argument("--no-sandbox") >> setup_webdriver.py
echo     chrome_options.add_argument("--disable-dev-shm-usage") >> setup_webdriver.py
echo     chrome_options.add_argument("--log-level=3") >> setup_webdriver.py
echo     driver_path = ChromeDriverManager().install() >> setup_webdriver.py
echo     service = Service(driver_path) >> setup_webdriver.py
echo     driver = webdriver.Chrome(service=service, options=chrome_options) >> setup_webdriver.py
echo     return driver >> setup_webdriver.py
echo. >> setup_webdriver.py
echo if __name__ == "__main__": >> setup_webdriver.py
echo     try: >> setup_webdriver.py
echo         driver = setup_chrome_driver() >> setup_webdriver.py
echo         print("Webdriver configurado com sucesso!") >> setup_webdriver.py
echo         driver.quit() >> setup_webdriver.py
echo     except Exception as e: >> setup_webdriver.py
echo         print(f"Erro ao configurar webdriver: {e}") >> setup_webdriver.py

REM Inicializar o webdriver para download
echo Inicializando webdriver (pode demorar na primeira execucao)...
python setup_webdriver.py

REM ===== COMPILAR EXECUTÁVEL =====
echo.
echo [6/7] Compilando executavel...

if not exist gui_interface.py (
    echo ERRO: Arquivo gui_interface.py nao encontrado!
    echo Verifique se voce esta no diretorio correto.
    call venv_build\Scripts\deactivate.bat
    pause
    exit /b 1
)

REM Limpar a pasta dist se já existir
if exist dist (
    echo Limpando pasta dist...
    rmdir /s /q dist
)

REM Criar pasta dist novamente
mkdir dist

echo Compilando com PyInstaller...
python -m PyInstaller --onefile --windowed --name="Self-Evolving-Bot" --add-data "resources;resources" --hidden-import=torch --hidden-import=transformers --hidden-import=numpy --hidden-import=scikit-learn --hidden-import=tensorboard --hidden-import=PIL --hidden-import=PyQt6 --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=qt_material --hidden-import=pyqtdarktheme --hidden-import=selenium --hidden-import=webdriver_manager --hidden-import=beautifulsoup4 --hidden-import=requests --collect-all=selenium --collect-all=webdriver_manager --add-data "improved_web_search.py;." --add-data "web_integration.py;." gui_interface.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Primeira tentativa falhou. Tentando com menos opcoes...
    python -m PyInstaller --onefile --windowed --name="Self-Evolving-Bot" --hidden-import=torch --hidden-import=transformers --hidden-import=numpy --hidden-import=requests --hidden-import=PyQt6 --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=selenium --hidden-import=webdriver_manager --hidden-import=beautifulsoup4 --add-data "improved_web_search.py;." --add-data "web_integration.py;." gui_interface.py
)

REM ===== LIMPEZA E FINALIZAÇÃO =====
echo.
echo [7/7] Finalizando e limpando...

REM Desativar ambiente virtual
call venv_build\Scripts\deactivate.bat

REM Verificar se o executável foi criado
if not exist dist\Self-Evolving-Bot.exe (
    echo.
    echo ERRO: O executavel nao foi criado corretamente!
    echo Tentando compilacao alternativa final...
    
    REM Ativar novamente o ambiente virtual para uma última tentativa
    call venv_build\Scripts\activate.bat
    
    REM Tentar compilação mais simples com as opções mínimas
    python -m PyInstaller --clean --name "Self-Evolving-Bot" --onefile --noconsole --hidden-import=torch --hidden-import=requests --hidden-import=selenium --hidden-import=PyQt6 --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --add-data "improved_web_search.py;." --add-data "web_integration.py;." gui_interface.py
    
    REM Desativar ambiente virtual novamente
    call venv_build\Scripts\deactivate.bat
    
    if not exist dist\Self-Evolving-Bot.exe (
        echo ERRO: Falha na compilacao do executavel.
        echo Verifique os logs acima para mais detalhes.
        pause
        exit /b 1
    )
)

echo.
echo Compilacao concluida com sucesso!
echo O executavel foi criado em: dist\Self-Evolving-Bot.exe
echo.
echo Pressione qualquer tecla para sair...
pause >nul 