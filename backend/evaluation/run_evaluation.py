
import json
import asyncio
from pathlib import Path

import pandas as pd

from app.core.database import SessionLocal
from rag.hybrid_search import hybrid_search
from app.services.reranker import rerank_chunks
from app.services.llm_service import generate_answer


BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "dataset.json"
RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(exist_ok=True)


async def evaluate_pipeline():

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    db = SessionLocal()

    evaluation_data = []

    try:
        for item in dataset:

            question = item["question"]
            ground_truth = item["ground_truth"]
            document_id = item["document_id"]

            print("\nQuestion:", question)

            # 1. Retrieve 20 candidates
            candidates = hybrid_search(
                db=db,
                query=question,
                document_id=document_id,
                limit=20,
                candidate_limit=20
            )

            print("Retrieved:", len(candidates))

            # 2. Rerank candidates
            reranked = rerank_chunks(
                query=question,
                documents=candidates,
                top_k=5
            )

            print("Reranked:", len(reranked))

            # 3. Prepare context
            contexts = [
                chunk.get("text", "")
                for chunk in reranked
                if chunk.get("text")
            ]

            context = "\n\n".join(contexts)

            # 4. Generate answer using Ollama
            answer = await generate_answer(
                question=question,
                context=context,
                history="No previous conversation."
            )

            print("Answer generated successfully")

            # 5. Store evaluation data
            evaluation_data.append({
                "question": question,
                "answer": answer,
                "contexts": contexts,
                "ground_truth": ground_truth
            })

    finally:
        db.close()

    # Save generated responses
    with open(
        RESULTS_DIR / "generated_responses.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            evaluation_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nRAG pipeline execution completed!")


if __name__ == "__main__":
    asyncio.run(evaluate_pipeline())
