import logging, asyncio
from http import HTTPStatus
from models import Event, User, Channel, Chat
from service import create_user, check_user_in_database, generate_random_sequence_number, \
    create_channel, check_chat, create_chat, check_chat_link_in_database, return_chats_from_channel, chat_link_and_queue_dict
from migrations import engine

from aiohttp import web


logging.basicConfig(level=logging.INFO)
routes = web.RouteTableDef()
queue_list = []


@routes.post('/events/{endpoint_id}')
async def request_handler(request):
    session = await engine.get_session()
    chat_link = await check_chat_link_in_database(session, request.match_info['endpoint_id'])
    await session.close()
    if chat_link:
        result = await request.json()
        event = Event(message=str(result), channel_link=chat_link)

        if chat_link not in chat_link_and_queue_dict:
            new_queue = asyncio.Queue()
            await new_queue.put(event)
            logging.info('Add event in queue ', event)
            chat_link_and_queue_dict[chat_link] = new_queue
        else:
            await chat_link_and_queue_dict[chat_link].put(event)

        response = web.Response(status=HTTPStatus.ACCEPTED, text='Event added')
        return response


@routes.post('/registrate_user')
async def register_user(request):
    user_info = await request.json()
    new_user = User(name=user_info['name'], channels=int(user_info['channel']))
    session = await engine.get_session()
    user_id = await create_user(session, new_user.name, new_user.channels)
    await session.close()
    response = web.json_response(content_type='application/json', data=user_id)
    return response


@routes.post('/channel')
async def register_channel(request):
    channel_info = await request.json()
    session = await engine.get_session()
    user_id = int(channel_info['user_id'])
    if await check_user_in_database(session, user_id):
        channel_link = str(await generate_random_sequence_number(10))
        new_channel = Channel(user_id=user_id,
                              channel_link=channel_link)
        channel_id = await create_channel(session, new_channel.user_id, new_channel.channel_link)
        await session.close()
        response = web.json_response(content_type='application/json', data=channel_id)
        return response
    else:
        response = web.Response(text='No chat found')
        return response


@routes.post('/chat')
async def register_chat(request):
    chat_info = await request.json()
    session = await engine.get_session()
    user_id = int(chat_info['user_id'])
    channel_id = int(chat_info['channel_id'])
    if await check_chat(session, user_id, channel_id):
        new_chat = Chat(
            user_id=user_id,
            channel_id=channel_id,
            type=chat_info['chat_type'],
            chat_link=chat_info['chat_link']
        )
        chat_id = await create_chat(session, new_chat.user_id, new_chat.channel_id, new_chat.type, new_chat.chat_link)
        await session.close()
        response = web.json_response(content_type='application/json', data=chat_id)
        return response
    else:
        response = web.Response(text='No chat found')
        return response
