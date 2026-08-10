import sys
import argparse
import config
from document_loader import process_documents_for_indexing
from vector_store import VectorStore
from rag_engine import RAGEngine

# Force UTF-8 encoding for standard output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def ingest_data(vector_store: VectorStore):
    """Loads documents from data/ and indexes them into Qdrant."""
    print("\n" + "=" * 50)
    print(" >>> INGESTING & INDEXING COLLEGE DATA <<< ")
    print("=" * 50)
    records = process_documents_for_indexing()
    if not records:
        print("[!] No document records found in 'data/' folder to index.")
        return
    count = vector_store.add_documents(records)
    print(f"[+] Successfully indexed {count} text chunks into local Qdrant Vector Store.")
    print("=" * 50 + "\n")

def interactive_chat(rag_engine: RAGEngine):
    """Interactive terminal chat loop."""
    print("\n" + "=" * 60)
    print(" COLLEGE RAG CHATBOT (Terminal CLI)")
    print(f" Model: {config.LLM_MODEL_NAME} ({config.OPENAI_BASE_URL}) | Vector DB: Qdrant Local")
    print(" Commands: '!clear' to reset chat memory, '!ingest' to index documents, 'exit' to quit.")

    while True:
        try:
            user_input = input("\nAsk a question: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q", "!exit"]:
                print("Exiting College ChatBot. Goodbye!")
                break

            if user_input.lower() in ["!clear", "!reset"]:
                rag_engine.clear_history()
                continue

            if user_input.lower() == "!ingest":
                ingest_data(rag_engine.vector_store)
                continue


            print("\nSearching Qdrant knowledge base & generating response...")
            response = rag_engine.generate_response(user_input)

            print("\nResponse:")
            print("-" * 50)
            print(response["answer"])
            print("-" * 50)

            if response["sources"]:
                print("Sources retrieved:")
                for src in response["sources"]:
                    print(f"  * {src['source']} (Similarity score: {src['score']:.4f})")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting College ChatBot. Goodbye!")
            break

def main():
    parser = argparse.ArgumentParser(description="College RAG Chatbot")
    parser.add_argument("--ingest", action="store_true", help="Force re-indexing of documents in data/ directory")
    args = parser.parse_args()

    print("[*] Starting College ChatBot...")
    vs = VectorStore()

    if args.ingest:
        ingest_data(vs)

    # Check if collection is empty, offer auto-ingest
    coll_info = vs.client.get_collection(config.COLLECTION_NAME)
    if coll_info.points_count == 0:
        print("[!] Local Qdrant collection is currently empty.")
        print("[*] Automatically triggering initial ingestion from data/ folder...")
        ingest_data(vs)

    rag = RAGEngine(vector_store=vs)

    # If argument question is passed non-interactively or interactive mode
    interactive_chat(rag)

if __name__ == "__main__":
    main()
