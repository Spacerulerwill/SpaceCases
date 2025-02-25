# spacecases

This directory contains the source code for the discord bot.

# Prerequisites

If you wish to host the bot locally you will need the following as a minimum:
- [uv](https://github.com/astral-sh/uv) if running the bot natively, or [docker](https://www.docker.com/) if you plan on running it containerised.
- **PostgreSQL** with a database and an associated superuser account.
- A **Discord bot user** setup with the necessary permissions:
  - **Create a Bot User**: Follow [this guide](https://discordpy.readthedocs.io/en/stable/discord.html) to create a Discord bot and obtain its token.
  - **Intents**: The bot uses the following privileged intents:
      - `Message Content`
      - `Server Members`
  - **Generating the Bot Invite Link**:
      - Use the following [scopes](https://discord.com/developers/docs/topics/oauth2#shared-resources-oauth2-scopes) when generating the invite link for the bot:
        - `bot`
        - `applications.commands`
      - Use the following [permissions](https://discord.com/developers/docs/topics/permissions) when generating the invite link for the bot:
        - `Send Messages`
- A **leaderboards server**. See [here](../services/leaderboards/README.md) for details on how to setup.

An **assets server** is not required, as you can use the official SpaceCases one at https://assets.spacecases.xyz. However, if you host your own you have the option of adding your own custom cases. See [here](../services/assets/README.md) for details on how to setup.

# Development Setup

You can use docker compose to get a quick development setup. Code changes will be reflected without having to rebuild any container images. It is **NOT** recommended for production  use.

```bash
git clone https://github.com/Spacerulerwill/SpaceCases             # Clone repository
cd SpaceCases/spacecases                                           # Change to SpaceCases directory
sudo docker build -t spacecaases -f Dockerfile ../                 # Build SpaceCases docker image
cd ../services/leaderboards                                        # Change to leaderboards directory
sudo docker build -t spacecases-leaderboards -f Dockerfile ../../  # Build leaderboards docker image
cd ../../spacecases                                                # Back to SpaceCases
sudo BOT_TOKEN=token OWNER_ID=owner-id docker compose up -d        # Run
```

# Normal Setup

Assuming you have all other components setup, you can now run the bot.

```bash
git clone https://github.com/Spacerulerwill/SpaceCases  # Clone repository
cd SpaceCases/spacecases                                # Change to SpaceCases directory
cp .env.example .env                                    # Create .env file
```

Use a text editor to fill out the environment variables in the `.env` file.

## Native (uv)

```bash
uv python install                                       # Install python 
uv sync                                                 # Download dependencies
uv run python -m spacecases                             # Run
```

Then you can use whatever scheduling system you like (for example, `crontab`) to periodically generate the leaderboards. The data in the `output` folder can then be served on your chosen domain using your preferred choice of HTTP server.

## via Docker

```bash 
sudo docker build -t spacecaases -f Dockerfile ../                                                           # Build docker image
sudo docker run -d -v spacecases-synced:/app/spacecases/synced --env-file .env --name spacecases spacecases  # Run
```
