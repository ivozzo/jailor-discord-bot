from boilerplate.mongodatabase import MongoDatabase
from classes.bot_configuration import BotConfiguration
from classes.bot_felony import BotFelony
import datetime


class JailorDatabase(MongoDatabase):
    def __init__(self, host, user, password, database, felony_repository, configuration_repository, logger):
        self.database = super().__init__(host=host, user=user, password=password, database=database)
        self.felony_repository = self.database[felony_repository]
        self.configuration_repository = self.database[configuration_repository]
        self.logger = logger

    def read_configuration(self, guild_id):
        configuration = self.configuration_repository.find_one({{"guildId": guild_id}})
        if configuration:
            self.logger.debug(f"Found configuration: {str(configuration)}")
            return configuration
        else:
            self.logger.debug(f"Cannot find any configuration matching guild {guild_id}")
            return None

    def remove_configuration(self, guild_id):
        deleted = self.configuration_repository.delete_many({"guildId": guild_id}).deleted_count
        if deleted > 0:
            self.logger.info(f"Deleted {deleted} configuration for guild {guild_id}")
            return True
        else:
            self.logger.info(f"Cannot delete configuration for guild {guild_id}")
            return False

    def update_configuration(self, guild_id, item, value):
        updated = self.configuration_repository.update_many({"guildId": guild_id}, {"$set": {item: value}})
        if updated > 0:
            self.logger.info(f"Updated configuration for guild {guild_id}")
            self.logger.debug(f"==> updated item {item} with value {value}")
            return True
        else:
            self.logger.info(f"Cannot update configuration for guild {guild_id}")
            self.logger.debug(f"==> Tried updating item {item} with value {value}")
            return False

    def create_configuration(self, guild_id):
        previous_configuration = self.read_configuration(guild_id=guild_id)
        if previous_configuration:
            self.logger.info(f"Configuration for {guild_id} already existing")
            self.logger.debug(f"==> {str(previous_configuration)}")
            return BotConfiguration.from_dict(previous_configuration)
        else:
            bot_configuration = BotConfiguration(guildId=guild_id)
            self.logger.info(f"Creating configuration for {guild_id}")
            self.configuration_repository.insert_one(bot_configuration.to_dict())
            return bot_configuration

    async def read_felonies(self, guild_id, felony_type):
        configuration = BotConfiguration.from_dict(self.read_configuration(guild_id))
        felonies = self.felony_repository.find({"guildId": guild_id, "type": felony_type,
                                                "timestamp": {"$lte": (datetime.datetime.now() - datetime.timedelta(
                                                    hours=int(configuration.warning_role_timer))).timestamp()}})
        self.logger.debug(f"Found these felonies of type {felony_type} for guild {guild_id}")
        self.logger.debug(f"{felonies}")
        return felonies

    def read_felony(self, guild_id, user_id, felony_type):
        felony = self.felony_repository.find_one({"guildId": guild_id, "userId": user_id, "type": felony_type})
        self.logger.debug(f"Found this felony for user {user_id} of type {felony_type} for guild {guild_id}")
        self.logger.debug(f"{felony}")
        return felony

    async def delete_felony(self, guild_id, user_id, felony_type):
        deleted = self.felony_repository.delete_many({"guildId": guild_id, "userId": user_id, "type": felony_type})
        if deleted > 0:
            self.logger.info(f"Deleted {deleted} felonies for user {user_id} in guild {guild_id}")
            return True
        else:
            self.logger.info(f"Cannot delete felonies for user {user_id} in guild {guild_id}")
            return False

    def update_felony(self, guild_id, user_id, previous_felony_type, reason, new_felony_type):
        updated = self.felony_repository.update_many(
            {"guildId": guild_id, "userId": user_id, "type": previous_felony_type}, {
                "$set": {"reason": reason, "type": new_felony_type, "timestamp": datetime.datetime.now().timestamp()}})
        if updated > 0:
            self.logger.info(f"Updated felonies for user {user_id} in {guild_id}")
            self.logger.debug(f"==> updated felony value {previous_felony_type} with value {new_felony_type}")
            return True
        else:
            self.logger.info(f"Cannot update felonies for user {user_id} in {guild_id}")
            self.logger.debug(f"==> tried updating felony value {previous_felony_type} with value {new_felony_type}")
            return False

    def create_felony(self, context, user, reason, felony_type):
        bot_felony = BotFelony(guildId=context.guild.id, guildName=context.guild.name, userId=user.id,
                               userName=user.name, type=felony_type.value, reason=reason,
                               authorId=context.author.id,
                               authorName=context.author.name)
        self.logger.info(f"Creating felony for {user.id} in guild {context.guild.id}")
        self.felony_repository.insert_one(bot_felony.to_dict())
        return bot_felony
