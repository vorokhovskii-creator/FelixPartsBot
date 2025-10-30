# Multilingual Support - Quick Start Guide

## What Was Implemented

Full multilingual support for Felix Hub System in **Russian**, **Hebrew**, and **English**.

## Quick Setup

### 1. Database Migration (Required Once)
```bash
cd felix_hub/backend
python migrate_add_language.py
```

This adds the `language` column to existing orders.

### 2. No Other Changes Needed!
- All code is already updated
- Existing orders continue working (default to Russian)
- New features activate automatically

## How to Use

### Telegram Bot

**Mechanics see language selection on first `/start`:**
```
/start
> Choose language / בחר שפה / Выберите язык
> 🇷🇺 Русский
> 🇮🇱 עברית  
> 🇬🇧 English
```

**Change language anytime:**
- Main menu → "🌐 Change language / שנה שפה / Изменить язык"

**All bot features work in selected language:**
- Order creation
- Status updates
- Notifications
- Help text

### Admin Panel

**Language selector in navbar:**
```
Click: 🇷🇺 for Russian
Click: 🇮🇱 for Hebrew (auto-switches to RTL layout)
Click: 🇬🇧 for English
```

**Features:**
- All text translates instantly
- Hebrew gets right-to-left layout
- Language saved in browser
- Works across all pages

## File Changes Summary

### New Files
- `bot/translations.py` - Bot translation dictionary
- `backend/static/i18n.js` - Admin panel translations
- `backend/migrate_add_language.py` - Database migration

### Modified Files
- `backend/models.py` - Added `language` field
- `backend/app.py` - Accept language in API
- `backend/utils/notifier.py` - Multilingual notifications
- `backend/templates/admin.html` - i18n attributes
- `backend/static/style.css` - RTL CSS rules
- `bot/bot.py` - Full multilingual support

## Testing

### Test Bot
1. Send `/start` to bot
2. Select each language
3. Create an order
4. Check "My Orders"
5. Change language via menu

### Test Admin
1. Open admin panel
2. Click each flag (🇷🇺🇮🇱🇬🇧)
3. Verify text changes
4. For Hebrew: Check RTL layout
5. Refresh: Language persists

### Test Notifications
1. Bot: Create order in any language
2. Admin: Change order status to "готов"
3. Bot: Receive notification in your language

## Key Features

✅ 3 languages supported (RU/HE/EN)
✅ Hebrew RTL (Right-to-Left) support
✅ Language persists across sessions
✅ Notifications in mechanic's language
✅ Admin panel language saved in browser
✅ Fallback to Russian if translation missing
✅ Existing orders still work
✅ No dependencies added

## Common Questions

**Q: Do I need to translate all existing data?**
A: No! Data stays in Russian. Only UI translates.

**Q: What happens to old orders?**
A: They default to Russian and work perfectly.

**Q: Can I add more languages?**
A: Yes! Edit `translations.py` and `i18n.js`.

**Q: How do I reset language in bot?**
A: Use the "Change language" option in main menu.

**Q: How do I reset language in admin?**
A: Click a different flag, or clear browser localStorage.

## Support

See full documentation: `MULTILANG_IMPLEMENTATION.md`

## Migration Rollback

If needed, remove language column:
```sql
ALTER TABLE orders DROP COLUMN language;
```

(Not recommended - column is harmless even if unused)
