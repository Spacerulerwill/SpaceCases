# Dockerfile to run the metadata
FROM ghcr.io/astral-sh/uv:python3.12-bookworm
WORKDIR /app

# common lib
RUN mkdir -p /app/common/src/common
ADD common/src/common/__init__.py /app/common/src/common
ADD common/pyproject.toml /app/common
ADD common/README.md /app/common


# static assets
COPY services/assets/static /app/services/assets/static

# scripts
ADD services/assets/src/constants.py /app/services/assets/src/constants.py
ADD services/assets/src/util.py /app/services/assets/src
ADD services/assets/src/gen_container_metadata.py /app/services/assets/src
ADD services/assets/src/gen_images.py /app/services/assets/src
ADD services/assets/src/gen_item_metadata.py /app/services/assets/src
ADD services/assets/src/refresh_prices.py /app/services/assets/src

# stuff for scripts to run
ADD services/assets/pyproject.toml /app/services/assets
ADD services/assets/user_agents.txt /app/services/assets

# script to run
ADD services/assets/entrypoint.sh /app/services/assets

# run
WORKDIR /app/services/assets
CMD ["sh", "entrypoint.sh"]
