# Testing Guide: Mechanic Module

This guide covers how to test the mechanic module comprehensively.

---

## 📋 Test Documentation

- **Test Checklist**: `MECHANIC_E2E_TEST_CHECKLIST.md` - 115+ test cases
- **Changelog**: `CHANGELOG_MECHANIC_E2E.md` - Bug fixes and improvements
- **E2E Script**: `test_mechanic_e2e.py` - Automated backend tests

---

## 🚀 Quick Start

### Prerequisites

1. Backend running on `http://localhost:5000` (or set `BASE_URL` env var)
2. Test mechanic account with credentials:
   - Email: `test@example.com`
   - Password: `password123`
3. Python 3.7+ with `requests` library

### Run Backend E2E Tests

```bash
# Install dependencies if needed
pip install requests

# Run tests
python3 test_mechanic_e2e.py

# Or with custom URL
BASE_URL=http://your-server.com python3 test_mechanic_e2e.py
```

### Expected Output

```
================================================================================
Starting Mechanic Module E2E Tests
================================================================================

================================================================================
1. AUTHENTICATION & PROTECTED ROUTES
================================================================================
  ✓ PASS Invalid credentials return 401
  ✓ PASS Valid credentials login succeeds
  ✓ PASS Token is returned
  ✓ PASS Mechanic data is returned
  ✓ PASS Protected route without token returns 401
  ✓ PASS Protected route with token succeeds

[... more tests ...]

================================================================================
TEST SUMMARY
================================================================================

  Total Tests: 35
  Passed: 35
  Failed: 0
  Pass Rate: 100.0%
```

---

## 🧪 Manual Frontend Testing

### 1. Setup Development Environment

```bash
cd felix_hub/frontend
npm install
npm run dev
```

Open browser to `http://localhost:5173`

### 2. Follow Test Checklist

Use `MECHANIC_E2E_TEST_CHECKLIST.md` and test each section:

#### Section 1: Authentication
- [ ] Test login with valid credentials
- [ ] Test login with invalid credentials
- [ ] Test email validation
- [ ] Test password validation
- [ ] Test redirect after login
- [ ] Test deeplink token login (if available)

#### Section 2: Dashboard
- [ ] Verify stats display correctly
- [ ] Test each filter (Все, Новые, В работе, Готовые)
- [ ] Click on an order to navigate
- [ ] Check empty state (if no orders)
- [ ] Check loading state

#### Section 3: Order Details
- [ ] Verify order information displays
- [ ] Test status change buttons
- [ ] Start and stop timer
- [ ] Add manual time entry
- [ ] Add comments
- [ ] Add custom work/part
- [ ] Navigate back to dashboard

#### Section 4: Time History
- [ ] Check stats display
- [ ] Test period filters
- [ ] Test custom date range
- [ ] Click on order link

#### Section 5: Profile
- [ ] Edit phone number
- [ ] Change password
- [ ] View all-time stats
- [ ] Logout

### 3. Mobile Responsiveness Testing

Open Chrome DevTools (F12) and test these viewports:

#### iPhone SE (375px)
```
1. Set viewport to 375x667
2. Test all pages
3. Verify touch targets are ≥44px
4. Check text readability
5. Test forms
```

#### Small Mobile (320px)
```
1. Set viewport to 320x568
2. Test critical paths:
   - Login
   - Dashboard
   - Order details (main tab)
3. Verify no horizontal scroll
```

#### Tablet (768px)
```
1. Set viewport to 768x1024
2. Verify proper grid layouts
3. Check that content isn't stretched
```

### 4. Error Testing

#### Network Errors
- Disconnect internet
- Try to load dashboard
- Verify error message appears

#### API Errors
- Try invalid order ID: `/mechanic/orders/99999`
- Try invalid status update
- Try empty comment submission

#### Console Check
```javascript
// Open console (F12)
// Should see NO red errors during normal usage
```

---

## 🎭 Test Accounts

### Mechanic Account
- **Email**: test@example.com
- **Password**: password123

If this account doesn't exist, create it:

```bash
cd felix_hub/backend
python create_test_mechanic.py
```

---

## 📊 Performance Testing

### Lighthouse Audit

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Test desktop
lighthouse http://localhost:5173/mechanic/dashboard --preset=desktop --view

# Test mobile (most important)
lighthouse http://localhost:5173/mechanic/dashboard --preset=mobile --view
```

### Target Scores
- Performance: ≥ 80
- Accessibility: ≥ 90
- Best Practices: ≥ 90
- SEO: ≥ 80

### Common Issues and Fixes

#### Low Performance Score
- Check bundle size
- Enable code splitting
- Optimize images
- Add caching headers

#### Low Accessibility Score
- Add missing ARIA labels
- Ensure color contrast
- Test keyboard navigation
- Add alt text to images

---

## 🐛 Bug Testing

### Test These Common Bugs

1. **Memory Leaks**
   - Navigate between pages multiple times
   - Check Chrome DevTools > Memory
   - No increasing heap size

2. **State Issues**
   - Add comment, check it appears
   - Start timer, refresh page, check timer persists
   - Update profile, check localStorage updates

3. **Race Conditions**
   - Start multiple timers quickly
   - Should show error
   - Only one timer should be active

4. **Form Validation**
   - Submit forms with empty fields
   - Submit forms with invalid data
   - Check error messages appear

---

## 📱 Cross-Browser Testing

### Minimum Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Test In Each Browser
1. Login
2. Dashboard view
3. Order details
4. Form submissions

### Known Issues
- Safari: Date inputs look different (acceptable)
- IE11: Not supported (modern features required)

---

## 🔍 Debugging Tests

### Backend Debugging

```python
# In test_mechanic_e2e.py, add debugging:
import pdb; pdb.set_trace()

# Or add prints:
print(f"Response: {response.json()}")
print(f"Status: {response.status_code}")
```

### Frontend Debugging

```javascript
// In browser console:
localStorage.getItem('mechanic_token')  // Check token
localStorage.getItem('mechanic')        // Check user data

// In React DevTools:
// Inspect component props and state
```

---

## 📝 Writing New Tests

### Backend Test Template

```python
def test_new_feature(self):
    """Test new feature"""
    print_section("X. NEW FEATURE")
    
    headers = {'Authorization': f'Bearer {self.token}'}
    
    try:
        response = requests.get(
            f'{API_BASE}/mechanic/new-endpoint',
            headers=headers,
            timeout=5
        )
        log_test(
            "New feature works",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
    except Exception as e:
        log_test("New feature works", False, str(e))
```

### Frontend Test Checklist Item

```markdown
### X.Y New Feature
- [ ] ✅ Feature loads correctly
- [ ] ✅ User can interact
- [ ] ✅ Success message shown
- [ ] ✅ Error handling works
- [ ] ✅ Mobile responsive
```

---

## 🎯 Test Coverage Goals

### Current Status
- Backend E2E: ~90% of critical paths
- Frontend Manual: ~85% of user flows
- Unit Tests: 0% (recommended to add)

### Target Coverage
- Backend E2E: 95%
- Frontend E2E: 90% (add Cypress/Playwright)
- Unit Tests: 70% for utilities and hooks

---

## 📚 Additional Resources

### Tools
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [React DevTools](https://react.dev/learn/react-developer-tools)

### Testing Best Practices
- Test user flows, not implementation details
- Test happy path and error cases
- Test edge cases (empty states, network errors)
- Test accessibility (keyboard navigation, screen readers)
- Test mobile first

### When to Run Tests
- ✅ Before committing code
- ✅ Before creating PR
- ✅ After merging main branch
- ✅ Before production deployment
- ✅ After production deployment (smoke tests)

---

## 🚨 CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install requests
      
      - name: Start backend
        run: |
          cd felix_hub/backend
          python app.py &
          sleep 10
      
      - name: Run E2E tests
        run: python3 test_mechanic_e2e.py
```

---

## ✅ Pre-Deployment Checklist

Before deploying to production:

- [ ] All automated tests pass
- [ ] Manual testing completed
- [ ] No console errors
- [ ] Lighthouse scores meet targets
- [ ] Mobile testing completed
- [ ] Cross-browser testing completed
- [ ] Performance acceptable
- [ ] Error handling works
- [ ] Loading states present
- [ ] Empty states handled
- [ ] Accessibility verified

---

## 📞 Support

If tests fail or you need help:

1. Check the error message
2. Review `TROUBLESHOOTING.md` (if exists)
3. Check `CHANGELOG_MECHANIC_E2E.md` for known issues
4. Contact development team

---

## 📅 Test Schedule

### Daily
- Smoke tests after deployment

### Weekly
- Full regression testing
- Performance audit

### Monthly
- Cross-browser testing
- Accessibility audit
- Security audit

### Per Release
- Complete E2E testing
- Manual testing of new features
- Performance testing
- Mobile testing
