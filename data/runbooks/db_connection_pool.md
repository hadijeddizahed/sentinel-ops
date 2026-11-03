# Runbook: PostgreSQL Database Connection Pool Exhaustion

## Error Code: ERR-DB-POOL / CONNECTION_TIMEOUT

### Symptoms
- Active connections reach capacity (`active_connections >= max_pool_connections` 100/100).
- Incoming microservice requests wait in FIFO queue and fail after 5000ms timeout.
- Client applications return HTTP 500 or HTTP 503 Internal Server Error.

### Immediate Mitigation Steps
1. Identify and kill long-running idle transactions:
   ```sql
   SELECT pg_terminate_backend(pid) 
   FROM pg_stat_activity 
   WHERE state = 'idle in transaction' 
     AND state_change < current_timestamp - INTERVAL '5 minutes';
   ```
2. Verify if a rogue batch job or unindexed query is locking database tables.
3. Temporarily increase PgBouncer pool ceiling by 20% if memory headroom permits.
4. If primary node is unresponsive, trigger Patroni failover to the synchronous read-replica.

