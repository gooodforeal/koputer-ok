"""
Telegram бот для авторизации пользователей
"""

import logging
from typing import Optional
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
import httpx

from telegram_bot.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Глобальные переменные для бота (инициализируются в start_bot)
bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None


async def cmd_start(message: types.Message):
    """
    Обработчик команды /start
    Если есть параметр - это токен авторизации, иначе приветствие
    """
    # Получаем параметр после /start
    args = message.text.split(maxsplit=1)

    if len(args) > 1 and args[1]:
        # Есть параметр - это авторизация
        auth_token = args[1]
        await handle_auth(message, auth_token)
    else:
        # Обычное приветствие
        await message.answer(
            "👋 Привет! Я бот для авторизации.\n\n"
            "Чтобы войти в систему:\n"
            "1. Откройте страницу входа в веб-приложении\n"
            "2. Нажмите кнопку «Войти через Telegram»\n"
            "3. Вы будете перенаправлены сюда автоматически"
        )


async def handle_auth(message: types.Message, auth_token: str):
    """
    Обрабатывает процесс авторизации пользователя через API бекенда
    """
    try:
        if not bot:
            logger.error("Бот не инициализирован!")
            await message.answer(
                "❌ Ошибка: бот не инициализирован. Обратитесь в поддержку."
            )
            return

        user = message.from_user
        logger.info(
            f"Обработка авторизации для пользователя {user.id} ({user.username}) с токеном {auth_token[:10]}..."
        )

        # Получаем фото профиля пользователя
        photo_url = None
        try:
            photos = await bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                file = await bot.get_file(photos.photos[0][-1].file_id)
                photo_url = f"https://api.telegram.org/file/bot{settings.telegram_bot_token}/{file.file_path}"
        except Exception as e:
            logger.warning(f"Не удалось получить фото профиля: {e}")

        # Формируем полное имя
        full_name = user.first_name or "Пользователь"
        if user.last_name:
            full_name += f" {user.last_name}"

        # Отправляем запрос на бекенд для авторизации
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{settings.backend_url}/api/auth/telegram/authorize",
                    json={
                        "auth_token": auth_token,
                        "telegram_id": str(user.id),
                        "username": user.username,
                        "first_name": user.first_name or "",
                        "last_name": user.last_name or "",
                        "photo_url": photo_url,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Авторизация успешна для пользователя {user.id}")
                    await message.answer(
                        "✅ Авторизация успешна!\n\n"
                        f"Привет, {full_name}!\n\n"
                        "Вернитесь в окно браузера - авторизация завершена!\n\n"
                        "Окно с ботом можно закрыть."
                    )
                elif response.status_code == 404:
                    logger.warning(f"Токен {auth_token[:10]}... не найден или истек")
                    await message.answer(
                        "❌ Ошибка авторизации!\n\n"
                        "Возможные причины:\n"
                        "• Ссылка авторизации устарела (действует 5 минут)\n"
                        "• Ссылка уже была использована\n\n"
                        "Попробуйте начать процесс авторизации заново."
                    )
                else:
                    error_text = response.text
                    logger.error(
                        f"Ошибка авторизации: {response.status_code} - {error_text}"
                    )
                    await message.answer(
                        "❌ Произошла ошибка при авторизации.\n"
                        "Пожалуйста, попробуйте позже или обратитесь в поддержку."
                    )

            except httpx.TimeoutException:
                logger.error("Таймаут при запросе к бекенду")
                await message.answer(
                    "❌ Превышено время ожидания ответа от сервера.\n"
                    "Пожалуйста, попробуйте позже."
                )
            except httpx.RequestError as e:
                logger.error(f"Ошибка при запросе к бекенду: {e}")
                await message.answer(
                    "❌ Не удалось соединиться с сервером.\n"
                    "Пожалуйста, попробуйте позже или обратитесь в поддержку."
                )

    except Exception as e:
        logger.error(f"Ошибка при авторизации: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при авторизации.\n"
            "Пожалуйста, попробуйте позже или обратитесь в поддержку."
        )


async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        "🤖 Помощь по использованию бота\n\n"
        "Этот бот используется для авторизации в веб-приложении.\n\n"
        "Как войти:\n"
        "1. Откройте страницу входа в веб-приложении\n"
        "2. Нажмите «Войти через Telegram»\n"
        "3. Вы будете перенаправлены в этот бот\n"
        "4. Бот автоматически авторизует вас\n"
        "5. Нажмите кнопку для возврата в приложение\n\n"
        "По вопросам обращайтесь в поддержку."
    )


async def echo_handler(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Я не понимаю эту команду 🤔\n\n"
        "Используйте:\n"
        "/start - начать работу\n"
        "/help - получить помощь"
    )


async def start_bot():
    """Запускает бота"""
    global bot, dp

    logger.info("Запуск Telegram бота...")

    try:
        # Проверяем наличие токена
        if not settings.telegram_bot_token:
            logger.error("TELEGRAM_BOT_TOKEN не установлен в настройках!")
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен")

        # Инициализируем бота и диспетчер
        bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.HTML)
        dp = Dispatcher()

        # Регистрируем обработчики
        dp.message.register(cmd_start, CommandStart())
        dp.message.register(cmd_help, Command("help"))
        dp.message.register(echo_handler)

        logger.info("Telegram бот инициализирован")

        # Удаляем вебхук если есть
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Вебхук удален, запускаем polling...")

        # Запускаем polling
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
        raise


async def stop_bot():
    """Останавливает бота"""
    global bot, dp

    logger.info("Остановка Telegram бота...")
    if bot:
        try:
            await bot.session.close()
        except Exception as e:
            logger.error(f"Ошибка при остановке бота: {e}")

    bot = None
    dp = None


if __name__ == "__main__":
    import asyncio

    asyncio.run(start_bot())
