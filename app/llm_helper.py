# app/llm_helper.py

import os
import json
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def complete_placeholders_with_llm(user_query: str, partial_sql: str, schema: dict) -> dict:
    """
    Consulta al LLM para sugerir cómo completar los placeholders faltantes.
    Devuelve un diccionario JSON con las claves y valores que faltaban.
    """

    schema_str = "\n".join(
        f"Table: {table}\nColumns: {', '.join([f'\"{col}\"' for col in cols])}"
        for table, cols in schema.items()
    )

    prompt = f"""
You are a SQL assistant. A partially filled SQL query contains unknown placeholders like UNKNOWN_COLUMN,
UNKNOWN_TABLE, UNKNOWN_GROUP, etc. Based on the user's request and the database schema,
identify the correct replacements for those placeholders.

Return a JSON with keys like:
{{
  "table": "\"singer\"",
  "column": "\"Name\"",
  "group_column": "\"Singer_ID\"",
  "agg_func": "AVG",
  "agg_column": "\"Duration\"",
  "value": "3"
}}

⚠️ STRICT INSTRUCTIONS:
- Return only a valid JSON. No commentary or explanation.
- Use identifiers **exactly as in the schema**, including double quotes.
- If you are unsure, give your best guess using schema columns.
- If a value does not apply, omit the key (do not return null or empty strings).
- Never remove quotes from identifiers. Respect casing.

---

User question:
\"\"\"{user_query}\"\"\"

Partial SQL:
\"\"\"{partial_sql}\"\"\"

Database schema:
{schema_str}

Return only the JSON object:
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw_content = response.choices[0].message.content
        if not raw_content:
            return {"error": "No response content from LLM."}

        # Limpiar posible envoltorio de triple backticks
        cleaned = raw_content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        return json.loads(cleaned)

    except Exception as e:
        return {"error": str(e)}
