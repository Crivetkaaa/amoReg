import asyncio
import aiohttp
from amo.amoreg import registrationAMO
from utilts.mail import createAccount, checkMail

def getSession() -> aiohttp.ClientSession:
    return aiohttp.ClientSession(
        headers={
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )

async def account_worker(queue: asyncio.Queue):
    """Воркер, который непрерывно обрабатывает аккаунты из очереди."""
    while True:
        mail_info = await queue.get()
        try:
            await registrationAMO(mail_info[2])
        except Exception as e:
            print(f"[Воркер] Ошибка при регистрации {mail_info[2]}: {e}")
        finally:
            queue.task_done()

async def main():
    session = getSession()
    queue = asyncio.Queue()
    
    worker_task = asyncio.create_task(account_worker(queue))
    
    mail_tasks = []
    
    try:
        for _ in range(0, 2):
            mail_info = await createAccount(session)
            await queue.put(mail_info)
            
            task = asyncio.create_task(checkMail(session, mail_info[0], mail_info[1]))
            mail_tasks.append(task)
            
            await asyncio.sleep(5)
            
        await queue.join()
        if mail_tasks:
            await asyncio.gather(*mail_tasks, return_exceptions=True)
            
    except Exception as e:
        print(f"[Main] Исключение: {e}")
    finally:
        worker_task.cancel()
        await session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Система] Программа остановлена пользователем.")
