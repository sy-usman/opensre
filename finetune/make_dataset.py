"""Step 6a: generate 40 training examples (incident details -> team-style incident summary).
Output: finetune/incident_summaries.jsonl in chat 'messages' format (works with Unsloth)."""
import json
import random
from pathlib import Path

random.seed(7)
SYSTEM = "You write incident summaries in our team style. Be short and factual."

# (type, cause template, impact template, fix template, follow-up, sev)
TYPES = [
    ("Database connection refused", "{dep} was down ({why}), so {svc} could not open connections on port 5432",
     "{pct}% of requests to {svc} failed", "Restored {dep} and restarted {svc} pods", "Add alert on DB pod Pending state", "SEV1"),
    ("OOMKilled", "{svc} loaded too much data in memory and hit its {mem} limit",
     "jobs in {svc} restarted {n} times, reports delayed", "Disabled the new flag and raised memory limit to 1Gi", "Process rows in batches instead of loading all at once", "SEV2"),
    ("502 Bad Gateway", "new {svc} release had a readiness probe timeout of 1s, so pods were not Ready",
     "{pct}% of API calls returned 502", "Rolled back {svc} to the previous version", "Raise probe timeout to 3s and test it in staging", "SEV1"),
    ("CrashLoopBackOff", "{svc} release was missing the env var {env}",
     "{svc} was unavailable for {mins} minutes", "Added {env} to the ConfigMap and redeployed", "Add a startup check for required env vars in CI", "SEV2"),
    ("High CPU", "a slow query in the new {svc} release caused CPU to stay at {pct2}%",
     "p95 latency on {svc} went up {x}x", "Rolled back and scaled {svc} to 5 replicas", "Add an index and load-test the query", "SEV3"),
    ("Disk full", "logs on {node} were not rotated and the disk reached 100%",
     "pods on {node} were evicted, {svc} ran with reduced capacity", "Cleaned old images and rotated logs, uncordoned {node}", "Enable log rotation on all nodes", "SEV3"),
]
SERVICES = ["orders-service", "checkout-api", "cart-service", "report-worker", "search-api", "billing-api", "user-service"]
DEPS = ["orders-db", "billing-db", "users-db"]
TEAMS = ["@payments-oncall", "@platform-oncall", "@core-api-oncall"]


def cap(s):
    return s[:1].upper() + s[1:]


def make_example(t):
    name, cause, impact, fix, follow, sev = t
    v = dict(svc=random.choice(SERVICES), dep=random.choice(DEPS), why=random.choice(["pod Pending due to disk pressure", "instance restarted"]),
             pct=random.choice([12, 27, 38, 54]), pct2=random.choice([92, 97, 99]), mem=random.choice(["512Mi", "256Mi"]),
             n=random.randint(3, 9), env=random.choice(["PAYMENT_API_URL", "REDIS_HOST", "JWT_SECRET"]),
             mins=random.choice([8, 14, 22]), x=random.choice([3, 5]), node=f"worker-{random.randint(1, 6)}")
    start = f"{random.randint(0, 23):02d}:{random.choice(['05', '12', '30', '45'])}"
    dur = random.choice([9, 18, 25, 41])
    owner = random.choice(TEAMS)
    details = (f"Alert: {name} on {v['svc']}. Started {start} UTC, resolved after {dur} min. "
               f"Root cause: {cause.format(**v)}. Impact: {impact.format(**v)}. "
               f"Fix: {fix.format(**v)}. Owner: {owner}.")
    summary = (f"[{sev}] {name} - {v['svc']}\n"
               f"What happened: {cap(impact.format(**v))}.\n"
               f"Why: {cap(cause.format(**v))}.\n"
               f"Fix: {fix.format(**v)}.\n"
               f"Duration: {dur} min (from {start} UTC)\n"
               f"Follow-up: {follow}.\n"
               f"Owner: {owner}")
    return {"messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": details},
                         {"role": "assistant", "content": summary}]}


rows = [make_example(t) for t in TYPES for _ in range(7)][:40]
random.shuffle(rows)
out = Path(__file__).parent / "incident_summaries.jsonl"
out.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
print(f"Wrote {len(rows)} examples to {out}")
print("Example output:\n" + rows[0]["messages"][2]["content"])
