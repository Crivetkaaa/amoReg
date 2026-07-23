import asyncio
import aiohttp
from mail.getMail import generateParallel
from amoreg.amoreg import regAMOParallel
from classes import AMOInfo
from twitch.twitchReg import regTwitchParallel

async def main():
    mailQueue = asyncio.Queue()
    amoQueue = asyncio.Queue()

    session = aiohttp.ClientSession(
        headers={
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    
    try:
        asyncio.create_task(generateParallel(session, mailQueue))
        asyncio.create_task(regAMOParallel(mailQueue, amoQueue))
        asyncio.create_task(regTwitchParallel(amoQueue))
        
        await asyncio.sleep(3600)
        
    finally:
        await session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Система] Программа остановлена.")
