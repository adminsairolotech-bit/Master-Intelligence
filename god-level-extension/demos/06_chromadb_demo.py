"""
ChromaDB Demo - 100% Working
Vector database for embeddings storage and similarity search
"""
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def run_chromadb_demo():
    print("=" * 60)
    print("[DB] CHROMADB DEMO - Vector Database")
    print("=" * 60)

    try:
        import chromadb
        from chromadb.config import Settings

        print("\n[OK] ChromaDB imported successfully!")

        # Initialize client
        print("\n[CONNECT] Connecting to ChromaDB...")
        client = chromadb.PersistentClient(path="./chromadb_data")
        print("   [OK] Persistent client created at ./chromadb_data")

        # Create collection
        print("\n[CREATE] Creating collection...")
        collection = client.get_or_create_collection(
            name="sai_documents",
            metadata={"description": "SAI Rolotech documents collection"}
        )
        print("   [OK] Collection 'sai_documents' created")

        # Add documents
        print("\n[ADD] Adding documents...")

        collection.add(
            documents=[
                "Python is a versatile programming language.",
                "Machine learning enables computers to learn from data.",
                "LangChain connects LLMs with external data sources.",
                "AutoGPT is an autonomous AI agent framework."
            ],
            ids=["doc1", "doc2", "doc3", "doc4"],
            metadatas=[
                {"topic": "programming", "language": "python"},
                {"topic": "ai", "language": "general"},
                {"topic": "llm", "language": "python"},
                {"topic": "agents", "language": "python"}
            ]
        )
        print("   [OK] 4 documents added to collection")

        # Query collection
        print("\n[QUERY] Querying collection...")
        results = collection.query(
            query_texts=["What is Python?"],
            n_results=2
        )
        print(f"   [OK] Query returned {len(results['ids'][0])} results")

        print("\n[ARCH] ChromaDB Architecture:")
        print("   ┌─────────────────────────────────────────────┐")
        print("   │              CHROMADB CLIENT                │")
        print("   │           (Persistent/Sync/Async)           │")
        print("   └─────────────────┬───────────────────────────┘")
        print("                     │")
        print("       ┌─────────────┼─────────────┐")
        print("       │             │             │")
        print("   ┌───┴───┐   ┌───┴───┐   ┌───┴───┐")
        print("   │Collection│  │Collection│  │Collection│")
        print("   │docs_1   │  │docs_2   │  │docs_3   │")
        print("   └───┬───┘   └───┬───┘   └───┬───┘")
        print("       │             │             │")
        print("       └─────────────┼─────────────┘")
        print("                     │")
        print("       ┌─────────────┼─────────────┐")
        print("       │             │             │")
        print("   ┌───┴───┐   ┌───┴───┐   ┌───┴───┐")
        print("   │ ID    │   │Embedding│  │Metadata│")
        print("   │ DOC   │   │ VECTOR │  │  DATA  │")
        print("   └───────┘   └────────┘  └────────┘")

        print("\n[STATS] Collection Stats:")
        print(f"   • Name: sai_documents")
        print(f"   • Documents: {collection.count()}")
        print(f"   • Embedding dimension: 384 (default)")

        print("\n[SUCCESS] CHROMADB OPERATIONAL!")
        print("   Use: collection.query(), collection.add(), collection.get()")

        return {
            "status": "success",
            "framework": "ChromaDB",
            "version": "1.1.1",
            "collection": "sai_documents",
            "document_count": collection.count(),
            "features": [
                "Vector database",
                "Embeddings storage",
                "Similarity search",
                "Collections",
                "Metadata filtering"
            ],
            "execution_ready": True
        }

    except ImportError as e:
        print(f"\n[ERROR] Import Error: {e}")
        print("   Run: pip install chromadb")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    result = run_chromadb_demo()
    print("\n" + "=" * 60)
    print("RESULT:", json.dumps(result, indent=2))
