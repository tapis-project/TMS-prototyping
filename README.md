# Minimal Tapis OAuth Demo

## Purpose

This is a mimimal demonstration of how to consume the OAuth2 Authorization Code flow using a Tapis client.

## Running the Demo

1. Install the [uv package manager](https://docs.astral.sh/uv/guides/install-python/) on your system if it isn't installed yet.

1. Clone the repo and copy `dev.env.sample` to the path `dev.env`, replacing the client key/secret with appropriate values.

3. `uv sync`

4. `uv run --env-file=dev.env fastapi dev main_globus.py`

5. Visit the running demo at http://localhost:8000/
