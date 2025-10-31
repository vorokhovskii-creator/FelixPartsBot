"""
Translation dictionary for Felix Hub Bot
Supports: Russian (ru), Hebrew (he), English (en)
"""

TRANSLATIONS = {
    'welcome': {
        'ru': '👋 Привет! Я Felix Parts Bot — помогу заказать запчасти.\n\nВыбери действие:',
        'he': '👋 שלום! אני Felix Parts Bot - אעזור לך להזמין חלפים.\n\nבחר פעולה:',
        'en': '👋 Hello! I am Felix Parts Bot — I will help you order parts.\n\nSelect an action:'
    },
    'select_category': {
        'ru': '🔍 Выбери категорию запчастей:',
        'he': '🔍 בחר קטגוריה של חלפים:',
        'en': '🔍 Select a parts category:'
    },
    'new_order': {
        'ru': '🆕 Новый заказ',
        'he': '🆕 הזמנה חדשה',
        'en': '🆕 New order'
    },
    'my_orders': {
        'ru': '📋 Мои заказы',
        'he': '📋 ההזמנות שלי',
        'en': '📋 My orders'
    },
    'help': {
        'ru': 'ℹ️ Помощь',
        'he': 'ℹ️ עזרה',
        'en': 'ℹ️ Help'
    },
    'change_language': {
        'ru': '🌐 Изменить язык',
        'he': '🌐 שנה שפה',
        'en': '🌐 Change language'
    },
    'select_language': {
        'ru': 'Выберите язык / בחר שפה / Select language:',
        'he': 'Выберите язык / בחר שפה / Select language:',
        'en': 'Выберите язык / בחר שפה / Select language:'
    },
    'select_parts': {
        'ru': 'Выбери детали из списка (можно несколько):\n\nВыбрано: {count}',
        'he': 'בחר חלקים מהרשימה (אפשר מספר):\n\nנבחרו: {count}',
        'en': 'Select parts from the list (you can select multiple):\n\nSelected: {count}'
    },
    'add_manual': {
        'ru': '➕ Добавить вручную',
        'he': '➕ הוסף ידנית',
        'en': '➕ Add manually'
    },
    'next': {
        'ru': '➡️ Далее',
        'he': '➡️ הבא',
        'en': '➡️ Next'
    },
    'cancel': {
        'ru': '❌ Отмена',
        'he': '❌ ביטול',
        'en': '❌ Cancel'
    },
    'back': {
        'ru': 'Назад',
        'he': 'חזור',
        'en': 'Back'
    },
    'back_to_categories': {
        'ru': 'К категориям',
        'he': 'לקטגוריות',
        'en': 'To categories'
    },
    'enter_vin': {
        'ru': '🚗 Введи VIN автомобиля (минимум 4 символа):',
        'he': '🚗 הכנס VIN של הרכב (לפחות 4 תווים):',
        'en': '🚗 Enter vehicle VIN (minimum 4 characters):'
    },
    'vin_too_short': {
        'ru': '❌ VIN слишком короткий. Введи минимум 4 символа:',
        'he': '❌ VIN קצר מדי. הכנס לפחות 4 תווים:',
        'en': '❌ VIN is too short. Enter at least 4 characters:'
    },
    'select_at_least_one': {
        'ru': '❌ Выбери хотя бы одну деталь!',
        'he': '❌ בחר לפחות חלק אחד!',
        'en': '❌ Select at least one part!'
    },
    'parts_type_question': {
        'ru': 'Какие запчасти нужны?',
        'he': 'איזה סוג חלפים נדרש?',
        'en': 'What type of parts are needed?'
    },
    'original': {
        'ru': '✨ Оригинал',
        'he': '✨ מקורי',
        'en': '✨ Original'
    },
    'not_original': {
        'ru': '🔧 Не оригинал',
        'he': '🔧 לא מקורי',
        'en': '🔧 Not original'
    },
    'photo_question': {
        'ru': 'Хочешь загрузить фото детали?',
        'he': 'האם תרצה להעלות תמונה של החלק?',
        'en': 'Do you want to upload a photo of the part?'
    },
    'upload_photo': {
        'ru': '📸 Загрузить фото',
        'he': '📸 העלה תמונה',
        'en': '📸 Upload photo'
    },
    'skip_photo': {
        'ru': '⏭️ Пропустить',
        'he': '⏭️ דלג',
        'en': '⏭️ Skip'
    },
    'send_photo': {
        'ru': '📸 Отправь фото детали:',
        'he': '📸 שלח תמונה של החלק:',
        'en': '📸 Send a photo of the part:'
    },
    'photo_received': {
        'ru': '✅ Фото получено!',
        'he': '✅ תמונה התקבלה!',
        'en': '✅ Photo received!'
    },
    'check_order': {
        'ru': '📋 <b>Проверь заказ:</b>\n\n👤 Механик: {mechanic}\n📦 Категория: {category}\n🚗 VIN: {vin}\n🔧 Детали:\n{parts}\n\n{original_text}\n{photo_text}',
        'he': '📋 <b>בדוק הזמנה:</b>\n\n👤 מכונאי: {mechanic}\n📦 קטגוריה: {category}\n🚗 VIN: {vin}\n🔧 חלקים:\n{parts}\n\n{original_text}\n{photo_text}',
        'en': '📋 <b>Check order:</b>\n\n👤 Mechanic: {mechanic}\n📦 Category: {category}\n🚗 VIN: {vin}\n🔧 Parts:\n{parts}\n\n{original_text}\n{photo_text}'
    },
    'original_yes': {
        'ru': '✨ Оригинал',
        'he': '✨ מקורי',
        'en': '✨ Original'
    },
    'original_no': {
        'ru': '🔧 Не оригинал',
        'he': '🔧 לא מקורי',
        'en': '🔧 Not original'
    },
    'photo_attached': {
        'ru': '📸 Фото прикреплено',
        'he': '📸 תמונה מצורפת',
        'en': '📸 Photo attached'
    },
    'confirm': {
        'ru': '✅ Подтвердить',
        'he': '✅ אשר',
        'en': '✅ Confirm'
    },
    'order_created': {
        'ru': '✅ Заказ №{order_id} создан!\n\nОжидай уведомление о готовности.',
        'he': '✅ הזמנה מס\' {order_id} נוצרה!\n\nחכה להודעה על מוכנות.',
        'en': '✅ Order #{order_id} created!\n\nWait for a ready notification.'
    },
    'order_creation_error': {
        'ru': '❌ Ошибка создания заказа: {error}',
        'he': '❌ שגיאה ביצירת הזמנה: {error}',
        'en': '❌ Order creation error: {error}'
    },
    'timeout_error': {
        'ru': '❌ Превышено время ожидания ответа от сервера. Попробуй позже.',
        'he': '❌ חריגה מזמן ההמתנה לתגובה מהשרת. נסה שוב מאוחר יותר.',
        'en': '❌ Server response timeout. Try again later.'
    },
    'connection_error': {
        'ru': '❌ Не удается подключиться к серверу. Проверь соединение.',
        'he': '❌ לא ניתן להתחבר לשרת. בדוק את החיבור.',
        'en': '❌ Cannot connect to server. Check your connection.'
    },
    'server_error': {
        'ru': '❌ Ошибка связи с сервером. Попробуй позже.',
        'he': '❌ שגיאת תקשורת עם השרת. נסה שוב מאוחר יותר.',
        'en': '❌ Server communication error. Try again later.'
    },
    'your_orders': {
        'ru': '📋 <b>Твои заказы:</b>\n\n',
        'he': '📋 <b>ההזמנות שלך:</b>\n\n',
        'en': '📋 <b>Your orders:</b>\n\n'
    },
    'no_orders': {
        'ru': 'У тебя пока нет заказов.',
        'he': 'אין לך הזמנות עדיין.',
        'en': 'You have no orders yet.'
    },
    'order_item': {
        'ru': '{emoji} <b>Заказ №{order_id}</b>\nVIN: {vin}\nСтатус: {status}\nДата: {date}\n\n',
        'he': '{emoji} <b>הזמנה מס\' {order_id}</b>\nVIN: {vin}\nסטטוס: {status}\nתאריך: {date}\n\n',
        'en': '{emoji} <b>Order #{order_id}</b>\nVIN: {vin}\nStatus: {status}\nDate: {date}\n\n'
    },
    'orders_load_error': {
        'ru': '❌ Ошибка загрузки заказов.',
        'he': '❌ שגיאה בטעינת הזמנות.',
        'en': '❌ Error loading orders.'
    },
    'help_text': {
        'ru': 'ℹ️ <b>Помощь</b>\n\nFelix Parts Bot помогает заказывать запчасти для СТО.\n\n<b>Основные команды:</b>\n• 🆕 Новый заказ - создать заказ на запчасти\n• 📋 Мои заказы - просмотр твоих заказов\n• 🌐 Изменить язык - сменить язык интерфейса\n• ℹ️ Помощь - это сообщение\n\n<b>Процесс заказа:</b>\n1️⃣ Выбери категорию запчастей\n2️⃣ Отметь нужные детали из списка\n3️⃣ Введи VIN автомобиля\n4️⃣ Укажи тип запчастей (оригинал/не оригинал)\n5️⃣ Загрузи фото (опционально)\n6️⃣ Подтверди заказ\n\nПо вопросам обращайся к администратору.',
        'he': 'ℹ️ <b>עזרה</b>\n\nFelix Parts Bot עוזר להזמין חלפים לשירות.\n\n<b>פקודות עיקריות:</b>\n• 🆕 הזמנה חדשה - ליצור הזמנת חלפים\n• 📋 ההזמנות שלי - לראות את ההזמנות שלך\n• 🌐 שנה שפה - לשנות שפת ממשק\n• ℹ️ עזרה - הודעה זו\n\n<b>תהליך ההזמנה:</b>\n1️⃣ בחר קטגוריה של חלפים\n2️⃣ סמן חלקים נדרשים מהרשימה\n3️⃣ הכנס VIN של הרכב\n4️⃣ ציין סוג חלפים (מקורי/לא מקורי)\n5️⃣ העלה תמונה (אופציונלי)\n6️⃣ אשר הזמנה\n\nלשאלות פנה למנהל.',
        'en': 'ℹ️ <b>Help</b>\n\nFelix Parts Bot helps order parts for the service station.\n\n<b>Main commands:</b>\n• 🆕 New order - create a parts order\n• 📋 My orders - view your orders\n• 🌐 Change language - change interface language\n• ℹ️ Help - this message\n\n<b>Order process:</b>\n1️⃣ Select parts category\n2️⃣ Mark needed parts from the list\n3️⃣ Enter vehicle VIN\n4️⃣ Specify parts type (original/not original)\n5️⃣ Upload photo (optional)\n6️⃣ Confirm order\n\nFor questions, contact the administrator.'
    },
    'action_cancelled': {
        'ru': '❌ Действие отменено.',
        'he': '❌ הפעולה בוטלה.',
        'en': '❌ Action cancelled.'
    },
    'enter_manual_part': {
        'ru': '✏️ Введи название детали вручную:',
        'he': '✏️ הכנס שם חלק באופן ידני:',
        'en': '✏️ Enter part name manually:'
    },
    'manual_part_added': {
        'ru': '✅ Добавлено: {part}\n\nВсего выбрано: {count}',
        'he': '✅ נוסף: {part}\n\nסה"כ נבחרו: {count}',
        'en': '✅ Added: {part}\n\nTotal selected: {count}'
    },
    'continue_selection': {
        'ru': '✅ Продолжить выбор',
        'he': '✅ המשך בחירה',
        'en': '✅ Continue selection'
    },
    'order_ready': {
        'ru': '✅ <b>Заказ №{order_id} готов!</b>\n\n📦 <b>Детали:</b>\n{parts}\n\n🚗 <b>VIN:</b> {vin}\n📅 <b>Дата заказа:</b> {date}\n\nЗабери запчасти у кладовщика! 🔧',
        'he': '✅ <b>הזמנה מס\' {order_id} מוכנה!</b>\n\n📦 <b>חלקים:</b>\n{parts}\n\n🚗 <b>VIN:</b> {vin}\n📅 <b>תאריך הזמנה:</b> {date}\n\nקח את החלפים מהמחסנאי! 🔧',
        'en': '✅ <b>Order #{order_id} is ready!</b>\n\n📦 <b>Parts:</b>\n{parts}\n\n🚗 <b>VIN:</b> {vin}\n📅 <b>Order date:</b> {date}\n\nPick up parts from warehouse! 🔧'
    },
    'my_assigned_orders': {
        'ru': '📋 <b>Ваши назначенные заказы:</b>\n\n',
        'he': '📋 <b>ההזמנות שהוקצו לך:</b>\n\n',
        'en': '📋 <b>Your assigned orders:</b>\n\n'
    },
    'no_assigned_orders': {
        'ru': '📭 У вас пока нет назначенных заказов.',
        'he': '📭 אין לך הזמנות שהוקצו כרגע.',
        'en': '📭 You have no assigned orders yet.'
    },
    'assigned_order_item': {
        'ru': '{emoji} <b>Заказ #{order_id}</b>\n🚗 VIN: {vin}\n📦 Статус: {status}\n📅 Назначен: {date}\n🔗 <a href="{deeplink}">Открыть</a>\n',
        'he': '{emoji} <b>הזמנה #{order_id}</b>\n🚗 VIN: {vin}\n📦 סטטוס: {status}\n📅 הוקצה: {date}\n🔗 <a href="{deeplink}">פתח</a>\n',
        'en': '{emoji} <b>Order #{order_id}</b>\n🚗 VIN: {vin}\n📦 Status: {status}\n📅 Assigned: {date}\n🔗 <a href="{deeplink}">Open</a>\n'
    },
    'not_a_mechanic': {
        'ru': '❌ Вы не зарегистрированы как механик в системе. Обратитесь к администратору.',
        'he': '❌ אתה לא רשום כמכונאי במערכת. פנה למנהל.',
        'en': '❌ You are not registered as a mechanic in the system. Contact administrator.'
    },
    'opening_order': {
        'ru': '🔗 Открываю заказ #{order_id}...',
        'he': '🔗 פותח הזמנה #{order_id}...',
        'en': '🔗 Opening order #{order_id}...'
    }
}

def get_text(key: str, lang: str = 'ru', **kwargs) -> str:
    """
    Get translated text by key and language.
    
    Args:
        key: Translation key
        lang: Language code (ru, he, en)
        **kwargs: Format parameters for the text
        
    Returns:
        Translated and formatted text. Falls back to Russian if translation not found.
    """
    translation = TRANSLATIONS.get(key, {})
    text = translation.get(lang, translation.get('ru', key))
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    
    return text
