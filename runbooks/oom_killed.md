# Runbook: Container OOMKilled / high memory
Symptoms: exit code 137, reason OOMKilled, memory near limit, repeated restarts.
Likely causes: memory limit too low, memory leak, loading too much data at once, new feature increasing memory use.
Fix steps:
1. Confirm OOM: kubectl describe pod <pod> | grep -i -A3 "last state".
2. Check what changed: recent deploys or feature flags; disable the suspect flag first (fastest mitigation).
3. Short-term: raise memory limit (e.g. 512Mi -> 1Gi): kubectl set resources deploy/<app> --limits=memory=1Gi.
4. Long-term: process data in batches/streams instead of loading all rows; add memory profiling.
5. Add an alert at 80% memory to catch it earlier.
Verify: no OOMKilled for 30 minutes, memory stable below 70%.
Escalate: owning team if a leak is suspected.
