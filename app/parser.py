# app/parser.py

from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import json

# Cargar variables de entorno desde .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Crear cliente OpenAI moderno (versión 1.x)
client = AsyncOpenAI(api_key=api_key)

async def parse_intent(nl_query: str) -> dict:
    """
    Llama a OpenAI para extraer intención SQL estructurada desde una consulta en lenguaje natural.
    Devuelve un diccionario con los elementos detectados.
    """

    prompt = f"""
You are an NL2SQL assistant. Given the following user request in natural language, extract the SQL intent as a structured JSON object.

Request:
\"\"\"{nl_query}\"\"\"

Output format:
{{
  "action": "SELECT",
  "tables": [],
  "columns": [],
  "conditions": [],
  "aggregations": [],
  "joins": false,
  "group_by": [],
  "order_by": [],
  "limit": null
}}

If some fields don't apply, leave them empty or null.
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        # Obtener contenido de la respuesta
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
