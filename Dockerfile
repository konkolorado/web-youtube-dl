FROM python:3.7-alpine

RUN apk update && apk add --no-cache build-base libressl-dev musl-dev libffi-dev ffmpeg
RUN pip install -U pip && pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app
ADD pyproject.toml /app
RUN poetry install

ADD web_youtube_dl /app/web_youtube_dl

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "web_youtube_dl.main:app"]