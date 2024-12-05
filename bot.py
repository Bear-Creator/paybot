import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import config

# Настройка логирования
logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger("BOT")
logging.getLogger("httpx").propagate = False

# Функция форматирования списка учасников
# def participants_formating(s):
#     lst = []
#     for i in s.split(","):
#         while i[0] = " ":
#             i = i[1:]
#         lst.append(i)
#     return lst

# Состояния пользователей
user_data = {}

# Функция подсчета стоимости
def calculate_price(ticket_count: int) -> int:
    logger.info(f"Calculating price for {ticket_count} tickets")
    ticket_price = 250  # Цена за один билет
    if ticket_count == 10:
        discount = 0.10  # Скидка 10%
        total_price = ticket_count * ticket_price * (1 - discount)
    else:
        total_price = ticket_count * ticket_price
    logger.info(f"Total price for {ticket_count} tickets: {total_price}")
    return int(total_price)

# Функция для обработки кнопки "Перезапустить бота"
async def restart_via_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Restarting bot via /start")
    query = update.callback_query
    await query.answer()

    # Отправляем новое сообщение с командой /start
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Нажмите сюда -> /start"
    )

# Стартовое сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot")
    keyboard = [
        [InlineKeyboardButton("Купить билет 🎟️", callback_data="buy_ticket")],
        [InlineKeyboardButton("Забронировать столик 🍽️", callback_data="reserve_table")],
        [InlineKeyboardButton("Перезапустить бота 🔄", callback_data="restart_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет, друг! Добро пожаловать во 'Время чудес'! 🎉\n"
        "Ты хочешь присоединиться к нам, я тебе в этом помогу. \n"
        "Выбери что ты хочешь сделать:",
        reply_markup=reply_markup
    )

# Главное меню
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"User {query.from_user.id} selected menu option: {query.data}")

    if query.data == "buy_ticket":
        await show_ticket_options(query, context)
    elif query.data == "reserve_table":
        await query.edit_message_text(f"Для бронирования столиков обращайтесь к @kste0009 \nНажмите -> /start")
    elif query.data == "restart_bot":
        await start(update, context)

# Выбор билетов
async def show_ticket_options(update_or_query, context):
    logger.info("Displaying ticket options")
    keyboard = [
        [InlineKeyboardButton("1 билет 🎟️", callback_data="1_ticket")],
        [InlineKeyboardButton("2 билета 🎟️", callback_data="2_tickets")],
        [InlineKeyboardButton("3 билета 🎟️", callback_data="3_tickets")],
        [InlineKeyboardButton("4 билета 🎟️", callback_data="4_tickets")],
        [InlineKeyboardButton("9+1 билетов 🎟️", callback_data="10_tickets")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(
            "Отлично! Мероприятие пройдёт 10 декабря.\n"
            "Скажи, сколько тебе нужно?\n"
            "P.S. При покупке 10 билетов - скидка 10%",
            reply_markup=reply_markup
        )
    else:
        await update_or_query.edit_message_text(
            "Отлично! Мероприятие пройдёт 10 декабря.\n"
            "Скажи, сколько тебе нужно?\n"
            "P.S. Специально для тайной вечеринке действует акция «9+1». \nПри покупке девяти билетов, десятый идет в подарок🎁",
            reply_markup=reply_markup
        )

# Обработка выбора билетов
async def handle_ticket_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"User {query.from_user.id} selected ticket option: {query.data}")

    user_id = query.from_user.id
    ticket_count = int(query.data.split("_")[0])  # Получаем количество билетов
    user_data[user_id] = {"tickets": ticket_count}

    # Рассчитываем цену
    total_price = calculate_price(ticket_count)
    user_data[user_id]["total_price"] = total_price  # Сохраняем итоговую цену

    await query.edit_message_text(
        f"Отлично! Количество билетов: {ticket_count}.\n"
        f"Итоговая цена: {total_price} py6.\n\n"
        f"Теперь уточним детали. Напиши, пожалуйста, свою фамилию и имя.\n"
        f"Если ты не один, то перечисли через запятую своих друзей, которым ты взял билеты!\n\n"
        f"Например: Иванов Иван, Петрова Анна"
    )
    user_data[user_id]["step"] = "participants"

# Ввод списка участников
async def handle_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_data and user_data[user_id].get("step") == "participants":
        participants = [i.strip() for i in update.message.text.split(",")]
        user_data[user_id]["participants"] = participants

        logger.info(f"User {user_id} provided participants: {participants}")

        await update.message.reply_text(
            f"Список участников принят, проверь, пожалуйста!:\n{chr(10).join(participants)}\n\n"
            "Теперь отправляю тебе реквизиты для оплаты.\n\n"
            f"`{config.card_number}`\n\n"
            "После оплаты, отправь, пожалуйста скриншот в виде фотографии сюда!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Неправильно! Перезапустить бота 🔄", callback_data="restart_bot")]
            ])
        )
        user_data[user_id]["step"] = "payment"
    else:
        logger.warning(f"Unexpected input from user {user_id} at step {user_data.get(user_id, {}).get('step')}")
        await update.message.reply_text("Пожалуйста, выбери действие из меню.")

# Обработка скриншота или других медиа
async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_data.get(user_id) and user_data[user_id].get("step") == "payment":
        ticket_count = user_data[user_id]["tickets"]
        total_price = user_data[user_id]["total_price"]
        participants = user_data[user_id]["participants"]

        logger.info(f"User {user_id} submitted payment proof for {ticket_count} tickets")

        # Сообщение менеджеру с данными о пользователе
        username = update.message.from_user.username
        user_tag = f"@{username}" if username else f"[{update.message.from_user.full_name}](tg://user?id={user_id})"

        # Отправляем данные о пользователе и участниках администратору
        await context.bot.send_message(
            chat_id=config.admin,
            text=(f"Оплата от {user_tag}\n"
                  f"Количество билетов: {ticket_count}\n"
                  f"Цена: {total_price} руб.\n"
                  f"Список участников:\n{chr(10).join(participants)}"),
            parse_mode="Markdown"
        )

        # Проверяем, если это фото
        if update.message.photo:
            # Отправляем фото
            await context.bot.send_photo(chat_id=config.admin, photo=update.message.photo[-1].file_id)
            await update.message.reply_text("Добавили в список присуствующих. Ждём вас 10 декабря в 22:00 в Тренде! \nБудьте нарядными и с хорошим настроением) \nИ не забудьте паспорта!")
        else:
            logger.warning(f"User {user_id} submitted unexpected media type.")
            await update.message.reply_text("Пришлите, пожалуйста, скриншот оплаты.")


# Основная функция
def main():
    application = Application.builder().token(config.token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(restart_via_start, pattern="^restart_bot$"))
    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^(buy_ticket|reserve_table|restart_bot)$"))
    application.add_handler(CallbackQueryHandler(handle_ticket_selection, pattern="^(1_ticket|2_tickets|3_tickets|4_tickets|10_tickets)$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_participants))
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))

    logger.info("Bot started")  
    application.run_polling()

if __name__ == "__main__":
    main()
