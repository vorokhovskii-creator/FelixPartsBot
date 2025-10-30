import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from config import (
    BOT_TOKEN,
    BACKEND_URL,
    CATEGORIES,
    CATEGORY,
    PARTS_SELECTION,
    VIN_INPUT,
    ORIGINAL_CHOICE,
    PHOTO_UPLOAD,
    CONFIRMATION
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def load_categories_from_api():
    """Загрузить категории из backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/categories", timeout=5)
        if response.status_code == 200:
            categories = response.json()
            result = {}
            for cat in categories:
                key = f"{cat['icon']} {cat['name_ru']}"
                result[key] = {'id': cat['id'], 'parts': []}
            return result
    except Exception as e:
        logger.warning(f"Failed to load categories from API: {e}")
    
    logger.info("Using fallback categories from config.py")
    result = {}
    for key in CATEGORIES.keys():
        result[key] = {'id': None, 'parts': []}
    return result


async def load_parts_from_api(category_id, category_name):
    """Загрузить детали категории из API"""
    if category_id:
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/parts",
                params={'category_id': category_id},
                timeout=5
            )
            if response.status_code == 200:
                parts = response.json()
                return [p['name_ru'] for p in parts if p['is_common']]
        except Exception as e:
            logger.warning(f"Failed to load parts from API: {e}")
    
    logger.info(f"Using fallback parts from config.py for {category_name}")
    return CATEGORIES.get(category_name, [])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data['mechanic_name'] = user.first_name
    context.user_data['telegram_id'] = str(user.id)
    
    keyboard = [
        [InlineKeyboardButton("🆕 Новый заказ", callback_data='new_order')],
        [InlineKeyboardButton("📋 Мои заказы", callback_data='my_orders')],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
    ]
    
    await update.message.reply_text(
        "👋 Привет! Я Felix Parts Bot — помогу заказать запчасти.\n\n"
        "Выбери действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['selected_parts'] = []
    
    categories = await load_categories_from_api()
    context.user_data['categories'] = categories
    
    keyboard = [
        [InlineKeyboardButton(cat, callback_data=f'cat_{i}')] 
        for i, cat in enumerate(categories.keys())
    ]
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data='cancel')])
    
    await query.message.reply_text(
        "🔍 Выбери категорию запчастей:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CATEGORY


async def select_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    categories = context.user_data.get('categories', {})
    cat_index = int(query.data.split('_')[1])
    category_name = list(categories.keys())[cat_index]
    
    context.user_data['category'] = category_name
    context.user_data['category_id'] = categories[category_name]['id']
    context.user_data['selected_parts'] = []
    
    parts = await load_parts_from_api(
        categories[category_name]['id'],
        category_name
    )
    context.user_data['available_parts'] = parts
    
    await show_parts_keyboard(query, context)
    return PARTS_SELECTION


async def show_parts_keyboard(query, context: ContextTypes.DEFAULT_TYPE):
    category = context.user_data['category']
    parts = context.user_data.get('available_parts', [])
    
    selected = context.user_data.get('selected_parts', [])
    keyboard = []
    
    for part in parts:
        check = "✅ " if part in selected else ""
        keyboard.append([InlineKeyboardButton(
            f"{check}{part}", 
            callback_data=f'part_{part}'
        )])
    
    keyboard.append([InlineKeyboardButton("➕ Добавить вручную", callback_data='manual')])
    keyboard.append([InlineKeyboardButton("➡️ Далее", callback_data='next_vin')])
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data='cancel')])
    
    await query.message.edit_text(
        f"Выбери детали из списка (можно несколько):\n\n"
        f"Выбрано: {len(selected)}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def toggle_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    part = query.data.replace('part_', '')
    selected = context.user_data.get('selected_parts', [])
    
    if part in selected:
        selected.remove(part)
    else:
        selected.append(part)
    
    context.user_data['selected_parts'] = selected
    
    await show_parts_keyboard(query, context)
    return PARTS_SELECTION


async def manual_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['waiting_manual_part'] = True
    
    await query.message.reply_text(
        "✏️ Введи название детали вручную:"
    )
    return PARTS_SELECTION


async def add_manual_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_manual_part'):
        return PARTS_SELECTION
    
    manual_part = update.message.text.strip()
    
    if manual_part:
        selected = context.user_data.get('selected_parts', [])
        selected.append(manual_part)
        context.user_data['selected_parts'] = selected
        context.user_data['waiting_manual_part'] = False
        
        keyboard = [
            [InlineKeyboardButton("✅ Продолжить выбор", callback_data='continue_selection')],
            [InlineKeyboardButton("➡️ Далее", callback_data='next_vin')]
        ]
        
        await update.message.reply_text(
            f"✅ Добавлено: {manual_part}\n\n"
            f"Всего выбрано: {len(selected)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    return PARTS_SELECTION


async def continue_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await show_parts_keyboard(query, context)
    return PARTS_SELECTION


async def input_vin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    selected = context.user_data.get('selected_parts', [])
    
    if len(selected) == 0:
        await query.message.reply_text(
            "❌ Выбери хотя бы одну деталь!"
        )
        await show_parts_keyboard(query, context)
        return PARTS_SELECTION
    
    await query.message.reply_text(
        "🚗 Введи VIN автомобиля (минимум 4 символа):"
    )
    return VIN_INPUT


async def process_vin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vin = update.message.text.strip()
    
    if len(vin) < 4:
        await update.message.reply_text(
            "❌ VIN слишком короткий. Введи минимум 4 символа:"
        )
        return VIN_INPUT
    
    context.user_data['vin'] = vin
    
    keyboard = [
        [InlineKeyboardButton("✨ Оригинал", callback_data='original_yes')],
        [InlineKeyboardButton("🔧 Не оригинал", callback_data='original_no')]
    ]
    
    await update.message.reply_text(
        "Какие запчасти нужны?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ORIGINAL_CHOICE


async def original_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    is_original = query.data == 'original_yes'
    context.user_data['is_original'] = is_original
    
    keyboard = [
        [InlineKeyboardButton("📸 Загрузить фото", callback_data='upload_photo')],
        [InlineKeyboardButton("⏭️ Пропустить", callback_data='skip_photo')]
    ]
    
    await query.message.reply_text(
        "Хочешь загрузить фото детали?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PHOTO_UPLOAD


async def request_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        "📸 Отправь фото детали:"
    )
    return PHOTO_UPLOAD


async def upload_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        context.user_data['photo_url'] = file.file_path
        
        await update.message.reply_text("✅ Фото получено!")
    
    await show_confirmation(update, context)
    return CONFIRMATION


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['photo_url'] = None
    await show_confirmation(update, context)
    return CONFIRMATION


async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    
    summary = (
        f"📋 <b>Проверь заказ:</b>\n\n"
        f"👤 Механик: {data['mechanic_name']}\n"
        f"📦 Категория: {data['category']}\n"
        f"🚗 VIN: {data['vin']}\n"
        f"🔧 Детали:\n"
    )
    
    for part in data['selected_parts']:
        summary += f"  • {part}\n"
    
    summary += f"\n{'✨ Оригинал' if data['is_original'] else '🔧 Не оригинал'}\n"
    if data.get('photo_url'):
        summary += "📸 Фото прикреплено\n"
    
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data='confirm')],
        [InlineKeyboardButton("❌ Отменить", callback_data='cancel')]
    ]
    
    if update.callback_query:
        await update.callback_query.message.reply_text(
            summary,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            summary,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = context.user_data
    
    order_data = {
        "mechanic_name": data['mechanic_name'],
        "telegram_id": data['telegram_id'],
        "category": data['category'],
        "vin": data['vin'],
        "selected_parts": data['selected_parts'],
        "is_original": data['is_original'],
        "photo_url": data.get('photo_url')
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/orders",
            json=order_data,
            timeout=10
        )
        
        if response.status_code == 201:
            order = response.json()
            await query.message.reply_text(
                f"✅ Заказ №{order['id']} создан!\n\n"
                f"Ожидай уведомление о готовности.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🆕 Новый заказ", callback_data='new_order')
                ]])
            )
        else:
            error_msg = response.json().get('error', 'Неизвестная ошибка')
            await query.message.reply_text(
                f"❌ Ошибка создания заказа: {error_msg}"
            )
    except requests.exceptions.Timeout:
        await query.message.reply_text(
            "❌ Превышено время ожидания ответа от сервера. Попробуй позже."
        )
    except requests.exceptions.ConnectionError:
        await query.message.reply_text(
            "❌ Не удается подключиться к серверу. Проверь соединение."
        )
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        await query.message.reply_text(
            f"❌ Ошибка связи с сервером. Попробуй позже."
        )
    
    context.user_data.clear()
    return ConversationHandler.END


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    telegram_id = str(update.effective_user.id)
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/orders",
            params={"telegram_id": telegram_id},
            timeout=10
        )
        
        if response.status_code == 200:
            orders = response.json()
            
            if not orders:
                await query.message.reply_text(
                    "У тебя пока нет заказов."
                )
                return
            
            text = "📋 <b>Твои заказы:</b>\n\n"
            for order in orders:
                status_emoji = {
                    'новый': '🆕',
                    'в работе': '⏳',
                    'готов': '✅',
                    'выдан': '📦'
                }
                
                text += (
                    f"{status_emoji.get(order['status'], '❓')} "
                    f"<b>Заказ №{order['id']}</b>\n"
                    f"VIN: {order['vin']}\n"
                    f"Статус: {order['status']}\n"
                    f"Дата: {order['created_at'][:10]}\n\n"
                )
            
            await query.message.reply_text(
                text,
                parse_mode='HTML'
            )
        else:
            await query.message.reply_text(
                "❌ Ошибка загрузки заказов."
            )
    except requests.exceptions.Timeout:
        await query.message.reply_text(
            "❌ Превышено время ожидания ответа от сервера."
        )
    except requests.exceptions.ConnectionError:
        await query.message.reply_text(
            "❌ Не удается подключиться к серверу."
        )
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        await query.message.reply_text(
            f"❌ Ошибка загрузки заказов."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    help_text = (
        "ℹ️ <b>Помощь</b>\n\n"
        "Felix Parts Bot помогает заказывать запчасти для СТО.\n\n"
        "<b>Основные команды:</b>\n"
        "• 🆕 Новый заказ - создать заказ на запчасти\n"
        "• 📋 Мои заказы - просмотр твоих заказов\n"
        "• ℹ️ Помощь - это сообщение\n\n"
        "<b>Процесс заказа:</b>\n"
        "1️⃣ Выбери категорию запчастей\n"
        "2️⃣ Отметь нужные детали из списка\n"
        "3️⃣ Введи VIN автомобиля\n"
        "4️⃣ Укажи тип запчастей (оригинал/не оригинал)\n"
        "5️⃣ Загрузи фото (опционально)\n"
        "6️⃣ Подтверди заказ\n\n"
        "По вопросам обращайся к администратору."
    )
    
    await query.message.reply_text(
        help_text,
        parse_mode='HTML'
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    
    await query.message.reply_text(
        "❌ Действие отменено.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🆕 Новый заказ", callback_data='new_order')
        ]])
    )
    return ConversationHandler.END


def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_category, pattern='^new_order$')],
        states={
            CATEGORY: [CallbackQueryHandler(select_parts, pattern='^cat_')],
            PARTS_SELECTION: [
                CallbackQueryHandler(toggle_part, pattern='^part_'),
                CallbackQueryHandler(input_vin, pattern='^next_vin$'),
                CallbackQueryHandler(manual_input, pattern='^manual$'),
                CallbackQueryHandler(continue_selection, pattern='^continue_selection$'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_manual_part)
            ],
            VIN_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_vin)],
            ORIGINAL_CHOICE: [CallbackQueryHandler(original_choice, pattern='^original_')],
            PHOTO_UPLOAD: [
                MessageHandler(filters.PHOTO, upload_photo),
                CallbackQueryHandler(request_photo, pattern='^upload_photo$'),
                CallbackQueryHandler(skip_photo, pattern='^skip_photo$')
            ],
            CONFIRMATION: [CallbackQueryHandler(confirm_order, pattern='^confirm$')]
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern='^cancel$')]
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(my_orders, pattern='^my_orders$'))
    application.add_handler(CallbackQueryHandler(help_command, pattern='^help$'))
    
    logger.info("Bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
