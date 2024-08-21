FROM python:3.12.1-alpine3.19

WORKDIR /app

COPY pyproject.toml pyproject.toml
RUN pip3 install poetry
RUN poetry install

COPY ./src/bot ./bot
COPY ./src/database ./database
COPY ./src/main.py ./main.py
COPY ./src/graphics ./graphics
COPY ./src/analytics ./analytics

ENV SERVER_PORT=8080

CMD ["sh", "-c", "exec poetry run python3 main.py"]