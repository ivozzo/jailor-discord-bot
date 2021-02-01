class BotConfiguration:
    def __init__(self, guildId, **args):
        self.guildId = guildId
        self.default_channel = args.get("default_channel")
        self.default_prefix = args.get("default_prefix", '$')

    def to_dict(self):
        return {
            "guildId": self.guildId,
            "default_channel": self.default_channel,
            "default_prefix": self.default_prefix
        }
