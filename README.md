# Assistente Médico com LangChain

## Descrição

Módulo responsável pela geração de respostas utilizando LangChain e modelos LLM da Groq.

## Funcionalidades

- geração de respostas contextualizadas
- memória de conversa
- reset de histórico
- logs simples
- prompt especializado em saúde da mulher

## Estrutura

src/langchain_assistant/

## Funções principais

### generate_response(user_input)

Recebe uma string e retorna uma resposta gerada pelo modelo.

### reset_conversation()

Reinicia o histórico da conversa.

## Como executar

1. Criar .env
2. Adicionar GROQ_API_KEY
3. Instalar dependências

```bash
pip install -r requirements.txt
```

Crie um arquivo `.env` com sua chave:

```
GROQ_API_KEY=sua_chave_aqui
```

Exemplo rápido de uso (interface esperada para integração):

```python
from src.langchain_assistant import generate_response, reset_conversation

print(generate_response("Estou com dores menstruais intensas."))
reset_conversation()
```

Para rodar um exemplo interativo:

```bash
python integration_example.py
```