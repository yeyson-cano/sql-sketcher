# app/join_resolver.py

import os
import json
from typing import Dict
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def suggest_join_info(
    user_input: str,
    missing_column: str,
    main_table: str,
    schema_columns: Dict[str, list]
) -> Dict[str, str]:
    """
    Usa el LLM para sugerir a qué tabla pertenece una columna y qué condición JOIN usar.
    """

    # 🔧 Preprocesar el esquema si hay columnas como diccionarios
    cleaned_schema = {
        table: [
            col["name"] if isinstance(col, dict) and "name" in col else str(col)
            for col in columns
        ]
        for table, columns in schema_columns.items()
    }

    schema_str = "\n".join(
        f"Table: {table}\nColumns: {', '.join(cols)}"
        for table, cols in cleaned_schema.items()
    )

    prompt = f"""
You are a SQL assistant helping to resolve JOIN conditions.

You are given:
- A user question.
- A missing column that likely belongs to a different table.
- The table where the current query is anchored.
- The full database schema.

Determine which table the column most likely belongs to and what JOIN condition should be used to connect it.

Format your response strictly as:
{{
  "join_table": "target_table",
  "on_condition": "\"main_table\".\"foreign_key\" = \"target_table\".\"id\""
}}

Use only the schema provided. Always use double quotes for identifiers.

---

User question:
\"\"\"{user_input}\"\"\"

Missing column:
{missing_column}

Main table:
{main_table}

Schema:
{schema_str}

Respond only with a JSON object:
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content
        if not content:
            return {"error": "No content returned from LLM."}

        # Limpiar marcas de código si vienen
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        return json.loads(cleaned)

    except Exception as e:
        return {"error": str(e)}
