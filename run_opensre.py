"""Run OpenSRE on alert JSON files and save the report text.

Usage:
    python run_opensre.py                       # all alerts in alerts/
    python run_opensre.py alerts/high_memory_oom.json
"""
import shutil
import subprocess
import sys
from pathlib import Path

from config import ALERT_DIR, REPORT_DIR

PROMPT = (
    "Investigate the attached alert like an SRE. Reply with these headings: "
    "Root cause, Evidence, Affected service, Severity, Suggested next checks. "
    "Use only facts from the alert."
)


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=900,
                          env={**__import__("os").environ, "NO_COLOR": "1"})


def investigate(alert_path: str) -> str:
    """Return OpenSRE's report for one alert file."""
    if shutil.which("opensre") is None:
        raise RuntimeError("opensre not found. Open a new terminal or check PATH (Step 2).")

    # New CLI (current main): headless 'ask' with the alert attached as a context file.
    result = _run(["opensre", "ask", PROMPT, "-i", alert_path, "--ephemeral"])

    # Older builds (the README you may have seen): 'investigate -i <file>'.
    if result.returncode != 0 and "No such command" in (result.stderr + result.stdout):
        result = _run(["opensre", "investigate", "-i", alert_path])

    if result.returncode != 0:
        raise RuntimeError(f"OpenSRE failed:\n{result.stderr or result.stdout}")
    return result.stdout.strip()


def save_report(alert_path: str, report: str) -> Path:
    out = Path(REPORT_DIR) / (Path(alert_path).stem + ".md")
    out.parent.mkdir(exist_ok=True)
    out.write_text(report, encoding="utf-8")
    return out


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(str(p) for p in Path(ALERT_DIR).glob("*.json"))
    for p in paths:
        print(f"\n=== Investigating {p} (CPU model, can take 1-5 min) ===")
        try:
            report = investigate(p)
            print(report)
            print(f"-> saved to {save_report(p, report)}")
        except Exception as e:  # keep going with the next alert
            print(f"ERROR: {e}")
