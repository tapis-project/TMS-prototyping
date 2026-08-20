# Minimal Tapis OAuth Demo

## Purpose

This is a mimimal demonstration of how to consume the OAuth2 Authorization Code flow using a Tapis client.

## Running the Demo

### Using uv

1. Install the [uv package manager](https://docs.astral.sh/uv/guides/install-python/) on your system if it isn't installed yet.
2. Clone the repo and copy `dev.env.sample` to the path `dev.env`, replacing the client key/secret with appropriate values.
3. `uv sync`

**-- Globus OAuth**

1. `uv run --env-file=dev.env fastapi dev main_globus.py`
2. Visit the running demo at http://127.0.0.1:8000/

**-- Tapis OAuth**

1. `uv run --env-file=dev.env fastapi dev main.py`
2. Visit the running demo at http://127.0.0.1:8000/

### Using Docker

1. Install [docker](https://docs.docker.com/get-started/get-docker/) on your system if it isn't installed yet.
2. Clone the repo and copy `dev.env.sample` to the path `dev.env`, replacing the client key/secret with appropriate values.

**-- Globus OAuth**

1. In the root of the repo run the command: `docker build -f Dockerfile.globus -t tms:sgw-globus .`
2. After the image build completes, run the command: `docker run --rm -it -p 8000:8000  -v ./dev.env:/mnt/data/.env:ro tms:sgw-globus`
3. Visit the running demo at http://127.0.0.1:8000/

**-- Tapis OAuth**

1. In the root of the repo run the command: `docker build -f Dockerfile -t tms:sgw-tapis .`
2. After the image build completes, run the command: `docker run --rm -it -p 8000:8000  -v ./dev.env:/mnt/data/.env:ro tms:sgw-tapis`
3. Visit the running demo at http://127.0.0.1:8000/
