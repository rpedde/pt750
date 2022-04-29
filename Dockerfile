FROM python:3.9

WORKDIR /app
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install --no-install-recommends -y \
    ghostscript \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN poetry config virtualenvs.create false
COPY ./pyproject.toml ./poetry.lock /app/

RUN poetry install -vv --no-root

COPY . /app

ENTRYPOINT ["/app/docker/docker-entrypoint.sh"]
CMD ["labels"]
