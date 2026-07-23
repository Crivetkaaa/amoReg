from classes import AMOInfo
import aiohttp
import random
import string
import asyncio

async def regTwitch(amoInfo: AMOInfo):
    mail = amoInfo.login.split("@")[0] + "+lead@mail.amocrm.ru"
    print(mail)
    session = amoInfo.session

    print(f"[Twitch] Старт регистрации {mail}")

    try:
        print("[Twitch] Делаю GET twitch")

        async with session.get(
            "https://www.twitch.tv/",
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:

            print(f"[Twitch] GET twitch статус {response.status}")

            response.raise_for_status()


        print("[Twitch] Формирую данные")



        data = {
            "username": "".join(random.choices(string.ascii_lowercase, k=10)),
            "password": "PVJ-GCh-9Rg-aye",
            "email": mail,
            "birthday": {
                "day": random.randint(1, 28),
                "month": random.randint(1, 12),
                "year": random.randint(1998, 2007)
            },
            "client_id": "kimne7v8kx6nc6f597421yth44739a"
        }
        print("[Twitch] Отправляю POST")


        
        headers = {
            "Content-Type": "application/json",
            "Referer": "https://www.twitch.tv/",
            "Origin": "https://www.twitch.tv"
        }

        async with session.post(
            "https://passport.twitch.tv/protected_register",
            json=data,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
        
            print(f"[Twitch] POST статус {response.status}")

            text = await response.text()

            print(f"[Twitch] Ответ: {text[:200]}")
            #TODO [Twitch] Ответ: {"request_id":"01KY859X89W70P22QK38HG3AQQ","has_existing_account":false,"error_code":5025}


    except asyncio.TimeoutError:
        print(
            f"[Twitch] Таймаут {mail}"
        )


    except Exception as e:
        print(
            f"[Twitch] Ошибка {mail}: {repr(e)}"
        )
        
async def regTwitchParallel(queue: asyncio.Queue):
    print("[Twitch] Ожидание аккаунтов...")
    while True:
        amoInfo = await queue.get()
        print(f"[Twitch] Получен аккаунт {amoInfo.login}")
        asyncio.create_task(regTwitch(amoInfo))
