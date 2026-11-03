# Runbook: Kafka Consumer Lag & Queue Backlog

## Error Code: ERR-KAFKA-LAG / CONSUMER_TIMEOUT

### Symptoms
- Consumer lag on topic `payments.transactions` exceeds 50,000 unread messages.
- End-to-end payment processing latency jumps from 200ms to > 15 seconds.
- Downstream microservices experience starved input queues.

### Immediate Mitigation Steps
1. Check Kafka partition rebalancing events in consumer logs:
   ```bash
   kubectl logs -f deployment/payment-consumer -n production | grep -i "rebalance"
   ```
2. Verify if a consumer pod crashed or is stuck in garbage collection pauses.
3. Scale out the consumer group pod replicas to match partition count (e.g., 12 partitions = 12 pods):
   ```bash
   kubectl scale deployment/payment-consumer --replicas=12 -n production
   ```
4. If a poison-pill message is blocking the partition offset, route it to the Dead Letter Queue (`payments.dlq`).

