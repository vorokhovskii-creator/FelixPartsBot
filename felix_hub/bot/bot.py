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
from translations import get_text

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data['mechanic_name'] = user.first_name
    context.user_data['telegram_id'] = str(user.id)
    
    # If language not set, show language selection
    if 'language' not in context.user_data:
        return await select_language(update, context)
    
    # Show main menu in selected language
    lang = context.user_data.get('language', 'ru')
    keyboard = [
        [InlineKeyboardButton(get_text('new_order', lang), callback_data='new_order')],
        [InlineKeyboardButton(get_text('my_orders', lang), callback_data='my_orders')],
        [InlineKeyboardButton(get_text('change_language', lang), callback_data='change_language')],
        [InlineKeyboardButton(get_text('help', lang), callback_data='help')]
    ]
    
    await update.message.reply_text(
        get_text('welcome', lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Language selection screen"""
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("🇮🇱 עברית", callback_data='lang_he')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')]
    ]
    
    text = get_text('select_language', 'ru')
    
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set selected language"""
    query = update.callback_query
    lang = query.data.split('_')[1]  # lang_ru -> ru
    
    context.user_data['language'] = lang
    
    await query.answer()
    await query.message.delete()
    
    # Show main menu
    keyboard = [
        [InlineKeyboardButton(get_text('new_order', lang), callback_data='new_order')],
        [InlineKeyboardButton(get_text('my_orders', lang), callback_data='my_orders')],
        [InlineKeyboardButton(get_text('change_language', lang), callback_data='change_language')],
        [InlineKeyboardButton(get_text('help', lang), callback_data='help')]
    ]
    
    await query.message.reply_text(
        get_text('welcome', lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get('language', 'ru')
    context.user_data['selected_parts'] = []
    
    keyboard = [
        [InlineKeyboardButton(cat, callback_data=f'cat_{i}')] 
        for i, cat in enumerate(CATEGORIES.keys())
    ]
    keyboard.append([InlineKeyboardButton(get_text('cancel', lang), callback_data='cancel')])
    
    await query.message.reply_text(
        get_text('select_category', lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CATEGORY


async def select_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cat_index = int(query.data.split('_')[1])
    category = list(CATEGORIES.keys())[cat_index]
    context.user_data['category'] = category
    context.user_data['selected_parts'] = []
    
    await show_parts_keyboard(query, context)
    return PARTS_SELECTION


async def show_parts_keyboard(query, context: ContextTypes.DEFAULT_TYPE):
    category = context.user_data['category']
    parts = CATEGORIES[category]
    lang = context.user_data.get('language', 'ru')
    
    selected = context.user_data.get('selected_parts', [])
    keyboard = []
    
    for part in parts:
        check = "✅ " if part in selected else ""
        keyboard.append([InlineKeyboardButton(
            f"{check}{part}", 
            callback_data=f'part_{part}'
        )])
    
    keyboard.append([InlineKeyboardButton(get_text('add_manual', lang), callback_data='manual')])
    keyboard.append([InlineKeyboardButton(get_text('next', lang), callback_data='next_vin')])
    keyboard.append([InlineKeyboardButton(get_text('cancel', lang), callback_data='cancel')])
    
    await query.message.edit_text(
        get_text('select_parts', lang, count=len(selected)),
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
    
    lang = context.user_data.get('language', 'ru')
    context.user_data['waiting_manual_part'] = True
    
    await query.message.reply_text(
        get_text('enter_manual_part', lang)
    )
    return PARTS_SELECTION


async def add_manual_part(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_manual_part'):
        return PARTS_SELECTION
    
    lang = context.user_data.get('language', 'ru')
    manual_part = update.message.text.strip()
    
    if manual_part:
        selected = context.user_data.get('selected_parts', [])
        selected.append(manual_part)
        context.user_data['selected_parts'] = selected
        context.user_data['waiting_manual_part'] = False
        
        keyboard = [
            [InlineKeyboardButton(get_text('continue_selection', lang), callback_data='continue_selection')],
            [InlineKeyboardButton(get_text('next', lang), callback_data='next_vin')]
        ]
        
        await update.message.reply_text(
            get_text('manual_part_added', lang, part=manual_part, count=len(selected)),
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
    
    lang = context.user_data.get('language', 'ru')
    selected = context.user_data.get('selected_parts', [])
    
    if len(selected) == 0:
        await query.message.reply_text(
            get_text('select_at_least_one', lang)
        )
        await show_parts_keyboard(query, context)
        return PARTS_SELECTION
    
    await query.message.reply_text(
        get_text('enter_vin', lang)
    )
    return VIN_INPUT


async def process_vin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('language', 'ru')
    vin = update.message.text.strip()
    
    if len(vin) < 4:
        await update.message.reply_text(
            get_text('vin_too_short', lang)
        )
        return VIN_INPUT
    
    context.user_data['vin'] = vin
    
    keyboard = [
        [InlineKeyboardButton(get_text('original', lang), callback_data='original_yes')],
        [InlineKeyboardButton(get_text('not_original', lang), callback_data='original_no')]
    ]
    
    await update.message.reply_text(
        get_text('parts_type_question', lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ORIGINAL_CHOICE


async def original_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get('language', 'ru')
    is_original = query.data == 'original_yes'
    context.user_data['is_original'] = is_original
    
    keyboard = [
        [InlineKeyboardButton(get_text('upload_photo', lang), callback_data='upload_photo')],
        [InlineKeyboardButton(get_text('skip_photo', lang), callback_data='skip_photo')]
    ]
    
    await query.message.reply_text(
        get_text('photo_question', lang),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PHOTO_UPLOAD


async def request_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get('language', 'ru')
    await query.message.reply_text(
        get_text('send_photo', lang)
    )
    return PHOTO_UPLOAD


async def upload_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('language', 'ru')
    if update.message.photo:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        context.user_data['photo_url'] = file.file_path
        
        await update.message.reply_text(get_text('photo_received', lang))
    
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
    lang = data.get('language', 'ru')
    
    parts_text = "\n".join([f"  • {part}" for part in data['selected_parts']])
    original_text = get_text('original_yes' if data['is_original'] else 'original_no', lang)
    photo_text = get_text('photo_attached', lang) if data.get('photo_url') else ""
    
    summary = get_text('check_order', lang,
        mechanic=data['mechanic_name'],
        category=data['category'],
        vin=data['vin'],
        parts=parts_text,
        original_text=original_text,
        photo_text=photo_text
    )
    
    keyboard = [
        [InlineKeyboardButton(get_text('confirm', lang), callback_data='confirm')],
        [InlineKeyboardButton(get_text('cancel', lang), callback_data='cancel')]
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
    lang = data.get('language', 'ru')
    
    order_data = {
        "mechanic_name": data['mechanic_name'],
        "telegram_id": data['telegram_id'],
        "category": data['category'],
        "vin": data['vin'],
        "selected_parts": data['selected_parts'],
        "is_original": data['is_original'],
        "photo_url": data.get('photo_url'),
        "language": lang
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
                get_text('order_created', lang, order_id=order['id']),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text('new_order', lang), callback_data='new_order')
                ]])
            )
        else:
            error_msg = response.json().get('error', 'Неизвестная ошибка')
            await query.message.reply_text(
                get_text('order_creation_error', lang, error=error_msg)
            )
    except requests.exceptions.Timeout:
        await query.message.reply_text(
            get_text('timeout_error', lang)
        )
    except requests.exceptions.ConnectionError:
        await query.message.reply_text(
            get_text('connection_error', lang)
        )
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        await query.message.reply_text(
            get_text('server_error', lang)
        )
    
    # Clear user_data but preserve language
    saved_lang = context.user_data.get('language', 'ru')
    context.user_data.clear()
    context.user_data['language'] = saved_lang
    return ConversationHandler.END


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get('language', 'ru')
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
                    get_text('no_orders', lang)
                )
                return
            
            text = get_text('your_orders', lang)
            for order in orders:
                status_emoji = {
                    'новый': '🆕',
                    'в работе': '⏳',
                    'готов': '✅',
                    'выдан': '📦'
                }
                
                text += get_text('order_item', lang,
                    emoji=status_emoji.get(order['status'], '❓'),
                    order_id=order['id'],
                    vin=order['vin'],
                    status=order['status'],
                    date=order['created_at'][:10]
                )
            
            await query.message.reply_text(
                text,
                parse_mode='HTML'
            )
        else:
            await query.message.reply_text(
                get_text('orders_load_error', lang)
            )
    except requests.exceptions.Timeout:
        await query.message.reply_text(
            get_text('timeout_error', lang)
        )
    except requests.exceptions.ConnectionError:
        await query.message.reply_text(
            get_text('connection_error', lang)
        )
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        await query.message.reply_text(
            get_text('orders_load_error', lang)
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get('language', 'ru')
    help_text = get_text('help_text', lang)
    
    await query.message.reply_text(
        help_text,
        parse_mode='HTML'
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get('language', 'ru')
    
    # Clear user_data but preserve language
    saved_lang = context.user_data.get('language', 'ru')
    context.user_data.clear()
    context.user_data['language'] = saved_lang
    
    await query.message.reply_text(
        get_text('action_cancelled', lang),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(get_text('new_order', lang), callback_data='new_order')
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
    application.add_handler(CallbackQueryHandler(select_language, pattern='^change_language$'))
    application.add_handler(CallbackQueryHandler(set_language, pattern='^lang_'))
    logger.info("Bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
