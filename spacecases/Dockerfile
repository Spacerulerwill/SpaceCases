FROM ghcr.io/astral-sh/uv:python3.12-alpine
WORKDIR /app

# add spacecases
COPY spacecases/spacecases /app/spacecases/spacecases
ADD spacecases/pyproject.toml /app/spacecases
ADD spacecases/.python-version /app/spacecases

# add common lib
RUN mkdir -p /app/common/src/common
ADD common/src/common/__init__.py /app/common/src/common
ADD common/pyproject.toml /app/common
ADD common/README.md /app/common

WORKDIR /app/spacecases
CMD ["uv", "run", "python", "-m", "spacecases"]
