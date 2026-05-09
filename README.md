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

Rodar a interface (Streamlit):

```bash
streamlit run app.py
```

Opcional (smoke test):

```bash
python -m langchain_assistant.test_assistant
```

## Integrar no projeto principal 

O jeito mais simples é literalmente copiar estes itens para a raiz do projeto principal:

- `langchain_assistant/`
- `app.py`
- `requirements.txt`

Depois:

1) Instale as dependências:

```bash
pip install -r requirements.txt
```

2) Garanta `GROQ_API_KEY` no ambiente.

3) (Opcional) Suba a UI:

```bash
streamlit run app.py
```

Uso recomendado (1 sessão por usuário/fluxo):

```python
from langchain_assistant import AssistantSession

session = AssistantSession()
texto = session.generate_response("Olá")

# Para pipelines (LangGraph/validação) que preferem exceção em vez de string de erro:
texto = session.generate_response("...", raise_on_error=True)
```