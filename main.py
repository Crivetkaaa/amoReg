import asyncio
import aiohttp
from mail.getMail import generateParallel
from amoreg.amoreg import regAMOParallel, checkAmoMail

async def main():
    mailQueue = asyncio.Queue()
    amoQueue = asyncio.Queue()

    # Сессия для генерации ящиков на почте
    session = aiohttp.ClientSession(
        headers={
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    
    try:
        # ИСПРАВЛЕНО: Запускаем бесконечные процессы параллельно через create_task
        asyncio.create_task(generateParallel(session, mailQueue))
        asyncio.create_task(regAMOParallel(mailQueue, amoQueue))
        
        # Этот чекер блокирует поток и удерживает main() активным, обрабатывая лиды нон-стоп
        await checkAmoMail(amoQueue)
        
    finally:
        await session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Система] Программа остановлена.")
