import os 
import sys
import shutil

# Função para buscar se o ChromeDriver já existe localmente
def find_local_chromedriver():
    # Locais possíveis do chromedriver
    possible_locations = [
        os.path.join(os.getcwd(), "chromedriver.exe"),
        os.path.join(os.getcwd(), "drivers", "chromedriver.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "ChromeDriver", "chromedriver.exe"),
        os.path.join(os.environ.get("APPDATA", ""), "ChromeDriver", "chromedriver.exe")
    ]
    
    for location in possible_locations:
        if os.path.exists(location):
            return location
    
    return None

# Tente importar o webdriver_manager, mas continue mesmo se falhar
webdriver_manager_available = False
try:
    from webdriver_manager.chrome import ChromeDriverManager 
    webdriver_manager_available = True
except ImportError:
    print("Módulo webdriver_manager não encontrado. Usando método alternativo.")

try:
    from selenium import webdriver 
    from selenium.webdriver.chrome.service import Service 
    from selenium.webdriver.chrome.options import Options 
    from selenium.common.exceptions import WebDriverException
    selenium_available = True
except ImportError:
    print("Módulo selenium não encontrado. A funcionalidade web será desativada.")
    selenium_available = False
 
def setup_chrome_driver(): 
    if not selenium_available:
        print("Selenium não está instalado. Não é possível configurar o WebDriver.")
        return None
        
    print("Configurando Chrome WebDriver para integração web...")
    
    chrome_options = Options() 
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage") 
    chrome_options.add_argument("--log-level=3")
    
    try:
        # Método 1: Usar webdriver_manager se disponível
        if webdriver_manager_available:
            print("Instalando/atualizando ChromeDriver usando webdriver_manager...")
            driver_path = ChromeDriverManager().install() 
            print(f"ChromeDriver instalado em: {driver_path}")
        else:
            # Método 2: Verificar se o ChromeDriver já existe localmente
            driver_path = find_local_chromedriver()
            if driver_path:
                print(f"ChromeDriver local encontrado em: {driver_path}")
            else:
                print("Não foi possível encontrar ou instalar o ChromeDriver.")
                print("A funcionalidade web será limitada.")
                return None
        
        service = Service(driver_path) 
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Conexão com Chrome WebDriver estabelecida com sucesso.")
        return driver
    except WebDriverException as e:
        print(f"Erro WebDriver: {e}")
        print("Verifique se o Google Chrome está instalado no seu sistema.")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None
 
if __name__ == "__main__": 
    try: 
        print("Iniciando teste de configuração do WebDriver...")
        driver = setup_chrome_driver() 
        
        if driver:
            print("Teste de navegação...")
            driver.get("https://www.google.com")
            print("Teste concluído com sucesso!")
            driver.quit()
            print("WebDriver configurado e pronto para uso com o Self-Evolving Bot.")
        else:
            print("Não foi possível inicializar o WebDriver.")
            print("O bot funcionará sem acesso à web.")
    except Exception as e: 
        print(f"Erro ao testar webdriver: {e}")
        print("O bot ainda pode funcionar, mas sem acesso à web.")
    
    # Pausa para mostrar as mensagens se executado diretamente
    if len(sys.argv) > 1 and sys.argv[1] == "--pause":
        input("Pressione ENTER para continuar...")
