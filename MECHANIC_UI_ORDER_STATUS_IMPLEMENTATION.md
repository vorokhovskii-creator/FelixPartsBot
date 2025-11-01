# Mechanic UI: Order Status Display and Sync Implementation

## Overview
This document describes the implementation of order status display and real-time synchronization in the mechanic UI.

## Features Implemented

### 1. Order Status Display
- **Order List**: Status chip/badge with color codes
- **Order Details**: Prominent status display with last updated timestamp
- **Color Coding**:
  - New (Новый): Blue
  - In Progress (В работе): Yellow  
  - Paused (На паузе): Gray
  - Waiting Parts (Ожидание запчастей): Orange
  - Completed (Завершен): Green
  - Cancelled (Отменен): Red

### 2. Data Synchronization
- **Polling Interval**: Every 30 seconds (configurable via `REFETCH_INTERVAL` constant)
- **Window Focus**: Automatic refetch when window gains focus
- **Visibility Change**: Refetch when tab becomes visible
- **Background Updates**: Polling pauses when tab is hidden to save resources

### 3. Timestamps
- **Created At**: Displayed in order list items
- **Updated At**: Displayed in order list items and order details header
- **Format**: Localized date-time string (DD.MM.YYYY HH:MM:SS)

## Files Created

### API Layer
- `frontend/src/api/orders.ts`: Order API functions and polling utility
  - `ordersApi.fetchOrders()`: Fetch orders list with optional status filter
  - `ordersApi.fetchOrderDetails()`: Fetch single order details
  - `ordersApi.updateOrderStatus()`: Update order status
  - `usePolling()`: Custom polling hook with window focus detection
  - `REFETCH_INTERVAL`: Configurable refresh interval (default: 30000ms)

- `frontend/src/api/index.ts`: API exports

### Feature Components
- `frontend/src/features/orders/OrdersList.tsx`: Orders list component with auto-refresh
  - Handles filtering by status
  - Automatic polling and focus-based refresh
  - Loading and error states
  
- `frontend/src/features/orders/OrderItem.tsx`: Individual order card component
  - Status badge with color coding
  - Created and updated timestamps
  - Click handler for navigation
  
- `frontend/src/features/orders/OrderDetails.tsx`: Order details component with auto-refresh
  - Prominent status display in header
  - Last updated timestamp
  - Automatic polling and focus-based refresh
  - Full order information display

- `frontend/src/features/orders/index.ts`: Feature exports

## Files Modified

### Pages
- `frontend/src/pages/MechanicDashboard.tsx`: 
  - Refactored to use new OrdersList component
  - Added stats polling
  - Removed duplicate order rendering logic

- `frontend/src/pages/OrderDetails.tsx`:
  - Simplified to wrapper component
  - Delegates to features/orders/OrderDetails

### Types
- `frontend/src/types/index.ts`:
  - Removed `phone` field from Order interface (not in backend model)
  - Maintained status and work_status fields

## Configuration

### Polling Interval
To change the refetch interval, modify the constant in `frontend/src/api/orders.ts`:

```typescript
export const REFETCH_INTERVAL = 30000; // milliseconds
```

### Status Colors
To change status colors, modify the `getStatusColor()` function in:
- `frontend/src/features/orders/OrderItem.tsx`
- `frontend/src/features/orders/OrderDetails.tsx`

## Architecture

### Polling Implementation
The polling system uses a custom `usePolling` utility that:
1. Sets up an interval timer for periodic updates
2. Listens for `visibilitychange` events to detect tab visibility
3. Listens for `focus` events to detect window focus
4. Only polls when the tab is visible
5. Cleans up listeners and timers on unmount

### Component Hierarchy
```
MechanicDashboard
└── OrdersList
    └── OrderItem (multiple)

OrderDetailsPage
└── OrderDetails
    ├── StatusButtons
    ├── TimeTracker
    ├── CommentsList
    └── CustomItemsSection
```

## Performance Considerations

1. **Conditional Polling**: Polling only occurs when the tab is visible
2. **Debouncing**: Focus events trigger immediate refresh without waiting for interval
3. **Incremental Loading**: Lists show existing data while refreshing in background
4. **Error Handling**: Failed refreshes don't clear existing data or show errors (only initial load)

## Acceptance Criteria Status

✅ Status is visible and correct for all orders
- Status badges displayed in order list
- Status prominently displayed in order details header

✅ Status updates in admin reflect in mechanic UI within 30s or on focus
- Automatic polling every 30 seconds
- Immediate refresh on window focus
- Immediate refresh on tab visibility change

✅ No performance regressions
- Polling pauses when tab is hidden
- Background updates don't interfere with UI
- Existing data shown during refresh

## Testing Recommendations

1. **Status Display**: Verify all status colors render correctly
2. **Polling**: Monitor network requests - should occur every 30s when tab is visible
3. **Focus Refresh**: Switch tabs and return - should trigger immediate refresh
4. **Hidden Tab**: Minimize browser - polling should pause
5. **Status Update**: Change status in admin panel - should reflect in mechanic UI within 30s
6. **Multiple Orders**: Verify status updates across multiple orders

## Future Enhancements

1. WebSocket implementation for real-time updates (eliminate polling)
2. Optimistic updates for status changes
3. Push notifications for status changes
4. Configurable refresh interval in UI settings
5. Network status indicator
6. Last refresh timestamp display
