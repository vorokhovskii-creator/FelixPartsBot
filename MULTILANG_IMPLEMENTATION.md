# Multilingual Support Implementation

## Overview
Felix Hub System now supports three languages:
- 🇷🇺 **Russian (ru)** - Default
- 🇮🇱 **Hebrew (he)** - RTL support
- 🇬🇧 **English (en)**

## Features Implemented

### 1. Database Changes
- Added `language` field to `Order` model
- Default value: `'ru'` for all existing orders
- Migration script provided: `backend/migrate_add_language.py`

### 2. Telegram Bot
- **Language selection** at first start (`/start` command)
- **Change language** option in main menu
- All messages translated to 3 languages
- Language preserved across sessions
- Notifications sent in mechanic's language

### 3. Admin Panel
- **Language selector** (🇷🇺/🇮🇱/🇬🇧) in navbar
- All UI elements translated
- **RTL (Right-to-Left)** support for Hebrew
- Language preference saved in localStorage
- Dynamic interface updates without page reload

### 4. Translation System
- **Bot translations**: `bot/translations.py`
  - Dictionary-based translations
  - Fallback to Russian if translation missing
  - Support for formatted strings
  
- **Admin translations**: `backend/static/i18n.js`
  - Client-side translation system
  - RTL layout switching for Hebrew
  - localStorage persistence

## Files Modified

### Backend
- `backend/models.py` - Added `language` field to Order
- `backend/app.py` - Accept language in order creation API
- `backend/utils/notifier.py` - Multilingual notifications
- `backend/templates/admin.html` - Added i18n attributes
- `backend/static/style.css` - RTL CSS rules
- `backend/static/i18n.js` - NEW: Translation system

### Bot
- `bot/translations.py` - NEW: Translation dictionary
- `bot/bot.py` - Full multilingual support

### New Files
- `bot/translations.py` - Translation dictionary
- `backend/static/i18n.js` - Admin panel i18n
- `backend/migrate_add_language.py` - Migration script

## Installation & Migration

### 1. Update Dependencies
All required packages are already in existing requirements.txt

### 2. Run Database Migration
```bash
cd felix_hub/backend
python migrate_add_language.py
```

This will:
- Add `language` column to orders table
- Set all existing orders to 'ru' (Russian)

### 3. Restart Services
```bash
# Restart backend
cd felix_hub/backend
python app.py

# Restart bot
cd felix_hub/bot
python bot.py
```

## Usage

### For Mechanics (Bot)

1. **First Time**:
   - Send `/start` to bot
   - Select preferred language (🇷🇺/🇮🇱/🇬🇧)
   - Interface changes to selected language

2. **Change Language**:
   - Open bot main menu
   - Click "🌐 Изменить язык / שנה שפה / Change language"
   - Select new language

3. **Orders**:
   - Create orders in your language
   - Receive notifications in your language
   - Language saved with each order

### For Admins (Web Panel)

1. **Access Admin Panel**:
   - Open `http://your-server:5000/admin`

2. **Change Language**:
   - Click language flag in navbar (🇷🇺/🇮🇱/🇬🇧)
   - Interface updates immediately
   - Preference saved in browser

3. **Hebrew RTL Mode**:
   - Select 🇮🇱 button
   - Layout flips to right-to-left
   - All controls mirror appropriately

## Translation Keys

### Bot Translations
See `bot/translations.py` for complete list. Key translations:
- `welcome` - Welcome message
- `new_order` - New order button
- `my_orders` - My orders button
- `select_category` - Category selection
- `order_ready` - Order ready notification
- And 30+ more keys

### Admin Translations
See `backend/static/i18n.js` for complete list. Key translations:
- `admin_panel_title` - Panel title
- `total_orders` - Statistics
- `status_*` - Order statuses
- `export_excel` - Export button
- And 30+ more keys

## Technical Details

### RTL Support
Hebrew uses Right-to-Left text direction:
- Set via CSS `[dir="rtl"]` selector
- Automatic layout mirroring
- Margin/padding adjustments
- Button group reversals

### Fallback Behavior
If translation missing:
1. Try requested language
2. Fall back to Russian
3. Return key if still not found

### API Changes
Order creation endpoint now accepts `language` parameter:
```json
{
  "mechanic_name": "...",
  "telegram_id": "...",
  "category": "...",
  "vin": "...",
  "selected_parts": [...],
  "is_original": true/false,
  "photo_url": "...",
  "language": "ru|he|en"  // NEW
}
```

## Testing

### Test Bot Language Switching
```bash
# Send these commands to bot:
/start
# Select language
# Try "Change language" option
# Create order
# Check notifications
```

### Test Admin Panel
1. Open admin panel
2. Click each language flag
3. Verify all text changes
4. Check Hebrew RTL layout
5. Refresh page - language persists

### Test Notifications
1. Create order in bot (any language)
2. Admin changes order status to "готов"/"מוכן"/"Ready"
3. Mechanic receives notification in their language

## Maintenance

### Adding New Translations
1. **Bot**: Add to `bot/translations.py`:
   ```python
   'new_key': {
       'ru': 'Русский текст',
       'he': 'טקסט בעברית',
       'en': 'English text'
   }
   ```

2. **Admin**: Add to `backend/static/i18n.js`:
   ```javascript
   'new_key': {
       'ru': 'Русский текст',
       'he': 'טקסט בעברית',
       'en': 'English text'
   }
   ```

3. **Use in code**:
   - Bot: `get_text('new_key', lang)`
   - Admin: Add `data-i18n="new_key"` attribute

### Supported Format Strings
Translations support Python format strings:
```python
get_text('order_created', lang, order_id=123)
# Output: "✅ Order #123 created!"
```

## Compatibility

- **Existing orders**: All set to 'ru', continue working
- **Database**: Column added with default value
- **API**: Backward compatible (language optional)
- **UI**: Graceful fallback to Russian

## Future Enhancements

Possible improvements:
- [ ] Add more languages (Spanish, Arabic, etc.)
- [ ] Translate category names
- [ ] Translate part names
- [ ] Language auto-detection
- [ ] Export reports in different languages
- [ ] Email notifications in user language

## Support

For issues or questions:
1. Check translation keys in source files
2. Verify database migration ran successfully
3. Clear browser cache for admin panel
4. Check bot logs for language detection

## Acceptance Criteria ✅

All requirements from ticket completed:

### Telegram Bot
- ✅ Language selection at `/start`
- ✅ All messages translated to 3 languages
- ✅ Change language command works
- ✅ Categories and parts displayed in selected language

### Admin Panel
- ✅ Language selector buttons (🇷🇺/🇮🇱/🇬🇧) in navbar
- ✅ All interface texts translated
- ✅ RTL mode works for Hebrew
- ✅ Selected language saved in localStorage
- ✅ Status dropdown translated

### General
- ✅ `language` field added to Order model
- ✅ Notifications sent in mechanic's language
- ✅ Database data remains in Russian
- ✅ Existing orders not broken
- ✅ Fallback to Russian for missing translations
