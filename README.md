# EvolvIQ - Streamlit + Supabase PostgreSQL

EvolvIQ is an AI-native intelligence workspace prototype with:

- Research Mode
- Knowledge Chat
- Upload Knowledge
- Knowledge Base
- Memory
- Knowledge Graph
- Supabase PostgreSQL persistence

## 1. Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Before running locally, create:

```text
.streamlit/secrets.toml
```

Use `.streamlit/secrets.toml.example` as the template.

## 2. Supabase setup

1. Create a Supabase account.
2. Create a new project.
3. Go to Project Settings -> Database -> Connection string.
4. Copy the URI / pooler connection string.
5. Replace `[YOUR-PASSWORD]` with your database password.
6. Add this to Streamlit secrets:

```toml
DATABASE_URL = "postgresql://postgres.PROJECT_REF:YOUR_PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres?sslmode=require"
```

The app creates tables automatically on startup.

## 3. Deploy to Streamlit Community Cloud

1. Push this project to GitHub.
2. Go to Streamlit Community Cloud.
3. New app -> select repo -> main file: `app.py`.
4. Open Advanced settings / Secrets.
5. Add:

```toml
DATABASE_URL = "your_supabase_connection_string"
```

6. Deploy.

## 4. Important security note

Never commit `.streamlit/secrets.toml` to GitHub. It is already listed in `.gitignore`.

## 5. Future upgrades

Next steps:

- Add OpenAI / local embeddings
- Add pgvector extension
- Add semantic search
- Add user authentication
- Add workspaces
- Add Supabase Storage for uploaded files
