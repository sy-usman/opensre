# Runbook: Pod CrashLoopBackOff
Symptoms: pod restarts many times, status CrashLoopBackOff, exit code 1 on startup.
Likely causes: missing env var/secret/config, bad image or startup command, dependency not reachable at boot.
Fix steps:
1. Read crash logs: kubectl logs <pod> --previous.
2. If missing env var/secret: compare deployment env with the previous version; add the missing value to the ConfigMap/Secret.
3. If the crash started right after a deploy: kubectl rollout undo deploy/<service>.
4. Re-apply the fixed config and watch: kubectl rollout status deploy/<service>.
Verify: restarts stop, pod Running and Ready for 10 minutes.
Escalate: service owner team.
