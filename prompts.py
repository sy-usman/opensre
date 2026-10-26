"""Step 4: Prompt engineering. A bad prompt vs a good prompt (system prompt + few-shot)."""

BAD_PROMPT = "Fix this: {root_cause}"

GOOD_SYSTEM_PROMPT = """You are an SRE assistant. You turn a root cause and a runbook into a fix plan.
Rules:
- Use ONLY the runbook text given. If the runbook does not cover it, write "Not in runbook".
- Output EXACTLY this format, nothing before or after:
RUNBOOK: <runbook file name>
SEVERITY: <SEV1|SEV2|SEV3>
IMMEDIATE ACTION (first 5 min):
1. ...
FIX STEPS:
1. ...
2. ...
3. ...
VERIFY:
- ...
ESCALATE IF:
- ...
- Max 5 fix steps. Each step is one line and starts with a verb. Keep real commands in backticks."""

# Few-shot examples teach the model the exact shape we want.
FEW_SHOT = [
    (
        "ROOT CAUSE: Node disk full on worker-3, pods evicted.\n"
        "RUNBOOK (disk_full.md): 1. Find the node... 2. Clean old images: crictl rmi --prune ... "
        "Verify: disk usage below 80%. Escalate: platform team.",
        "RUNBOOK: disk_full.md\n"
        "SEVERITY: SEV2\n"
        "IMMEDIATE ACTION (first 5 min):\n"
        "1. Cordon worker-3: `kubectl cordon worker-3`\n"
        "FIX STEPS:\n"
        "1. Confirm pressure: `kubectl describe node worker-3 | grep -i pressure`\n"
        "2. Clean old images: `crictl rmi --prune`\n"
        "3. Rotate large logs in /var/log\n"
        "VERIFY:\n"
        "- Disk below 80% and DiskPressure False\n"
        "ESCALATE IF:\n"
        "- Disk still above 90% after 15 minutes -> platform team",
    ),
    (
        "ROOT CAUSE: CPU 97% on search-api after v5 deploy.\n"
        "RUNBOOK (high_cpu.md): 1. Compare traffic vs CPU... 2. Scale out... 3. If after deploy: rollback... "
        "Verify: CPU below 70%. Escalate: service owner.",
        "RUNBOOK: high_cpu.md\n"
        "SEVERITY: SEV2\n"
        "IMMEDIATE ACTION (first 5 min):\n"
        "1. Roll back: `kubectl rollout undo deploy/search-api`\n"
        "FIX STEPS:\n"
        "1. Check traffic vs CPU graph to confirm deploy is the cause\n"
        "2. Scale out if needed: `kubectl scale deploy/search-api --replicas=5`\n"
        "3. Profile the hot endpoint in v5 before redeploying\n"
        "VERIFY:\n"
        "- CPU below 70% and p95 latency normal\n"
        "ESCALATE IF:\n"
        "- CPU stays high after rollback -> service owner",
    ),
]


def good_messages(root_cause: str, runbook_name: str, runbook_text: str) -> list[tuple[str, str]]:
    msgs = [("system", GOOD_SYSTEM_PROMPT)]
    for user, assistant in FEW_SHOT:
        msgs += [("human", user), ("ai", assistant)]
    msgs.append(("human", f"ROOT CAUSE: {root_cause}\nRUNBOOK ({runbook_name}):\n{runbook_text}"))
    return msgs
