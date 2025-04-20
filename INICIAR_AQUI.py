"""
Inicializador Self-Evolving Bot
Este é um script simples para iniciar a instalação de forma segura
"""
import os
import sys
import subprocess
import platform
import time
import shutil

def mostrar_mensagem(mensagem, esperar=0):
    """Mostra uma mensagem formatada"""
    print("\n" + "=" * 60)
    print(mensagem)
    print("=" * 60)
    if esperar > 0:
        time.sleep(esperar)

def executar_comando(comando):
    """Executa um comando e mostra a saída"""
    try:
        print(f"Executando: {comando}")
        resultado = subprocess.run(
            comando, 
            shell=True, 
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        return resultado.returncode == 0
    except Exception as e:
        print(f"Erro ao executar comando: {e}")
        return False

def verificar_python():
    """Verifica se o Python está instalado"""
    mostrar_mensagem("Verificando instalação do Python...")
    
    # Métodos de verificação
    comandos = [
        "python --version",
        "py --version",
        "python3 --version"
    ]
    
    for cmd in comandos:
        if executar_comando(cmd):
            return True
    
    mostrar_mensagem("Python não encontrado! Por favor, instale o Python 3.8 ou superior.")
    mostrar_mensagem("Você pode baixar em https://www.python.org/downloads/")
    mostrar_mensagem("Certifique-se de marcar a opção 'Add Python to PATH' durante a instalação.")
    return False

def criar_arquivos_basicos():
    """Cria os arquivos básicos se não existirem"""
    # Verifica se o verificador de arquivos existe
    if not os.path.exists("verificar_arquivos.py"):
        mostrar_mensagem("Criando verificar_arquivos.py...")
        
        conteudo = '''"""
Script para verificar e gerar os arquivos necessários para a instalação
"""
import os
import sys
import platform
from pathlib import Path

def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem e cria os que faltam"""
    print("Verificando arquivos necessários...")
    
    arquivos_necessarios = [
        "requirements.txt",
        "gui_interface.py",
        "self_evolving_bot.py",
        "bot_interface.py"
    ]
    
    arquivos_faltando = []
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print(f"Os seguintes arquivos estão faltando: {', '.join(arquivos_faltando)}")
        print("Tentando criar arquivos faltantes...")
        
        # Cria requirements.txt se estiver faltando
        if "requirements.txt" in arquivos_faltando:
            criar_requirements()
            if os.path.exists("requirements.txt"):
                arquivos_faltando.remove("requirements.txt")
        
        # Verifica novamente após tentativa de criação
        arquivos_faltando = []
        for arquivo in arquivos_necessarios:
            if not os.path.exists(arquivo):
                arquivos_faltando.append(arquivo)
        
        if arquivos_faltando:
            print(f"ERRO: Ainda faltam os seguintes arquivos essenciais: {', '.join(arquivos_faltando)}")
            print("Por favor, faça o download completo do projeto antes de executar o instalador.")
            print("Verifique se você extraiu corretamente todos os arquivos do pacote baixado.")
            return False
    
    print("Todos os arquivos necessários estão presentes.")
    return True

def criar_requirements():
    """Cria o arquivo requirements.txt se não existir"""
    conteudo = """torch>=2.0.0
numpy>=1.21.0
PyQt6>=6.4.0
qt-material>=2.14
pillow>=9.0.0
python-dotenv>=0.19.0
tensorboard>=2.8.0
transformers>=4.30.0
scikit-learn>=1.0.0"""
    
    try:
        with open("requirements.txt", "w") as f:
            f.write(conteudo)
        
        print("Arquivo requirements.txt criado com sucesso.")
    except Exception as e:
        print(f"Erro ao criar requirements.txt: {e}")

def mostrar_info_sistema():
    """Mostra informações do sistema para diagnóstico"""
    print("\nInformações do sistema:")
    print(f"Sistema Operacional: {platform.system()} {platform.version()}")
    print(f"Python: {platform.python_version()}")
    print(f"Diretório Atual: {os.getcwd()}")
    
    print("\nArquivos no diretório atual:")
    for arquivo in os.listdir("."):
        try:
            tamanho = os.path.getsize(arquivo) / 1024
            print(f"- {arquivo} ({tamanho:.1f} KB)")
        except:
            print(f"- {arquivo} (erro ao obter tamanho)")

if __name__ == "__main__":
    # Certifica-se de estar no diretório do script
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"Diretório atual: {os.getcwd()}")
    except Exception as e:
        print(f"Aviso: Não foi possível mudar para o diretório do script: {e}")
    
    if verificar_arquivos():
        print("Verificação concluída com sucesso!")
        sys.exit(0)
    else:
        mostrar_info_sistema()
        print("\nFalha na verificação de arquivos. Não é possível continuar.")
        print("Por favor, verifique se você tem todos os arquivos necessários.")
        sys.exit(1)'''
        
        with open("verificar_arquivos.py", "w") as f:
            f.write(conteudo)

def criar_interface_padrao():
    """Cria arquivos de interface se estiverem faltando"""
    # Verifica bot_interface.py
    if not os.path.exists("bot_interface.py"):
        mostrar_mensagem("Criando bot_interface.py...")
        
        conteudo = '''from self_evolving_bot import SelfEvolvingBot
import torch
import sys
import time

def main():
    print("Inicializando o bot...")
    bot = SelfEvolvingBot()
    
    # Tenta carregar estado anterior
    try:
        bot.load_state()
        print("Estado anterior carregado com sucesso!")
    except:
        print("Iniciando novo modelo...")
    
    print("\nBem-vindo ao Self-Evolving Bot!")
    print("Digite 'sair' para encerrar a conversa")
    print("Digite 'salvar' para salvar o estado atual")
    print("Digite 'treinar' para entrar no modo de treinamento")
    
    context = None
    training_mode = False
    
    while True:
        user_input = input("\nVocê: ").strip()
        
        if user_input.lower() == 'sair':
            print("Salvando estado antes de sair...")
            bot.save_state()
            print("Até logo!")
            break
            
        elif user_input.lower() == 'salvar':
            bot.save_state()
            print("Estado salvo com sucesso!")
            continue
            
        elif user_input.lower() == 'treinar':
            training_mode = not training_mode
            print(f"Modo de treinamento {'ativado' if training_mode else 'desativado'}")
            continue
        
        if training_mode:
            print("\nModo de treinamento ativo")
            print("Digite a resposta correta para a última mensagem:")
            correct_response = input("Resposta correta: ").strip()
            
            # Treina o bot
            loss = bot.learn_from_conversation(user_input, correct_response, context)
            print(f"Treinamento concluído. Loss: {loss:.4f}")
            
            # Atualiza o contexto
            context = {
                'input': user_input,
                'response': correct_response
            }
        else:
            # Gera resposta
            print("\nBot pensando...", end='', flush=True)
            start_time = time.time()
            
            response = bot.generate_response(user_input)
            
            elapsed_time = time.time() - start_time
            print(f"\rBot ({elapsed_time:.2f}s): {response}")
            
            # Atualiza o contexto
            context = {
                'input': user_input,
                'response': response
            }
            
            # Pergunta sobre a qualidade da resposta
            feedback = input("\nA resposta foi adequada? (s/n): ").lower()
            if feedback == 'n':
                print("Por favor, entre no modo de treinamento ('treinar') para corrigir a resposta.")

if __name__ == "__main__":
    main()'''
        
        with open("bot_interface.py", "w") as f:
            f.write(conteudo)

def limpar_ambiente():
    """Remove arquivos temporários que podem causar problemas"""
    arquivos_temporarios = ["__pycache__", "*.pyc", "*.pyo", "*.bak"]
    
    mostrar_mensagem("Limpando ambiente...")
    
    try:
        # Remove pastas __pycache__
        for root, dirs, files in os.walk(".", topdown=False):
            for name in dirs:
                if name == "__pycache__":
                    caminho = os.path.join(root, name)
                    print(f"Removendo diretório: {caminho}")
                    shutil.rmtree(caminho, ignore_errors=True)
        
        print("Ambiente limpo.")
    except Exception as e:
        print(f"Erro ao limpar ambiente: {e}")

def main():
    """Função principal"""
    mostrar_mensagem("INICIALIZADOR DO SELF-EVOLVING BOT", 1)
    mostrar_mensagem("Este script irá preparar e iniciar a instalação do bot.", 2)
    
    # Verifica se o Python está instalado
    if not verificar_python():
        mostrar_mensagem("Não foi possível continuar sem o Python.", 3)
        return
    
    # Limpa o ambiente
    limpar_ambiente()
    
    # Cria arquivos básicos
    criar_arquivos_basicos()
    criar_interface_padrao()
    
    # Executa o verificador de arquivos
    mostrar_mensagem("Verificando arquivos necessários...")
    if not executar_comando("python verificar_arquivos.py"):
        mostrar_mensagem("Falha na verificação de arquivos. Não é possível continuar.", 3)
        return
    
    # Inicia a instalação
    mostrar_mensagem("Iniciando instalação do bot...")
    if os.path.exists("instalar_bot.py"):
        executar_comando("python instalar_bot.py")
    else:
        mostrar_mensagem("Arquivo de instalação não encontrado.", 3)
        return
    
    mostrar_mensagem("Processo concluído!", 2)

if __name__ == "__main__":
    # Muda para o diretório do script
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"Diretório atual: {os.getcwd()}")
    except Exception as e:
        print(f"Aviso: Não foi possível mudar para o diretório do script: {e}")
    
    main()
    
    # Mantém o console aberto no Windows
    if platform.system() == "Windows":
        print("\nPressione Enter para sair...")
        input() 