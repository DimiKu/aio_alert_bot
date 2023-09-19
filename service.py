import asyncio
import string, secrets
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import *
from migrations import engine
from bot_requests import send_message
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
chat_link_and_queue_dict = defaultdict()
queue_for_messages = asyncio.Queue()


async def get_users(session: AsyncSession):
    result = await session.execute(select(Users))
    return result.scalars().all()


async def create_user(session: AsyncSession, name: str, channel: int):
    new_user = Users(name=name, channels=channel)
    try:
        session.add(new_user)
    except Exception as exc:
        logging.info('Failed add user ', exc)
    await session.commit()
    answer = {
        'User_id': new_user.id
    }
    return answer


async def create_channel(session: AsyncSession, user_id: int, channel_link: str):
    new_channel = Channels(user_id=user_id,
                           channel_link=channel_link)
    try:
        session.add(new_channel)
        await session.commit()
    except Exception as exc:
        logging.info('Failed create channel ', exc)
    answer = {
        'Channel_id': new_channel.id,
        'Channel_link': new_channel.channel_link
    }
    return answer


async def create_chat(session: AsyncSession, user_id: int, channel_id: int, chat_type: str, chat_link: str):
    new_chat = Chats(
        user_id=user_id,
        channel_id=channel_id,
        chat_type=chat_type,
        chat_link=chat_link
    )
    try:
        session.add(new_chat)
    except Exception as exc:
        logging.info('Failed create chat ', exc)
    await session.commit()
    answer = {
        'Chat_id': new_chat.id
    }
    return answer


async def check_chat(session: AsyncSession, user_id: int, channel_id: int):
    users = await session.execute(select(Channels).filter(Channels.user_id == user_id and Channels.id == channel_id))
    try:
        await session.close()
        return users.scalars().all()[0].id
    except Exception as exc:
        logging.info('Chat not exist ', exc)


async def check_user_in_database(session: AsyncSession, user_id: int):
    users = await session.execute(select(Users).filter(Users.id == user_id))
    try:
        await session.close()
        return users.scalars().all()[0].name
    except Exception:
        logging.exception('User not exist ')


async def check_chat_link_in_database(session: AsyncSession, channel_link: int):
    channel_link_id = await session.execute(select(Channels).filter(Channels.channel_link == channel_link))
    channel_link_id = channel_link_id.scalars().all()
    await session.close()
    if channel_link_id:
        return channel_link_id[0].channel_link
    else:
        raise Exception('Chat not exist in database ')


async def generate_random_sequence_number(length):
    link = ''.join(secrets.choice(string.digits) for digit in range(length))
    return link


async def return_chats_from_channel(session: AsyncSession, channel_link: str):
    chats_id = await session.execute(select(Chats.chat_link).join(Channels, Chats.channel_id == Channels.id).filter(Channels.channel_link == channel_link))
    try:
        await session.close()
        return chats_id.scalars().all()
    except Exception as exc:
        logging.info('Chat not exist ', exc)


async def collect_event_and_send(event_dict, chat_id):
    for event, count in event_dict.items():
        message = 'I got event ' + event + 'count: ' + str(count)
        try:
            answer = await send_message(chat_id, message)
        except Exception as exc:
            logging.info('Failed send message ', exc)


async def check_queue(queue):
    channel_link = None
    if not queue.empty():
        await asyncio.sleep(10)
        events = {}
        while not queue.empty():
            event = await queue.get()

            if not events.get(event.message):
                events[event.message] = 0

            events[event.message] += event.count
            channel_link = event.channel_link
        session = await engine.get_session()
        chats = await return_chats_from_channel(session, channel_link)
        await session.close()

        for chat in chats:
            await collect_event_and_send(events, chat)


async def queue_checker():
    while True:
        if chat_link_and_queue_dict:
            queue_tasks = []
            for chat_id, queue in chat_link_and_queue_dict.items():
                queue_tasks.append(check_queue(queue))
            await asyncio.gather(*queue_tasks)
        # TODO  await asyncio.sleep(1)
        # TODO прочитать
        else:
            await asyncio.sleep(1)
