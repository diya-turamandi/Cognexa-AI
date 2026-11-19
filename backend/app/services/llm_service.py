
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


async def generate_answer(
    question: str,
    context: str,
    history: str = "No previous conversation."
):

    prompt = f"""
You are Cognexa AI, an intelligent document assistant.

Your job is to answer questions using the uploaded document
context and the conversation history.

RULES:

1. Use the document context as the primary source of factual information.
2. Use conversation history to understand follow-up questions.
3. Do not invent facts or information.
4. If the answer is not available in the document context,
   clearly say that you could not find it in the uploaded documents.
5. Give clear and structured answers.
6. Include page numbers when available.
7. If the user asks a follow-up question, understand it
   using the previous conversation.

PREVIOUS CONVERSATION:

{history}

DOCUMENT CONTEXT:

{context}

CURRENT QUESTION:

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
