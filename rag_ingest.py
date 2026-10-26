"""Step 3a: load runbooks -> split -> embed with nomic-embed-text -> store in ChromaDB."""
import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHROMA_DIR, EMBED_MODEL, OLLAMA_URL, RUNBOOK_DIR

docs = [
    Document(page_content=p.read_text(encoding="utf-8"), metadata={"source": p.name})
    for p in sorted(Path(RUNBOOK_DIR).glob("*.md"))
]
# Runbooks are short, so big chunks keep each runbook mostly whole.
chunks = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=100).split_documents(docs)

shutil.rmtree(CHROMA_DIR, ignore_errors=True)  # fresh index every run
Chroma.from_documents(
    chunks,
    OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL),
    persist_directory=CHROMA_DIR,
    collection_name="runbooks",
)
print(f"Stored {len(chunks)} chunks from {len(docs)} runbooks in {CHROMA_DIR}/")
