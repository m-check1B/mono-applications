# Queue-Core E2E Tests

## Overview

This directory contains comprehensive end-to-end tests for the RabbitMQ adapter and its integration with platform services.

## Test Suites

### 1. `rabbitmq.adapter.e2e.test.ts`
Comprehensive tests for RabbitMQ adapter functionality:

- **Basic Connectivity**: Connection establishment, topology setup, multiple connections
- **Message Publishing/Consumption**: Exchange routing, direct queue messaging, priority handling
- **Call Center Workflows**: Inbound calls, transcription events, AI processing requests
- **Error Handling**: Consumer errors, nack/requeue, dead letter queue
- **Multi-Step Workflows**: Sequential processing, parallel processing with fanout
- **Performance**: High throughput, message ordering, queue statistics
- **Correlation & Tracking**: Correlation IDs, metadata preservation
- **Event Integration**: Message lifecycle events, consumer lifecycle

**Test Coverage**: 13 test groups, 25+ individual tests

### 2. `platform-integration.e2e.test.ts`
Integration tests with other platform services:

- **Auth-Core Integration**: Authentication events, JWT validation, authorization failures, event correlation
- **Events-Core Integration**: Platform events, fan-out patterns, event replay
- **Cross-Service Error Handling**: Service unavailability, circuit breaker, retry with exponential backoff
- **Service Mesh Communication**: Message routing, request-reply pattern
- **Monitoring & Observability**: Metrics tracking, monitoring events

**Test Coverage**: 5 test groups, 15+ individual tests

## Prerequisites

### Running Tests Locally

1. **Start RabbitMQ**:
   ```bash
   docker run -d --name rabbitmq-test \
     -p 5672:5672 \
     -p 15672:15672 \
     rabbitmq:3-management
   ```

2. **Set Environment Variable**:
   ```bash
   export RABBITMQ_URL=amqp://localhost:5672
   ```

3. **Run Tests**:
   ```bash
   # From queue-core directory
   pnpm test

   # Run specific suite
   pnpm test rabbitmq.adapter.e2e

   # Run with coverage
   pnpm test --coverage

   # Watch mode
   pnpm test:watch
   ```

### CI/CD Environment

Tests automatically skip if RabbitMQ is not available (non-blocking for CI).

Set `RABBITMQ_URL` in CI environment or use docker-compose:

```yaml
# .github/workflows/test.yml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - 5672:5672
    env:
      RABBITMQ_DEFAULT_USER: test
      RABBITMQ_DEFAULT_PASS: test
```

## Test Scenarios

### Critical Path Tests

1. **Message Flow**: Publish → Route → Consume → Ack
2. **Error Recovery**: Failure → Nack → Requeue → Success
3. **Dead Letter**: Rejection → DLX → Dead Letter Queue
4. **Workflow**: Step1 → Step2 → Step3 (sequential)
5. **Fan-out**: Publish → Multiple Consumers (parallel)

### Integration Tests

1. **Auth Events**: Login → Token Validation → Call Authorization
2. **Platform Events**: Config Change → Service Fan-out → All Services Updated
3. **Circuit Breaker**: Failures → Threshold → Circuit Open → Fast Fail
4. **Request-Reply**: Request + ReplyTo → Process → Reply

## Performance Expectations

- **Throughput**: 100 messages/second (local testing)
- **Latency**: < 100ms per message (p95)
- **Ordering**: Sequential when prefetch=1
- **Priority**: Higher priority processed first
- **Reliability**: No message loss with persistence

## Troubleshooting

### Connection Refused
```bash
# Check if RabbitMQ is running
docker ps | grep rabbitmq

# Check RabbitMQ logs
docker logs rabbitmq-test
```

### Tests Timing Out
```bash
# Increase timeout in test file
const TEST_TIMEOUT = 60000; // 60 seconds

# Or skip long-running tests
pnpm test --testTimeout=60000
```

### Queue Not Found
```bash
# Clean up test queues
docker exec rabbitmq-test rabbitmqctl list_queues
docker exec rabbitmq-test rabbitmqctl purge_queue test-queue
```

## Coverage Goals

- **Line Coverage**: > 80%
- **Branch Coverage**: > 75%
- **Function Coverage**: > 80%

Current coverage:
```bash
pnpm test --coverage
```

## Adding New Tests

1. Create test in appropriate suite file
2. Follow existing patterns (arrange, act, assert)
3. Clean up resources in afterEach/afterAll
4. Use appropriate timeouts
5. Add descriptive test names

Example:
```typescript
it('should handle new scenario', async () => {
  // Arrange
  const testData = { ... };
  await adapter.createQueue('test-queue');

  // Act
  await adapter.sendToQueue('test-queue', testData);

  // Assert
  const stats = await adapter.getQueueStats('test-queue');
  expect(stats.messageCount).toBe(1);

  // Cleanup
  await adapter.purgeQueue('test-queue');
}, TEST_TIMEOUT);
```

## Related Documentation

- [RabbitMQ Adapter Documentation](../adapters/rabbitmq.adapter.ts)
- [Queue Types](../types/queue.types.ts)
- [Platform Integration Guide](/docs/PLATFORM_INTEGRATION.md)
