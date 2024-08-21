FROM python:3.12.1-alpine3.19

WORKDIR /app

COPY ./src/analytics/pyproject.toml pyproject.toml
RUN pip3 install poetry
RUN poetry install

COPY ./src/analytics ./analytics
COPY ./src/database ./database

ENV PYTHONPATH=.

CMD ["sh", "-c", "exec poetry run python3 analytics/userbot.py"]
