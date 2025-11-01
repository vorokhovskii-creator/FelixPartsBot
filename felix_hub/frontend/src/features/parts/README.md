# Parts Picker Component

A comprehensive parts selection component with category filtering and search functionality.

## Features

- **Category Browsing**: Display and select from available part categories
- **Category Filtering**: Filter parts by selected category
- **Search**: Search parts within the selected category by name (supports Russian, Hebrew, and English names)
- **Multi-select**: Support for selecting multiple parts (configurable)
- **Single-select**: Optional single-selection mode
- **Accessibility**: Full keyboard navigation and screen reader support
- **Error Handling**: Graceful error handling with user-friendly messages
- **Loading States**: Clear loading indicators during data fetching

## Usage

### Basic Usage

```tsx
import { PartsPicker } from '@/features/parts';

function MyComponent() {
  const [selectedPartIds, setSelectedPartIds] = useState<number[]>([]);

  return (
    <PartsPicker
      selectedIds={selectedPartIds}
      onSelect={setSelectedPartIds}
      onConfirm={(ids) => {
        console.log('Selected parts:', ids);
        // Handle confirmation
      }}
    />
  );
}
```

### Single Selection Mode

```tsx
<PartsPicker
  selectedIds={selectedPartIds}
  onSelect={setSelectedPartIds}
  multiSelect={false}
  onConfirm={(ids) => {
    const selectedId = ids[0];
    // Handle single selection
  }}
/>
```

### Without Confirm Button

```tsx
<PartsPicker
  selectedIds={selectedPartIds}
  onSelect={(ids) => {
    // Handle selection change immediately
    console.log('Selection changed:', ids);
  }}
  showConfirmButton={false}
/>
```

### With Initial Category

```tsx
<PartsPicker
  selectedIds={selectedPartIds}
  onSelect={setSelectedPartIds}
  initialCategoryId={5}
  onConfirm={handleConfirm}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `selectedIds` | `number[]` | `[]` | Array of selected part IDs |
| `onSelect` | `(ids: number[]) => void` | `undefined` | Callback when selection changes |
| `onConfirm` | `(ids: number[]) => void` | `undefined` | Callback when confirm button is clicked |
| `multiSelect` | `boolean` | `true` | Allow multiple parts selection |
| `showConfirmButton` | `boolean` | `true` | Show confirm button at the bottom |
| `confirmButtonText` | `string` | `'Подтвердить выбор'` | Text for the confirm button |
| `initialCategoryId` | `number` | `undefined` | Initial category to display |

## Accessibility

The component includes:

- Proper ARIA labels and roles
- Keyboard navigation support (Enter, Space keys)
- Screen reader announcements for loading and error states
- Focus management
- Semantic HTML structure
- `role="checkbox"` and `aria-checked` for part selection
- `role="list"` and `role="listitem"` for lists

## API Integration

The component fetches data from:

- `GET /api/categories` - Fetch all categories
- `GET /api/parts?category_id={id}` - Fetch parts by category

## Error Handling

The component gracefully handles:

- Categories loading failures
- Parts loading failures
- Network errors
- Empty states

All errors are displayed with user-friendly messages and options to retry.
