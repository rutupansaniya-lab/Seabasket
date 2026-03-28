FROM python:3.9

WORKDIR /code

RUN pip install "poetry ==1.3.1"

COPY pyproject.toml pyproject.toml

COPY poetry.lock poetry.lock

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
