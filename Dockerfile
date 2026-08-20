FROM python:3.13

WORKDIR /srv

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock .python-version /srv/
RUN uv sync

COPY static /srv/static
COPY templates /srv/templates
COPY main.py settings.py json_endpoints.py /srv/

CMD ["uv", "run", "--env-file", "/mnt/data/.env", "fastapi", "run", "main.py"]
