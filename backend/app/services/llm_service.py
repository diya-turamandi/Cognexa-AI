
import os
import httpx

from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2"
)


async def generate_answer(question: str, context: str):

    prompt = f"""
You are Cognexa AI, an intelligent document assistant.

Answer the user's question using ONLY the provided context.

Rules:
1. Do not invent information.
2. If the answer is not in the context, say:
   "I could not find this information in the uploaded documents."
3. Give clear and structured answers.
4. Cite sources using the page numbers provided.
5. Be concise but informative.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    async with httpx.AsyncClient(timeout=120.0) as client:

        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        response.raise_for_status()

        data = response.json()

        return data["response"].strip()
