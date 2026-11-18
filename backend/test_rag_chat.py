
from rag.retriever import retrieve_relevant_chunks
from rag.answer_generator import generate_answer
from rag.vector_store import close_vector_store


def main():
    try:
        print("\n========== COGNEXA AI ==========")

        question = input("\nAsk your PDF: ").strip()

        if not question:
            print("Please enter a question.")
            return

        print("\nSearching your documents...")

        chunks = retrieve_relevant_chunks(
            query=question,
            limit=5
        )

        if not chunks:
            print("No relevant information found.")
            return

        print("Generating answer using local Ollama LLM...")

        result = generate_answer(
            question=question,
            retrieved_chunks=chunks
        )

        print("\n========== ANSWER ==========\n")
        print(result["answer"])

        print("\n========== SOURCES ==========\n")

        for source in result["sources"]:
            print(
                f"File: {source['filename']} | "
                f"Page: {source['page']} | "
                f"Score: {source['score']}"
            )

    except Exception as error:
        print(f"\nError: {error}")

    finally:
        close_vector_store()


if __name__ == "__main__":
    main()
