# generate_embeddings.py

import asyncio
from app.template_repository import generate_template_embeddings

if __name__ == "__main__":
    print("🚀 Generando embeddings de plantillas...")
    asyncio.run(generate_template_embeddings())
    print("✅ Embeddings generados y guardados en templates.json")
