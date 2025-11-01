# Production Rollout - Quick Reference Guide

**⚡ Quick action guide for enabling feature flags in production**

## 🎯 Objective

Enable 6 feature flags in production following a staged rollout sequence.

## ⏱️ Timeline

- **Phase 1**: Database Migrations (15-30 min)
- **Phase 2**: API Features (30 min + 15 min monitoring)
- **Phase 3**: UI Features (30 min + 15 min monitoring)
- **Phase 4**: Notifications (30 min + 30 min monitoring)
- **Phase 5**: Smoke Tests (1 hour)
- **Phase 6**: 24-hour monitoring

**Total**: 2-4 hours active work + 24 hours monitoring

## 🚦 Pre-Flight Checks

```bash
# 1. Backend health
curl https://felix-hub-backend.onrender.com/health
# Expected: {"status": "ok"}

# 2. Frontend accessible
curl -I https://felix-hub-mechanics-frontend.onrender.com
# Expected: 200 OK

# 3. Current feature flags (should all be false)
curl https://felix-hub-backend.onrender.com/api/config/feature-flags
# Expected: All flags = false

# 4. Database backup (verify in Render dashboard)
# Dashboard → Database → Backups → Verify recent backup exists
```

## 📋 Phase 1: Database Migrations

### On Render Backend Service

```bash
# Open Shell in Render Dashboard → felix-hub-backend → Shell

cd /opt/render/project/src/felix_hub/backend

# Check migrations
python migrations/run_migrations.py status

# Apply migrations
python migrations/run_migrations.py apply

# Verify
echo "SELECT column_name FROM information_schema.columns WHERE table_name='orders' AND column_name='car_number';" | psql $DATABASE_URL
# Should return: car_number

# Restart service (or it will auto-restart)
```

✅ **Checkpoint**: Migrations applied, service restarted successfully

---

## 📋 Phase 2: Enable API Features

### 2A. Enable Car Number

**Render Dashboard** → `felix-hub-backend` → Environment

```
ENABLE_CAR_NUMBER=true
```

Click **Save Changes** → Service auto-restarts

**Wait**: 30 seconds

**Verify**:
```bash
curl https://felix-hub-backend.onrender.com/api/config/feature-flags | jq '.ENABLE_CAR_NUMBER'
# Expected: true
```

### 2B. Enable Part Categories

**Render Dashboard** → `felix-hub-backend` → Environment

```
ENABLE_PART_CATEGORIES=true
```

Click **Save Changes** → Service auto-restarts

**Wait**: 30 seconds

**Verify**:
```bash
curl https://felix-hub-backend.onrender.com/api/config/feature-flags | jq '.ENABLE_PART_CATEGORIES'
# Expected: true

curl https://felix-hub-backend.onrender.com/api/categories
# Expected: 200 OK with array
```

### 2C. Monitor

**Wait**: 15 minutes

**Check**:
- Logs: No errors
- Response time: Normal (< 1s)
- Error rate: < 1%

✅ **Checkpoint**: API features enabled and stable

---

## 📋 Phase 3: Enable UI Features

### 3A. Update Frontend Environment

**Render Dashboard** → `felix-hub-mechanics-frontend` → Environment

```
VITE_ENABLE_MECH_I18N=true
VITE_ENABLE_UI_REFRESH=true
```

Click **Save Changes**

### 3B. Trigger Rebuild

**Render Dashboard** → `felix-hub-mechanics-frontend` → Manual Deploy → Deploy latest commit

**Wait**: 5-10 minutes for build to complete

### 3C. Verify UI

Open in browser: `https://felix-hub-mechanics-frontend.onrender.com/mechanic/login`

**Quick Checks**:
- [ ] Page loads without errors
- [ ] Language switcher visible (if ENABLE_MECH_I18N)
- [ ] UI looks modernized (if ENABLE_UI_REFRESH)
- [ ] Can login successfully
- [ ] Dashboard loads
- [ ] No console errors (F12)

### 3D. Monitor

**Wait**: 15 minutes

**Check**:
- Console: No errors
- Performance: Page loads < 3s
- User reports: None

✅ **Checkpoint**: UI features enabled and functional

---

## 📋 Phase 4: Enable Notifications

### 4A. Verify Telegram Setup

**Render Dashboard** → `felix-hub-backend` → Environment

Verify these exist:
```
TELEGRAM_BOT_TOKEN=<your-token>
ADMIN_CHAT_IDS=<comma-separated-ids>
```

**Test bot**:
```bash
# Replace $BOT_TOKEN with actual token
curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/getMe"
# Expected: 200 OK with bot info
```

### 4B. Enable Admin Notifications

**Render Dashboard** → `felix-hub-backend` → Environment

```
ENABLE_TG_ADMIN_NOTIFS=true
```

Click **Save Changes** → Service auto-restarts

**Wait**: 30 seconds

**Test**: Create a test order and verify admin receives Telegram notification

### 4C. Enable Mechanic Notifications

**Render Dashboard** → `felix-hub-backend` → Environment

```
ENABLE_TG_MECH_NOTIFS=true
```

Click **Save Changes** → Service auto-restarts

**Wait**: 30 seconds

**Test**: Update order status and verify mechanic receives Telegram notification

### 4D. Monitor

**Wait**: 30 minutes

**Check**:
- Notifications arriving within 5 seconds
- No Telegram API errors in logs
- Backend performance stable

✅ **Checkpoint**: Notifications enabled and working

---

## 📋 Phase 5: Smoke Tests

### Critical Path Test

1. **Create Order** (via Telegram bot or API)
   - Include car number
   - Select categorized part
   - Verify admin notification received

2. **View in Dashboard**
   - Login to mechanic interface
   - Find order in list
   - Verify car number displayed
   - Verify category displayed
   - Check UI refresh applied

3. **Update Status**
   - Change status to "In Progress"
   - Verify mechanic notification received (if mechanic has Telegram)

4. **Language Test**
   - Switch language in mechanic UI
   - Verify translations work
   - Switch back to default

5. **Complete Order**
   - Mark as completed
   - Verify notification sent
   - Verify order shows in completed filter

### Performance Check

```bash
# Response time test
time curl https://felix-hub-backend.onrender.com/api/orders
# Should complete in < 1 second

# Frontend load test
# Open in browser with DevTools → Network tab
# Full page load should be < 3 seconds
```

✅ **Checkpoint**: All smoke tests passed

---

## 📋 Phase 6: 24-Hour Monitoring

### Hour 1-2 (Check every 15 min)

```bash
# Health check
curl https://felix-hub-backend.onrender.com/health

# Feature flags
curl https://felix-hub-backend.onrender.com/api/config/feature-flags

# Check logs in Render Dashboard
# Look for errors or warnings
```

### Hour 3-12 (Check every 1-2 hours)

- Logs: No increase in errors
- Performance: Response times stable
- Notifications: Being sent successfully
- Users: No complaints

### Hour 13-24 (Check every 4-6 hours)

- System: Stable
- Metrics: Normal
- Alerts: None

✅ **Checkpoint**: System stable for 24 hours

---

## 🆘 Emergency Rollback

### Quick Disable All Features

**Render Dashboard** → `felix-hub-backend` → Environment

```
ENABLE_CAR_NUMBER=false
ENABLE_PART_CATEGORIES=false
ENABLE_TG_ADMIN_NOTIFS=false
ENABLE_TG_MECH_NOTIFS=false
```

**Render Dashboard** → `felix-hub-mechanics-frontend` → Environment

```
VITE_ENABLE_MECH_I18N=false
VITE_ENABLE_UI_REFRESH=false
```

Click **Save Changes** on both services

**Time to rollback**: < 2 minutes

### Rollback Migrations (if needed)

```bash
# On Render backend shell
cd /opt/render/project/src/felix_hub/backend
python migrations/run_migrations.py rollback
```

### Verify Rollback

```bash
# All flags should be false
curl https://felix-hub-backend.onrender.com/api/config/feature-flags

# Health check
curl https://felix-hub-backend.onrender.com/health
```

---

## 📊 Success Criteria Checklist

At the end of 24 hours, all should be ✅:

- [ ] All 6 feature flags enabled
- [ ] Zero downtime during rollout
- [ ] Error rate < 1%
- [ ] API latency increase < 10%
- [ ] Notifications delivered within 5 seconds
- [ ] All smoke tests passed
- [ ] No critical errors in logs
- [ ] No user complaints about major issues

---

## 📞 When to Call for Help

**Immediate Escalation**:
- ❌ Service is down (health check fails)
- ❌ Error rate > 5%
- ❌ Data loss detected
- ❌ Database connection failures

**Investigation Needed**:
- ⚠️ Error rate > 2%
- ⚠️ API response time > 2s
- ⚠️ Notifications not sending
- ⚠️ User reports of issues

**Contact**: See PRODUCTION_ROLLOUT_PLAN.md for contact details

---

## 🔗 Full Documentation

For detailed procedures, see: **PRODUCTION_ROLLOUT_PLAN.md**
