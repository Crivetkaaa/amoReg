import aiohttp
import random
import string
from bs4 import BeautifulSoup as bs


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