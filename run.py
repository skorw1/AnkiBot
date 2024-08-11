import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app.database import create_tables

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота и диспетчера
bot = Bot(token=TOKEN)
dispatcher = Dispatcher()

async def on_startup_func():
    print("Запуск on_startup...")
    await create_tables()
    logging.info('База данных успешно настроена')

async def main() -> None:
    dispatcher.include_router(router)
    
    logging.info("Бот запускается...")
    await on_startup_func()
    await dispatcher.start_polling(bot, on_startup=on_startup_func)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Внезапная ошибка: {str(e)}")
