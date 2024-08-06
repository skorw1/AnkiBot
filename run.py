import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота и диспетчера
bot = Bot(token=TOKEN)
dispatcher = Dispatcher()

async def main() -> None:
    dispatcher.include_router(router)
    
    logging.info("Бот запускается...")
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Внезапная ошибка: {str(e)}")
