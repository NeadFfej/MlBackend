FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /mackendml

WORKDIR /mackendml

COPY poetry.lock pyproject.toml ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

COPY config /mackendml/config
COPY src /mackendml/src
COPY alembic.ini /mackendml
COPY .env /mackendml
