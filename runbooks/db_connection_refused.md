# Runbook: Database connection refused
Symptoms: "connection refused" on DB port (5432/3306), app error rate spikes, DB has 0 active connections.
Likely causes: DB pod/instance down, DB pod Pending (node pressure), wrong host/port after config change, network policy blocking.
Fix steps:
1. Check DB is running: kubectl get pods -l app=<db> -n <ns> (or cloud console status).
2. If Pending/CrashLoop: kubectl describe pod <db-pod> and fix node pressure (free disk, move to healthy node).
3. Verify port open from app pod: kubectl exec <app-pod> -- nc -zv <db-host> 5432.
4. Check recent config/secret change for DB_HOST/DB_PORT; roll back if wrong.
5. Once DB is up, restart app pods to reset connection pools: kubectl rollout restart deploy/<app>.
Verify: error rate back below 1%, DB active_connections > 0.
Escalate: DBA on-call if DB does not start in 15 minutes.
