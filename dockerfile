# FROM node:20.5.1-alpine3.18 as build-frontend

# COPY frontend/* /app

# WORKDIR /app

# RUN npm run build

# RUN ls



FROM python:3.10.12-alpine3.18

COPY server/requirements.txt /python/requirements.txt

RUN pip install --no-cache-dir -r /python/requirements.txt

COPY server/src /python/src

WORKDIR /python/src

COPY docker/docker-entrypoint.sh /docker-entrypoint.sh

COPY docker/default_env /default_env

COPY frontend/* /www/html/

ENTRYPOINT /docker-entrypoint.sh