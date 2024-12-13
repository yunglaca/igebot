from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_kb(user_telegram_id: int) -> ReplyKeyboardMarkup:
    """Основная клавиатура с кнопками для входа и регистрации."""
    kb_list = [
        [KeyboardButton(text="Войти"), KeyboardButton(text="Зарегистрироваться")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Воспользуйтесь меню:"
    )
    return keyboard


def other_kb(user_telegram_id: int) -> ReplyKeyboardMarkup:
    kb_list = [
        [KeyboardButton(text="Посмотреть баллы"), KeyboardButton(text="Записать баллы")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Воспользуйтесь меню:"
    )
    return keyboard


def ege_inline_kb() -> InlineKeyboardMarkup:
    """Клавиатура для ввода баллов ЕГЭ (выбор предмета)."""
    subjects_list = [
        "Русский язык",
        "Математика База",
        "Математика Профиль",
        "Физика",
        "Химия",
        "Биология",
        "Литература",
        "Обществознание",
        "История",
        "География",
        "Информатика",
        "Иностранный язык (английский)",
        "Иностранный язык (немецкий)",
        "Иностранный язык (французский)",
        "Иностранный язык (испанский)",
        "Иностранный язык (китайский)",
    ]


    subject_buttons = [
        [InlineKeyboardButton(text=subject, callback_data=f"ege_{subject}")] for subject in subjects_list
    ]

    # Создаем объект InlineKeyboardMarkup и организуем кнопки по строкам
    subject_kb = InlineKeyboardMarkup(inline_keyboard=subject_buttons, row_width=2)

    return subject_kb


def cancel_kb() -> ReplyKeyboardMarkup:
    """Клавиатура для отмены ввода и возврата в главное меню."""
    cancel_button = [KeyboardButton(text="Отмена")]
    cancel_kb = ReplyKeyboardMarkup(
        keyboard=[cancel_button],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Отмена",
    )
    return cancel_kb
