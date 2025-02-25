# leaderboards

This directory contains the script for generating leaderboards

# Setup

```bash
git clone https://github.com/Spacerulerwill/SpaceCases  # Clone the repository
cd SpaceCases/services/leaderboards                     # Move into the repository directory
cp .env.example .env                                    # Create env file
```

Then use a text editor to fill in the appropriate values in the `.env` file

## Native (uv)

```bash
uv python install                                       # Install python
uv sync                                                 # Download dependencies
uv run --no-sync src/gen_leaderboards.py                # Generate the initial leaderboards
```

Then you can use whatever scheduling system you like (for example, `crontab`) to periodically generate the leaderboards. The data in the `output` folder can then be served on your chosen domain using your preferred choice of HTTP server.

## via Docker

```bash
sudo docker build -t spacecases-leaderboards -f Dockerfile ../../                                                                      # Build the docker image `spacecases-leaderboards`
sudo docker run -d -v /your/output/path:/app/services/leaderboards/output --env-file .env --name leaderboards spacecases-leaderboards  # Run the service
```

The docker container will automatically refresh the leaderboards for you. The data in `/your/output/path` can then be served on your chosen domain using your preferred choice of HTTP server.
