from utilts.config import create_session


async def registrationTwitch():

    async with create_session() as session:

        # Открываем главную страницу, чтобы получить cookies
        async with session.get("https://www.twitch.tv/") as response:
            response.raise_for_status()
            await response.read()

        payload = {
            "username": "ksnvlksdnvlks",
            "password": "PP4-zuc-QHq-DKV",
            "email": "fdsfsdfvdfgfdgfds@gmail.com",
            "birthday": {
                "day": 20,
                "month": 7,
                "year": 2008,
                "isOver18": True
            },
            "email_verification_enabled": False,
            "client_id": "kimne78kx3ncx6brgo4mv6wki5h1ko",
            "is_password_guide": "nist"
        }

        async with session.post(
            "https://passport.twitch.tv/protected_register",
            json=payload
        ) as response:

            response.raise_for_status()

            print("Status:", response.status)
            print("Response:", await response.text())