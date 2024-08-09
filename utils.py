import requests
import asyncio
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from functools import wraps
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import logging
import time
from config import API_KEY
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp

logging.basicConfig(level=logging.INFO)

last_message_time = {}
MESSAGE_LIMIT = timedelta(seconds=2)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def is_english_alphabet_only(text: str) -> bool:
    pattern = r'^[a-zA-Z]+$'
    return bool(re.fullmatch(pattern, text))


def anti_spam_decorator(func):
    """
    Декоратор для анти-спама, который проверяет, прошло ли достаточно времени между сообщениями от одного пользователя.
    """
    @wraps(func)
    async def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        now = datetime.now()
        if user_id in last_message_time and now - last_message_time[user_id] < MESSAGE_LIMIT:
            logging.info("Сообщение заблокировано для пользователя", user_id)
            await message.answer('Пожалуйста, подождите до отправки следующего сообщения.')
            return
        last_message_time[user_id] = now
        return await func(message, *args, **kwargs)
    return wrapper



def google_translate(sentence: str) -> str:
    """
    Переводит предложение с использованием Google Translate через Selenium.
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://translate.google.com/?hl=ru&sl=en&tl=ru&op=translate")
        elem = driver.find_element(By.CLASS_NAME, "er8xn")
        elem.clear()
        elem.send_keys(sentence)
        time.sleep(2)  # Может быть заменено на более надёжное ожидание
        input_elem = driver.find_element(By.CLASS_NAME, "ryNqvb")
        return input_elem.text
    finally:
        driver.quit()







def download_audio(word: str) -> None:
    """
    Скачивает аудиофайл произношения слова из Cambridge Dictionary.
    """
    url = f'https://dictionary.cambridge.org/dictionary/english-russian/{word}'
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')
    sources = soup.find_all('source')

    if sources:
        audio_type = sources[0].get('type')
        audio_url = sources[0].get('src')

        if audio_url:
            if not audio_url.startswith('http'):
                audio_url = requests.compat.urljoin(url, audio_url)

            file_extension = audio_type.split('/')[-1]
            file_name = f'audio_{word}.{file_extension}'
            audio_response = requests.get(audio_url, headers=HEADERS)

            with open(file_name, 'wb') as file:
                file.write(audio_response.content)
            logging.info(f'Аудиофайл {file_name} успешно скачан')
        else:
            logging.warning('Нерабочий URL для аудиофайла')
    else:
        logging.warning('Не удалось найти аудиофайлы на странице.')
"""
Переводит предложение через бесплатный Microsoft Translate Api.
"""


def check_word(word: str) -> str:
    """
    Извлекает перевод одного слова из словаря Cambridge Dictionary.
    """

    if len(word) <= 1:
        raise ValueError("Слово должно содержать хотя бы 2 буквы.")
    
    if not is_english_alphabet_only(word):
        raise ValueError("Слово должно состоять только из английских букв.")

    url = f'https://dictionary.cambridge.org/dictionary/english-russian/{word}'
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')
    word_element = soup.find('span', class_='trans dtrans dtrans-se')

    if word_element:
        return word_element.get_text()
    else:
        raise LookupError("Перевод не найден")
    
    
def microsoft_translate(sentence: str) -> str:
    url = "https://microsoft-translator-text.p.rapidapi.com/translate"

    querystring = {
        "api-version": "3.0",
        "profanityAction": "NoAction",
        "textType": "plain",
        "to": "ru"}

    payload = [{
        "Text": f"{sentence}",
    }]

    headers = {
        "x-rapidapi-key": f"{API_KEY}",
        "x-rapidapi-host": "microsoft-translator-text.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, params=querystring)
    return response.json()[0]['translations'][0]['text']


async def async_microsoft_translate(session: aiohttp.ClientSession, sentence: str) -> str:
    url = "https://microsoft-translator-text.p.rapidapi.com/translate"
    querystring = {
        "api-version": "3.0",
        "profanityAction": "NoAction",
        "textType": "plain",
        "to": "ru"
    }
    payload = [{
        "Text": sentence,
    }]
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "microsoft-translator-text.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    async with session.post(url, json=payload, headers=headers, params=querystring) as response:
        response_json = await response.json()
        translated_sentence = response_json[0]['translations'][0]['text']
        return (sentence, translated_sentence)


async def async_check_word(session: aiohttp.ClientSession, word: str) -> str:
    if len(word) <= 1:
        raise ValueError("Слово должно содержать хотя бы 2 буквы.")
    if not is_english_alphabet_only(word):
        raise ValueError("Слово должно состоять только из английских букв.")
    
    url = f'https://dictionary.cambridge.org/dictionary/english-russian/{word}'
    async with session.get(url, headers=HEADERS) as response:
        text = await response.text()
        soup = BeautifulSoup(text, 'lxml')
        word_element = soup.find('span', class_='trans dtrans dtrans-se')
        
        if word_element:
            return (word, word_element.get_text())
        else:
            print('Перевод не найден.')
            return

async def handle_multiple_requests(sentences: list[str]) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for sentence in sentences:
            if len(sentence.split()) == 1:  # если это одно слово
                task = async_check_word(session, sentence)
            else:  # если это предложение
                task = async_microsoft_translate(session, sentence)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        print(results)
        return results