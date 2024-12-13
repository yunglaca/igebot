import logging

from aiogram import F, Router
from aiogram.filters import CommandStart, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from app.database import get_db
from app.kb import cancel_kb, ege_inline_kb, main_kb, other_kb
from app.model import EgeScore, User

router = Router()

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Определяем состояния для FSM
class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()


class EgeScoreInput(StatesGroup):
    waiting_for_subject = State()
    waiting_for_score = State()

class ScoreOutOfBorders(Exception):
    pass


def get_user_id(message: Message) -> int:
    """Возвращает user_id, если from_user существует, иначе логирует ошибку."""
    if message.from_user and message.from_user.id:
        return message.from_user.id
    else:
        raise ValueError("Сообщение не содержит идентификатора пользователя.")

def get_message_text(message: Message) -> str:
    """Возвращает текст сообщения, если он существует, иначе логирует предупреждение и возвращает пустую строку."""
    if message.text:
        return message.text.strip()
    else:
        logging.warning("Сообщение не содержит текста.")
        return ""


# Хэндлер команды /start
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Приветственное сообщение и начало работы."""
    logging.info(f"Команда /start от пользователя {get_user_id(message)}")
    await message.answer(
        "Привет! Ты можешь зарегистрироваться, чтобы узнать свои баллы ЕГЭ.", reply_markup=main_kb(get_user_id(message))
    )


# Хэндлер начала регистрации
@router.message(F.text == "Зарегистрироваться")
async def start_registration(message: Message, state: FSMContext) -> None:
    """Начало регистрации: запрашиваем имя."""
    logging.info(f"Пользователь {get_user_id(message)} начал регистрацию.")

    await message.answer("Введите ваше имя:")
    await state.set_state(Registration.waiting_for_name)


# Хэндлер для кнопки "Войти"
@router.message(F.text == "Войти")
async def login(message: Message, state: FSMContext) -> None:
    """Проверка наличия пользователя в базе данных и вывод результатов или предложение внести их."""
    logging.info(f"Пользователь {get_user_id(message)} нажал кнопку 'Войти'.")

    # Проверяем, есть ли пользователь в базе данных
    async for db in get_db():
        logging.info(f"prep user, {get_user_id(message)},{type(get_user_id(message))}")
        result = await db.execute(select(User).where(User.telegram_id == get_user_id(message)))
        user = result.scalars().first()

        if user:
            logging.info(f"user = {user}")
            # Если пользователь существует
            await message.answer(
                "Привет! ты можешь посмотреть или записать свои баллы егэ", reply_markup=other_kb(get_user_id(message))
            )
        else:
            # Если пользователь не найден, предлагаем зарегистрироваться
            await message.answer(
                "Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь для начала.",
                reply_markup=main_kb(get_user_id(message)),
            )


# Хэндлер обработки имени
@router.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext) -> None:
    """Обрабатываем имя пользователя."""
    logging.info(f"Пользователь {get_user_id(message)} ввел имя: {get_message_text(message)}")
    name = get_message_text(message).strip()
    await state.update_data(first_name=name)
    await message.answer("Введите вашу фамилию:")
    await state.set_state(Registration.waiting_for_surname)


# Хэндлер обработки фамилии
@router.message(Registration.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext) -> None:
    """Обрабатываем фамилию и завершаем регистрацию."""
    logging.info(f"Пользователь {get_user_id(message)} ввел фамилию: {get_message_text(message)}")
    surname = get_message_text(message).strip()
    user_data = await state.get_data()
    first_name = user_data.get("first_name")

    async for db in get_db():
        new_user = User(telegram_id=get_user_id(message), first_name=first_name, last_name=surname)
        db.add(new_user)
        await db.commit()

    await message.answer(f"Вы успешно зарегистрированы, {first_name} {surname}!")
    await message.answer("Теперь вы можете ввести свои баллы ЕГЭ. Выберите предмет:", reply_markup=ege_inline_kb())
    await state.set_state(EgeScoreInput.waiting_for_subject)


# Хэндлер для выбора предмета
@router.message(EgeScoreInput.waiting_for_subject)
async def process_subject(message: Message, state: FSMContext) -> None:
    """Обрабатываем выбор предмета."""
    logging.info(f"Пользователь {get_user_id(message)} выбрал предмет: {get_message_text(message)}")
    await state.update_data(subject=get_message_text(message).strip())
    await message.answer(
        "Введите баллы за этот предмет:", reply_markup=cancel_kb()
    )  # Отправляем клавиатуру с кнопкой "Отмена"
    await state.set_state(EgeScoreInput.waiting_for_score)


# Хэндлер для ввода баллов
@router.message(EgeScoreInput.waiting_for_score)
async def process_score(message: Message, state: FSMContext) -> None:
    """Обрабатываем введенные баллы."""
    logging.info(f"Пользователь {get_user_id(message)} ввел баллы: {get_message_text(message)}")

    # Проверка баллов (будет использоваться валидация)
    try:
        score = int(get_message_text(message).strip())
        if score < 0 or score > 100:
            raise ScoreOutOfBorders
    except ScoreOutOfBorders:
        await message.answer("Баллы должны быть в пределах от 0 до 100.")
        return
    except ValueError:
        await message.answer("Ошибка. Пожалуйста, введите валидные баллы.")
        return

    user_data = await state.get_data()
    subject = user_data.get("subject")
    user_id = get_user_id(message)

    # Сохранение баллов в базе данных                                      
    async for db in get_db():
        _user = await db.execute(select(User).where(User.telegram_id == user_id))
        user = _user.scalars().first()
        if user:
            # Проверяем, существует ли уже запись для данного предмета
            existing_entry = await db.execute(
                select(EgeScore).where(EgeScore.user_id == user.id, EgeScore.subject == subject)
            )
            score_entry = existing_entry.scalars().first()

            if score_entry:
                # Если запись существует, обновляем баллы
                score_entry.score = score
                await message.answer(f"Ваши баллы по предмету {subject} обновлены: {score}.")
            else:
                # Если записи нет, создаём новую
                new_score_entry = EgeScore(user_id=user.id, subject=subject, score=score)
                db.add(new_score_entry)
                

            # Сохраняем изменения в базе данных
            await db.commit()

    await message.answer(
        f"Ваши баллы по предмету {subject}: {score} успешно сохранены.", reply_markup=other_kb(get_user_id(message))
    )
    await state.clear()


# Хэндлер просмотра баллов
@router.message(F.text == "Посмотреть баллы")
async def view_score(message: Message, state: FSMContext) -> None:
    """Начало регистрации: запрашиваем имя."""
    logging.info(f"Пользователь {get_user_id(message)} смотрит баллы")
    async for db in get_db():
        _user = await db.execute(select(User).where(User.telegram_id == get_user_id(message)))
        user: User = _user.scalars().first()  # type: ignore
        _scores = await db.execute(select(EgeScore).where(EgeScore.user_id == user.id))
        scores = _scores.scalars().all()
        logging.info(f"score = {scores}")
        if scores:
            # Если у пользователя есть результаты ЕГЭ, показываем их
            result_message = "Ваши результаты ЕГЭ:\n"
            for score in scores:
                result_message += f"{score.subject}: {score.score} баллов\n"
            await message.answer(result_message, reply_markup=other_kb(get_user_id(message)))
        else:
            # Если нет результатов, предлагаем ввести их
            await message.answer(
                "У вас нет результатов ЕГЭ. Пожалуйста, введите свои баллы.", reply_markup=ege_inline_kb()
            )
            await state.set_state(EgeScoreInput.waiting_for_subject)


# Хэндлер записи баллов
@router.message(F.text == "Записать баллы")
async def save_score(message: Message, state: FSMContext) -> None:
    """Начало регистрации: запрашиваем имя."""
    logging.info(f"Пользователь {get_user_id(message)} Записывает баллы")
    async for db in get_db():
        _user = await db.execute(select(User).where(User.telegram_id == get_user_id(message)))
        user: User = _user.scalars().first()  # type: ignore
        _scores = await db.execute(select(EgeScore).where(EgeScore.user_id == user.id))  # type: ignore
        scores = _scores.scalars().all()
        logging.info(f"score = {scores}")
        await message.answer("Пожалуйста, введите свои баллы.", reply_markup=ege_inline_kb())
        await state.set_state(EgeScoreInput.waiting_for_subject)


# Хэндлер для отмены ввода
@router.message(F.text == "Отмена")
async def cancel_registration(message: Message, state: FSMContext) -> None:
    """Отмена ввода баллов и возврат в главное меню."""
    logging.info(f"Пользователь {get_user_id(message)} отменил ввод баллов.")
    await message.answer("Ввод баллов отменен. Вы можете начать снова.", reply_markup=main_kb(get_user_id(message)))
    await state.clear()


# Хэндлер для ввода баллов ЕГЭ
@router.message(F.text == "Внести баллы ЕГЭ")
async def start_ege_input(message: Message, state: FSMContext) -> None:
    """Запрос на выбор предмета для ввода баллов."""
    logging.info(f"Пользователь {get_user_id(message)} начал вводить баллы ЕГЭ.")
    await message.answer("Выберите предмет для ввода баллов:", reply_markup=ege_inline_kb())
    await state.set_state(EgeScoreInput.waiting_for_subject)


# Хэндлер для отмены ввода
@router.message(F.text == "Отмена")
async def cancel_input(message: Message, state: FSMContext) -> None:
    """Отмена ввода данных и возврат в главное меню."""
    await state.clear()
    await message.answer(
        "Ввод данных отменен. Вы можете вернуться в главное меню.", reply_markup=main_kb(get_user_id(message))
    )


class StartsWithFilter(Filter):
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.startswith(self.prefix)  # type: ignore


@router.callback_query(StartsWithFilter(prefix="ege_"))
async def handle_ege_subject(callback: CallbackQuery, state: FSMContext) -> None:
    """Обрабатываем выбор предмета для ввода баллов."""
    # Получаем название предмета
    subject = callback.data[len("ege_"):]  # type: ignore
    await state.update_data(subject=subject)

    await callback.message.answer(f"Вы выбрали предмет: {subject}. Введите баллы (0-100):")  # type: ignore
    await state.set_state(EgeScoreInput.waiting_for_score)

    await callback.answer()



