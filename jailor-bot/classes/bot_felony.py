from enums.felony_type import FelonyType
import time


class BotFelony:
    def __init__(self, **args):
        self.guildId = args.get("guildId")
        self.guildName = args.get("guildName")
        self.type = FelonyType(args.get("type")) if args.get("type") and type(
            args.get("type")) is int else FelonyType.WARNING
        self.userId = args.get("userId")
        self.userName = args.get("userName")
        self.reason = args.get("reason", "")
        self.timestamp = args.get("timestamp", time.time())
        self.authorId = args.get("authorId")
        self.authorName = args.get("authorName")

    def to_dict(self):
        return {
            "guildId": self.guildId,
            "guildName": self.guildName,
            "type": self.type.value,
            "userId": self.userId,
            "userName": self.userName,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "authorId": self.authorId,
            "authorName": self.authorName
        }

    @staticmethod
    def from_dict(obj):
        return BotFelony(**obj)
