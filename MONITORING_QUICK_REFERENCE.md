# Monitoring Quick Reference

## 🚀 Quick Start

### Check Overall Health
```bash
curl https://your-app.com/health
```

### View Dashboard
```bash
curl https://your-app.com/api/metrics/dashboard
```

### Check Notification Success Rate
```bash
curl https://your-app.com/api/metrics/notifications/success-rate?hours=24
```

## 📊 Key Metrics Endpoints

| Endpoint | Purpose | Key Threshold |
|----------|---------|---------------|
| `/health` | Overall health status | 200 = healthy, 503 = unhealthy |
| `/api/metrics/notifications/success-rate` | Notification reliability | Target: >99% |
| `/api/metrics/alerts` | Active alert conditions | 0 alerts = healthy |
| `/api/metrics/dashboard` | Complete overview | - |

## 🔍 Log Search Patterns

### Track a Request
```bash
grep "requestId=a1b2c3d4" felix_hub.log
```

### Find Failed Notifications
```bash
grep "DEAD_LETTER" felix_hub.log
```

### Track Order Flow
```bash
grep "orderId=123" felix_hub.log
```

### Circuit Breaker Events
```bash
grep "Circuit breaker.*OPEN" felix_hub.log
```

## 🚨 Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Notification Success Rate | 95-99% | <95% |
| Stuck Orders (>24h) | Any | - |
| Notification Failures/hour | - | ≥10 |
| Circuit Breaker | - | OPEN |

## 📈 Example Queries

### Last 7 Days Order Trend
```bash
curl https://your-app.com/api/metrics/orders/daily?days=7
```

### Recent Notification Failures
```bash
curl https://your-app.com/api/metrics/notifications/failures?hours=1
```

### Circuit Breaker Status
```bash
curl https://your-app.com/api/metrics/circuit-breakers
```

### Today's Summary
```bash
curl https://your-app.com/api/metrics/summary
```

## 🔧 Troubleshooting

### High Failure Rate
1. Check circuit breaker: `/api/metrics/circuit-breakers`
2. Review failures: `/api/metrics/notifications/failures?hours=1`
3. Verify Telegram bot token

### Circuit Breaker Open
1. Check external service (Telegram API)
2. Review recent errors in logs
3. Wait for automatic recovery (2 min timeout)

### Missing Metrics
1. Verify database connection: `/health`
2. Check NotificationLog table exists
3. Review app logs for errors

## 📝 Log Format

All logs include correlation IDs and context:
```
[requestId=a1b2c3d4] [orderId=123, mechanic_id=5] Order created successfully
```

## 🔔 Setting Up Alerts

### Render/Railway
Configure health check:
- Path: `/health`
- Healthy status: 200
- Unhealthy status: 503

### Log-Based Alerts
Search for:
- `DEAD_LETTER` - Permanent failures
- `Circuit breaker.*OPEN` - Service degradation
- `status:critical` - Critical alerts

## 💡 Quick Tips

1. **Daily Check**: View `/api/metrics/dashboard` each morning
2. **After Deploy**: Monitor for 1 hour, check success rate
3. **Incident Response**: Start with `/api/metrics/alerts`
4. **Debug Flow**: Use requestId to trace through logs
5. **Performance**: All metrics endpoints cache where possible

## 📚 Full Documentation

See `MONITORING_GUIDE.md` for comprehensive documentation.
