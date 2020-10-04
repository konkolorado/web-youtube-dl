FROM python:3.8-alpine
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false

RUN apk update && \
    apk add --no-cache \
    build-base \
    curl \
    ffmpeg \
    libffi-dev \
    libressl-dev \
    musl-dev
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="${PATH}:/root/.poetry/bin"

WORKDIR /app
COPY poetry.lock pyproject.toml README.rst ./
RUN poetry install --no-dev

ADD --chown=1001 web_youtube_dl web_youtube_dl
RUN poetry build --format wheel && pip install dist/*.whl

USER 1001
CMD ["/usr/local/bin/web-youtube-dl"]