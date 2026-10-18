FROM python:3.14.8-slim-bookworm

RUN pip install --no-cache-dir pygments==2.21.0

# Tells the bin/ scripts that they already run inside this image
ENV CODEBASE_DOCKER=1

WORKDIR /app
