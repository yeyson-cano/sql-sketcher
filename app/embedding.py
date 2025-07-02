# app/embedding.py

from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_embedding(text: str) -> list[float]:
    """
    Obtiene el embedding semántico del texto usando la API text-embedding-ada-002.
    """
    response = await client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding
