FROM python:3.10

WORKDIR /app
ENV PYTHONPATH=/app

RUN sed -i /etc/apt/sources.list -e 's/ main/ main contrib non-free/' || /bin/true
RUN sed -i /etc/apt/sources.list.d/debian.sources -e 's/Components: main/Components: main contrib non-free/' || /bin/true
RUN apt-get update && apt-get install --no-install-recommends -y \
    ghostscript \
    libsnmp-dev \
    libudev-dev \
    libsnmp-base \
    snmp-mibs-downloader \
    libgl1 \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN poetry config virtualenvs.create false
COPY ./pyproject.toml ./poetry.lock /app/

RUN poetry install -vv --no-root

COPY . /app

ENTRYPOINT ["/app/docker/docker-entrypoint.sh"]
CMD ["labels"]
