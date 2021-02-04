from enums.felony_type import FelonyType
import time


class BotFelony:
    def __init__(self, **args):
        self.guildId = args.get("guildId")
        self.type = FelonyType(args.get("type")) if args.get("type") and type(
            args.get("type")) is int else FelonyType.WARNING
        self.userId = args.get("userId")
        self.reason = args.get("reason", "")
        self.timestamp = args.get("timestamp", time.time())

    def to_dict(self):
        return {
            "guildId": self.guildId,
            "type": self.type.value,
            "userId": self.userId,
            "reason": self.reason,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(obj):
        return BotFelony(**obj)
