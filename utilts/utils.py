import aiohttp
import random
import string
from bs4 import BeautifulSoup as bs
import asyncio


async def getName() -> tuple[str, str]:

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
    }

    params = {
        "gender": "m",
        "number": "2",
        "sets": "1",
        "randomsurname": "yes",
        "norare": "yes",
        "nodiminutives": "yes",
        "usage_rus": "1",
    }
    try:
        async with aiohttp.request(
            "GET", 
            "https://www.behindthename.com/random/random.php",
            params=params,
            headers=headers
        ) as response:

            response.raise_for_status()

            html = await response.text()


        soup = bs(
            html,
            "lxml"
        )

        result = soup.find(
            "div",
            class_="random-results"
        )

        values = [
            x.text.strip()
            for x in result.find_all("a")
        ]

        name = values[0]
        surname = values[1]
    
    except aiohttp.ConnectionTimeoutError:
        name = "".join(
                random.choices(string.ascii_lowercase, k=random.randint(4, 10))
            )
        surname = "".join(
                random.choices(string.ascii_lowercase, k=random.randint(4, 15))
            )
        
    except Exception as e:
        print(e)
        

    return name, surname


async def getPhone() -> str:

    return (
        "+7"
        + "".join(
            random.choices(
                string.digits,
                k=10
            )
        )
    )

async def save_account_to_file(login: str, password: str, endpoint: str):
    """Асинхронно записывает данные аккаунта в текстовый файл."""
    log_line = f"Логин: {login} | Пароль: {password} | Эндпоинт: {endpoint}\n"
    # Режим 'a' добавляет новые строки в конец файла, не затирая старые
    async with asyncio.Lock(): # Защита от одновременной записи из разных тасков
        with open("accounts.txt", "a", encoding="utf-8") as file:
            file.write(log_line)
