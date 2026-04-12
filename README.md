# Work Hours Bot

This bot aims to help you track your busy time.

## Installation and Start
Recomended:
1) clone repo
2) use uv and `uv sync` in project dir to install all dependencies
3) run `python src/main.py`

## Configuration
To configure the bot use environment variables:
- BOT_TOKEN - telegram token of the bot from @BotFather
- REGISTRATION_PASSWORD - minimal auth, only people who know this can register
- DEPLOY_METHOD - polling | webhook (webhook is unavailable for now)
- DB_LOCATION - location of the sqlite database on the disk (other db's are unavailable for now)