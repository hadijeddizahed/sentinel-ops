# Runbook: Kubernetes Container OOMKilled (Exit Code 137)

## Error Code: ERR-KUBE-137 / OOMKILLED

### Symptoms
- Pod terminated abruptly with status `OOMKilled` and exit code `137`.
- Container transitions into `CrashLoopBackOff`.
- Linux kernel cgroups killed the container process due to memory consumption exceeding limit.

### Immediate Mitigation Steps
1. Inspect the last termination state and kernel kill reason:
   ```bash
   kubectl describe pod <pod-name> -n production | grep -A 5 "Last State"
   ```
2. Verify memory metrics in Grafana prior to the crash.
3. Temporarily increase container memory limit in the Helm deployment manifest by 50% (e.g. 512Mi -> 768Mi).
4. Profile container for Java heap or Python object leaks if memory continues rising monotonically.

