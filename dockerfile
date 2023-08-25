FROM python:3.10.12-alpine3.18

COPY frontend/* /www/html/

COPY server/requirements.txt /python/requirements.txt

RUN pip install --no-cache-dir -r /python/requirements.txt

COPY server/src /python/src

WORKDIR /python/src

COPY docker/docker-entrypoint.sh /docker-entrypoint.sh

COPY docker/default_env /default_env

ENTRYPOINT /docker-entrypoint.sh