import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                            QLabel, QFrame, QScrollArea, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap

# Importação de temas com fallback
theme_system = "qt_material"
QDARKTHEME_OLD_API = True  # Por padrão assume a API antiga

try:
    # Primeira opção: qt_material
    from qt_material import apply_stylesheet
except ImportError:
    try:
        # Segunda opção: pyqtdarktheme
        import qdarktheme
        theme_system = "qdarktheme"
        # Verificar a versão do qdarktheme pois a API mudou
        qdarktheme_version = getattr(qdarktheme, "__version__", "0.1.7")
        if qdarktheme_version.startswith("0.1"):
            # Na versão 0.1.x, usamos qdarktheme.setup_theme
            QDARKTHEME_OLD_API = True
        else:
            # Em versões mais recentes, a API seria diferente
            QDARKTHEME_OLD_API = False
    except ImportError:
        theme_system = "none"
        print("Aviso: Nenhum sistema de tema disponível. A interface usará o tema padrão.")

# Tenta usar o bot aprimorado com capacidade web, caso contrário usa o bot padrão
try:
    from web_integration import get_web_enabled_bot
    from self_evolving_bot import SelfEvolvingBot
    def bot_factory():
        try:
            base_bot = SelfEvolvingBot()
            web_bot = get_web_enabled_bot(base_bot, auto_learn=True, web_enabled=True)
            print("Usando bot com capacidade de navegação web aprimorada!")
            return web_bot
        except Exception as e:
            print(f"Erro ao inicializar bot com navegação web: {e}")
            print("Caindo para o bot padrão sem navegação web...")
            return SelfEvolvingBot()
except ImportError:
    from self_evolving_bot import SelfEvolvingBot
    bot_factory = SelfEvolvingBot
    print("Usando bot padrão (sem navegação web aprimorada)")

class BotWorker(QThread):
    response_ready = pyqtSignal(str)
    thinking = pyqtSignal(bool)
    
    def __init__(self, bot, message):
        super().__init__()
        self.bot = bot
        self.message = message
        
    def run(self):
        self.thinking.emit(True)
        
        # Verifica qual método de resposta o bot possui
        if hasattr(self.bot, 'generate_response'):
            response = self.bot.generate_response(self.message)
        elif hasattr(self.bot, 'get_response'):
            response = self.bot.get_response(self.message)
        else:
            response = "Desculpe, não consigo processar sua solicitação no momento."
            
        self.thinking.emit(False)
        self.response_ready.emit(response)

class FeedbackWidget(QWidget):
    feedback_submitted = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.feedback_label = QLabel("Resposta foi útil?")
        
        self.yes_button = QPushButton("👍")
        self.yes_button.setToolTip("Resposta boa (aprender)")
        self.yes_button.setMaximumWidth(40)
        self.yes_button.clicked.connect(lambda: self.submit_feedback(1.0))
        
        self.no_button = QPushButton("👎")
        self.no_button.setToolTip("Resposta ruim (não aprender)")
        self.no_button.setMaximumWidth(40)
        self.no_button.clicked.connect(lambda: self.submit_feedback(0.0))
        
        layout.addWidget(self.feedback_label)
        layout.addWidget(self.yes_button)
        layout.addWidget(self.no_button)
        layout.addStretch()
        
        self.setVisible(False)
    
    def submit_feedback(self, score):
        self.feedback_submitted.emit(score)
        self.setVisible(False)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bot = bot_factory()  # Usa a fábrica de bot configurada
        self.dark_mode = False  # Inicialmente em modo claro
        self.last_response = None
        self.last_user_message = None  # Inicializar a variável para armazenar a última mensagem
        self.app = None  # Inicialização do atributo app como None
        
        # Adiciona métodos de compatibilidade caso não existam no bot
        if not hasattr(self.bot, 'toggle_auto_learning'):
            self.bot.toggle_auto_learning = lambda: None
            
        if not hasattr(self.bot, 'toggle_web_access'):
            self.bot.toggle_web_access = lambda: None
            
        if not hasattr(self.bot, 'set_auto_learn'):
            self.bot.set_auto_learn = lambda enabled: None
            
        if not hasattr(self.bot, 'set_web_enabled'):
            self.bot.set_web_enabled = lambda enabled: None
            
        # Garantir que toggle_auto_learning esteja definido corretamente
        if hasattr(self.bot, 'set_auto_learn'):
            self.bot.toggle_auto_learning = lambda: self.bot.set_auto_learn(not getattr(self.bot, 'auto_learn', True))
            
        # Garantir que toggle_web_access esteja definido corretamente    
        if hasattr(self.bot, 'set_web_enabled'):
            self.bot.toggle_web_access = lambda: self.bot.set_web_enabled(not getattr(self.bot, 'web_enabled', True))
            
        # Método de compatibilidade para feedback
        if not hasattr(self.bot, 'provide_feedback'):
            def compatibility_feedback(input_text, response, score):
                try:
                    if score > 0.5:
                        if hasattr(self.bot, 'learn_from_conversation'):
                            self.bot.learn_from_conversation(input_text, response)
                            return "Obrigado pelo feedback positivo! Estou aprendendo com essa interação."
                        elif hasattr(self.bot, 'learn'):
                            self.bot.learn(input_text, response)
                            return "Obrigado pelo feedback positivo! Estou aprendendo com essa interação."
                    return None
                except Exception as e:
                    print(f"Erro em compatibility_feedback: {e}")
                    return None
                    
            self.bot.provide_feedback = compatibility_feedback
            
        # Método de compatibilidade para aprendizado
        if not hasattr(self.bot, 'learn_from_conversation'):
            if hasattr(self.bot, 'learn'):
                self.bot.learn_from_conversation = self.bot.learn
            else:
                self.bot.learn_from_conversation = lambda input_text, response: None
            
        # Métodos de compatibilidade entre interface generate_response/get_response
        if hasattr(self.bot, 'learn') and not hasattr(self.bot, 'generate_response') and hasattr(self.bot, 'get_response'):
            self.bot.generate_response = self.bot.get_response
        elif hasattr(self.bot, 'learn') and not hasattr(self.bot, 'get_response') and hasattr(self.bot, 'generate_response'):
            self.bot.get_response = self.bot.generate_response
        
        # Verificar save_state necessário para closeEvent
        if not hasattr(self.bot, 'save_state'):
            self.bot.save_state = lambda: None
        
        self.init_ui()
        
    def init_ui(self):
        # Configuração da janela principal
        self.setWindowTitle('Self-Evolving Bot')
        self.setMinimumSize(800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        # Layout para indicadores e botões de controle no topo
        top_controls = QHBoxLayout()
        
        # Botão para alternar tema claro/escuro
        self.theme_button = QPushButton("Modo Escuro")
        self.theme_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #111111;
            }
        """)
        self.theme_button.clicked.connect(self.toggle_theme)
        top_controls.addWidget(self.theme_button)
        
        # Checkbox para auto-aprendizado
        self.auto_learn_checkbox = QCheckBox("Auto-aprendizado")
        self.auto_learn_checkbox.setChecked(True)
        self.auto_learn_checkbox.stateChanged.connect(self.toggle_auto_learning)
        top_controls.addWidget(self.auto_learn_checkbox)
        
        # Checkbox para acesso à web
        self.web_access_checkbox = QCheckBox("Acesso à Web")
        self.web_access_checkbox.setChecked(True)
        self.web_access_checkbox.stateChanged.connect(self.toggle_web_access)
        top_controls.addWidget(self.web_access_checkbox)
        
        # Espaçador para empurrar o indicador para a direita
        top_controls.addStretch()
        
        # Área de modo de treinamento
        self.training_indicator = QLabel("Modo normal")
        self.training_indicator.setStyleSheet("""
            QLabel {
                background-color: #E0E0E0;
                color: #333;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        top_controls.addWidget(self.training_indicator)
        
        # Adiciona o layout de controles ao layout principal
        main_layout.addLayout(top_controls)
        
        # Área de chat
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        main_layout.addWidget(self.chat_area)
        
        # Widget de feedback
        self.feedback_widget = FeedbackWidget()
        self.feedback_widget.feedback_submitted.connect(self.handle_feedback)
        main_layout.addWidget(self.feedback_widget)
        
        # Área de entrada
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Digite sua mensagem...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a80d2;
            }
            QPushButton:pressed {
                background-color: #2a70c2;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        # Botão de treinamento
        self.train_button = QPushButton("Treinar")
        self.train_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:pressed {
                background-color: #1a8a45;
            }
        """)
        self.train_button.clicked.connect(self.toggle_training)
        input_layout.addWidget(self.train_button)
        
        main_layout.addWidget(input_frame)
        
        # Status inicial
        self.training_mode = False
        self.training_input = None
        
        # Status de "pensando"
        self.thinking_indicator = QLabel("Pensando...")
        self.thinking_indicator.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                margin-top: 5px;
            }
        """)
        self.thinking_indicator.setVisible(False)
        main_layout.addWidget(self.thinking_indicator)
        
        # Exibe mensagem de boas-vindas
        self.add_message("Bot", "Olá! Sou o Self-Evolving Bot, um assistente virtual que aprende com nossas conversas. Como posso ajudar?")
    
    def toggle_theme(self):
        """Alterna entre temas claro e escuro"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            self.theme_button.setText("Modo Claro")
        else:
            self.theme_button.setText("Modo Escuro")
            
        # Salvar o estado antes de atualizar
        was_training_mode = self.training_mode
        
        # Aplicar o tema
        self.update_styles()
        
        # Garantir que o modo de treinamento seja preservado
        self.training_mode = was_training_mode
        if self.training_mode:
            self.training_indicator.setText("Modo treinamento")
        else:
            self.training_indicator.setText("Modo normal")
            
        # Forçar atualização da interface
        self.repaint()
    
    def update_styles(self):
        """Atualiza os estilos baseado no tema selecionado"""
        if self.dark_mode:
            if theme_system == "qt_material" and self.app is not None:
                apply_stylesheet(self.app, theme='dark_blue.xml')
            elif theme_system == "qdarktheme":
                if QDARKTHEME_OLD_API:
                    qdarktheme.setup_theme("dark")
                else:
                    self.setStyleSheet(qdarktheme.load_stylesheet("dark"))
            else:
                # Tema escuro básico
                self.chat_area.setStyleSheet("""
                    QTextEdit {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border-radius: 10px;
                        padding: 10px;
                        font-size: 14px;
                    }
                """)
                self.centralWidget().setStyleSheet("""
                    background-color: #1e1e1e;
                    color: #ffffff;
                """)
        else:
            if theme_system == "qt_material" and self.app is not None:
                apply_stylesheet(self.app, theme='light_blue.xml')
            elif theme_system == "qdarktheme":
                if QDARKTHEME_OLD_API:
                    qdarktheme.setup_theme("light")
                else:
                    self.setStyleSheet(qdarktheme.load_stylesheet("light"))
            else:
                # Tema claro básico
                self.chat_area.setStyleSheet("""
                    QTextEdit {
                        background-color: #f5f5f5;
                        color: #000000;
                        border-radius: 10px;
                        padding: 10px;
                        font-size: 14px;
                    }
                """)
                self.centralWidget().setStyleSheet("""
                    background-color: #ffffff;
                    color: #000000;
                """)
                
        # Atualiza indicador de treinamento conforme o tema
        if self.training_mode:
            if self.dark_mode:
                self.training_indicator.setStyleSheet("""
                    QLabel {
                        background-color: #FF5722;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                """)
            else:
                self.training_indicator.setStyleSheet("""
                    QLabel {
                        background-color: #FF5722;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                """)
        else:
            if self.dark_mode:
                self.training_indicator.setStyleSheet("""
                    QLabel {
                        background-color: #333333;
                        color: #CCCCCC;
                        padding: 5px 10px;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                """)
            else:
                self.training_indicator.setStyleSheet("""
                    QLabel {
                        background-color: #E0E0E0;
                        color: #333333;
                        padding: 5px 10px;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                """)
    
    def toggle_auto_learning(self, state):
        """Ativa ou desativa o aprendizado automático"""
        is_enabled = state == Qt.CheckState.Checked.value
        if hasattr(self.bot, 'set_auto_learn'):
            self.bot.set_auto_learn(is_enabled)
        else:
            self.bot.toggle_auto_learning()
        status = "ativado" if is_enabled else "desativado"
        self.add_message("Sistema", f"Auto-aprendizado {status}.")
    
    def toggle_web_access(self, state):
        """Ativa ou desativa o acesso à web"""
        is_enabled = state == Qt.CheckState.Checked.value
        if hasattr(self.bot, 'set_web_enabled'):
            self.bot.set_web_enabled(is_enabled)
        else:
            self.bot.toggle_web_access()
        status = "ativado" if is_enabled else "desativado"
        self.add_message("Sistema", f"Acesso à web {status}.")
    
    def handle_feedback(self, score):
        """Processa o feedback do usuário sobre a resposta"""
        if not self.last_response:
            return
            
        input_text = self.last_response['input']
        response = self.last_response['response']
        
        # Tenta usar o método específico de feedback
        feedback_success = False
        if hasattr(self.bot, 'provide_feedback'):
            try:
                feedback_msg = self.bot.provide_feedback(input_text, response, score)
                feedback_success = True
                if feedback_msg:
                    self.add_message("Sistema", feedback_msg)
            except Exception as e:
                print(f"Erro ao fornecer feedback: {e}")
        
        # Se não conseguiu usar provide_feedback ou ocorreu erro, tenta aprender diretamente
        if not feedback_success and score >= 0.7:
            try:
                if hasattr(self.bot, 'learn_from_conversation'):
                    self.bot.learn_from_conversation(input_text, response)
                    feedback_success = True
                elif hasattr(self.bot, 'learn'):
                    self.bot.learn(input_text, response)
                    feedback_success = True
            except Exception as e:
                print(f"Erro ao aprender: {e}")
                
        # Mensagem padrão de feedback
        if not feedback_success:
            if score >= 0.7:
                self.add_message("Sistema", "Obrigado pelo feedback positivo!")
            else:
                self.add_message("Sistema", "Obrigado pelo feedback! Você pode me ajudar a melhorar usando o modo de treinamento.")
    
    def send_message(self):
        """Envia a mensagem do usuário para o bot"""
        message = self.input_field.text().strip()
        if not message:
            return
            
        # Limpa o campo de entrada
        self.input_field.clear()
        
        # Se estiver no modo de treinamento
        if self.training_mode:
            if self.training_input is None:
                # Primeiro passo: salva a pergunta
                self.training_input = message
                self.add_message("Você", message)
                self.add_message("Sistema", "Agora digite a resposta que você quer que eu aprenda para essa pergunta.")
            else:
                # Segundo passo: aprende a resposta
                training_response = message
                self.add_message("Você (resposta de treinamento)", message)
                
                # Aprende a associação pergunta-resposta
                self.bot.learn_from_conversation(self.training_input, training_response)
                
                # Exibe feedback de treinamento
                self.handle_training_response(training_response)
                
                # Reseta o modo de treinamento
                self.training_input = None
                self.training_mode = False
                self.training_indicator.setText("Modo normal")
                self.update_styles()
                self.train_button.setText("Treinar")
        else:
            # Exibe a mensagem do usuário
            self.add_message("Você", message)
            
            # Salva a mensagem do usuário para uso no feedback
            self.last_user_message = message
            
            # Cria e inicia a thread de processamento
            self.worker = BotWorker(self.bot, message)
            self.worker.response_ready.connect(self.handle_response)
            self.worker.thinking.connect(self.handle_thinking)
            self.worker.start()
    
    def handle_training_response(self, response):
        """Processa a resposta de treinamento"""
        self.add_message("Sistema", "Aprendi essa resposta! Experimente perguntar novamente para ver se eu aprendi corretamente.")
    
    def handle_response(self, response):
        """Processa a resposta do bot e a exibe na área de chat"""
        self.add_message("Bot", response)
        
        # Verifica se a resposta contém indicação de pesquisa web
        if "Com base em informações da web:" in response:
            # Adiciona um indicador visual de que a informação veio da web
            self.add_message("Sistema", "ℹ️ Esta resposta inclui dados obtidos através de pesquisa na internet.")
        elif "Tentei buscar informações adicionais na web, mas ocorreu um erro" in response:
            # Adiciona um alerta visual sobre o erro na pesquisa web
            self.add_message("Sistema", "⚠️ Ocorreu um erro durante a pesquisa na internet. A resposta pode estar incompleta.")
            
        # Salva a última resposta para uso no feedback
        if hasattr(self, 'last_user_message') and self.last_user_message:
            self.last_response = {
                'input': self.last_user_message,
                'response': response
            }
        else:
            # Fallback para compatibilidade
            self.last_response = {
                'input': self.worker.message if hasattr(self, 'worker') else "Mensagem desconhecida",
                'response': response
            }
            
        self.feedback_widget.setVisible(True)
    
    def handle_thinking(self, thinking):
        """Atualiza o indicador de "pensando"""""
        self.thinking_indicator.setVisible(thinking)
    
    def toggle_training(self):
        """Alterna o modo de treinamento"""
        self.training_mode = not self.training_mode
        
        if self.training_mode:
            self.training_indicator.setText("Modo de treinamento")
            self.train_button.setText("Cancelar")
            self.add_message("Sistema", "Modo de treinamento ativado. Digite uma pergunta para a qual você quer me ensinar a resposta.")
        else:
            self.training_indicator.setText("Modo normal")
            self.train_button.setText("Treinar")
            self.training_input = None
            self.add_message("Sistema", "Modo de treinamento desativado.")
            
        self.update_styles()
    
    def add_message(self, sender, message):
        """Adiciona uma mensagem à área de chat"""
        # Formatação conforme o remetente
        if sender == "Você":
            # Mensagem do usuário com estilo
            html = f'<div style="margin: 10px 0;"><span style="font-weight: bold; color: #4A90E2;">{sender}:</span> {message}</div>'
        elif sender == "Bot":
            # Mensagem do bot com estilo
            html = f'<div style="margin: 10px 0;"><span style="font-weight: bold; color: #27AE60;">{sender}:</span> {message}</div>'
        elif sender == "Sistema":
            # Mensagem de sistema com estilo
            html = f'<div style="margin: 10px 0;"><span style="font-style: italic; color: #7F8C8D;">{sender}: {message}</span></div>'
        elif sender == "Você (resposta de treinamento)":
            # Mensagem de treinamento com estilo
            html = f'<div style="margin: 10px 0;"><span style="font-weight: bold; color: #FF5722;">{sender}:</span> {message}</div>'
        else:
            # Estilo padrão
            html = f'<div style="margin: 10px 0;"><span style="font-weight: bold;">{sender}:</span> {message}</div>'
            
        # Adiciona a mensagem formatada
        self.chat_area.append(html)
        
        # Rola para o final
        cursor = self.chat_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.chat_area.setTextCursor(cursor)
    
    def closeEvent(self, event):
        """Captura o evento de fechamento da janela"""
        # Salva o estado do bot antes de fechar
        try:
            # Se o bot tiver um método 'close', chama-o para liberar recursos
            if hasattr(self.bot, 'close'):
                self.bot.close()
            else:
                self.bot.save_state()
        except:
            pass
        
        # Aceita o evento (fecha a janela)
        event.accept()

def main():
    try:
        print("Iniciando aplicação...")
        app = QApplication(sys.argv)
        print("Criando janela principal...")
        window = ChatWindow()
        print("Configurando referência da aplicação...")
        window.app = app  # Armazena referência ao QApplication para temas
        print("Aplicando estilos iniciais...")
        window.update_styles()  # Aplica os estilos depois de configurar a referência app
        print("Exibindo janela...")
        window.show()
        print("Iniciando loop de eventos...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione ENTER para sair...")

if __name__ == "__main__":
    main() 