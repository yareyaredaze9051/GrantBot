import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# База данных олимпиад (можно заменить на подключение к реальной БД)
olympiads_db = {
    "Москва": {
        "Всерос": {
            "level": 1,
            "benefits": "Зачисление без вступительных испытаний (БВИ) на соответствующие направления",
            "subjects": ["Математика", "Физика", "Химия", "Биология", "Информатика", "Литература", "История",
                         "Обществознание"]
        },
        "Олимпиада СПбГУ": {
            "level": 2,
            "benefits": "100 баллов по профильному предмету или БВИ в зависимости от уровня и степени диплома",
            "subjects": ["Математика", "Физика", "Химия", "Биология", "Экономика", "Право"]
        },
        "Высшая проба": {
            "level": 1,
            "benefits": "БВИ или 100 баллов по профильному предмету",
            "subjects": ["Математика", "Экономика", "Право", "Философия", "Социология"]
        },
        "Физтех": {
            "level": 2,
            "benefits": "Дополнительные баллы или БВИ в МФТИ",
            "subjects": ["Математика", "Физика"]
        },
        "Ломоносов": {
            "level": 1,
            "benefits": "БВИ или 100 баллов по профильному предмету",
            "subjects": ["Математика", "Физика", "Химия", "Биология", "Геология", "Психология"]
    }},
    "Нижний Новгород": {
        "Национальная Технологическая Олимпиада Профиль Технологии Дополненной Реальности": {
            "level": 3,
            "benefits": "БВИ или 100 баллов по профильному предмету в некоторые ВУЗы",
            "subjects": ["Информатика"]

        },
        "Будущие исследователи - Будущее науки": {
            "level": 2,
            "benefits": "БВИ или 100 баллов по профильному предмету в некоторые ВУЗы",
            "subjects": ["Физика", "Химия", "История"]
    }
    },
    "Санкт-Петербург": {
        "Открытая Олимпиада Школьников по информатике ИТМО": {
            "level": 1,
            "benefits": "Зачисление без вступительных испытаний (БВИ) на соответствующие направления",
            "subjects": ["Информатика"]
    },
        "Олимпиада школьников СПбГУ":{
            "level": 1,
            "benefits": "Зачисление без вступительных испытаний (БВИ) на соответствующие направления",
            "subjects": ["Информатика", "Математика", "Физика"]
    },
        "Отраслевая олимпиада школьников 'Газпром'":{
            "level": 3,
            "benefits": "БВИ или 100 баллов по профильному предмету в некоторые ВУЗы",
            "subjects": ["Математика", "Физика", "Химия", "Инженерное дело"]
        }
    }
}


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот, который поможет тебе узнать о льготах при поступлении по олимпиадам.\n\n"
        "Доступные команды:\n"
        "/olympiads - список олимпиад с льготами\n"
        "/benefits - узнать льготы конкретной олимпиады"
    )


# Команда /olympiads - список олимпиад
async def olympiads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите название города после команды, например: /olympiads Москва")
        return
    keyboard = []
    city = " ".join(context.args)
    # Создаем кнопки для каждой олимпиады
    for olympiad in olympiads_db[city]:
        keyboard.append([InlineKeyboardButton(olympiad, callback_data=f"olympiad_{olympiad}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    print(reply_markup)
    await update.message.reply_text(
        "Список олимпиад, дающих льготы при поступлении:",
        reply_markup=reply_markup
    )


# Команда /benefits - поиск льгот по названию
async def benefits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите название олимпиады после команды, например: /benefits Всерос")
        return
    found = False
    olympiad_name = " ".join(context.args)
    for city in olympiads_db.keys():
        if olympiad_name in olympiads_db[city].keys():
            data = olympiads_db[city][olympiad_name]
            await send_olympiad_info(update, olympiad_name, data)
            found = True
            break

    if not found:
        await update.message.reply_text(
            "Олимпиада не найдена. Попробуйте другое название или посмотрите список олимпиад командой /olympiads")


# Обработчик нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("olympiad_"):
        olympiad_name = query.data[9:]
        if olympiad_name in olympiads_db:
            await send_olympiad_info_query(query, olympiad_name, olympiads_db[olympiad_name])
        else:
            await query.edit_message_text("Информация об этой олимпиаде временно недоступна")


# Функция для отправки информации об олимпиаде (для команды /benefits)
async def send_olympiad_info(update: Update, name: str, data: dict) -> None:
    message = (
        f"🏆 <b>{name}</b>\n\n"
        f"🔹 Уровень: {data['level']}\n"
        f"🔹 Льготы: {data.get('benefits', 'нет информации')}\n"
        f"🔹 Предметы: {', '.join(data['subjects'])}\n\n"
        "Для получения актуальной информации уточните на сайте вуза или в правилах приема."
    )
    await update.message.reply_text(message, parse_mode='HTML')


# Функция для отправки информации об олимпиаде (для inline-кнопок)
async def send_olympiad_info_query(query, name: str, data: dict) -> None:
    message = (
        f"🏆 <b>{name}</b>\n\n"
        f"🔹 Уровень: {data['level']}\n"
        f"🔹 Льготы: {data.get('benefits', 'нет информации')}\n"
        f"🔹 Предметы: {', '.join(data['subjects'])}\n\n"
        "Для получения актуальной информации уточните на сайте вуза или в правилах приема."
    )
    await query.edit_message_text(message, parse_mode='HTML')


# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")


def main() -> None:
    # Создаем приложение и передаем токен бота
    application = Application.builder().token("8152366556:AAGqqyyJNYOUwESXyaTxCb5Yn4r_92L15so").build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("olympiads", olympiads))
    application.add_handler(CommandHandler("benefits", benefits))
    application.add_handler(CallbackQueryHandler(button))

    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()