from dataclasses import dataclass
import aiohttp

@dataclass
class EmailInfo:
    uuid: str
    email_id: str
    email_address: str

@dataclass
class AMOInfo:
    login: str
    password: str
    endpoint: str
    session: aiohttp.ClientSession