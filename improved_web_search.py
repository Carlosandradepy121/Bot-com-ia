import os
import json
import time
import requests
from urllib.parse import quote_plus
import re
from collections import deque
import socket
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Importações opcionais com fallback
try:
    from bs4 import BeautifulSoup
    bs4_available = True
except ImportError:
    bs4_available = False
    print("Aviso: BeautifulSoup4 não encontrado. Algumas funcionalidades serão limitadas.")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    selenium_available = True
except ImportError:
    selenium_available = False
    print("Aviso: Selenium não encontrado. Busca na web com navegador não estará disponível.")

# Importação opcional do webdriver_manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    webdriver_manager_available = True
except ImportError:
    webdriver_manager_available = False
    print("Aviso: webdriver_manager não encontrado. ChromeDriver deve ser configurado manualmente.")

class WebSearchException(Exception):
    """Exceção personalizada para erros de busca na web."""
    pass

class WebSearcher:
    """Classe para realizar buscas na internet e extrair informações relevantes."""
    
    def __init__(self, api_key: Optional[str] = None, 
                 cache_results: bool = True,
                 max_results: int = 5,
                 timeout: int = 10):
        """
        Inicializa o buscador web.
        
        Args:
            api_key: Chave de API opcional para serviços de busca premium
            cache_results: Se deve armazenar em cache os resultados
            max_results: Número máximo de resultados a retornar
            timeout: Tempo limite para requisições em segundos
        """
        self.api_key = api_key
        self.cache_results = cache_results
        self.max_results = max_results
        self.timeout = timeout
        self.cache = {}
        self.last_search_time = 0
        self.search_delay = 1  # Segundos entre buscas para evitar bloqueios
        # Verifica conexão com internet
        try:
            socket.create_connection(("www.google.com", 80), timeout=2)
            self.online = True
            print("WebSearcher: Conexão com a internet disponível.")
        except:
            self.online = False
            print("WebSearcher: Sem conexão com a internet.")
        
    def search(self, query: str) -> str:
        """
        Realiza uma busca na web e retorna as informações mais relevantes.
        
        Args:
            query: A consulta de busca
            
        Returns:
            Texto com as informações relevantes encontradas
            
        Raises:
            WebSearchException: Se ocorrer um erro durante a busca
        """
        if not self.online:
            return f"Sem conexão com a internet. Não foi possível buscar informações sobre '{query}'."
            
        # Verifica se o resultado está em cache
        if self.cache_results and query in self.cache:
            print(f"Usando resultado em cache para: '{query}'")
            return self.cache[query]["result"]
            
        # Respeita o delay entre buscas
        current_time = time.time()
        time_since_last = current_time - self.last_search_time
        if time_since_last < self.search_delay:
            time.sleep(self.search_delay - time_since_last)
            
        try:
            # Tenta primeiro com a busca usando DuckDuckGo web
            print(f"Buscando informações sobre: '{query}'")
            results = self._direct_web_search(query)
            
            # Se não obtiver resultados, tenta o método de fallback
            if not results:
                print("Sem resultados diretos. Usando método alternativo.")
                results = self._fallback_search(query)
            
            # Processa e resume os resultados
            summary = self._summarize_results(results, query)
            
            # Atualiza o tempo da última busca
            self.last_search_time = time.time()
            
            # Armazena em cache se habilitado
            if self.cache_results:
                self.cache[query] = {
                    "timestamp": datetime.now().isoformat(),
                    "result": summary
                }
                
            return summary
            
        except Exception as e:
            error_msg = f"Erro na busca web: {str(e)}"
            raise WebSearchException(error_msg)
    
    def _direct_web_search(self, query: str) -> List[Dict[str, str]]:
        """
        Realiza uma busca direta usando DuckDuckGo ou Google.
        
        Args:
            query: A consulta de busca
            
        Returns:
            Lista de resultados com título, url e trecho
        """
        try:
            # Codifica a consulta para URL
            encoded_query = quote_plus(query)
            
            # Tenta primeiro pelo DuckDuckGo
            ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"Conectando-se a {ddg_url}")
            response = requests.get(ddg_url, headers=headers, timeout=self.timeout)
            
            if not bs4_available:
                print("BeautifulSoup não disponível, usando resultados simulados.")
                return self._get_simulated_results(query)
                
            results = []
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                result_elements = soup.select('.result')
                
                for i, result in enumerate(result_elements):
                    if i >= self.max_results:
                        break
                        
                    title_elem = result.select_one('.result__a')
                    snippet_elem = result.select_one('.result__snippet')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        results.append({
                            'title': title,
                            'snippet': snippet,
                            'url': url
                        })
                        
                print(f"Encontrados {len(results)} resultados do DuckDuckGo")
                return results
                
            print(f"Falha na busca DuckDuckGo (status code {response.status_code}), tentando Google")
                
            # Se DuckDuckGo falhar, tenta com Google
            google_url = f"https://www.google.com/search?q={encoded_query}"
            response = requests.get(google_url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Busca divs que contêm resultados
                for div in soup.find_all('div', class_=['g', 'tF2Cxc']):
                    if len(results) >= self.max_results:
                        break
                        
                    title_elem = div.find('h3')
                    anchor = div.find('a')
                    snippet_div = div.find('div', class_=['VwiC3b', 'yXK7lf'])
                    
                    if title_elem and anchor:
                        title = title_elem.get_text(strip=True)
                        url = anchor.get('href', '')
                        snippet = snippet_div.get_text(strip=True) if snippet_div else ""
                        
                        if title and (url.startswith('http') or url.startswith('https')):
                            results.append({
                                'title': title,
                                'snippet': snippet,
                                'url': url
                            })
                
                print(f"Encontrados {len(results)} resultados do Google")
                return results
                
        except Exception as e:
            print(f"Erro na busca direta: {e}")
        
        # Em caso de falha, retorna um resultado vazio
        return []
    
    def _get_simulated_results(self, query: str) -> List[Dict[str, str]]:
        """Retorna resultados simulados quando os serviços reais não estão disponíveis"""
        return [
            {
                "title": f"Informações sobre {query}",
                "url": f"https://exemplo.com/info/{quote_plus(query)}",
                "snippet": f"Informação relevante sobre {query}. Este é um resultado simulado para demonstração."
            },
            {
                "title": f"{query} - Wikipédia",
                "url": f"https://pt.wikipedia.org/wiki/{quote_plus(query)}",
                "snippet": f"Segundo a Wikipédia, {query} é um tópico importante com várias características interessantes."
            }
        ]
    
    def _fallback_search(self, query: str) -> List[Dict[str, str]]:
        """
        Método de busca alternativo usando um serviço público básico.
        
        Args:
            query: A consulta de busca
            
        Returns:
            Lista de resultados com título, url e trecho
        """
        # Esta é uma implementação simulada para demonstração
        # Em um ambiente real, você poderia usar a API de busca do DuckDuckGo, Bing, etc.
        
        results = []
        try:
            # Simulando uma busca - em uma implementação real, usaria uma API ou scraping ético
            encoded_query = quote_plus(query)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # Nota: Em uma implementação real, este seria um endpoint de API válido
            # Esta linha está comentada pois não fará uma busca real
            # response = requests.get(f"https://api.exemplo.com/search?q={encoded_query}", headers=headers, timeout=self.timeout)
            
            # Resultados simulados para demonstração
            simulated_results = [
                {
                    "title": f"Informações sobre {query}",
                    "url": f"https://exemplo.com/info/{encoded_query}",
                    "snippet": f"Informação relevante sobre {query}. Este é um resultado simulado para demonstração."
                },
                {
                    "title": f"{query} - Wikipédia",
                    "url": f"https://pt.wikipedia.org/wiki/{encoded_query}",
                    "snippet": f"Segundo a Wikipédia, {query} é um tópico importante com várias características interessantes."
                }
            ]
            
            results = simulated_results[:self.max_results]
            
        except requests.RequestException as e:
            print(f"Erro na requisição: {e}")
            # Em caso de falha, retorna um resultado vazio
            return []
            
        return results
    
    def _summarize_results(self, results: List[Dict[str, str]], query: str) -> str:
        """
        Processa os resultados da busca e cria um resumo coerente.
        
        Args:
            results: Lista de resultados da busca
            query: A consulta original
            
        Returns:
            Texto resumido com as informações mais relevantes
        """
        if not results:
            return f"Não foram encontradas informações online sobre '{query}'."
            
        # Extrai os trechos mais relevantes
        snippets = [result["snippet"] for result in results if "snippet" in result]
        
        if not snippets:
            return f"Foram encontrados resultados para '{query}', mas sem informações detalhadas."
            
        # Constrói um resumo básico
        summary = f"De acordo com informações online: {' '.join(snippets[:3])}"
        
        # Adiciona fontes, se disponíveis
        if results and "url" in results[0]:
            sources = [f"{i+1}. {result['url']}" for i, result in enumerate(results[:3]) if "url" in result]
            if sources:
                summary += f"\n\nFontes: " + "; ".join(sources)
                
        return summary.strip()
    
    def clear_cache(self):
        """Limpa o cache de resultados."""
        self.cache = {}
        
    def set_api_key(self, api_key: str):
        """
        Define a chave de API para serviços premium.
        
        Args:
            api_key: A chave de API
        """
        self.api_key = api_key
        
    def get_trending_topics(self) -> List[str]:
        """
        Obtém tópicos em tendência atualmente.
        
        Returns:
            Lista de tópicos em tendência
        """
        # Implementação simulada
        return [
            "Inteligência Artificial",
            "Desenvolvimento Sustentável",
            "Novas Tecnologias",
            "Ciência de Dados",
            "Programação Python"
        ]

class ImprovedWebSearch:
    """Módulo aprimorado para pesquisa web usando Selenium com Chrome"""
    
    def __init__(self, cache_size=100, headless=True):
        self.online = self._check_connection()
        self.cache = {}
        self.cache_size = cache_size
        self.cache_keys = deque(maxlen=cache_size)
        self.driver = None
        self.headless = headless
        self.load_cache()
        
    def _check_connection(self):
        """Verifica se há conexão com a internet"""
        try:
            # Tenta conectar ao Google para testar a conexão
            socket.create_connection(("www.google.com", 80), timeout=2)
            return True
        except (OSError, socket.timeout):
            print("Aviso: Sem conexão com a internet. Modo offline ativado.")
            return False
    
    def _initialize_driver(self):
        """Inicializa o driver do Chrome se ainda não estiver inicializado"""
        if self.driver is not None:
            return True
            
        if not selenium_available:
            print("Selenium não está disponível. Impossível inicializar o driver.")
            return False
            
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--log-level=3")  # Silencia logs menos importantes
            
            # Método 1: Usar ChromeDriverManager se disponível
            if webdriver_manager_available:
                try:
                    print("Usando ChromeDriverManager para instalar o driver...")
                    driver_path = ChromeDriverManager().install()
                    service = Service(driver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    return True
                except Exception as e:
                    print(f"Erro ao usar ChromeDriverManager: {e}")
            
            # Método 2: Procurar ChromeDriver localmente
            print("Procurando ChromeDriver instalado localmente...")
            driver_path = self._find_local_chromedriver()
            if driver_path:
                print(f"ChromeDriver encontrado em: {driver_path}")
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                return True
                
            # Método 3: Tentar usar ChromeDriver do PATH
            try:
                print("Tentando usar ChromeDriver do PATH...")
                self.driver = webdriver.Chrome(options=chrome_options)
                return True
            except Exception as e:
                print(f"Erro ao usar ChromeDriver do PATH: {e}")
                
            print("Erro: ChromeDriver não encontrado. Verifique se o Chrome está instalado.")
            return False
                
        except Exception as e:
            print(f"Erro ao inicializar driver do Chrome: {e}")
            return False
    
    def _find_local_chromedriver(self):
        """Procura o ChromeDriver em locais comuns no sistema"""
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
    
    def load_cache(self):
        """Carrega o cache de pesquisas do disco"""
        if os.path.exists('web_cache.json'):
            try:
                with open('web_cache.json', 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.cache = cache_data.get('cache', {})
                    self.cache_keys = deque(cache_data.get('keys', []), maxlen=self.cache_size)
                print(f"Cache de pesquisas carregado: {len(self.cache)} entradas")
            except Exception as e:
                print(f"Erro ao carregar cache de pesquisas: {e}")
    
    def save_cache(self):
        """Salva o cache de pesquisas no disco"""
        try:
            cache_data = {
                'cache': self.cache,
                'keys': list(self.cache_keys)
            }
            with open('web_cache.json', 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"Cache de pesquisas salvo: {len(self.cache)} entradas")
        except Exception as e:
            print(f"Erro ao salvar cache de pesquisas: {e}")
    
    def close(self):
        """Fecha o driver do Chrome se estiver aberto"""
        if self.driver is not None:
            try:
                self.driver.quit()
                self.driver = None
            except:
                pass
    
    def search_google(self, query, max_results=5):
        """Realiza uma pesquisa no Google usando Selenium"""
        # Normaliza a consulta
        normalized_query = query.lower().strip()
        
        # Verifica se a consulta está no cache
        if normalized_query in self.cache:
            print(f"Usando resultados em cache para: {normalized_query}")
            return self.cache[normalized_query]
        
        # Se estiver offline, retorna vazio
        if not self.online:
            print("Dispositivo offline. Não é possível realizar pesquisa.")
            return []
        
        # Inicializa o driver se necessário
        if not self._initialize_driver():
            print("Não foi possível inicializar o driver. Usando método alternativo.")
            return self._fallback_search(query, max_results)
        
        try:
            print(f"Realizando pesquisa no Google para: '{query}'")
            # Acessa o Google
            self.driver.get("https://www.google.com")
            
            # Aguarda carregamento da página e aceita cookies se necessário
            try:
                cookie_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceito') or contains(text(), 'Accept') or contains(@aria-label, 'Accept')]"))
                )
                cookie_button.click()
                print("Aceitou cookies do Google")
            except Exception as e:
                # Prossegue se não houver diálogo de cookies
                print(f"Sem diálogo de cookies ou erro: {e}")
                pass
                
            # Encontra a caixa de pesquisa e insere a consulta
            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                print("Consulta enviada para o Google")
            except Exception as e:
                print(f"Erro ao enviar consulta para o Google: {e}")
                return self._fallback_search(query, max_results)
            
            # Aguarda os resultados carregarem
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "search"))
                )
                # Pequena pausa para garantir o carregamento completo
                time.sleep(2)
                print("Página de resultados carregada")
            except Exception as e:
                print(f"Erro ao aguardar carregamento de resultados: {e}")
                # Tentar continuar mesmo sem o elemento específico
                time.sleep(3)
            
            # Extrai os resultados - versão mais robusta com múltiplos seletores
            search_results = []
            selectors = [
                "div.g", 
                "div.Gx5Zad", 
                "div.kvH3mc",
                "div.tF2Cxc",
                "div.yuRUbf"
            ]
            
            result_elements = []
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Encontrados {len(elements)} resultados com seletor {selector}")
                    result_elements = elements
                    break
            
            if not result_elements:
                print("Nenhum resultado encontrado com os seletores padrão")
                # Capturar qualquer div que possa conter resultados
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-hveid]")
                print(f"Tentativa alternativa: {len(result_elements)} elementos encontrados")
            
            for i, element in enumerate(result_elements):
                if i >= max_results:
                    break
                    
                try:
                    # Extrai título, snippet e URL com múltiplas tentativas
                    title = ""
                    url = ""
                    snippet = ""
                    
                    # Tenta diferentes seletores para o título
                    for title_selector in ["h3", "h3.LC20lb", ".DKV0Md", ".vvjwJb"]:
                        try:
                            title_element = element.find_element(By.CSS_SELECTOR, title_selector)
                            title = title_element.text
                            if title:
                                break
                        except:
                            continue
                    
                    # Tenta diferentes seletores para o URL
                    for url_selector in ["a", "a[href]", ".yuRUbf a", ".NJjxre a"]:
                        try:
                            link_element = element.find_element(By.CSS_SELECTOR, url_selector)
                            url = link_element.get_attribute("href")
                            if url:
                                break
                        except:
                            continue
                    
                    # Tenta diferentes seletores para o snippet
                    for snippet_selector in ["div.VwiC3b", ".s3v9rd", ".VwiC3b", ".lEBKkf"]:
                        try:
                            snippet_element = element.find_element(By.CSS_SELECTOR, snippet_selector)
                            snippet = snippet_element.text
                            if snippet:
                                break
                        except:
                            continue
                    
                    if title or url or snippet:
                        search_results.append({
                            'title': title or "Sem título",
                            'snippet': snippet or "Sem descrição",
                            'url': url or ""
                        })
                        print(f"Resultado {i+1} extraído: {title[:30]}...")
                except Exception as result_error:
                    print(f"Erro ao extrair resultado {i+1}: {result_error}")
                    continue
            
            print(f"Total de resultados processados: {len(search_results)}")
            if not search_results:
                print("Nenhum resultado extraído. Usando método alternativo.")
                return self._fallback_search(query, max_results)
            
            # Adiciona ao cache
            self.cache[normalized_query] = search_results
            self.cache_keys.append(normalized_query)
            
            # Se o cache atingiu o tamanho máximo, remove o item mais antigo
            if len(self.cache) > self.cache_size:
                oldest_key = self.cache_keys[0]
                if oldest_key in self.cache:
                    del self.cache[oldest_key]
            
            # Salva o cache atualizado
            self.save_cache()
            
            return search_results
            
        except Exception as e:
            print(f"Erro ao realizar pesquisa com Selenium: {e}")
            # Tenta usar método alternativo se o Selenium falhar
            return self._fallback_search(query, max_results)
    
    def _fallback_search(self, query, max_results=5):
        """Método alternativo de pesquisa usando requests (fallback)"""
        try:
            print(f"Usando método de pesquisa alternativo para: '{query}'")
            # Codifica a consulta para URL
            encoded_query = quote_plus(query)
            
            # Tenta primeiro pelo DuckDuckGo
            ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            google_url = f"https://www.google.com/search?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Tenta com DuckDuckGo
            search_results = []
            try:
                response = requests.get(ddg_url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print("Conexão com DuckDuckGo bem-sucedida")
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = soup.select('.result')
                    
                    for i, result in enumerate(results):
                        if i >= max_results:
                            break
                            
                        title_elem = result.select_one('.result__a')
                        snippet_elem = result.select_one('.result__snippet')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = title_elem.get('href', '')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                            
                            search_results.append({
                                'title': title,
                                'snippet': snippet,
                                'url': url
                            })
                            print(f"Resultado DuckDuckGo {i+1} extraído: {title[:30]}...")
            except Exception as ddg_error:
                print(f"Erro ao pesquisar no DuckDuckGo: {ddg_error}")
            
            # Se não conseguiu resultados com DuckDuckGo, tenta Google como texto
            if not search_results:
                try:
                    response = requests.get(google_url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        print("Conexão com Google bem-sucedida")
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Tenta extrair resultados do Google (mais difícil com JavaScript desativado)
                        for i, div in enumerate(soup.find_all('div', class_=['g', 'tF2Cxc', 'yuRUbf'])):
                            if i >= max_results:
                                break
                                
                            try:
                                title_elem = div.find('h3')
                                a_elem = div.find('a')
                                snippet_div = div.find('div', class_=['VwiC3b', 'yXK7lf'])
                                
                                if title_elem and a_elem:
                                    title = title_elem.get_text(strip=True)
                                    url = a_elem.get('href', '')
                                    snippet = snippet_div.get_text(strip=True) if snippet_div else ""
                                    
                                    search_results.append({
                                        'title': title,
                                        'snippet': snippet,
                                        'url': url
                                    })
                                    print(f"Resultado Google {i+1} extraído: {title[:30]}...")
                            except:
                                continue
                except Exception as google_error:
                    print(f"Erro ao pesquisar no Google: {google_error}")
            
            # Resultados simulados como último recurso
            if not search_results:
                print("Sem resultados reais. Criando resultados demonstrativos.")
                search_results = [
                    {
                        'title': f"Informações sobre {query}",
                        'snippet': f"Não foi possível obter informações reais sobre '{query}'. Este é um resultado simulado para demonstração.",
                        'url': f"https://www.google.com/search?q={encoded_query}"
                    },
                    {
                        'title': f"Busca por {query}",
                        'snippet': f"Este é um resultado simulado pois não foi possível obter resultados reais da web. A funcionalidade de busca pode precisar de configuração adicional.",
                        'url': f"https://duckduckgo.com/?q={encoded_query}"
                    }
                ]
            
            # Adiciona ao cache
            normalized_query = query.lower().strip()
            self.cache[normalized_query] = search_results
            self.cache_keys.append(normalized_query)
            self.save_cache()
            
            return search_results
            
        except Exception as e:
            print(f"Erro ao realizar pesquisa fallback: {e}")
            return []
    
    def search(self, query, max_results=5):
        """Método principal de pesquisa, tenta usar o Chrome primeiro"""
        return self.search_google(query, max_results)
    
    def get_info_from_web(self, query):
        """Obtém informações da web e as formata para uso pelo bot"""
        results = self.search(query)
        
        if not results:
            return "Desculpe, não consegui encontrar informações sobre isso no momento."
        
        # Formata os resultados para uma resposta legível
        response = f"Encontrei algumas informações sobre '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            response += f"{i}. {result['title']}\n"
            if result['snippet']:
                response += f"   {result['snippet']}\n"
            if result['url']:
                response += f"   Link: {result['url']}\n"
            response += "\n"
        
        response += "Espero que essas informações sejam úteis! Posso buscar mais detalhes se você precisar."
        return response
    
    def fetch_webpage_content(self, url):
        """Obtém o conteúdo de uma página web específica"""
        if not self.online:
            return "Não foi possível acessar a página, verifique sua conexão com a internet."
            
        try:
            # Tenta primeiro com requests (mais rápido)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove scripts, estilos e outros elementos não desejados
                for script in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                    script.extract()
                
                # Extrai texto principal
                text = soup.get_text(separator='\n', strip=True)
                
                # Limpa linhas em branco excessivas
                text = re.sub(r'\n\s*\n', '\n\n', text)
                
                # Limita o tamanho do texto
                if len(text) > 2000:
                    text = text[:2000] + "... (conteúdo truncado)"
                
                return f"Conteúdo da página {url}:\n\n{text}"
            else:
                return f"Erro ao acessar a página: status {response.status_code}"
                
        except Exception as e:
            # Se falhar, tenta com Selenium
            if not self._initialize_driver():
                return f"Não foi possível acessar a página: {str(e)}"
                
            try:
                self.driver.get(url)
                time.sleep(3)  # Aguarda carregamento
                
                # Extrai o conteúdo da página
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                
                # Limita o tamanho do texto
                if len(body_text) > 2000:
                    body_text = body_text[:2000] + "... (conteúdo truncado)"
                
                return f"Conteúdo da página {url}:\n\n{body_text}"
                
            except Exception as e2:
                return f"Erro ao acessar a página: {str(e2)}"

# Exemplo de uso
if __name__ == "__main__":
    search_engine = ImprovedWebSearch()
    query = "Python programming language"
    print(f"Pesquisando: {query}")
    
    results = search_engine.search(query)
    if results:
        print(f"Encontrados {len(results)} resultados:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['snippet']}")
            print(f"   URL: {result['url']}")
            print()
    else:
        print("Nenhum resultado encontrado ou erro na pesquisa")
    
    search_engine.close() 