"""Step 7: Streamlit UI. Alert -> OpenSRE report -> RAG fix plan -> fine-tuned summary."""
import json
from pathlib import Path

import streamlit as st
from langchain_ollama import ChatOllama

from config import ALERT_DIR, CHAT_MODEL, OLLAMA_URL, REPORT_DIR, SUMMARY_MODEL
from rag_assistant import fix_plan
from run_opensre import investigate, save_report

st.set_page_config(page_title="Local SRE", page_icon="🚨", layout="wide")
st.title("🚨 Local SRE – AI Incident Assistant")
st.caption("OpenSRE + Ollama + LangChain RAG + fine-tuned summary model, all running locally")

alerts = sorted(Path(ALERT_DIR).glob("*.json"))
choice = st.sidebar.selectbox("1. Select alert", alerts, format_func=lambda p: p.stem)
use_cache = st.sidebar.checkbox("Use saved OpenSRE report (faster demo)", value=True)
alert = json.loads(choice.read_text())

with st.expander("📟 Alert JSON", expanded=True):
    st.json(alert)

if st.sidebar.button("▶ Run pipeline", type="primary"):
    # ---- 1. OpenSRE investigation ----
    st.subheader("1️⃣ OpenSRE investigation report")
    cached = Path(REPORT_DIR) / f"{choice.stem}.md"
    if use_cache and cached.exists():
        report = cached.read_text(encoding="utf-8")
        st.info(f"Loaded saved report: {cached}")
    else:
        with st.spinner("OpenSRE is investigating with Ollama (CPU: 1-5 min)..."):
            try:
                report = investigate(str(choice))
                save_report(str(choice), report)
            except Exception as e:
                st.error(str(e))
                st.stop()
    st.markdown(report)

    # ---- 2. RAG fix plan ----
    st.subheader("2️⃣ Fix steps from runbooks (RAG)")
    root_cause = f"{alert['alert_name']}. {alert['annotations'].get('summary', '')}\n{report[:1500]}"
    with st.spinner("Searching runbooks in ChromaDB and writing fix plan..."):
        rag = fix_plan(root_cause)
    st.caption(f"Matched runbook: **{rag['runbook']}** · candidates: {rag['candidates']}")
    st.code(rag["plan"], language="markdown")

    # ---- 3. Fine-tuned summary ----
    st.subheader("3️⃣ Incident summary (fine-tuned model)")
    details = (f"Alert: {alert['alert_name']} on {alert['labels'].get('service')}. "
               f"Started {alert['startsAt']}. Root cause and evidence: {report[:800]} "
               f"Fix plan: {rag['plan'][:600]}")
    try:
        llm = ChatOllama(model=SUMMARY_MODEL, base_url=OLLAMA_URL, temperature=0.2)
        summary = llm.invoke(details).content
        model_used = SUMMARY_MODEL
    except Exception:
        llm = ChatOllama(model=CHAT_MODEL, base_url=OLLAMA_URL, temperature=0.2)
        summary = llm.invoke("Write a 6-line incident summary:\n" + details).content
        model_used = f"{CHAT_MODEL} (fallback: fine-tuned model not loaded)"
    st.success(summary)
    st.caption(f"Model: {model_used}")
else:
    st.info("👈 Select an alert and click **Run pipeline**.")
