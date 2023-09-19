import requests
from constants import headers, telegram_api
import aiohttp

get_me_req = requests.get(telegram_api + 'getMe',
                          headers=headers)


async def get_events():
    async with aiohttp.ClientSession() as session:
        async with session.get(telegram_api + "getUpdates", headers=headers) as resp:
            return await resp.json()


async def send_message(chat_id, text):
    async with aiohttp.ClientSession() as session:
        async with session.get(telegram_api + "sendMessage?chat_id={}&text={}".format(chat_id, text)) as resp:
            return await resp.json()
