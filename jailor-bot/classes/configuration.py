class Configuration:
    def __init__(self, guildId, default_channel=None, default_prefix=None):
        self.guildId = guildId
        self.default_channel = default_channel if default_channel else None
        self.default_prefix = default_prefix if default_prefix else '$'
