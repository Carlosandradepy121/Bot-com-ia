import os
import json
from datetime import datetime
from typing import Optional, Dict, List, Union, Any

# Variáveis globais
WEB_AVAILABLE = False
WEB_CACHE_FILE = "web_cache.json"

# Tenta importar o WebSearcher de improved_web_search
try:
    # Primeiro tenta importar o WebSearcher da classe antiga
    from improved_web_search import WebSearcher
    print("WebSearcher importado com sucesso.")
    WEB_AVAILABLE = True
except (ImportError, AttributeError):
    try:
        # Se falhar, tenta importar e usar ImprovedWebSearch como alternativa
        from improved_web_search import ImprovedWebSearch
        
        # Adapta a interface da classe ImprovedWebSearch para funcionar como WebSearcher
        class WebSearcherAdapter:
            def __init__(self, *args, **kwargs):
                print("Usando ImprovedWebSearch adaptado como WebSearcher")
                self.web_search = ImprovedWebSearch(headless=True)
                
            def search(self, query: str) -> str:
                try:
                    # Obtém informações da web usando o método get_info_from_web
                    results = self.web_search.get_info_from_web(query)
                    if results:
                        # Remove o prefixo do resultado para compatibilidade
                        if results.startswith("Encontrei algumas informações sobre"):
                            # Extrai apenas o conteúdo relevante
                            parts = results.split("\n\n", 1)
                            if len(parts) > 1:
                                clean_results = parts[1]
                            else:
                                clean_results = results
                        else:
                            clean_results = results
                        return clean_results
                    return f"Não foi possível encontrar informações sobre '{query}'."
                except Exception as e:
                    print(f"Erro ao buscar informações: {e}")
                    return f"Erro na busca web: {str(e)}"
                    
            def clear_cache(self):
                if hasattr(self.web_search, 'clear_cache'):
                    self.web_search.clear_cache()
                elif hasattr(self.web_search, 'save_cache'):
                    self.web_search.save_cache()
        
        WebSearcher = WebSearcherAdapter
        print("Adaptador de WebSearcher criado com sucesso.")
        WEB_AVAILABLE = True
    except ImportError:
        print("Módulo de busca web não disponível. Funcionalidade de pesquisa na internet desativada.")
        
        # Classe WebSearcher substituta quando o módulo original não está disponível
        class WebSearcher:
            def __init__(self, *args, **kwargs):
                print("WebSearcher substituta iniciada - funcionalidade limitada.")
                
            def search(self, query: str) -> str:
                return f"A busca na web está desabilitada. Não foi possível buscar informações sobre '{query}'."
                
            def clear_cache(self):
                pass

class WebEnabledBot:
    """Versão aprimorada do bot com capacidade de busca na web."""
    
    def __init__(self, base_bot, auto_learn=True, web_enabled=False):
        """
        Inicializa o bot com capacidade web.
        
        Args:
            base_bot: O bot base que será aprimorado com capacidades web
            auto_learn: Se o bot deve aprender automaticamente com as interações
            web_enabled: Se a busca na web está ativada
        """
        self.base_bot = base_bot
        self.auto_learn = auto_learn
        self.web_enabled = web_enabled and WEB_AVAILABLE
        self.web_searcher = WebSearcher() if self.web_enabled else None
        self.web_cache = self._load_web_cache()
        
        # Garantir que a chave 'queries' exista no cache
        if "queries" not in self.web_cache:
            self.web_cache["queries"] = {}
            self._save_web_cache()
        
        # Adicionar métodos de compatibilidade
        self._add_compatibility_methods()
        
    def _add_compatibility_methods(self):
        """Adiciona métodos de compatibilidade para garantir que WebEnabledBot funcione com SelfEvolvingBot"""
        
        # Garantir que learn_from_conversation esteja disponível
        if not hasattr(self, 'learn_from_conversation'):
            self.learn_from_conversation = self.learn
            
        # Métodos adicionais do SelfEvolvingBot para compatibilidade
        if not hasattr(self, 'toggle_auto_learning'):
            self.toggle_auto_learning = lambda: self.set_auto_learn(not self.auto_learn)
            
        if not hasattr(self, 'toggle_web_access'):
            self.toggle_web_access = lambda: self.set_web_enabled(not self.web_enabled)
            
        # Garantir que close esteja disponível para liberação de recursos
        if not hasattr(self, 'close'):
            def compatibility_close():
                if hasattr(self.web_searcher, 'clear_cache'):
                    self.web_searcher.clear_cache()
                self._save_web_cache()
                
            self.close = compatibility_close
            
        # Garantir que save_state esteja disponível
        if not hasattr(self, 'save_state'):
            self.save_state = lambda: self._save_web_cache()
        
    def _load_web_cache(self) -> Dict:
        """Carrega o cache de pesquisas web do arquivo."""
        default_cache = {"queries": {}, "last_updated": datetime.now().isoformat()}
        
        if os.path.exists(WEB_CACHE_FILE):
            try:
                with open(WEB_CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    
                # Garantir que o cache tenha a estrutura correta
                if not isinstance(cache, dict):
                    print("Formato de cache inválido. Criando novo cache.")
                    return default_cache
                    
                # Garantir que a chave 'queries' exista
                if "queries" not in cache:
                    print("Cache não contém a chave 'queries'. Adicionando-a.")
                    cache["queries"] = {}
                    
                return cache
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erro ao carregar cache web: {e}. Criando novo cache.")
        
        return default_cache
    
    def _save_web_cache(self):
        """Salva o cache de pesquisas web no arquivo."""
        try:
            # Garantir que as chaves necessárias existam antes de salvar
            if "queries" not in self.web_cache:
                self.web_cache["queries"] = {}
                
            self.web_cache["last_updated"] = datetime.now().isoformat()
            
            with open(WEB_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.web_cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Erro ao salvar cache web: {e}")
    
    def get_response(self, user_input: str) -> str:
        """
        Obtém uma resposta para a entrada do usuário, usando a web se necessário.
        
        Args:
            user_input: A entrada do usuário
            
        Returns:
            A resposta do bot
        """
        # Primeiro tenta responder com o conhecimento existente
        if hasattr(self.base_bot, 'get_response'):
            basic_response = self.base_bot.get_response(user_input)
        elif hasattr(self.base_bot, 'generate_response'):
            basic_response = self.base_bot.generate_response(user_input)
        else:
            basic_response = "Desculpe, não consigo processar sua solicitação no momento."
        
        # Se a busca web não estiver habilitada, retorna apenas a resposta básica
        if not self.web_enabled or not self.web_searcher:
            return basic_response
            
        # Verifica se a resposta básica indica incerteza ou falta de conhecimento
        uncertainty_indicators = [
            "não sei", "não tenho certeza", "não disponho dessa informação",
            "não tenho conhecimento", "não possuo informações", 
            "não fui treinado", "não tenho dados", "desconheço"
        ]
        
        # Adiciona nova verificação para forçar pesquisa web
        forced_search = any(keyword in user_input.lower() for keyword in ["pesquise", "busque", "procure na web", "na internet"])
        
        needs_web_search = forced_search or any(indicator.lower() in basic_response.lower() for indicator in uncertainty_indicators)
        
        # Garantir que a chave 'queries' exista
        if "queries" not in self.web_cache:
            self.web_cache["queries"] = {}
        
        if needs_web_search:
            # Verifica se a consulta já está no cache
            if user_input in self.web_cache["queries"]:
                cache_entry = self.web_cache["queries"][user_input]
                
                # Verificar se o cache tem formato válido
                if not isinstance(cache_entry, dict) or "timestamp" not in cache_entry or "result" not in cache_entry:
                    # Cache inválido, reconstruir
                    print("Formato de cache inválido para esta consulta. Atualizando...")
                else:
                    try:
                        cache_age = datetime.now() - datetime.fromisoformat(cache_entry["timestamp"])
                        
                        # Se o cache for recente (menos de 1 dia), usa-o
                        if cache_age.days < 1:
                            web_info = cache_entry["result"]
                            if web_info:
                                if isinstance(web_info, str) and len(web_info.strip()) > 0:
                                    return f"Com base em informações da web: {web_info}"
                                else:
                                    print(f"Cache contém resultado inválido: {web_info}")
                    except (ValueError, TypeError) as e:
                        print(f"Erro ao processar timestamp do cache: {e}")
            
            # Realiza a busca na web
            try:
                print(f"Realizando busca na web para: '{user_input}'")
                web_result = self.web_searcher.search(user_input)
                
                # Verifica se o resultado é válido
                if not web_result or not isinstance(web_result, str) or len(web_result.strip()) == 0:
                    print(f"Busca web retornou resultado vazio ou inválido: '{web_result}'")
                    return f"{basic_response} [Nota: Tentei buscar informações adicionais na web, mas não encontrei dados relevantes.]"
                
                # Atualiza o cache
                self.web_cache["queries"][user_input] = {
                    "timestamp": datetime.now().isoformat(),
                    "result": web_result
                }
                self._save_web_cache()
                
                return f"Com base em informações da web: {web_result}"
            except Exception as e:
                error_msg = str(e)
                print(f"Erro na busca web: {error_msg}")
                return f"{basic_response} [Nota: Tentei buscar informações adicionais na web, mas ocorreu um erro: {error_msg}]"
        
        return basic_response
    
    def learn(self, user_input: str, response: str):
        """
        Permite que o bot aprenda com a interação se o auto-aprendizado estiver ativado.
        
        Args:
            user_input: A entrada do usuário
            response: A resposta fornecida
        """
        if not self.auto_learn:
            return False
            
        if hasattr(self.base_bot, 'learn'):
            self.base_bot.learn(user_input, response)
            return True
        elif hasattr(self.base_bot, 'learn_from_conversation'):
            self.base_bot.learn_from_conversation(user_input, response)
            return True
        else:
            print("O bot base não possui métodos de aprendizado (learn/learn_from_conversation).")
            return False
    
    def set_web_enabled(self, enabled: bool):
        """
        Ativa ou desativa a funcionalidade de busca na web.
        
        Args:
            enabled: Se a busca na web deve ser ativada
        """
        if enabled and not WEB_AVAILABLE:
            return False
            
        self.web_enabled = enabled and WEB_AVAILABLE
        
        if self.web_enabled and self.web_searcher is None:
            self.web_searcher = WebSearcher()
        
        return self.web_enabled
    
    def set_auto_learn(self, enabled: bool):
        """
        Ativa ou desativa o auto-aprendizado.
        
        Args:
            enabled: Se o auto-aprendizado deve ser ativado
        """
        self.auto_learn = enabled
        return self.auto_learn
    
    @property
    def knowledge_base(self):
        """Acessa a base de conhecimento do bot base."""
        return self.base_bot.knowledge_base
    
    @property
    def memory(self):
        """Acessa a memória do bot base."""
        return self.base_bot.memory

    def generate_response(self, user_input: str) -> str:
        """
        Método compatível com SelfEvolvingBot para obter resposta.
        Este método redireciona para get_response.
        
        Args:
            user_input: A entrada do usuário
            
        Returns:
            A resposta do bot
        """
        # Garantir que o cache esteja corretamente inicializado
        if not hasattr(self, 'web_cache') or self.web_cache is None:
            self.web_cache = self._load_web_cache()
            
        if "queries" not in self.web_cache:
            self.web_cache["queries"] = {}
            
        return self.get_response(user_input)

def get_web_enabled_bot(base_bot, auto_learn=True, web_enabled=False):
    """
    Cria e retorna um bot com capacidade web.
    
    Args:
        base_bot: O bot base
        auto_learn: Se o auto-aprendizado deve ser ativado
        web_enabled: Se a busca na web deve ser ativada
    
    Returns:
        Um bot aprimorado com capacidade web
    """
    if not WEB_AVAILABLE:
        print("Aviso: Módulo de busca web não disponível. Utilizando bot padrão.")
        return base_bot
        
    return WebEnabledBot(base_bot, auto_learn, web_enabled)