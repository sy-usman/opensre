# Runbook: 502 Bad Gateway at ingress / load balancer
Symptoms: 502 spike at nginx/ALB, "upstream prematurely closed connection" or "no live upstreams".
Likely causes: upstream pods not Ready, failing readiness probe, bad deploy, upstream timeouts too low, pods crashing.
Fix steps:
1. Check upstream pods: kubectl get pods -l app=<service> and look at the READY column.
2. Check readiness probe failures: kubectl describe pod <pod> (Events section).
3. If a deploy happened just before: kubectl rollout undo deploy/<service> (fastest fix).
4. If the probe timeout is too strict (e.g. 1s), increase timeoutSeconds to 3-5s.
5. Check ingress logs for which upstream IP fails; delete the bad pod if only one is failing.
Verify: 502 rate below 0.5%, all pods Ready.
Escalate: service owner if rollback does not help in 10 minutes.
