/**
 * Internationalization for Felix Hub Admin Panel
 * Supports: Russian (ru), Hebrew (he), English (en)
 */

const I18N = {
    'admin_panel_title': {
        'ru': '🔧 Felix Hub - Админ-панель',
        'he': '🔧 Felix Hub - פאנל ניהול',
        'en': '🔧 Felix Hub - Admin Panel'
    },
    'total_orders': {
        'ru': 'Всего заказов',
        'he': 'סה"כ הזמנות',
        'en': 'Total Orders'
    },
    'today': {
        'ru': 'Сегодня',
        'he': 'היום',
        'en': 'Today'
    },
    'in_progress': {
        'ru': 'В работе',
        'he': 'בתהליך',
        'en': 'In Progress'
    },
    'ready': {
        'ru': 'Готовы',
        'he': 'מוכן',
        'en': 'Ready'
    },
    'status': {
        'ru': 'Статус:',
        'he': 'סטטוס:',
        'en': 'Status:'
    },
    'mechanic': {
        'ru': 'Механик:',
        'he': 'מכונאי:',
        'en': 'Mechanic:'
    },
    'search': {
        'ru': 'Поиск:',
        'he': 'חיפוש:',
        'en': 'Search:'
    },
    'reset_filters': {
        'ru': '❌ Сбросить фильтры',
        'he': '❌ אפס מסננים',
        'en': '❌ Reset Filters'
    },
    'export_excel': {
        'ru': '📤 Экспорт в Excel',
        'he': '📤 ייצוא ל-Excel',
        'en': '📤 Export to Excel'
    },
    'refresh': {
        'ru': '🔄 Обновить',
        'he': '🔄 רענן',
        'en': '🔄 Refresh'
    },
    'order_details': {
        'ru': 'Детали заказа',
        'he': 'פרטי הזמנה',
        'en': 'Order Details'
    },
    'status_new': {
        'ru': 'Новый',
        'he': 'חדש',
        'en': 'New'
    },
    'status_in_progress': {
        'ru': 'В работе',
        'he': 'בתהליך',
        'en': 'In Progress'
    },
    'status_ready': {
        'ru': 'Готов',
        'he': 'מוכן',
        'en': 'Ready'
    },
    'status_delivered': {
        'ru': 'Выдан',
        'he': 'נמסר',
        'en': 'Delivered'
    },
    'delete': {
        'ru': 'Удалить',
        'he': 'מחק',
        'en': 'Delete'
    },
    'print': {
        'ru': 'Печать',
        'he': 'הדפס',
        'en': 'Print'
    },
    'close': {
        'ru': 'Закрыть',
        'he': 'סגור',
        'en': 'Close'
    },
    'all': {
        'ru': 'Все',
        'he': 'הכל',
        'en': 'All'
    },
    'mechanic_placeholder': {
        'ru': 'Имя механика',
        'he': 'שם מכונאי',
        'en': 'Mechanic name'
    },
    'search_placeholder': {
        'ru': 'VIN или ID',
        'he': 'VIN או מזהה',
        'en': 'VIN or ID'
    },
    'loading': {
        'ru': 'Загрузка...',
        'he': 'טוען...',
        'en': 'Loading...'
    },
    'date': {
        'ru': 'Дата',
        'he': 'תאריך',
        'en': 'Date'
    },
    'category': {
        'ru': 'Категория',
        'he': 'קטגוריה',
        'en': 'Category'
    },
    'vin': {
        'ru': 'VIN',
        'he': 'VIN',
        'en': 'VIN'
    },
    'parts': {
        'ru': 'Детали',
        'he': 'חלקים',
        'en': 'Parts'
    },
    'original': {
        'ru': 'Оригинал',
        'he': 'מקורי',
        'en': 'Original'
    },
    'actions': {
        'ru': 'Действия',
        'he': 'פעולות',
        'en': 'Actions'
    },
    'id': {
        'ru': 'ID',
        'he': 'מזהה',
        'en': 'ID'
    }
};

// Get current language from localStorage or default to Russian
let currentLang = localStorage.getItem('adminLang') || 'ru';

/**
 * Get translation by key
 * @param {string} key - Translation key
 * @returns {string} - Translated text
 */
function t(key) {
    return I18N[key]?.[currentLang] || I18N[key]?.['ru'] || key;
}

/**
 * Set interface language
 * @param {string} lang - Language code (ru, he, en)
 */
function setLanguage(lang) {
    if (!['ru', 'he', 'en'].includes(lang)) {
        console.error('Unsupported language:', lang);
        return;
    }
    
    currentLang = lang;
    localStorage.setItem('adminLang', lang);
    
    // Update active button state
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-lang="${lang}"]`)?.classList.add('active');
    
    updateUI();
}

/**
 * Update all UI elements with translations
 */
function updateUI() {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const translation = t(key);
        
        if (el.tagName === 'INPUT' || el.tagName === 'SELECT') {
            // For inputs, update placeholder
            if (el.hasAttribute('placeholder')) {
                el.placeholder = translation;
            }
        } else if (el.tagName === 'OPTION') {
            // For options, update text content
            el.textContent = translation;
        } else {
            // For other elements, update text content
            el.textContent = translation;
        }
    });
    
    // Set text direction for Hebrew (RTL)
    const isRTL = currentLang === 'he';
    document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
    document.documentElement.setAttribute('lang', currentLang);
    
    // Update body class for language-specific styling
    document.body.classList.remove('lang-ru', 'lang-he', 'lang-en');
    document.body.classList.add(`lang-${currentLang}`);
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', () => {
    // Set active button
    document.querySelector(`[data-lang="${currentLang}"]`)?.classList.add('active');
    updateUI();
});
