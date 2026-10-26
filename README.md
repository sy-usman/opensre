# local-sre – AI incident assistant (demo)

Run everything inside WSL Ubuntu, from this folder:

    ollama pull llama3.2:3b && ollama pull nomic-embed-text && ollama pull llama3.2:1b
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python run_opensre.py            # OpenSRE reports -> reports/
    python rag_ingest.py             # runbooks -> ChromaDB
    python rag_assistant.py          # test RAG
    python compare_prompts.py        # bad vs good prompt
    python finetune/compare_models.py  # base vs fine-tuned
    streamlit run app.py

The full step-by-step guide is in the Claude Doc.
