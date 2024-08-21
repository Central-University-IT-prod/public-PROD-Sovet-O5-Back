FROM python:3.12.1-alpine3.19

WORKDIR /app

COPY ./src/miniapp_api/pyproject.toml pyproject.toml
RUN pip3 install poetry
RUN poetry install

COPY ./src/database ./database
COPY ./src/miniapp_api ./miniapp_api
COPY ./src/graphics ./graphics
COPY ./src/analytics ./analytics

CMD ["sh", "-c", "exec poetry run python3 -m uvicorn miniapp_api.main:app --port 4242 --host 0.0.0.0"]
