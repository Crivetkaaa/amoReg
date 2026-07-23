import aiohttp
import asyncio
import json
import re
from bs4 import BeautifulSoup as bs
from classes import EmailInfo, AMOInfo
from utilts.utils import save_account_to_file

def getInfo(html: str):
    soup = bs(html, "lxml")
    links = soup.find_all("a", style=re.compile(r"color:\s*#2e84e3"))
    if len(links) >= 3:
        return links[0].get_text(strip=True), links[1].get_text(strip=True), links[2].get_text(strip=True)
    return None

async def lisenMail(session: aiohttp.ClientSession, emailInfo: EmailInfo, amoQueue: asyncio.Queue):
    data = {"uuid": emailInfo.uuid, "selected_email_id": emailInfo.email_id, "known_message_id": 0}
    try:
        while True:
            async with session.post("https://api.tempamail.com/webapp/messages", data=data) as response:
                if response.status != 200:
                    await asyncio.sleep(10)
                    continue
                    
                res = await response.json(content_type=None)
                if res.get('messages'):
                    email = res['messages'][0]
                    data["known_message_id"] = email.get("id")
                    
                    raw_from = email.get("from")
                    if isinstance(raw_from, str):
                        try: raw_from = json.loads(raw_from)
                        except json.JSONDecodeError: raw_from = {}
                            
                    sender_address = raw_from.get('address', '') if isinstance(raw_from, dict) else ''
                    
                    if "support@amocrm.ru" in sender_address:
                        info = getInfo(email.get('body', ''))
                        if info:
                            amoInfo = AMOInfo(login=info[0], password=info[1], endpoint=info[2], session=session)
                            await save_account_to_file(login=info[0], password=info[1], endpoint=info[2])
                           
                            await amoQueue.put(amoInfo)
                            return 
                else:    
                    print(f"[{emailInfo.email_address}] Ожидание письма...")
            await asyncio.sleep(10)
    except Exception as e:
        print(f"Ошибка в lisenMail [{emailInfo.email_address}]: {e}")
        await session.close()

    finally:
        del_data = {
            "uuid": emailInfo.uuid,
            "selected_email_id": emailInfo.email_id
        }

        try:
            async with session.post('https://api.tempamail.com/webapp/email/delete', data=del_data) as resp:
                if resp.status == 200:
                    print(f"[{emailInfo.email_address}] Ящик успешно удален с сервера TempAMail.")
                else:
                    print(f"[Error] Не удалось удалить ящик {emailInfo.email_address}. Статус: {resp.status}")
        except Exception as e:
            print(f"[Error] Ошибка при отправке запроса удаления почты: {e}")

async def createAccount(session: aiohttp.ClientSession, queue: asyncio.Queue) -> EmailInfo:
    data = {"app_uuid": "a5x-cj6a-ka1q"}
    try:
        async with session.post("https://api.tempamail.com/webapp/client/create", data=data) as response:
            res = await response.json(content_type=None)
            email = EmailInfo(
                uuid=res['client']['uuid'],
                email_id=res['email']['id'],
                email_address=res['email']['address']
            )
            await queue.put(email)
            print(f"[Почта] Создан ящик {email.email_address}")
    except Exception as e:
        print(f"Ошибка создания ящика: {e}")

async def generateParallel(session: aiohttp.ClientSession, queue: asyncio.Queue) -> None:
    print("[Конвейер] Бесконечный генератор почты запущен...")
    while True:
        asyncio.create_task(createAccount(session, queue))
        await asyncio.sleep(12)
