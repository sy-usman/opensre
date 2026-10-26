# OpenSRE – AI-Powered Incident Response Assistant

OpenSRE brings AI into the SRE incident workflow. When an alert fires, the system automatically investigates it, retrieves the right runbook, generates a structured fix plan, and produces a concise incident summary — all running locally on your machine without sending data to any external service.

---

## What It Does

| Stage | Component | What happens |
|---|---|---|
| 1 | **Alert ingestion** | Reads a structured alert (JSON) describing the incident |
| 2 | **AI investigation** | OpenSRE CLI queries a local LLM to produce root cause, evidence, severity, and next checks |
| 3 | **RAG fix plan** | Runbooks are embedded into ChromaDB; the closest match is retrieved and fed to the LLM to generate step-by-step fix instructions |
| 4 | **Incident summary** | A fine-tuned model condenses everything into a 6-line incident summary ready for post-mortems or tickets |
| 5 | **UI** | Streamlit dashboard wires all four stages into a single-click pipeline |

---

## How AI Is Integrated

### Local LLM via Ollama
All inference runs on-device through [Ollama](https://ollama.com). No cloud API keys, no data leaving your machine.

- **`llama3.2:3b`** — primary chat model used by OpenSRE for investigation and RAG answer generation
- **`nomic-embed-text`** — embedding model that converts runbook text into vectors for semantic search
- **`llama3.2:1b`** — base model used as the starting point for fine-tuning

### Retrieval-Augmented Generation (RAG)
Runbooks are chunked, embedded, and stored in a local ChromaDB vector database (`rag_ingest.py`). At query time, the system performs semantic similarity search against the alert's root cause description and injects the best-matching runbook into the LLM prompt — ensuring answers are grounded in your actual operational knowledge, not hallucinated.

```
Alert root cause
      │
      ▼
ChromaDB similarity search
      │
      ▼
Best-matching runbook injected into prompt
      │
      ▼
LLM generates structured fix plan (IMMEDIATE ACTION → FIX STEPS → VERIFY → ESCALATE IF)
```

### Prompt Engineering
`prompts.py` implements a system prompt + few-shot strategy. A bad prompt (`"Fix this: {root_cause}"`) produces vague, inconsistent output. The production prompt constrains the model to a strict output schema and provides two worked examples so the model learns the exact structure expected — SEV level, verb-led steps, commands in backticks.

### Fine-Tuned Summary Model
`finetune/` contains the dataset pipeline and a Modelfile to fine-tune `llama3.2:1b` on incident summaries (`sre-summary` in Ollama). The fine-tuned model is compared against the untuned base in `finetune/compare_models.py` to validate that specialization improves summary quality.

---

## Project Structure

```
opensre/
├── alerts/                  # Sample alert payloads (JSON)
├── runbooks/                # Markdown runbooks per failure mode
├── finetune/
│   ├── incident_summaries.jsonl   # Fine-tuning dataset
│   ├── make_dataset.py            # Dataset builder
│   ├── Modelfile                  # Ollama fine-tune config
│   └── compare_models.py          # Base vs fine-tuned comparison
├── reports/                 # Generated investigation reports
├── app.py                   # Streamlit UI
├── run_opensre.py           # OpenSRE CLI wrapper
├── rag_ingest.py            # Embed runbooks → ChromaDB
├── rag_assistant.py         # RAG retrieval + fix plan generation
├── compare_prompts.py       # Bad prompt vs good prompt demo
├── prompts.py               # System prompt + few-shot examples
├── config.py                # Model names, paths, URLs
└── requirements.txt
```

---

## Prerequisites

- [WSL 2 / Ubuntu](https://learn.microsoft.com/en-us/windows/wsl/) (recommended) or Linux/macOS
- [Ollama](https://ollama.com/download) installed and running (`ollama serve`)
- [OpenSRE CLI](https://github.com/opensre/opensre) on your PATH
- Python 3.11+
- 16 GB RAM recommended (8 GB minimum with the 1B model)

---

## Setup

```bash
# 1. Pull required models
ollama pull llama3.2:3b
ollama pull nomic-embed-text
ollama pull llama3.2:1b

# 2. Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Run the full investigation pipeline (CLI)
```bash
python run_opensre.py                        # all alerts in alerts/
python run_opensre.py alerts/high_cpu.json   # single alert
```
Reports are saved to `reports/`.

### Build the runbook vector index
```bash
python rag_ingest.py
```
Run this once after adding or editing any runbook in `runbooks/`.

### Test RAG retrieval
```bash
python rag_assistant.py "orders-service gets connection refused from orders-db:5432"
```

### Compare prompt strategies
```bash
python compare_prompts.py
```

### Fine-tune and compare models
```bash
# Build dataset, create fine-tuned model, then compare
python finetune/make_dataset.py
ollama create sre-summary -f finetune/Modelfile
python finetune/compare_models.py
```

### Launch the Streamlit UI
```bash
streamlit run app.py
```
Open `http://localhost:8501`, select an alert from the sidebar, and click **Run pipeline**.

---

## Alerts Included

| Alert | Failure mode |
|---|---|
| `high_cpu.json` (via Datadog example) | CPU saturation after deploy |
| `high_memory_oom.json` | OOM kill |
| `db_connection_refused.json` | Database connectivity failure |
| `bad_gateway_502.json` | Upstream 502 errors |

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM inference | [Ollama](https://ollama.com) (llama3.2) |
| LLM orchestration | [LangChain](https://python.langchain.com) |
| Vector database | [ChromaDB](https://www.trychroma.com) |
| Embeddings | nomic-embed-text (via Ollama) |
| UI | [Streamlit](https://streamlit.io) |
| Alert source | OpenSRE CLI |
