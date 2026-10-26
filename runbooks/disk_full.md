# Runbook: Disk full / node disk pressure
Symptoms: "No space left on device", node condition DiskPressure, pods Evicted or Pending.
Likely causes: logs not rotated, large temp files, old container images, growing database volume.
Fix steps:
1. Find the node: kubectl describe node <node> | grep -i pressure.
2. Clean old images: crictl rmi --prune.
3. Rotate or delete large logs in /var/log.
4. For DB volumes: expand the PVC size.
5. Cordon the node if it keeps filling: kubectl cordon <node>.
Verify: disk usage below 80%, DiskPressure False, pods scheduled.
Escalate: platform team.
