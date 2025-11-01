# Production Rollout - Documentation Index

**Quick navigation to all production rollout documentation and tools**

## 📚 Main Documentation

### Primary Guides

| Document | Purpose | Audience | Est. Time |
|----------|---------|----------|-----------|
| **[PRODUCTION_ROLLOUT_PLAN.md](PRODUCTION_ROLLOUT_PLAN.md)** | Complete step-by-step rollout procedure with detailed instructions | Ops Team, Tech Leads | 2-4 hours |
| **[ROLLOUT_QUICK_REFERENCE.md](ROLLOUT_QUICK_REFERENCE.md)** | Quick action guide - condensed version for experienced operators | Ops Team | 15 min |
| **[SMOKE_TEST_CHECKLIST.md](SMOKE_TEST_CHECKLIST.md)** | Comprehensive testing checklist for post-deployment verification | QA, Ops Team | 1 hour |

### Supporting Documentation

| Document | Purpose |
|----------|---------|
| **[FEATURE_FLAGS_GUIDE.md](FEATURE_FLAGS_GUIDE.md)** | Deep dive into feature flags system and usage |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | General deployment guide for all environments |
| **[DEPLOYMENT_CHECKLIST_MIGRATIONS.md](DEPLOYMENT_CHECKLIST_MIGRATIONS.md)** | Database migration procedures |
| **[QUICK_DEPLOYMENT_GUIDE.md](QUICK_DEPLOYMENT_GUIDE.md)** | Quick deployment steps for frontend |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Common issues and solutions |

---

## 🛠️ Tools & Scripts

### Verification & Monitoring

```bash
# Verify production rollout status
./verify_production_rollout.sh

# With custom URLs
./verify_production_rollout.sh --backend-url https://your-backend.com --frontend-url https://your-frontend.com
```

**What it checks:**
- ✅ Backend and frontend health
- ✅ All feature flags status
- ✅ API endpoints accessibility
- ✅ Response times
- ✅ Migration status information

### Rollback Tools

```bash
# Full rollback (disable all features)
./rollback_production_features.sh --full

# Partial rollback (specific features)
./rollback_production_features.sh --partial ENABLE_TG_ADMIN_NOTIFS,ENABLE_TG_MECH_NOTIFS

# Database migrations rollback only
./rollback_production_features.sh --migrations-only

# Show help
./rollback_production_features.sh --help
```

**What it provides:**
- 📋 Step-by-step rollback instructions for Render Dashboard
- ⚠️ Data loss warnings for migration rollbacks
- ✅ Post-rollback verification checklist

---

## 🚀 Quick Start: First-Time Rollout

**For operators performing the rollout for the first time:**

### Phase 0: Preparation (30 minutes)

1. **Read the documentation**
   - [ ] Read [PRODUCTION_ROLLOUT_PLAN.md](PRODUCTION_ROLLOUT_PLAN.md) completely
   - [ ] Review [ROLLOUT_QUICK_REFERENCE.md](ROLLOUT_QUICK_REFERENCE.md) for quick commands
   - [ ] Familiarize yourself with [SMOKE_TEST_CHECKLIST.md](SMOKE_TEST_CHECKLIST.md)

2. **Verify prerequisites**
   - [ ] Access to Render Dashboard (https://dashboard.render.com)
   - [ ] Access to Telegram for notification testing
   - [ ] Database backup completed and verified
   - [ ] Team members notified and available

3. **Baseline verification**
   ```bash
   # Run verification script to document baseline
   ./verify_production_rollout.sh
   ```

### Phase 1-6: Execute Rollout (2-4 hours)

Follow the detailed plan in [PRODUCTION_ROLLOUT_PLAN.md](PRODUCTION_ROLLOUT_PLAN.md):

- **Phase 1**: Database Migrations (15-30 min)
- **Phase 2**: Enable API Features (30 min + 15 min monitoring)
- **Phase 3**: Enable UI Features (30 min + 15 min monitoring)
- **Phase 4**: Enable Notifications (30 min + 30 min monitoring)
- **Phase 5**: Comprehensive Smoke Testing (1 hour)
- **Phase 6**: 24-Hour Monitoring

### Post-Rollout: Monitoring (24 hours)

Monitor using the guidelines in [PRODUCTION_ROLLOUT_PLAN.md - Phase 6](PRODUCTION_ROLLOUT_PLAN.md#-phase-6-24-hour-monitoring)

---

## 📊 Feature Flags Reference

### Complete List of Feature Flags

| Flag | Service | Default (Prod) | Purpose |
|------|---------|----------------|---------|
| `ENABLE_CAR_NUMBER` | Backend | OFF | Car number field in orders |
| `ENABLE_PART_CATEGORIES` | Backend | OFF | Categorized parts catalog |
| `ENABLE_TG_ADMIN_NOTIFS` | Backend | OFF | Telegram admin notifications |
| `ENABLE_TG_MECH_NOTIFS` | Backend | OFF | Telegram mechanic notifications |
| `VITE_ENABLE_MECH_I18N` | Frontend | OFF | Multi-language support |
| `VITE_ENABLE_UI_REFRESH` | Frontend | OFF | Modernized UI components |

### Enabling Feature Flags

**Backend (felix-hub-backend):**
```
Render Dashboard → felix-hub-backend → Environment → Add/Edit Variables
ENABLE_CAR_NUMBER=true
```

**Frontend (felix-hub-mechanics-frontend):**
```
Render Dashboard → felix-hub-mechanics-frontend → Environment → Add/Edit Variables
VITE_ENABLE_MECH_I18N=true
```

After saving, service auto-restarts (wait 30-60 seconds).

---

## 🗂️ Database Migrations

### Available Migrations

| Migration | Purpose | Rollback Risk |
|-----------|---------|---------------|
| `001_add_car_number_column.py` | Adds `car_number` to orders table | Low (column data lost) |
| `002_create_categories_parts_tables.py` | Creates categories and parts tables | Medium (tables dropped) |

### Running Migrations

**On Render (via Shell):**
```bash
cd /opt/render/project/src/felix_hub/backend

# Check status
python migrations/run_migrations.py status

# Apply all
python migrations/run_migrations.py apply

# Rollback all
python migrations/run_migrations.py rollback
```

**Locally:**
```bash
cd felix_hub/backend
python migrations/run_migrations.py apply
```

---

## 🔴 Emergency Procedures

### Critical Issue - Immediate Rollback

**Scenario**: System is down, critical errors, or severe performance degradation

**Action**: Follow emergency rollback in [PRODUCTION_ROLLOUT_PLAN.md - Emergency Rollback](PRODUCTION_ROLLOUT_PLAN.md#emergency-rollback-critical-issues)

**Quick commands**:
```bash
# Get rollback instructions
./rollback_production_features.sh --full

# This provides Render Dashboard instructions to:
# 1. Disable all feature flags
# 2. Rollback migrations if needed
# 3. Verify system recovery
```

**Time to recover**: < 2 minutes (feature flags) + 2-5 minutes (migrations if needed)

### Single Feature Issue - Partial Rollback

**Scenario**: One feature causing problems, others working fine

**Action**:
```bash
# Example: Disable only notification features
./rollback_production_features.sh --partial ENABLE_TG_ADMIN_NOTIFS,ENABLE_TG_MECH_NOTIFS
```

---

## ✅ Success Criteria

### At Completion (after 24 hours)

All must be ✅ to consider rollout successful:

- [ ] All 6 feature flags enabled in production
- [ ] Zero downtime during rollout
- [ ] Error rate < 1%
- [ ] API latency increase < 10% vs baseline
- [ ] Telegram notifications delivered within 5 seconds
- [ ] All smoke tests passed
- [ ] No critical errors in logs for 24 hours
- [ ] No user complaints about major issues
- [ ] Post-rollout report completed

---

## 📞 Support & Escalation

### When to Escalate

**Immediate Escalation (Critical)**:
- ❌ Service is down (health check fails)
- ❌ Error rate > 5%
- ❌ Data loss detected
- ❌ Database connection failures

**Investigation Needed (High)**:
- ⚠️ Error rate > 2%
- ⚠️ API response time > 2s (p95)
- ⚠️ Notifications not being sent
- ⚠️ Multiple user reports of issues

### Resources

**Documentation**:
- Technical issues: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Feature flags: See [FEATURE_FLAGS_GUIDE.md](FEATURE_FLAGS_GUIDE.md)
- Deployment: See [DEPLOYMENT.md](DEPLOYMENT.md)

**External Resources**:
- Render Status: https://status.render.com
- Render Docs: https://render.com/docs
- Telegram API Status: https://telegram.org/status

---

## 📝 Reporting & Documentation

### During Rollout

**Keep a log of**:
- Start/end time of each phase
- Any errors or warnings encountered
- Response times and metrics at each checkpoint
- Decisions made and reasons

### Post-Rollout

**Complete**:
- Post-Rollout Report (template in [PRODUCTION_ROLLOUT_PLAN.md](PRODUCTION_ROLLOUT_PLAN.md))
- Update this index if procedures changed
- Document lessons learned
- Share with team in retrospective

---

## 🔄 Rollout Sequence Diagram

```
START
  ↓
[Pre-Flight Checks] ← verify_production_rollout.sh
  ↓
[Phase 1: Database Migrations]
  ├─ 001_add_car_number_column
  └─ 002_create_categories_parts_tables
  ↓
[Phase 2: API Features]
  ├─ ENABLE_CAR_NUMBER
  └─ ENABLE_PART_CATEGORIES
  ↓ (15 min monitoring)
[Phase 3: UI Features]
  ├─ VITE_ENABLE_MECH_I18N
  └─ VITE_ENABLE_UI_REFRESH
  ↓ (15 min monitoring)
[Phase 4: Notifications]
  ├─ ENABLE_TG_ADMIN_NOTIFS
  └─ ENABLE_TG_MECH_NOTIFS
  ↓ (30 min monitoring)
[Phase 5: Smoke Tests] ← SMOKE_TEST_CHECKLIST.md
  ↓
[Phase 6: 24h Monitoring]
  ↓
[Success] → Complete Post-Rollout Report
  ↓
END

(At any point if issues occur)
  → [Rollback] ← rollback_production_features.sh
```

---

## 📅 Recommended Rollout Schedule

**Best Time for Production Rollout**:
- ✅ Off-peak hours (e.g., 10 PM - 2 AM local time)
- ✅ Mid-week (Tuesday-Thursday) - easier to get support if needed
- ✅ When full team is available for monitoring
- ✅ When customer support team is prepared
- ❌ Avoid Friday afternoon/evening
- ❌ Avoid right before holidays or weekends
- ❌ Avoid during known high-traffic periods

---

## 🎓 Training Resources

**For new team members**:
1. Start with [FEATURE_FLAGS_GUIDE.md](FEATURE_FLAGS_GUIDE.md) to understand the system
2. Read [PRODUCTION_ROLLOUT_PLAN.md](PRODUCTION_ROLLOUT_PLAN.md) in full
3. Practice in staging environment first
4. Shadow an experienced operator during a rollout
5. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

---

## 📊 Metrics & Monitoring

**Key Metrics to Track**:

During Rollout:
- Backend health endpoint status
- API response times (p50, p95, p99)
- Error rate (percentage of 5xx responses)
- Notification delivery rate
- Frontend load times

Post-Rollout (24h):
- Error rate trend
- Response time trend
- User complaints/reports
- Notification success rate
- Database query performance

**Where to Monitor**:
- Render Dashboard → Service → Metrics
- Render Dashboard → Service → Logs
- Application logs (filter by ERROR, WARNING)
- Browser console (for frontend issues)

---

## 🔖 Version History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024 | 1.0 | Initial production rollout plan and tooling | Dev Team |

---

## ✨ Quick Tips

💡 **Before you start**: Always create a database backup  
💡 **During rollout**: Keep verification script running in another terminal  
💡 **Monitor actively**: First 2 hours are critical  
💡 **Communicate**: Keep team updated on progress and any issues  
💡 **Document**: Note everything - it helps with future rollouts  
💡 **Don't panic**: Rollback procedures are tested and ready  
💡 **Test in staging first**: Never try new procedures in production first  

---

**Last Updated**: 2024  
**Maintained By**: DevOps Team  
**For Questions**: See support contacts in [PRODUCTION_ROLLOUT_PLAN.md](PRODUCTION_ROLLOUT_PLAN.md)
