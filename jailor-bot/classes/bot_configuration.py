class BotConfiguration:
    def __init__(self, **args):
        self.guildId = args.get("guildId")
        self.role = args.get("role")
        self.command_channel = args.get("command_channel")
        self.command_prefix = args.get("command_prefix", 'j!')
        self.warning_role = args.get("default_role")
        self.warning_role_timer = args.get("default_role_timer", "1d")
        self.mute_role = args.get("mute_role")
        self.mute_role_timer = args.get("default_role_timer", "1d")

    def to_dict(self):
        return {
            "guildId": self.guildId,
            "role": self.role,
            "command_channel": self.command_channel,
            "command_prefix": self.command_prefix,
            "warning_role": self.warning_role,
            "warning_role_timer": self.warning_role_timer,
            "mute_role": self.mute_role,
            "mute_role_timer": self.mute_role_timer
        }

    @staticmethod
    def from_dict(obj):
        return BotConfiguration(**obj)
