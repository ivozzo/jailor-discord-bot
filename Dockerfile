FROM arm32v7/python:3.9-slim

ARG version
ENV BOT_VERSION=${version}

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY dist/jailor-bot-${version}.tar.gz app.tar.gz
RUN tar -zxvf app.tar.gz

COPY docker/settings jailor-bot-${version}/jailor-bot/config/settings

WORKDIR /app/jailor-bot-${BOT_VERSION}

CMD python jailor-bot/jailor.py