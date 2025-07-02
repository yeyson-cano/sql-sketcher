# SQL Sketcher – NL2SQL Project

> Modular project for generating complex SQL sketches from natural language queries, integrating LLM-based parsing, semantic embeddings, template selection, and SQL validation over PostgreSQL.

---

## 📌 Project Summary

This system converts natural language queries in English into valid SQL sketches using a multi-step pipeline that includes:

- Intent parsing via GPT-3.5-turbo
- Semantic embedding via OpenAI `text-embedding-ada-002`
- Template selection via hybrid scoring
- Automatic SQL structure assembly
- Dry-run SQL validation over PostgreSQL

Designed as part of a 2025 undergraduate software engineering thesis.

---

## 🧱 Stack

- **Python 3.10+**
- **FastAPI**
- **PostgreSQL 15+** (for dry-run validation)
- **OpenAI API** (GPT-3.5, Embeddings)
- Optional: `uvicorn`, `httpx`, `numpy`, `psycopg2`

---

## 🚀 Quickstart (dev mode)

1. Clone the repo:
   ```bash
   git clone https://github.com/tuusuario/sql-sketcher.git
   cd sql-sketcher
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. Set your API key and DB config as environment variables:

   ```bash
   export OPENAI_API_KEY=your_key
   export DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
   ```

4. Run the app:

   ```bash
   uvicorn main:app --reload
   ```

---

## 🧪 Sample Request (via Swagger UI)

POST `/generate-sql`

```json
{
  "query": "Show the average revenue per region"
}
```

Sample response:

```json
{
  "status": "valid",
  "sql": "SELECT region, AVG(revenue) FROM sales GROUP BY region;"
}
```

---

## 📂 Folder structure (once built)

```
sql-sketcher/
├── main.py
├── parser.py
├── embedding.py
├── templates.json
├── selector.py
├── validator.py
├── config.py
└── README.md
```

---

## 📘 License

MIT License

---

Developed with heart and precision by **Yeyson Cano**
*Universidad Nacional Mayor de San Marcos* — Ingeniería de Software, 2025
