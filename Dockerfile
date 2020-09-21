FROM python:3.7-alpine as base

RUN apk update && apk add --no-cache build-base libressl-dev musl-dev libffi-dev ffmpeg
RUN pip install -U pip && pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app
ADD pyproject.toml /app
RUN poetry install

ADD web_youtube_dl /app/web_youtube_dl
RUN chown 1001 /app/web_youtube_dl
RUN poetry build && pip install dist/*.whl

FROM base as final
USER 1001
CMD ["/usr/local/bin/web-youtube-dl"]