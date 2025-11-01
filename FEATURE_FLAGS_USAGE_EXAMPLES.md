# Feature Flags - Usage Examples

This document provides practical examples of how to use feature flags in Felix Hub.

## Backend Examples

### Example 1: Check feature flag in route handler

```python
from flask import jsonify
import config

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    
    # Check if car number feature is enabled
    if config.ENABLE_CAR_NUMBER:
        car_number = data.get('car_number')
        if car_number:
            # Validate and process car number
            normalized = normalize_car_number(car_number)
            order.car_number = normalized
    
    # Process order...
    return jsonify({'success': True})
```

### Example 2: Conditional notification sending

```python
from services.telegram import notify_admin_new_order
import config

def create_order(data):
    # Create order in database
    order = Order(**data)
    db.session.add(order)
    db.session.commit()
    
    # Send admin notification only if enabled
    if config.ENABLE_TG_ADMIN_NOTIFS:
        notify_admin_new_order(order, db.session)
    
    return order
```

### Example 3: Conditional catalog categorization

```python
import config

@app.route('/api/parts', methods=['GET'])
def get_parts():
    if config.ENABLE_PART_CATEGORIES:
        # Return categorized parts
        categories = Category.query.order_by(Category.sort_order).all()
        return jsonify([{
            'id': cat.id,
            'name': cat.name_ru,
            'icon': cat.icon,
            'parts': [p.to_dict() for p in cat.parts]
        } for cat in categories])
    else:
        # Return flat list of parts
        parts = Part.query.filter_by(is_common=True).all()
        return jsonify([p.to_dict() for p in parts])
```

## Frontend Examples

### Example 1: Wrap App with FeatureFlagsProvider

```tsx
// main.tsx
import { FeatureFlagsProvider } from './config';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <FeatureFlagsProvider>
      <App />
    </FeatureFlagsProvider>
  </React.StrictMode>
);
```

### Example 2: Use feature flags in components

```tsx
import { useFeatureFlags } from '@/config';

function OrderForm() {
  const { isEnabled } = useFeatureFlags();

  return (
    <form>
      <input type="text" name="customer" placeholder="Customer name" />
      
      {/* Conditionally render car number field */}
      {isEnabled('ENABLE_CAR_NUMBER') && (
        <input 
          type="text" 
          name="carNumber" 
          placeholder="Car number" 
        />
      )}
      
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Example 3: Higher-Order Component for feature gating

```tsx
import { withFeatureFlag } from '@/config';

// Component only renders if ENABLE_UI_REFRESH is true
const ModernOrderCard = ({ order }) => (
  <div className="modern-card">
    <h3>{order.title}</h3>
    <p>{order.description}</p>
  </div>
);

// Legacy component as fallback
const LegacyOrderCard = ({ order }) => (
  <div className="legacy-card">
    <h3>{order.title}</h3>
    <p>{order.description}</p>
  </div>
);

// Export with feature flag
export default withFeatureFlag(
  'ENABLE_UI_REFRESH',
  ModernOrderCard,
  LegacyOrderCard  // Fallback
);
```

### Example 4: Direct flag access

```tsx
import { isFeatureEnabled } from '@/config/env';

function PartsSelector() {
  const [parts, setParts] = useState([]);

  useEffect(() => {
    const fetchParts = async () => {
      const endpoint = isFeatureEnabled('ENABLE_PART_CATEGORIES')
        ? '/api/parts/categorized'
        : '/api/parts';
      
      const response = await fetch(endpoint);
      const data = await response.json();
      setParts(data);
    };

    fetchParts();
  }, []);

  return <div>{/* Render parts */}</div>;
}
```

### Example 5: Multiple flag checks

```tsx
import { useFeatureFlags } from '@/config';

function MechanicDashboard() {
  const { flags, isEnabled } = useFeatureFlags();

  // Check multiple flags
  const showModernUI = isEnabled('ENABLE_UI_REFRESH');
  const showMultiLang = isEnabled('ENABLE_MECH_I18N');
  const showCarNumbers = isEnabled('ENABLE_CAR_NUMBER');

  return (
    <div className={showModernUI ? 'modern-layout' : 'classic-layout'}>
      {showMultiLang && <LanguageSwitcher />}
      
      <OrdersList showCarNumbers={showCarNumbers} />
      
      {/* Debug: Show all flags (remove in production) */}
      {process.env.NODE_ENV === 'development' && (
        <pre>{JSON.stringify(flags, null, 2)}</pre>
      )}
    </div>
  );
}
```

### Example 6: Conditional routing

```tsx
import { useFeatureFlags } from '@/config';

function AppRoutes() {
  const { isEnabled } = useFeatureFlags();

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/orders" element={<Orders />} />
      
      {/* Only show parts catalog if categorization is enabled */}
      {isEnabled('ENABLE_PART_CATEGORIES') && (
        <Route path="/catalog" element={<PartsCatalog />} />
      )}
      
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
```

### Example 7: Feature flag loading state

```tsx
import { useFeatureFlags } from '@/config';

function App() {
  const { isLoading, flags } = useFeatureFlags();

  if (isLoading) {
    return <LoadingSpinner message="Loading configuration..." />;
  }

  return <MainApp />;
}
```

### Example 8: Manual refresh feature flags

```tsx
import { useFeatureFlags } from '@/config';

function AdminPanel() {
  const { flags, refresh } = useFeatureFlags();
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refresh();
    setRefreshing(false);
    toast.success('Feature flags refreshed');
  };

  return (
    <div>
      <h2>Feature Flags</h2>
      <button onClick={handleRefresh} disabled={refreshing}>
        {refreshing ? 'Refreshing...' : 'Refresh Flags'}
      </button>
      
      <ul>
        {Object.entries(flags).map(([key, value]) => (
          <li key={key}>
            {key}: <strong>{value ? 'ON' : 'OFF'}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## Testing Examples

### Example 1: Mock feature flags in tests

```tsx
import { setFeatureFlags, resetFeatureFlags } from '@/config/env';

describe('OrderForm', () => {
  afterEach(() => {
    resetFeatureFlags();
  });

  it('shows car number field when enabled', () => {
    setFeatureFlags({ ENABLE_CAR_NUMBER: true });
    
    render(<OrderForm />);
    
    expect(screen.getByPlaceholderText('Car number')).toBeInTheDocument();
  });

  it('hides car number field when disabled', () => {
    setFeatureFlags({ ENABLE_CAR_NUMBER: false });
    
    render(<OrderForm />);
    
    expect(screen.queryByPlaceholderText('Car number')).not.toBeInTheDocument();
  });
});
```

### Example 2: Test with FeatureFlagsProvider

```tsx
import { FeatureFlagsProvider } from '@/config';

const renderWithFeatureFlags = (component, flags = {}) => {
  // Override feature flags for testing
  setFeatureFlags(flags);
  
  return render(
    <FeatureFlagsProvider>
      {component}
    </FeatureFlagsProvider>
  );
};

test('renders modern UI when flag enabled', () => {
  renderWithFeatureFlags(<Dashboard />, { ENABLE_UI_REFRESH: true });
  
  expect(screen.getByTestId('modern-ui')).toBeInTheDocument();
});
```

## Environment-Specific Configuration

### Development

```bash
# .env.development
ENVIRONMENT=development
VITE_API_URL=http://localhost:5000/api
# All feature flags default to ON
```

### Staging

```bash
# .env.staging
ENVIRONMENT=staging
VITE_API_URL=https://staging.felix-hub.com/api
# All feature flags default to ON for testing
```

### Production

```bash
# .env.production
ENVIRONMENT=production
VITE_API_URL=https://api.felix-hub.com/api

# Explicitly enable only tested features
VITE_ENABLE_CAR_NUMBER=true
VITE_ENABLE_MECH_I18N=true

# Keep new features OFF until ready
VITE_ENABLE_UI_REFRESH=false
VITE_ENABLE_PART_CATEGORIES=false
```

## Deployment Scenarios

### Scenario 1: Deploy new feature to staging

1. Merge feature branch to `staging`
2. Set `ENVIRONMENT=staging` (all flags ON by default)
3. Deploy and test
4. If issues found, fix and redeploy

### Scenario 2: Gradual rollout to production

1. Merge to `main` branch
2. Set `ENVIRONMENT=production` (all flags OFF by default)
3. Deploy with feature flag OFF
4. Once deployed, enable flag via environment variable:
   ```bash
   ENABLE_NEW_FEATURE=true
   ```
5. Restart backend (no redeployment needed)
6. Monitor for issues
7. If problems occur, set `ENABLE_NEW_FEATURE=false` and restart

### Scenario 3: A/B testing

```python
import config
import random

@app.route('/api/orders')
def get_orders():
    # Enable new UI for 50% of users
    use_new_ui = config.ENABLE_UI_REFRESH and random.random() < 0.5
    
    return jsonify({
        'orders': orders,
        'use_new_ui': use_new_ui
    })
```

### Scenario 4: Rollback

```bash
# Quick rollback - disable feature
ENABLE_PROBLEMATIC_FEATURE=false

# Restart service
pm2 restart backend

# No code changes or redeployment needed
```

## Best Practices Summary

1. **Always use feature flags for risky changes**
2. **Test in staging first** with flags ON
3. **Deploy to production** with flags OFF
4. **Enable gradually** and monitor
5. **Have rollback plan** ready
6. **Remove flags** once feature is stable
7. **Document dependencies** between features
8. **Log flag states** on application startup
9. **Use meaningful flag names** that describe the feature
10. **Keep flags simple** - boolean on/off only

## Debugging

### View current flags in browser console

```javascript
// In browser console
fetch('/api/config/feature-flags')
  .then(r => r.json())
  .then(flags => console.table(flags));
```

### View backend flags in logs

```python
# Add to app initialization
config.log_feature_flags(logger)
```

Output:
```
INFO - Environment: production
INFO - Feature Flags:
INFO -   ENABLE_CAR_NUMBER: True
INFO -   ENABLE_PART_CATEGORIES: False
INFO -   ENABLE_TG_ADMIN_NOTIFS: True
INFO -   ENABLE_TG_MECH_NOTIFS: True
INFO -   ENABLE_MECH_I18N: True
INFO -   ENABLE_UI_REFRESH: False
```
