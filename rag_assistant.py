"""Step 3b: RAG assistant. Root cause -> retrieve best runbook from Chroma -> structured fix plan."""
import sys

from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings

from config import CHAT_MODEL, CHROMA_DIR, EMBED_MODEL, OLLAMA_URL
from prompts import good_messages

_store = None


def store() -> Chroma:
    global _store
    if _store is None:
        _store = Chroma(
            persist_directory=CHROMA_DIR,
            collection_name="runbooks",
            embedding_function=OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL),
        )
    return _store


def retrieve(root_cause: str, k: int = 2):
    """R in RAG: return (doc, distance) pairs, best first. Lower distance = closer match."""
    return store().similarity_search_with_score(root_cause, k=k)


def fix_plan(root_cause: str) -> dict:
    """A + G in RAG: put the best runbook into the prompt and generate a fix plan."""
    hits = retrieve(root_cause)
    best_doc, score = hits[0]
    llm = ChatOllama(model=CHAT_MODEL, base_url=OLLAMA_URL, temperature=0)
    answer = llm.invoke(good_messages(root_cause, best_doc.metadata["source"], best_doc.page_content))
    return {
        "runbook": best_doc.metadata["source"],
        "distance": round(float(score), 3),
        "candidates": [(d.metadata["source"], round(float(s), 3)) for d, s in hits],
        "plan": answer.content,
    }


if __name__ == "__main__":
    rc = " ".join(sys.argv[1:]) or "orders-service gets connection refused from orders-db:5432, db pod Pending"
    result = fix_plan(rc)
    print("Retrieved:", result["candidates"])
    print(result["plan"])
