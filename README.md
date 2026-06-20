# Finanças Pessoais

Aplicativo Streamlit para lançamentos, parcelas e análises financeiras. Está preparado para funcionar localmente com SQLite e, quando publicado, com PostgreSQL do Supabase.

## Desenvolvimento local

1. Crie `.streamlit/secrets.toml` a partir de `.streamlit/secrets.toml.example`.
2. Defina uma senha forte em `APP_PASSWORD`.
3. Execute:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run contole_financeiro.py
```

Sem `DATABASE_URL`, os dados são gravados localmente em `data/financas.db`.

## Publicar para acessar de qualquer lugar

1. Crie um projeto no Supabase e, no SQL Editor, execute `supabase/schema.sql`.
2. Em **Connect**, copie a URL de conexão do **Session pooler**.
3. Envie este projeto para um repositório privado no GitHub. Nunca envie `.streamlit/secrets.toml` ou `data/financas.db`.
4. Em Streamlit Community Cloud, crie um app a partir do repositório e escolha `contole_financeiro.py` como arquivo principal.
5. Em **Advanced settings → Secrets**, cole:

```toml
DATABASE_URL = "postgresql://..."
APP_PASSWORD = "uma-senha-forte-e-exclusiva"
```

O app receberá um endereço `https://...streamlit.app`, acessível por celular ou computador. A senha protege o aplicativo; não compartilhe o link ou a senha com pessoas não autorizadas.