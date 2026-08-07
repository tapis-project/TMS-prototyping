#! /bin/bash

docker run --rm  -v `pwd`:`pwd` -w `pwd` -p 8000:8000 \
    ghcr.io/astral-sh/uv:debian \
    uv run --env-file=dev.env fastapi dev --host 0.0.0.0 main_globus.py