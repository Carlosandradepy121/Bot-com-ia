# Self-Evolving Bot

Um bot inteligente baseado em redes neurais com interface gráfica PyQt.

## Sobre o Projeto

O Self-Evolving Bot é um assistente de conversação que utiliza um sistema híbrido de IA para aprender e evoluir com cada interação. O bot aprende através de conversas e é capaz de manter conhecimento mesmo offline.

## Recursos do Sistema de IA

- **Base de Conhecimento Pré-treinada**: Respostas pré-definidas para perguntas comuns
- **Sistema de Aprendizado**: Aprende novas respostas através do modo de treinamento
- **Gerador de Linguagem**: Cria respostas coerentes com base no treinamento
- **Memória Persistente**: Armazena conversas e conhecimentos mesmo após reiniciar
- **Funciona 100% Offline**: Não requer conexão com internet para funcionar

## Requisitos

- Python 3.8 ou superior
- PyQt6
- PyTorch
- Qt-Material
- Outras dependências listadas em `requirements.txt`

## Instalação

### Método 1: Execução direta (recomendado)

1. Clone ou baixe este repositório
2. Execute o arquivo `executar_bot.bat` para iniciar o bot diretamente

O script detectará automaticamente sua instalação Python e instalará quaisquer dependências necessárias.

### Método 2: Instalação manual

```bash
# Instale as dependências
pip install -r requirements.txt

# Execute o bot
python run_with_qt_material.py
```

### Método 3: Compilar executável

Execute o arquivo `compilar_exe.bat` para criar um executável autônomo. 
Após a compilação, o executável será criado na pasta `dist`.

## Estrutura do Projeto

- `run_with_qt_material.py` - Inicializador principal do bot com suporte a temas
- `gui_interface.py` - Interface gráfica baseada em PyQt6
- `self_evolving_bot.py` - Implementação do sistema de IA do bot
- `executar_bot.bat` - Script para executar o bot diretamente
- `compilar_exe.bat` - Script para compilar um executável

## Como Usar

### Modo Normal de Conversa

1. Inicie o bot usando um dos métodos acima
2. A interface do bot será exibida
3. Digite suas mensagens na caixa de entrada na parte inferior
4. O bot responderá com base em seu conhecimento e treinamento anterior

### Modo de Treinamento

1. Clique no botão "Ativar Treinamento" para entrar no modo de treinamento
2. Digite uma pergunta e pressione Enter
3. Digite a resposta que você quer que o bot aprenda e pressione Enter
4. O sistema confirmará o aprendizado
5. Repita os passos 2-4 para ensinar mais respostas
6. Clique em "Desativar Treinamento" quando terminar

## Sistema de Arquivos de Dados

O bot armazena seu conhecimento e memórias em vários arquivos:

- `knowledge.json` - Base de conhecimento personalizada
- `memories.pkl` - Histórico de conversas anteriores
- `language_model.pkl` - Modelo de linguagem treinado

Estes arquivos são criados automaticamente e permitem que o bot mantenha seu conhecimento entre as sessões.

## Resolução de Problemas

### Problema com torch._C

Se você encontrar o erro `No module named 'torch._C'`, execute o script `executar_bot.bat` que tentará resolver o problema automaticamente reinstalando o PyTorch.

### Problema com qt_material

Se ocorrerem erros relacionados ao qt_material, o script `run_with_qt_material.py` tentará criar os arquivos necessários e resolver o problema.

### Bot não responde corretamente

Se o bot não estiver respondendo adequadamente:
1. Tente usar o modo de treinamento para ensinar respostas específicas
2. Verifique se os arquivos de dados não estão corrompidos
3. Como último recurso, exclua os arquivos `knowledge.json`, `memories.pkl` e `language_model.pkl` para reiniciar o treinamento

## Funcionalidades

- Interface gráfica moderna com PyQt6
- Temas personalizáveis via qt-material
- Aprendizado baseado em interações
- Sistema de memória de conversas
- Geração de texto com base em padrões aprendidos

## Licença

Este projeto é distribuído sob a licença MIT. 