from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from migrations.engine import Base
from dataclasses import dataclass


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    channels = Column(Integer)


class Channels(Base):
    __tablename__ = 'channels'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer)
    channel_link = Column(String)


class Chats(Base):
    __tablename__ = 'chats'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    chat_link = Column(String)
    chat_type = Column(String)


@dataclass
class Chat:
    user_id: int
    channel_id: int
    type: str
    chat_link: str


@dataclass
class Channel:
    user_id: int
    channel_link: str


@dataclass
class Event:
    message: str
    channel_link: str
    count: int = 1

    def inc(self):
        self.count += 1


@dataclass
class User:
    name: str
    channels: int
