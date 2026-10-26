"""Step 6d: same incident details -> base model vs fine-tuned model."""
from langchain_ollama import ChatOllama

import sys
sys.path.append("..")
sys.path.append(".")
from config import BASE_SUMMARY_MODEL, OLLAMA_URL, SUMMARY_MODEL

SYSTEM = "You write incident summaries in our team style. Be short and factual."
DETAILS = ("Alert: 502 Bad Gateway on cart-service. Started 13:45 UTC, resolved after 18 min. "
           "Root cause: new cart-service release v3.2.0 had a readiness probe timeout of 1s, so pods were not Ready. "
           "Impact: 27% of API calls returned 502. Fix: Rolled back cart-service to v3.1.9. Owner: @core-api-oncall.")

for name in (BASE_SUMMARY_MODEL, SUMMARY_MODEL):
    llm = ChatOllama(model=name, base_url=OLLAMA_URL, temperature=0.2)
    print("=" * 25, name, "=" * 25)
    print(llm.invoke([("system", SYSTEM), ("human", DETAILS)]).content, "\n")
