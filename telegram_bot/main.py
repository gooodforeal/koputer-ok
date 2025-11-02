"""
Точка входа для Telegram бота
"""
import asyncio
import signal
import logging
from telegram_bot.bot import start_bot, stop_bot

logger = logging.getLogger(__name__)

# Глобальная переменная для хранения задачи бота
bot_task = None


def signal_handler(sig, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info("Получен сигнал остановки, завершаем работу...")
    if bot_task:
        bot_task.cancel()


async def main():
    """Основная функция запуска бота"""
    global bot_task
    
    # Устанавливаем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        bot_task = asyncio.create_task(start_bot())
        await bot_task
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    except asyncio.CancelledError:
        logger.info("Задача бота отменена")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise
    finally:
        await stop_bot()


if __name__ == "__main__":
    asyncio.run(main())

