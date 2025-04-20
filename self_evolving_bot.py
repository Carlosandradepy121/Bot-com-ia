import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
import os
import re
import random
from datetime import datetime
import pickle
from collections import deque
import threading
import time
import requests
from urllib.parse import quote_plus
import html
import socket

class KnowledgeBase:
    """Base de conhecimento com respostas predefinidas"""
    
    def __init__(self):
        # Dicionário com padrões e respostas
        self.patterns = {
            r'ol[aá]|oi|e a[ií]|tudo bem': [
                "Olá! Como posso ajudar você hoje?",
                "Oi! Em que posso ser útil?",
                "Olá! Estou aqui para ajudar. O que você precisa?"
            ],
            r'como vai|como est[aá]|tudo bem': [
                "Estou bem, obrigado por perguntar! E você?",
                "Tudo ótimo! Como posso ajudar hoje?",
                "Estou funcionando perfeitamente! Como posso ser útil?"
            ],
            r'quem [ée] voc[eê]|seu nome|como se chama': [
                "Sou o Self-Evolving Bot, um assistente virtual que aprende com nossas conversas.",
                "Meu nome é Self-Evolving Bot. Sou um assistente de IA projetado para evoluir com cada interação.",
                "Sou um assistente virtual chamado Self-Evolving Bot. Estou aqui para aprender e ajudar!"
            ],
            r'obrigad[oa]|valeu|agradecido': [
                "De nada! Fico feliz em ajudar.",
                "Por nada! Estou aqui quando precisar.",
                "Disponha! Se precisar de mais alguma coisa, é só pedir."
            ],
            r'tchau|adeus|at[eé] (logo|mais)|vou sair': [
                "Até mais! Foi um prazer conversar com você.",
                "Tchau! Volte quando quiser conversar novamente.",
                "Adeus! Tenha um ótimo dia!"
            ],
            r'o que voc[eê] (pode|sabe) fazer': [
                "Posso conversar sobre diversos assuntos, responder perguntas e aprender com nossas interações.",
                "Sou capaz de manter um diálogo, responder perguntas e melhorar com o tempo através de treinamento.",
                "Estou aqui para conversar e ajudar com informações. Também aprendo com cada conversa!"
            ],
            r'hora|que horas s[aã]o': [
                f"Agora são {datetime.now().strftime('%H:%M')}.",
                f"O horário atual é {datetime.now().strftime('%H:%M')}.",
                f"São {datetime.now().strftime('%H:%M')} no momento."
            ],
            r'data|dia (é hoje|hoje é|atual)': [
                f"Hoje é {datetime.now().strftime('%d/%m/%Y')}.",
                f"A data atual é {datetime.now().strftime('%d/%m/%Y')}.",
                f"Estamos em {datetime.now().strftime('%d/%m/%Y')}."
            ],
            r'tempo|clima': [
                "Não tenho acesso a informações de tempo em tempo real, mas posso ajudar com outras perguntas!",
                "Infelizmente não posso verificar o clima atual, pois funciono offline.",
                "Como sou um assistente offline, não posso verificar o clima no momento."
            ],
            r'conte (uma|alguma) piada': [
                "Por que o computador foi ao médico? Porque estava com vírus!",
                "O que o zero disse para o oito? Bonito cinto!",
                "Por que o livro de matemática ficou triste? Porque tinha muitos problemas."
            ],
            r'voc[eê] [ée] (inteligente|esperto)': [
                "Sou tão inteligente quanto meus treinamentos me permitem ser. E estou sempre aprendendo!",
                "Tenho capacidade de aprender e evoluir com cada conversa. Então espero ficar cada vez mais inteligente!",
                "Minha inteligência é baseada em aprendizado contínuo. Cada conversa me ajuda a melhorar!"
            ]
        }
        
        # Carrega conhecimento personalizado se existir
        self.custom_knowledge = {}
        self.load_knowledge()
    
    def load_knowledge(self):
        """Carrega conhecimento personalizado do disco"""
        if os.path.exists('knowledge.json'):
            try:
                with open('knowledge.json', 'r', encoding='utf-8') as f:
                    self.custom_knowledge = json.load(f)
                print(f"Base de conhecimento carregada: {len(self.custom_knowledge)} entradas")
            except Exception as e:
                print(f"Erro ao carregar base de conhecimento: {e}")
                self.custom_knowledge = {}
    
    def save_knowledge(self):
        """Salva conhecimento personalizado no disco"""
        try:
            with open('knowledge.json', 'w', encoding='utf-8') as f:
                json.dump(self.custom_knowledge, f, ensure_ascii=False, indent=2)
            print(f"Base de conhecimento salva: {len(self.custom_knowledge)} entradas")
        except Exception as e:
            print(f"Erro ao salvar base de conhecimento: {e}")
    
    def get_response(self, input_text):
        """Retorna uma resposta com base no texto de entrada"""
        # Verifica primeiro no conhecimento personalizado (correspondência exata)
        normalized_input = input_text.lower().strip()
        if normalized_input in self.custom_knowledge:
            responses = self.custom_knowledge[normalized_input]
            return random.choice(responses) if isinstance(responses, list) else responses
        
        # Verifica padrões predefinidos
        for pattern, responses in self.patterns.items():
            if re.search(pattern, normalized_input, re.IGNORECASE):
                return random.choice(responses)
        
        # Tenta similaridade no conhecimento personalizado
        best_match = None
        best_score = 0
        for key in self.custom_knowledge:
            # Verifica palavras em comum
            words_input = set(normalized_input.split())
            words_key = set(key.split())
            common_words = words_input.intersection(words_key)
            
            # Calcula pontuação simples de similaridade
            if len(words_input) > 0 and len(words_key) > 0:
                score = len(common_words) / max(len(words_input), len(words_key))
                if score > 0.5 and score > best_score:  # 50% de correspondência mínima
                    best_score = score
                    best_match = key
        
        if best_match:
            responses = self.custom_knowledge[best_match]
            return random.choice(responses) if isinstance(responses, list) else responses
        
        return None
    
    def add_knowledge(self, input_text, response):
        """Adiciona nova entrada à base de conhecimento"""
        normalized_input = input_text.lower().strip()
        
        if normalized_input in self.custom_knowledge:
            if isinstance(self.custom_knowledge[normalized_input], list):
                if response not in self.custom_knowledge[normalized_input]:
                    self.custom_knowledge[normalized_input].append(response)
            else:
                current = self.custom_knowledge[normalized_input]
                self.custom_knowledge[normalized_input] = [current, response]
        else:
            self.custom_knowledge[normalized_input] = [response]
        
        self.save_knowledge()
        return True

class MemoryModule:
    def __init__(self, max_size=1000):
        self.memory = deque(maxlen=max_size)
        
    def add_memory(self, input_text, response, context=None):
        self.memory.append({
            'input': input_text,
            'response': response,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        })
    
    def get_relevant_memories(self, query, top_k=5):
        # Busca simples por similaridade de texto
        relevant_memories = []
        query_words = set(query.lower().split())
        
        for memory in self.memory:
            memory_words = set(memory['input'].lower().split())
            # Calcula interseção de palavras
            common_words = query_words.intersection(memory_words)
            if common_words:
                # Pontuação baseada em palavras em comum
                score = len(common_words) / max(len(query_words), len(memory_words))
                relevant_memories.append((memory, score))
        
        # Ordena por pontuação e retorna os top_k
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in relevant_memories[:top_k]]
    
    def save_memories(self):
        """Salva memórias no disco"""
        memories_list = list(self.memory)
        try:
            with open('memories.pkl', 'wb') as f:
                pickle.dump(memories_list, f)
            print(f"Memórias salvas: {len(memories_list)} entradas")
        except Exception as e:
            print(f"Erro ao salvar memórias: {e}")
    
    def load_memories(self):
        """Carrega memórias do disco"""
        if os.path.exists('memories.pkl'):
            try:
                with open('memories.pkl', 'rb') as f:
                    memories_list = pickle.load(f)
                    self.memory = deque(memories_list, maxlen=self.memory.maxlen)
                print(f"Memórias carregadas: {len(self.memory)} entradas")
            except Exception as e:
                print(f"Erro ao carregar memórias: {e}")

class SimpleLanguageModel:
    """Modelo de linguagem simples para geração de texto"""
    
    def __init__(self):
        # Dicionário de n-gramas
        self.ngrams = {}
        self.load_model()
    
    def train(self, text, n=2):
        """Treina o modelo com texto e n-gramas de tamanho n"""
        words = text.split()
        if len(words) < n:
            return
        
        # Gera n-gramas
        for i in range(len(words) - n + 1):
            # Chave é uma tupla com as n-1 primeiras palavras
            key = tuple(words[i:i+n-1])
            # Valor é a próxima palavra
            value = words[i+n-1]
            
            if key not in self.ngrams:
                self.ngrams[key] = []
            self.ngrams[key].append(value)
    
    def generate(self, seed_text, max_length=50):
        """Gera texto a partir de um texto semente"""
        words = seed_text.split()
        if len(words) == 0:
            return ""
        
        # Usa os últimos n-1 tokens como semente (assumindo n=2)
        n = 2  # Para simplificar, usamos bigrams (n=2)
        current = tuple(words[-min(n-1, len(words)):])  # Últimas n-1 palavras ou menos
        
        result = list(words)
        
        # Gera novas palavras até o limite
        for _ in range(max_length):
            if current in self.ngrams:
                # Escolhe próxima palavra aleatoriamente
                next_word = random.choice(self.ngrams[current])
                result.append(next_word)
                
                # Atualiza a chave atual
                if len(current) >= n-1:
                    current = current[1:] + (next_word,)
                else:
                    current = current + (next_word,)
            else:
                # Se não encontrar n-grama, tenta com menos palavras
                if len(current) > 1:
                    current = current[1:]
                else:
                    break
        
        return ' '.join(result)
    
    def save_model(self):
        """Salva modelo no disco"""
        try:
            with open('language_model.pkl', 'wb') as f:
                pickle.dump(self.ngrams, f)
            print(f"Modelo salvo: {len(self.ngrams)} n-gramas")
        except Exception as e:
            print(f"Erro ao salvar modelo: {e}")
    
    def load_model(self):
        """Carrega modelo do disco"""
        if os.path.exists('language_model.pkl'):
            try:
                with open('language_model.pkl', 'rb') as f:
                    self.ngrams = pickle.load(f)
                print(f"Modelo carregado: {len(self.ngrams)} n-gramas")
            except Exception as e:
                print(f"Erro ao carregar modelo: {e}")
                # Inicializa com dados de exemplo
                self._initialize_default_model()
        else:
            # Inicializa com dados de exemplo
            self._initialize_default_model()
    
    def _initialize_default_model(self):
        """Treina o modelo com frases padrão"""
        default_texts = [
            "Olá, como posso ajudar você hoje?",
            "Estou aqui para responder suas perguntas.",
            "Posso ajudar com várias tarefas e responder perguntas diversas.",
            "Me conte mais sobre o que você precisa saber.",
            "Estou aprendendo a cada conversa que temos.",
            "Se tiver dúvidas é só perguntar.",
            "Minha função é ajudar e aprender com nossas interações.",
            "Como um assistente virtual, estou sempre aprendendo.",
            "Posso responder perguntas sobre diversos assuntos.",
            "Estou evoluindo a cada conversa que temos.",
            "Se tiver alguma dúvida específica, por favor pergunte.",
            "Estou aqui para auxiliar no que precisar.",
            "Posso te ajudar com informações e respostas.",
            "Vamos conversar e aprender juntos.",
            "Sou um bot que evolui com cada interação."
        ]
        
        for text in default_texts:
            self.train(text)
        
        print("Modelo inicializado com frases padrão")

class WebSearchModule:
    """Módulo para realizar pesquisas na web e extrair informações"""
    
    def __init__(self, cache_size=100):
        self.online = self._check_connection()
        self.cache = {}
        self.cache_size = cache_size
        self.cache_keys = deque(maxlen=cache_size)
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
    
    def search(self, query, max_results=3):
        """Realiza uma pesquisa na web e retorna os resultados"""
        # Normaliza a consulta
        normalized_query = query.lower().strip()
        
        # Verifica se a consulta está no cache
        if normalized_query in self.cache:
            print(f"Usando resultados em cache para: {normalized_query}")
            return self.cache[normalized_query]
        
        # Se estiver offline, retorna vazio
        if not self.online:
            return []
        
        try:
            # Verifica novamente a conexão antes de fazer a requisição
            self.online = self._check_connection()
            if not self.online:
                return []
            
            # Codifica a consulta para URL
            encoded_query = quote_plus(query)
            
            # API gratuita do SerpApi (limitada, mas funcional para demonstração)
            url = f"https://serpapi.com/search.json?q={encoded_query}&api_key=sua_chave_api"
            
            # Para fins de demonstração, vamos simular uma resposta
            # Em um ambiente real, você usaria:
            # response = requests.get(url, timeout=5)
            # results = response.json()
            
            # Simulando uma pesquisa básica usando DuckDuckGo (sem API key)
            ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(ddg_url, headers=headers, timeout=5)
            
            # Extrai resultados básicos do HTML (simplificado)
            search_results = []
            if response.status_code == 200:
                # Extração muito simplificada para demonstração
                content = response.text
                # Encontra snippets de resultados
                result_blocks = re.findall(r'<a class="result__a" href="([^"]+)"[^>]*>(.*?)</a>.*?<div class="result__snippet">(.*?)</div>', content, re.DOTALL)
                
                for i, (url, title, snippet) in enumerate(result_blocks):
                    if i >= max_results:
                        break
                    
                    # Limpa os textos de HTML
                    clean_title = re.sub(r'<[^>]+>', '', title)
                    clean_title = html.unescape(clean_title).strip()
                    
                    clean_snippet = re.sub(r'<[^>]+>', '', snippet)
                    clean_snippet = html.unescape(clean_snippet).strip()
                    
                    search_results.append({
                        'title': clean_title,
                        'snippet': clean_snippet,
                        'url': url
                    })
            
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
            print(f"Erro ao realizar pesquisa web: {e}")
            return []
    
    def get_info_from_web(self, query):
        """Obtém informações da web e as formata para uso pelo bot"""
        results = self.search(query)
        
        if not results:
            return None
        
        # Formata os resultados para uma resposta legível
        response = f"Encontrei algumas informações sobre '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            response += f"{i}. {result['title']}\n"
            response += f"   {result['snippet']}\n\n"
        
        response += "Espero que essas informações sejam úteis!"
        return response

class AutoLearningModule:
    """Módulo para aprendizado automático durante as interações normais"""
    
    def __init__(self, knowledge_base, language_model):
        self.knowledge_base = knowledge_base
        self.language_model = language_model
        self.feedback_threshold = 0.7  # Limiar para considerar aprendizado válido
        self.learning_rate = 0.5       # Taxa para balancear novo conhecimento
        self.auto_learning_enabled = True
    
    def toggle_auto_learning(self):
        """Ativa ou desativa o aprendizado automático"""
        self.auto_learning_enabled = not self.auto_learning_enabled
        return self.auto_learning_enabled
    
    def analyze_conversation(self, input_text, response, user_feedback=None):
        """Analisa a conversa para aprendizado automático"""
        if not self.auto_learning_enabled:
            return False
        
        # 1. Se temos feedback explícito positivo do usuário, aprende diretamente
        if user_feedback and user_feedback > self.feedback_threshold:
            self.knowledge_base.add_knowledge(input_text, response)
            self.language_model.train(response)
            return True
        
        # 2. Análise de qualidade da resposta (simplificada)
        quality_score = self._assess_response_quality(input_text, response)
        
        # 3. Se a qualidade é boa o suficiente, aprende automaticamente
        if quality_score > self.feedback_threshold:
            print(f"Aprendizado automático ativado para: '{input_text}'")
            self.knowledge_base.add_knowledge(input_text, response)
            self.language_model.train(response)
            return True
        
        return False
    
    def _assess_response_quality(self, input_text, response):
        """Avalia a qualidade da resposta para determinar se é bom aprendizado"""
        # Esta é uma implementação simplificada de avaliação de qualidade
        
        # Verifica comprimento (respostas muito curtas ou muito longas são suspeitas)
        input_length = len(input_text.split())
        response_length = len(response.split())
        
        length_ratio = min(response_length / max(1, input_length), 10) / 10
        if response_length < 3 or length_ratio < 0.3:
            return 0.3  # Resposta muito curta ou desproporcional
        
        # Verifica coerência (presença de palavras da pergunta na resposta)
        input_words = set([word.lower() for word in input_text.split() if len(word) > 3])
        response_words = set([word.lower() for word in response.split() if len(word) > 3])
        
        common_words = input_words.intersection(response_words)
        coherence_score = len(common_words) / max(1, len(input_words)) * 0.5
        
        # Verifica se a resposta não é genérica demais
        generic_phrases = [
            "não sei", "não tenho certeza", "desculpe", "não posso", 
            "não conheço", "não entendi", "me diga mais"
        ]
        
        generic_score = 1.0
        response_lower = response.lower()
        for phrase in generic_phrases:
            if phrase in response_lower:
                generic_score *= 0.7  # Penaliza respostas genéricas
        
        # Calcula pontuação final
        final_score = (length_ratio * 0.3) + (coherence_score * 0.4) + (generic_score * 0.3)
        return min(1.0, final_score)

class SelfEvolvingBot:
    def __init__(self):
        print("Inicializando Self-Evolving Bot...")
        self.knowledge_base = KnowledgeBase()
        self.memory_module = MemoryModule()
        self.language_model = SimpleLanguageModel()
        self.web_search = WebSearchModule()
        self.auto_learning = AutoLearningModule(self.knowledge_base, self.language_model)
        
        self.response_fallbacks = [
            "Desculpe, ainda estou aprendendo sobre esse assunto. Pode me ensinar?",
            "Não tenho certeza sobre isso. Poderia me explicar mais?",
            "Estou evoluindo constantemente. O que você gostaria que eu soubesse sobre isso?",
            "Hmm, não tenho informações suficientes sobre isso ainda. Gostaria de me ajudar a aprender?",
            "Essa é uma boa pergunta, mas ainda não tenho uma resposta. Poderia me instruir?"
        ]
        
        # Controle de internet
        self.web_enabled = True
        
        # Inicializa a memória
        self.memory_module.load_memories()
        
        # Conjunto de dados de exemplo pré-treinados
        self._load_default_training_data()
        
        # Palavras-chave para acionar busca na web
        self.web_search_triggers = [
            "procure", "pesquise", "busque", "encontre", "o que é", 
            "quem é", "como funciona", "me diga sobre", "informações sobre",
            "notícias sobre", "atualidades", "novidades", "explicação sobre",
            "significado de", "definição de"
        ]
    
    def _load_default_training_data(self):
        """Carrega dados de treinamento padrão"""
        examples = [
            ("Qual é seu nome?", "Meu nome é Self-Evolving Bot. Sou um assistente virtual que aprende com nossas conversas."),
            ("O que você faz?", "Sou um assistente virtual projetado para conversar e aprender continuamente com cada interação."),
            ("Como você funciona?", "Funciono através de um sistema híbrido que combina uma base de conhecimento, modelos de linguagem e memória de conversas anteriores."),
            ("Quem te criou?", "Fui criado como um projeto de IA para demonstrar capacidades de aprendizado e evolução através de conversas."),
            ("O que você pode fazer?", "Posso conversar sobre diversos assuntos, responder perguntas, aprender com nossos diálogos, pesquisar informações na internet e evoluir com o tempo."),
            ("Como posso te ensinar?", "Para me ensinar, ative o modo de treinamento clicando no botão 'Treinar'. Depois, digite uma pergunta e em seguida a resposta que você quer que eu aprenda."),
            ("Você usa internet?", "Sim! Agora posso acessar a internet para buscar informações atualizadas quando solicitado."),
            ("Você lembra das nossas conversas?", "Sim, mantenho um registro das nossas interações anteriores que me ajudam a fornecer respostas mais relevantes com o tempo."),
            ("Qual linguagem de programação você usa?", "Fui desenvolvido em Python, utilizando tecnologias como PyQt para a interface e vários módulos para processamento de linguagem natural."),
            ("Você é inteligente?", "Minha inteligência é limitada ao que aprendi e fui programado para fazer, mas estou sempre evoluindo a cada interação."),
            ("Você aprende sozinho?", "Sim! Além do modo de treinamento, agora também tenho um sistema de aprendizado automático que me permite aprender durante conversas normais.")
        ]
        
        # Adiciona exemplos à base de conhecimento
        for question, answer in examples:
            self.knowledge_base.add_knowledge(question, answer)
            # Treina o modelo de linguagem
            self.language_model.train(answer)
    
    def _should_search_web(self, input_text):
        """Determina se deve realizar uma busca na web com base no texto de entrada"""
        if not self.web_enabled or not self.web_search.online:
            return False
            
        input_lower = input_text.lower()
        
        # Verifica se a entrada contém palavras-chave para busca na web
        for trigger in self.web_search_triggers:
            if trigger in input_lower:
                return True
        
        # Verifica se é uma pergunta substancial sem resposta no conhecimento local
        is_question = any(q in input_lower for q in ["?", "o que", "como", "quando", "onde", "por que", "quem", "qual"])
        has_local_answer = self.knowledge_base.get_response(input_text) is not None
        
        return is_question and not has_local_answer and len(input_text.split()) >= 3
    
    def toggle_web_access(self):
        """Ativa ou desativa o acesso à internet"""
        self.web_enabled = not self.web_enabled
        return self.web_enabled
    
    def toggle_auto_learning(self):
        """Ativa ou desativa o aprendizado automático"""
        return self.auto_learning.toggle_auto_learning()
    
    def generate_response(self, input_text):
        # 1. Tenta obter resposta da base de conhecimento
        response = self.knowledge_base.get_response(input_text)
        
        # 2. Se não encontrou e deve pesquisar na web, faz isso
        if not response and self._should_search_web(input_text):
            web_response = self.web_search.get_info_from_web(input_text)
            if web_response:
                # Armazena a resposta da web para aprendizado
                self.memory_module.add_memory(
                    input_text, 
                    web_response, 
                    {'source': 'web_search', 'timestamp': datetime.now().isoformat()}
                )
                # Treina o modelo com essa resposta
                self.language_model.train(web_response)
                return web_response
        
        # 3. Se ainda não encontrou, busca memórias relevantes
        if not response:
            relevant_memories = self.memory_module.get_relevant_memories(input_text)
            if relevant_memories:
                most_relevant = relevant_memories[0]
                # Treina o modelo com essa memória
                self.language_model.train(most_relevant['response'])
                # Usa a resposta armazenada
                response = most_relevant['response']
        
        # 4. Se ainda não encontrou, gera resposta com o modelo de linguagem
        if not response:
            language_response = self.language_model.generate(input_text)
            if language_response and len(language_response.split()) > len(input_text.split()):
                response = language_response
        
        # 5. Resposta padrão quando não tem conhecimento suficiente
        if not response:
            response = random.choice(self.response_fallbacks)
        
        # Armazena a interação na memória
        self.memory_module.add_memory(input_text, response)
        
        # Aplica aprendizado automático
        self.auto_learning.analyze_conversation(input_text, response)
        
        return response
    
    def learn_from_conversation(self, input_text, response, context=None, user_feedback=1.0):
        """Aprende com uma interação de conversa (treinamento explícito)"""
        # Adiciona à base de conhecimento
        self.knowledge_base.add_knowledge(input_text, response)
        
        # Treina o modelo de linguagem
        self.language_model.train(response)
        
        # Armazena na memória
        self.memory_module.add_memory(input_text, response, context)
        
        # Salva o estado atualizado
        self.save_state()
        
        return True
    
    def provide_feedback(self, input_text, response, score):
        """Permite que o usuário forneça feedback explícito sobre a qualidade da resposta"""
        if score >= 0.7:  # Feedback positivo
            # Reforça o aprendizado
            self.auto_learning.analyze_conversation(input_text, response, score)
            return "Obrigado pelo feedback positivo! Estou aprendendo com essa interação."
        else:  # Feedback negativo
            return "Obrigado pelo feedback! Você poderia me ajudar a melhorar me ensinando a resposta correta?"
    
    def save_state(self):
        """Salva todo o estado do bot"""
        self.knowledge_base.save_knowledge()
        self.memory_module.save_memories()
        self.language_model.save_model()
        self.web_search.save_cache()
    
    def load_state(self):
        """Carrega o estado do bot"""
        # Os módulos já carregam seus estados nos construtores
        # Esta função existe para manter compatibilidade com a interface existente
        pass

if __name__ == "__main__":
    bot = SelfEvolvingBot()
    print("Bot inicializado e pronto para aprender!")
    
    # Teste interativo simples
    print("\nDigite 'sair' para encerrar o teste.")
    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() == 'sair':
            break
        
        response = bot.generate_response(user_input)
        print(f"Bot: {response}")
    
    bot.save_state()
    print("Estado do bot salvo. Encerrando.") 