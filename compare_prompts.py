"""Step 4: run the SAME root cause through a bad prompt and a good prompt, side by side."""
from langchain_ollama import ChatOllama

from config import CHAT_MODEL, OLLAMA_URL
from prompts import BAD_PROMPT
from rag_assistant import fix_plan

ROOT_CAUSE = "report-worker OOMKilled (exit 137) at 512Mi limit after feature flag monthly_report_v2 enabled"

llm = ChatOllama(model=CHAT_MODEL, base_url=OLLAMA_URL, temperature=0)

print("=" * 30, "BAD PROMPT", "=" * 30)
print(llm.invoke(BAD_PROMPT.format(root_cause=ROOT_CAUSE)).content)

print("\n" + "=" * 30, "GOOD PROMPT (system + few-shot + RAG)", "=" * 30)
print(fix_plan(ROOT_CAUSE)["plan"])
