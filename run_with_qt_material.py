"""
Inicializador alternativo para resolver problemas com qt_material
"""
import sys
import os
import platform
import importlib
import subprocess
import traceback
from pathlib import Path

def verificar_instalacao():
    """Verifica se o ambiente tem as dependências necessárias"""
    print("Verificando dependências necessárias...")
    
    # Lista de módulos necessários
    modulos_necessarios = [
        "PyQt6",
        "torch",
        "qt_material",
        "numpy"
    ]
    
    faltando = []
    problemas = []
    for modulo in modulos_necessarios:
        try:
            importlib.import_module(modulo)
            print(f"✓ {modulo} está instalado")
            
            # Verificação especial para PyTorch (torch._C)
            if modulo == "torch":
                try:
                    import torch._C
                    print("✓ torch._C está acessível")
                except ImportError as e:
                    print(f"✗ Problema com torch._C: {e}")
                    problemas.append(("torch", "Módulo torch._C não encontrado"))
        except ImportError:
            faltando.append(modulo)
            print(f"✗ {modulo} não está instalado")
    
    # Primeiro, instala os módulos faltantes
    if faltando:
        print("\nAlgumas dependências estão faltando. Tentando instalar...")
        for modulo in faltando:
            try:
                print(f"Instalando {modulo}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", modulo])
                print(f"✓ {modulo} instalado com sucesso")
            except Exception as e:
                print(f"✗ Não foi possível instalar {modulo}: {e}")
                return False
    
    # Depois, tenta corrigir problemas com módulos específicos
    if problemas:
        print("\nTentando corrigir problemas com módulos instalados...")
        for modulo, problema in problemas:
            if modulo == "torch" and "torch._C" in problema:
                print("Detectado problema com PyTorch (torch._C). Tentando reinstalar...")
                try:
                    # Desinstala primeiro
                    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio"])
                    # Reinstala
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio"])
                    
                    # Verifica se corrigiu
                    try:
                        import torch._C
                        print("✓ Problema com torch._C corrigido!")
                    except ImportError:
                        print("✗ Não foi possível corrigir o problema com torch._C")
                        print("  Tente executar manualmente: pip uninstall torch && pip install torch")
                        return False
                except Exception as e:
                    print(f"✗ Erro ao reinstalar PyTorch: {e}")
                    return False
    
    print("Todas as dependências estão instaladas.")
    return True

def verificar_arquivos_qt_material():
    """Verifica se os arquivos do qt_material estão acessíveis"""
    try:
        import qt_material
        
        # Verifica template file
        template_path = os.path.join(os.path.dirname(qt_material.__file__), "material.qss.template")
        if not os.path.exists(template_path):
            print(f"✗ Arquivo template qt_material não encontrado: {template_path}")
            
            # Tenta criar o arquivo template
            try:
                print("Tentando criar arquivo template...")
                
                # Conteúdo base do template
                template_content = """
/* ---------------------------------------------------------------------------

    Created by the qtsass compiler v0.1.1

    The definitions are in the "qdarkstyle.qss._styles.scss" module

    WARNING! All changes made in this file will be lost!

--------------------------------------------------------------------------- */
{% set icon_path = resource_path if resource_path else '\":/icons\"' %}

QWidget {
    {{ background_color }};
    {{ text_color }};
    font-size: {{ font_size }}px;
    font-family: {{ font_family }};
}

QToolTip {
    border: 1px solid {{ border_color }};
    {{ background_color }};
    {{ text_color }};
    padding: 5px;
}

/* QWidget ----------------------------------------------------------------

--------------------------------------------------------------------------- */

QWidget:disabled {
    {{ text_disabled_color }};
    {{ disabled_background_color }};
}

QWidget:item:hover {
    {{ hover_background_color }};
    {{ text_color }};
}

QWidget:item:selected {
    {{ selection_color }};
    {{ selection_text_color }};
}

QMenuBar::item:disabled {
    {{ text_disabled_color }};
}

/* QAbstractItemView ------------------------------------------------------

--------------------------------------------------------------------------- */

QAbstractItemView {
    {{ alternate_background_color }};
    {{ text_color }};
    padding: 5px;
}

QAbstractItemView::item:hover {
    {{ hover_background_color }};
    {{ text_color }};
}

QAbstractItemView::item:selected {
    {{ selection_color }};
    {{ selection_text_color }};
}
"""
                
                # Cria o diretório se não existir
                os.makedirs(os.path.dirname(template_path), exist_ok=True)
                
                # Salva o arquivo
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                
                print(f"✓ Arquivo template criado em: {template_path}")
                return True
            except Exception as template_error:
                print(f"✗ Não foi possível criar o arquivo template: {template_error}")
                return False
            
        print(f"✓ Arquivos do qt_material encontrados em: {os.path.dirname(qt_material.__file__)}")
        return True
    except Exception as e:
        print(f"✗ Erro ao verificar arquivos do qt_material: {e}")
        return False

def executar_bot():
    """Importa e executa o bot com qt_material de forma segura"""
    print("Iniciando Self-Evolving Bot...")
    
    # Verifica se o arquivo existe
    if not os.path.exists("gui_interface.py"):
        print("Erro: gui_interface.py não encontrado.")
        return False
    
    # Verifica arquivos do qt_material
    if not verificar_arquivos_qt_material():
        print("Aviso: Problemas com qt_material detectados, mas tentando continuar...")
    
    try:
        # Importa PyQt6 primeiro
        print("Importando PyQt6...")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        
        # Agora importa qt_material
        print("Importando qt_material...")
        from qt_material import apply_stylesheet
        
        # Cria o aplicativo
        print("Criando aplicativo Qt...")
        app = QApplication(sys.argv)
        
        # Aplica estilo (antes de importar a interface gráfica)
        print("Aplicando estilo material...")
        try:
            apply_stylesheet(app, theme='light_blue.xml')
        except Exception as e:
            print(f"Aviso: Erro ao aplicar estilo: {e}")
            print("Continuando sem estilo material...")
        
        # Importa a interface gráfica apenas depois
        print("Importando interface gráfica...")
        try:
            import gui_interface
        except ImportError as e:
            if "torch._C" in str(e):
                print("\nErro crítico com PyTorch (torch._C)!")
                print("Tentando corrigir automaticamente...")
                
                # Tenta corrigir reinstalando torch
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio"])
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio"])
                    
                    print("\nPyTorch reinstalado! Tente iniciar o bot novamente.")
                    return False
                except Exception as reinstall_err:
                    print(f"Não foi possível corrigir: {reinstall_err}")
                    return False
            else:
                print(f"Erro ao importar interface: {e}")
                return False
        
        # Inicia o bot
        print("Inicializando janela principal...")
        window = gui_interface.ChatWindow()
        window.show()
        
        # Adiciona mensagem de boas-vindas após um pequeno delay
        def add_welcome_message():
            try:
                window.add_message("Bot", "Olá! Sou o Self-Evolving Bot. Como posso ajudar?")
            except Exception as e:
                print(f"Aviso: Erro ao adicionar mensagem de boas-vindas: {e}")
        
        QTimer.singleShot(500, add_welcome_message)
        
        # Executa o loop de eventos
        print("Iniciando loop de eventos Qt...")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Erro ao iniciar o bot: {e}")
        print("\nDetalhes do erro:")
        traceback.print_exc()
        return False
    
    return True

def main():
    """Função principal"""
    print("=" * 60)
    print("SELF-EVOLVING BOT - INICIALIZADOR ALTERNATIVO")
    print("=" * 60)
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 60)
    print()
    
    # Certifica-se de estar no diretório correto
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir:
            os.chdir(script_dir)
            print(f"Diretório de trabalho: {os.getcwd()}")
    except Exception as e:
        print(f"Aviso: Não foi possível mudar para o diretório do script: {e}")
    
    # Verifica instalação
    if not verificar_instalacao():
        print("\nFalha na verificação de dependências.")
        input("Pressione Enter para sair...")
        return 1
    
    # Executa o bot
    if not executar_bot():
        print("\nFalha ao executar o bot.")
        input("Pressione Enter para sair...")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Erro fatal: {e}")
        traceback.print_exc()
        print("\nO programa encontrou um erro fatal e não pode continuar.")
        input("Pressione Enter para sair...")
        sys.exit(1) 