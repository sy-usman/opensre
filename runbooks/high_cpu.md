# Runbook: High CPU usage
Symptoms: CPU above 90% for 5+ minutes, latency rising, CPU throttling.
Likely causes: traffic spike, hot loop or bad query after deploy, missing autoscaling.
Fix steps:
1. Compare traffic vs CPU graph: traffic spike or code change?
2. Scale out quickly: kubectl scale deploy/<service> --replicas=<n+2>, or check the HPA.
3. If it started after a deploy: kubectl rollout undo deploy/<service>.
4. Profile the hot endpoint or slow DB query.
Verify: CPU below 70%, p95 latency normal.
Escalate: service owner.
