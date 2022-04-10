FROM node:16-buster-slim

WORKDIR /app

COPY ./package.json /app

RUN apt-get update && apt-get -y install python3 build-essential && apt-get clean

RUN npm install && npm cache clean --force

ENV PATH ./node_modules/.bin/:$PATH
