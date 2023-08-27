FROM node:20.5.1-alpine3.18 as build-frontend

RUN npm install -g vite

RUN mkdir -p /app

COPY frontend/ /app/

WORKDIR /app

RUN npm install 

RUN vite build --base=/static/



FROM python:3.10.12-alpine3.18 as run

COPY server/requirements.txt /python/requirements.txt

RUN pip install --no-cache-dir -r /python/requirements.txt

COPY server/src /python/src

WORKDIR /python/src

COPY docker/docker-entrypoint.sh /docker-entrypoint.sh

COPY docker/default_env /default_env

COPY --from=build-frontend /app/dist/ /www/html/

ENTRYPOINT /docker-entrypoint.sh