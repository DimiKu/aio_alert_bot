FROM python:3.8-slim-buster

RUN pip install --upgrade pip

WORKDIR /aio_bot

COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY venv .
