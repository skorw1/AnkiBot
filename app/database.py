import aiosqlite
import asyncio


async def create_tables():
    print("Создание таблиц...")
    async with aiosqlite.connect('sqlite.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL
                )
            ''')

            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER NOT NULL,
                    word TEXT NOT NULL,
                    translation TEXT NOT NULL,
                    FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
                )
            ''')

            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS learned_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    word_id INTEGER NOT NULL,
                    learned_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (word_id) REFERENCES words (id)
                )
            ''')

            await db.commit()
    print("Таблицы созданы.")


async def add_topics(user_id: int, name: str):
    async with aiosqlite.connect('sqlite.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute('INSERT INTO topics (user_id, title) VALUES (?, ?)', (user_id, name))
            await db.commit()

async def if_topic_exist(user_id, title):
    async with aiosqlite.connect('sqlite.db') as db:

        async with db.cursor() as cursor:
            await cursor.execute('SELECT id FROM topics WHERE user_id = ? AND title = ?', (user_id, title))
            topic_id = await cursor.fetchone()
            
            if topic_id:
                return topic_id
            else:
                return None

async def delete_topics(user_id: int, title: str):
    async with aiosqlite.connect('sqlite.db') as db:

        async with db.cursor() as cursor:
            await cursor.execute('SELECT id FROM topics WHERE user_id = ? AND title = ?', (user_id, title))
            topic_id = await cursor.fetchone()
            
            if topic_id:
                topic_id = topic_id[0]
                await cursor.execute('DELETE FROM topics WHERE id = ?', (topic_id,))
                await db.commit()
                print(f'Тема - "{title}" удалена успешно')
                return True
            else:
                print(f'не найдено тем с названием "{title}" для пользователя {user_id}.')
                return False
        

async def delete_words_by_topic_title(user_id: int, title: str) -> bool:
    async with aiosqlite.connect('sqlite.db') as db:
        await db.execute('PRAGMA foreign_keys = ON;')
        async with db.cursor() as cursor:
            try:
                # Получаем ID темы по названию и user_id
                await cursor.execute('SELECT id FROM topics WHERE user_id = ? AND title = ?', (user_id, title))
                topic_id = await cursor.fetchone()
                print(f'Полученный topic_id: {topic_id}')

                if topic_id:
                    topic_id = topic_id[0]
                    
                    # Удаляем все слова, связанные с этой темой
                    await cursor.execute('DELETE FROM words WHERE topic_id = ?', (topic_id,))
                    
                    # Подтверждаем изменения
                    await db.commit()
                    print(f'Все слова, связанные с темой "{title}", удалены успешно')
                else:
                    print(f'Тема с названием "{title}" для пользователя {user_id} не найдена.')

            except Exception as e:
                print(f'Ошибка при удалении слов: {e}')
                await db.rollback()  # Откат транзакции в случае ошибки

async def add_word(topic_id: int, word: str, translation: str):
    async with aiosqlite.connect('sqlite.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute('INSERT INTO words (topic_id, word, translation) VALUES (?, ?, ?)', (topic_id, word, translation))
            await db.commit()
            return cursor.lastrowid

async def get_words_by_topic(topic_id: int):
    async with aiosqlite.connect('sqlite.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT word, translation FROM words WHERE topic_id = ?', (topic_id,))
            words = await cursor.fetchall()
    return words

async def get_topics_by_user(user_id: int):
    async with aiosqlite.connect('sqlite.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT id, title FROM topics WHERE user_id = ?', (user_id,))
            topics = await cursor.fetchall()
    return topics

async def add_learned_word(user_id: int, word_id: int):
    async with aiosqlite.connect('sqlite.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute('''
                INSERT INTO learned_words (user_id, word_id) VALUES (?, ?)
            ''', (user_id, word_id))
            await db.commit()

async def get_count_words_by_user(user_id: int):
    async with aiosqlite.connect('sqlite.db') as db:
        async with db.cursor() as cursor:
            # Получаем все ID слов, которые связаны с данным user_id из таблицы learned_words
            await cursor.execute('SELECT COUNT(DISTINCT word_id) FROM learned_words WHERE user_id = ?', (user_id,))
            count_words = await cursor.fetchone()
    return count_words[0] if count_words else 0
