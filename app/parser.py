# app/parser.py

from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import json
from typing import Dict

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Crear cliente OpenAI
client = AsyncOpenAI(api_key=api_key)

async def parse_intent(nl_query: str, schema: Dict[str, list]) -> dict:
    """
    Extrae la intención SQL a partir de una pregunta NL, usando OpenAI y el esquema proporcionado.
    :param nl_query: La consulta en lenguaje natural.
    :param schema: Diccionario con tablas y sus columnas. Ej: { "table1": ["col1", "col2"], ... }
    """

    try:
        schema_info = "\n".join(
            f"Table: {table}\nColumns: {', '.join(cols)}"
            for table, cols in schema.items()
        )
    except Exception as e:
        return {"error": f"Schema formatting error: {str(e)}"}

    prompt = f"""
You are an NL2SQL assistant. The user will ask questions in natural language.
Use the provided database schema to extract the SQL intent in structured JSON format.

Only include tables and columns that appear in the schema.

### Database Schema:
{schema_info}

### Natural Language Query:
\"\"\"{nl_query}\"\"\"

### Structured Output Format:
{{
  "action": "SELECT",
  "tables": ["table_name"],
  "columns": ["column1", "column2"],
  "conditions": [
    {{
      "column": "column_name",
      "operator": ">",        // or <, =, LIKE, etc.
      "value": 5              // can be number or string
    }}
  ],
  "aggregations": [
    {{
      "function": "AVG",       // or SUM, COUNT, MAX, etc.
      "column": "score"
    }}
  ],
  "joins": false,
  "group_by": ["column_name"],
  "order_by": ["column_name"],
  "limit": 10
}}

If a field is not needed, leave it as an empty list, null, or false.
Return only the JSON. Do not include explanations.
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        parsed_raw = response.choices[0].message.content

        if not parsed_raw:
            return {"error": "No response content received from OpenAI."}

        try:
            parsed = json.loads(parsed_raw)
            return parsed
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON format returned by OpenAI.",
                "raw_response": parsed_raw
            }

    except Exception as e:
        return {"error": str(e)}
