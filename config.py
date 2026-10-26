"""Shared settings. Change model names here only."""
OLLAMA_URL = "http://localhost:11434"
CHAT_MODEL = "llama3.2:3b"          # OpenSRE + RAG model (OpenSRE's own wizard recommends 3B for 16 GB RAM)
EMBED_MODEL = "nomic-embed-text"    # embeddings for RAG
SUMMARY_MODEL = "sre-summary"       # your fine-tuned model (Step 6)
BASE_SUMMARY_MODEL = "llama3.2:1b"  # same base model, NOT fine-tuned (for comparison)
CHROMA_DIR = "chroma_db"
RUNBOOK_DIR = "runbooks"
ALERT_DIR = "alerts"
REPORT_DIR = "reports"
