import random
import string
import aiohttp
from utilts.config import create_session
from utilts.getFake import getName, getPhone
    
def generate_email(name, surname):
    return (
        name.lower()
        + surname.lower()
        + str(random.randint(1955, 2008))
        + "@"
        + "".join(random.choices(string.ascii_lowercase, k=random.randint(4, 6)))
        + "."
        + "".join(random.choices(string.ascii_lowercase, k=random.randint(2, 5)))
    )

async def registrationAMO(mail:str = None):
    session = create_session()

    try:
        async with session.get("https://www.amocrm.ru") as response:
            response.raise_for_status()

        name, surname = await getName()
        phone = await getPhone()
        if mail == None:
            mail =generate_email(name, surname) 

        print("Регистрация:", mail, phone)

        data = {
            "ACTION": "REGISTER_NEW_ACCOUNT",
            "need_json_response": "true",
            "account[user_name]": mail,
            "account[first_name]": f"{name} {surname}",
            "account[phone_num]": phone,
            "account[assistance]": "0",
            "coupon_code": "",
            "ga[counter_id]": "UA-42302238-1",
            "ym[counter_id]": "561575",
            "utm[source]": "yandex",
            "utm[content]": "17743455843",
            "utm[campaign]": "710602246",
            "utm[medium]": "cpc",
            "utm[term]": "автоматизация+срм",
            "real_host": "www.amocrm.ru",
        }

        async with session.post(
            "https://www.amocrm.ru/registration",
            data=data,
            headers={
                "Referer": "https://www.amocrm.ru/",
                "Origin": "https://www.amocrm.ru",
                "X-Requested-With": "XMLHttpRequest",
            }
        ) as response:
            response.raise_for_status()
            result = await response.json()

            account_info = result["response"]["accounts"][0]
            subdomain = account_info["subdomain"]
            api_key = account_info["user_api_key"]

            print(f"Статус регистрации: {response.status}")

            
        return session

    except Exception as e:
        await session.close()
        print(f"Произошла ошибка: {e}")
        raise

    finally:
        await session.close()


async def checkMailAmo(session: aiohttp.ClientSession, subdomain: string, api_key: string):
    api_headers = {
    "Authorization": f"Bearer {api_key}",

    "Accept": "application/json"}

    url_events = f"https://{subdomain}.amocrm.ru/api/v4/leads"
    print(f"Запрос к API: {url_events}")

    async with session.get(url_events, headers=api_headers) as response:
        print(f"Статус API events: {response.status}")
        if response.status == 200:
            res = await response.json()
            print("События аккаунта:", res)
        elif response.status == 204:
            print("Событий пока нет (пустой аккаунт)")
        else:
            print("Ошибка API:", await response.text())
