from infrastructure.env import EnvVars, get_env


class BotConfig:
    def __init__(self):
        self.bot_token: str = get_env(EnvVars.BOT_TOKEN)
        self.deploy_method = get_env(EnvVars.DEPLOY_METHOD).lower()
        if ":" not in self.bot_token:
            raise ValueError("Incorrect bot token")
        if self.deploy_method not in {"webhook", "polling"}:
            raise ValueError("Deploy method must be either 'webhook' or 'polling'")
