import aiohttp
import asyncio
from utilts.utils import getName, getPhone
from mail.getMail import lisenMail
from classes import EmailInfo, AMOInfo

def getSession():
    return aiohttp.ClientSession(
        headers={
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )

async def lisenAmoMail(amoInfo: AMOInfo, amoQueue: asyncio.Queue):
    session = amoInfo.session
    subdomain = amoInfo.endpoint.replace("https://", "").replace("/", "")
    url = f"https://{subdomain}/api/v4/leads"
    
    api_headers = {
        "Authorization": f"Bearer {amoInfo.password}",
        "Accept": "application/json"
    }
    
    print(f"[{subdomain}] Фоновый мониторинг API Leads успешно запущен.")
    try:
        while True:
            async with session.get(url, headers=api_headers) as response:
                if response.status == 200:
                    res = await response.json()
                    print(f"[{subdomain}] Сделки:", res)
                elif response.status == 204:
                    print(f"[{subdomain}] Аккаунт пустой (сделок нет).")
                else:
                    print(f"[{subdomain}] Ошибка API: {response.status}")
                    break
            await asyncio.sleep(20)

    except Exception as e:
        print(f"Ошибка в lisenAmoMail [{subdomain}]: {e}")
    finally:
        await session.close()
        amoQueue.task_done()

async def checkAmoMail(amoQueue: asyncio.Queue):
    print("[Конвейер] Мониторинг очереди готовых аккаунтов amoCRM запущен...")
    while True:
        amoInfo = await amoQueue.get()
        asyncio.create_task(lisenAmoMail(amoInfo, amoQueue))

async def regAMO(mail: EmailInfo, queue: asyncio.Queue, amoQueue: asyncio.Queue):
    session = getSession()
    try:
        async with session.get("https://www.amocrm.ru") as response:
            response.raise_for_status()

        name, surname = await getName()
        phone = await getPhone()

        data = {
            "ACTION": "REGISTER_NEW_ACCOUNT", "need_json_response": "true",
            "account[user_name]": mail.email_address, "account[first_name]": f"{name} {surname}",
            "account[phone_num]": phone, "account[assistance]": "0", "coupon_code": "",
            "ga[counter_id]": "UA-42302238-1", "ym[counter_id]": "561575",
            "utm[source]": "yandex", "utm[content]": "17743455843", "utm[campaign]": "710602246",
            "utm[medium]": "cpc", "utm[term]": "автоматизация+срм", "real_host": "www.amocrm.ru",
        }

        async with session.post(
            "https://www.amocrm.ru/registration", data=data,
            headers={"Referer": "https://www.amocrm.ru/", "Origin": "https://www.amocrm.ru", "X-Requested-With": "XMLHttpRequest"}
        ) as response:
            response.raise_for_status()

            if response.status == 200:
                asyncio.create_task(lisenMail(session, mail, amoQueue))
            else:
                await session.close()
    except Exception as e:
        print(f"[{mail.email_address}] Ошибка регистрации: {e}")
        await session.close() 
    finally:
        queue.task_done()

async def regAMOParallel(queue: asyncio.Queue, amoQueue: asyncio.Queue):
    print("[Конвейер] Очередь регистраций запущена...")
    while True:
        email_info = await queue.get()
        asyncio.create_task(regAMO(email_info, queue, amoQueue))
        await asyncio.sleep(10)
