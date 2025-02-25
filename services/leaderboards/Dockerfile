# Dockerfile to run the metadata
FROM ghcr.io/astral-sh/uv:python3.12-bookworm
WORKDIR /app

# common lib
RUN mkdir -p /app/common/src/common
ADD common/src/common/__init__.py /app/common/src/common
ADD common/pyproject.toml /app/common
ADD common/README.md /app/common

RUN mkdir -p /app/services/leaderboards
ADD services/leaderboards/pyproject.toml /app/services/leaderboards
ADD services/leaderboards/gen_leaderboards.py /app/services/leaderboards
ADD services/leaderboards/gen_leaderboards.py /app/services/leaderboards
ADD services/leaderboards/gen_leaderboards.sh /app/services/leaderboards

WORKDIR /app/services/leaderboards
CMD ["sh", "gen_leaderboards.sh"]