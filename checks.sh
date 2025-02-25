#! /bin/bash

LIGHT_BLUE="\e[94m"
WHITE="\e[97m"

echo -e "$LIGHT_BLUE"Starting global checks $dir"$WHITE"
echo Spell checking...
uv pip install --system codespell > /dev/null 2>&1
uv run codespell .

directories=("spacecases" "common" "services/leaderboards" "services/assets")

# Iterate over the directories
for dir in "${directories[@]}"; do
    cd $dir
    echo -e "$LIGHT_BLUE"Starting checks for $dir"$WHITE"
    uv sync >/dev/null 2>&1
    echo Typechecking...
    uv run --no-sync pyright
    echo Formatting...
    uv run --no-sync ruff format .
    echo Linting...
    uv run --no-sync ruff check . --fix
    cd - > /dev/null
done