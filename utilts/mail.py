import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
import re


def getInfo(html: str):
    soup = bs(html, "lxml")
    
    # Находим ссылки по цвету стиля, они идут строго по порядку: Логин, Пароль, Эндпоинт
    links = soup.find_all("a", style=re.compile(r"color:\s*#2e84e3"))
    
    if len(links) >= 3:
        login = links[0].get_text(strip=True)
        password = links[1].get_text(strip=True)
        endpoint = links[2].get_text(strip=True)
        
        print(f"Логин: {login}")
        print(f"Пароль: {password}")
        print(f"Эндпоинт: {endpoint}")

async def checkMail(session: aiohttp.ClientSession, uuid:str, email_id:str):
    data = {
        "uuid":uuid,
        "selected_email_id":email_id,
        "known_message_id":"0", # 0 - get all
    }
    try:
        i = 1
        check = True
        while check: 
            async with session.post("https://api.tempamail.com/webapp/messages", data=data) as responce:
                res = await responce.json()
                if res.get('messages'):
                    email = res['messages'][0]
                    
                    last_id = email.get("id")
                    data["known_message_id"] = last_id
                    
                    raw_from = email.get("from")
                    if isinstance(raw_from, str):
                        import json
                        try:
                            raw_from = json.loads(raw_from)
                        except json.JSONDecodeError:
                            raw_from = {}
                            
                    sender_address = raw_from.get('address', '') if isinstance(raw_from, dict) else ''
                    
                    if "support@amocrm.ru" in sender_address:
                        getInfo(email.get('body', ''))
                        check = False
        
                else:    
                    print(i, "Whait a minet")

                i += 1
                await asyncio.sleep(10)

    except Exception as e:
        print(e)

async def createAccount(session: aiohttp.ClientSession):
    data = {
        "app_uuid": "a5x-cj6a-ka1q"
    }
    try:
        async with session.post("https://api.tempamail.com/webapp/client/create", data=data) as response:
            res = await response.json()
            return res['client']['uuid'], res['email']['id'], res['email']['address']

    except Exception as e:
        print(e)

async def main():
    await createAccount()

if __name__ == "__main__":
    asyncio.run(main())