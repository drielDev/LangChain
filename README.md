# Assistente (LangChain)

## Executar localmente

1) Instale as dependências:

```bash
pip install -r requirements.txt
```

2) Configure a variável de ambiente:

```text
GROQ_API_KEY=sua_chave_aqui
```

3) Rode um exemplo:

```bash
python integration_example.py
```

Opcional (smoke test):

```bash
python -m langchain_assistant.test_assistant
```

## Integrar no projeto principal 

1) Copie a pasta `langchain_assistant/` para a raiz do projeto principal.

2) Instale as dependências (use o seu `requirements.txt` ou mescle no do projeto principal).

3) Garanta `GROQ_API_KEY` no ambiente.

Uso recomendado (1 sessão por usuário/fluxo):

```python
from langchain_assistant import AssistantSession

session = AssistantSession()
texto = session.generate_response("Olá")

# Para pipelines (LangGraph/validação) que preferem exceção em vez de string de erro:
texto = session.generate_response("...", raise_on_error=True)
```