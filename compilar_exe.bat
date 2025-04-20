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

REM Instalar torch primeiro
echo Instalando torch...
python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu

REM Instalar dependências ML/AI
echo Instalando dependencias de ML/AI...
python -m pip install numpy==2.2.5
python -m pip install transformers==4.51.3
python -m pip install scikit-learn==1.6.1
python -m pip install tensorboard==2.19.0

REM Instalar dependências para web scraping e navegação
echo Instalando dependencias para navegacao web...
python -m pip install requests>=2.28.0
python -m pip install beautifulsoup4>=4.12.0
python -m pip install selenium>=4.14.0
python -m pip install webdriver-manager>=4.0.0

REM Instalar dependências na ordem correta para evitar o aviso do qt_material
echo Instalando PyQt6 primeiro...
python -m pip install PyQt6==6.9.0

echo Instalando outras dependencias essenciais...
python -m pip install python-dotenv==1.1.0
python -m pip install jinja2>=3.1.2
python -m pip install pillow==11.2.1
python -m pip install pyqtdarktheme==0.1.7

REM Instalar qt_material por último para garantir que o PyQt já esteja instalado
echo Instalando qt_material (depois do PyQt)...
python -m pip install qt-material==2.14

REM Instalar PyInstaller
echo.
echo [3/7] Instalando PyInstaller...
python -m pip install pyinstaller

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
python -m PyInstaller --onefile --windowed --name="Self-Evolving-Bot" --add-data "resources;resources" --hidden-import=torch --hidden-import=transformers --hidden-import=numpy --hidden-import=scikit-learn --hidden-import=tensorboard --hidden-import=PIL --hidden-import=PyQt6 --hidden-import=qt_material --hidden-import=pyqtdarktheme --hidden-import=selenium --hidden-import=webdriver_manager --hidden-import=beautifulsoup4 --hidden-import=requests --collect-all=selenium --collect-all=webdriver_manager --add-data "improved_web_search.py;." --add-data "web_integration.py;." gui_interface.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Primeira tentativa falhou. Tentando com menos opcoes...
    python -m PyInstaller --onefile --windowed --name="Self-Evolving-Bot" --hidden-import=torch --hidden-import=transformers --hidden-import=numpy --hidden-import=requests --hidden-import=PyQt6 --hidden-import=selenium --hidden-import=webdriver_manager --hidden-import=beautifulsoup4 --add-data "improved_web_search.py;." --add-data "web_integration.py;." gui_interface.py
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
    python -m PyInstaller --clean --name "Self-Evolving-Bot" --onefile --noconsole --hidden-import=torch --hidden-import=requests --hidden-import=selenium --add-data "improved_web_search.py;." --add-data "web_integration.py;." gui_interface.py
    
    REM Desativar ambiente virtual novamente
    call venv_build\Scripts\deactivate.bat
    
    if not exist dist\Self-Evolving-Bot.exe (
        echo ERRO: Falha na compilacao do executavel.
        pause
        exit /b 1
    ) else (
        echo Ultima tentativa bem-sucedida!
    )
) else (
    echo Executavel criado com sucesso!
)

REM Limpar arquivos temporários
if exist build (
    rmdir /s /q build
)

REM Copiar arquivos de dados necessários
if exist knowledge.json (
    echo Copiando base de conhecimento para a pasta dist...
    copy knowledge.json dist\
)

if exist memories.pkl (
    echo Copiando memórias para a pasta dist...
    copy memories.pkl dist\
)

if exist web_cache.json (
    echo Copiando cache web para a pasta dist...
    copy web_cache.json dist\
)

if exist language_model.pkl (
    echo Copiando modelo de linguagem para a pasta dist...
    copy language_model.pkl dist\
)

echo.
echo ===================================================================
echo                      COMPILACAO CONCLUIDA!
echo ===================================================================
echo.
echo O executavel foi criado em: dist\Self-Evolving-Bot.exe
echo.
echo NOTA: Para usar a funcionalidade de pesquisa web, o Google Chrome 
echo deve estar instalado no computador.
echo.
echo Pressione qualquer tecla para sair...
pause >nul 