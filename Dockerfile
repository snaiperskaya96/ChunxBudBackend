FROM python:3.8.0-alpine

RUN apk update \
  && apk add \
    build-base \
    protobuf

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

COPY . .
