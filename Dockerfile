FROM python:3.8.5-alpine

ENV PYTHONUNBUFFERED 1

RUN apk add --update --no-cache postgresql-client python3-dev \
  libffi-dev jpeg-dev freetype-dev libjpeg-turbo-dev libpng-dev \
  curl jq

RUN apk add --update --no-cache --virtual .tmp-build-deps \
  gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev \
  make musl-dev g++

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app
RUN pip install --upgrade setuptools pip
RUN pip install -r ./requirements.txt
RUN apk del .tmp-build-deps

ADD app/ /app
