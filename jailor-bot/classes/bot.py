import discord
import asyncio
import traceback
from classes.bot_configuration import BotConfiguration
from enums.felony_type import FelonyType


class JailorBot(discord.Client):

    def __init__(self, database, logger):
        super(JailorBot, self).__init__()
        self.database = database
        self.logger = logger

    async def on_error(self, event_method, *args, **kwargs):
        self.logger.error(f"Something went wrong: {event_method}")
        traceback.print_exc()

    async def on_message(self, message):
        self.logger.debug(message)
        if message.author == self.user:
            return

        conf = BotConfiguration.from_dict(self.database.read_configuration(guild_id=message.guild.id))

        if conf.command_channel:
            if int(clean_channel_id(conf.command_channel)) != message.channel.id:
                return

        if message.content.startswith(conf.command_prefix):
            args = message.content.split()
            if args[0] == conf.command_prefix:
                self.logger.debug("matched space!")
            if args[1] == "help":
                await send_commands_list(prefix=conf.command_prefix, channel=message.channel)
            elif args[1] == "config":
                await self.config_manager(args=args, configuration=conf, message=message)
            elif args[1] == "warn":
                await self.add_user_felony(configuration=conf, context=message, args=args,
                                           felony_type=FelonyType.WARNING)
            elif args[1] == "mute":
                await self.add_user_felony(configuration=conf, context=message, args=args, felony_type=FelonyType.MUTE)
            elif args[1] == "unmute":
                await self.remove_user_felony(configuration=conf, context=message, args=args,
                                              felony_type=FelonyType.MUTE)
            elif args[1] == "kick":
                await self.kick_user(context=message, args=args)
            else:
                await send_error(message.channel, "Command not found!")
        else:
            return

    async def kick_user(self, context, args):
        reason = ' '.join(map(str, args[3:]))
        confirmation_message = await send_confirmation(title="Kick user",
                                                       description="Kick user confirmation, click ✅ to confirm",
                                                       context=context, reason=reason)

        def check_confirmation(reaction, user):
            return user == context.author and str(reaction.emoji) == "✅"

        try:
            reaction, user = await self.wait_for("reaction_add", timeout=15.0, check=check_confirmation)
        except asyncio.TimeoutError:
            embed = get_embed(title="Timeout", description="Timeout met for confirmation", color=discord.Color.red())
            confirmation_message.clear_reactions()
            await confirmation_message.edit(embed=embed)
        else:
            user = await context.guild.fetch_member(clean_user_id(args[2]))
            embed = get_embed(title="Kick",
                              description=f"You've been kicked from {context.guild.name}",
                              color=discord.Color.dark_magenta())
            embed.add_field(inline=False, name="Reason", value=f"{reason}")
            await user.send(embed=embed)
            await context.guild.kick(user=user, reason=f"{reason}")
            embed = get_embed(title="Done",
                              description=f"User {user.name} has been successfully kicked from {context.guild.name}",
                              color=discord.Color.green())
            embed.add_field(inline=False, name="Reason", value=f"{reason}")
            await confirmation_message.edit(embed=embed)

        await confirmation_message.clear_reactions()

    async def remove_felony(self, guild, felonies, felony_type):
        configuration = BotConfiguration.from_dict(self.database.read_configuration(guild_id=guild.id))
        role = None
        if felony_type == 1 and configuration.warning_role:
            role = get_role(guild=guild, roleId=configuration.warning_role)

        if felony_type == 2 and configuration.mute_role:
            role = get_role(guild=guild, roleId=configuration.mute_role)

        for felony in felonies:
            user = await guild.fetch_member(felony["userId"])
            if user and role:
                await user.remove_roles(role, reason="Felony expired")
            await self.database.delete_felony(guild_id=guild.id, user_id=felony["userId"], felony_type=felony_type)

    async def config_manager(self, args, configuration, message):
        self.logger.debug(args)
        if len(args) > 3:
            if args[2] == "command_channel":
                await self.update_channel(configuration=configuration, context=message,
                                          value_to_update=args[3])
                return
            elif args[2] == "command_prefix":
                await self.update_prefix(configuration=configuration, context=message,
                                         value_to_update=args[3])
                return
            elif args[2] == "role":
                await self.update_role(configuration=configuration, context=message,
                                       value_to_update=args[3])
                return
            elif args[2] == "warning_role":
                await self.update_warning_role(configuration=configuration, context=message,
                                               value_to_update=args[3])
                return

            elif args[2] == "warning_role_timer":
                await self.update_warning_role_timer(configuration=configuration, context=message,
                                                     value_to_update=args[3])
                return

            elif args[2] == "mute_role":
                await self.update_mute_role(configuration=configuration, context=message,
                                            value_to_update=args[3])
                return

            elif args[2] == "mute_role_timer":
                await self.update_mute_role_timer(configuration=configuration, context=message,
                                                  value_to_update=args[3])
                return

        await send_configuration(configuration=configuration, channel=message.channel)

    async def add_user_felony(self, configuration, context, args, felony_type):
        if len(args) > 3:
            user = await context.guild.fetch_member(clean_user_id(args[2]))
            reason = ' '.join(map(str, args[3:]))

            previous_role = None
            target_role = None
            title = ""
            description = ""
            previous_felony = None
            warning_role = get_role(guild=context.guild, roleId=configuration.warning_role)
            mute_role = get_role(guild=context.guild, roleId=configuration.mute_role)

            if user:
                if felony_type == FelonyType.WARNING and configuration.warning_role:
                    previous_felony = self.database.read_felony(guild_id=context.guild.id, user_id=user.id,
                                                                felony_type=felony_type.value)
                    if previous_felony:
                        title = "Mute"
                        description = "You've been muted!"
                        previous_role = warning_role
                        target_role = mute_role
                    else:
                        title = "Warning"
                        description = "You've been warned!"
                        target_role = warning_role
                if felony_type == FelonyType.MUTE and configuration.mute_role:
                    title = "Mute"
                    description = "You've been muted!"
                    target_role = mute_role
                embed = get_embed(title=title, description=description, color=discord.Color.gold())
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.set_author(name=context.author.name, icon_url=context.author.avatar_url)

                if previous_felony:
                    self.logger.debug(f"Found previous felony {str(previous_felony)}")
                    self.database.update_felony(guild_id=context.guild.id, user_id=user.id,
                                                previous_felony_type=felony_type.value, reason=reason,
                                                new_felony_type=felony_type.value + 1)
                else:
                    self.database.create_felony(context=context, user=user, reason=reason, felony_type=felony_type)

                if target_role and previous_felony:
                    await user.add_roles(target_role, reason=reason)
                    await user.remove_roles(previous_role, reason="Felony upgrade")
                if target_role and not previous_felony:
                    await user.add_roles(target_role, reason=reason)
                await user.send(embed=embed)
        else:
            await send_error(context.channel, "Reason for felony is missing!")

    async def remove_user_felony(self, configuration, context, args, felony_type):
        user = await context.guild.fetch_member(clean_user_id(args[2]))
        role = get_role(guild=context.guild, roleId=configuration.mute_role)
        if user and role:
            await user.remove_roles(role, reason="Removing felony as request")
        await self.database.delete_felony(guild_id=context.guild.id, user_id=user.id, felony_type=felony_type.value)

    async def update_channel(self, configuration, context, value_to_update):
        if value_to_update == "disable":
            configuration.command_channel = None
            self.database.update_configuration(guildId=configuration.guildId, item="command_channel", value=None)
            await send_done(channel=context.channel, description="Command channel disabled")
        else:
            if get_channel(context, clean_channel_id(value_to_update)):
                configuration.command_channel = value_to_update
                self.database.update_configuration(guildId=configuration.guildId, item="command_channel",
                                                   value=value_to_update)
                await send_done(channel=context.channel, description="Command channel updated")

    async def update_role(self, configuration, context, value_to_update):
        if value_to_update == "disable":
            configuration.role = None
            self.database.update_configuration(guildId=configuration.guildId, item="role", value=None)
            await send_done(channel=context.channel, description="Role check disabled")
        else:
            if get_role(context.guild, clean_role_id(value_to_update)) in context.guild.roles:
                configuration.role = value_to_update
                self.database.update_configuration(guildId=configuration.guildId, item="role", value=value_to_update)
                await send_done(channel=context.channel, description="Role check updated")

    async def update_warning_role_timer(self, configuration, context, value_to_update):
        if not value_to_update.isnumeric():
            await send_error(context.channel, "The specified value is not numeric")
        else:
            self.database.update_configuration(guildId=configuration.guildId, item="warning_role_timer",
                                               value=int(value_to_update))
            await send_done(channel=context.channel, description="Timer for warned users updated")

    async def update_mute_role_timer(self, configuration, context, value_to_update):
        if not value_to_update.isnumeric():
            await send_error(context.channel, "The specified value is not numeric")
        else:
            self.database.update_configuration(guildId=configuration.guildId, item="mute_role_timer",
                                               value=int(value_to_update))
            await send_done(channel=context.channel, description="Timer for muted users updated")

    async def update_warning_role(self, configuration, context, value_to_update):
        if get_role(context.guild, clean_role_id(value_to_update)) in context.guild.roles:
            configuration.warning_role = value_to_update
            self.database.update_configuration(guildId=configuration.guildId, item="warning_role",
                                               value=value_to_update)
            await send_done(channel=context.channel, description="Role for warned users updated")

    async def update_mute_role(self, configuration, context, value_to_update):
        if get_role(context.guild, clean_role_id(value_to_update)) in context.guild.roles:
            configuration.mute_role = value_to_update
            self.database.update_configuration(guildId=configuration.guildId, item="mute_role", value=value_to_update)
            await send_done(channel=context.channel, description="Role for muted users updated")

    async def update_prefix(self, configuration, context, value_to_update):
        configuration.command_prefix = value_to_update
        self.database.update_configuration(guildId=configuration.guildId, item="command_prefix", value=value_to_update)
        await send_done(channel=context.channel, description="Command prefix updated")


async def send_confirmation(context, title, description, reason):
    embed = get_embed(title=title, description=description, color=discord.Color.dark_magenta())
    embed.add_field(name="Reason", inline=False, value=reason)
    confirmation_message = await context.channel.send(embed=embed)
    await confirmation_message.add_reaction(emoji="✅")
    await confirmation_message.add_reaction(emoji="❎")
    return confirmation_message


async def send_error(channel, description):
    title = f"Error"
    description = description
    embed = get_embed(title=title, description=description, color=discord.Color.red())
    await channel.send(embed=embed)


async def send_done(channel, description):
    title = f"Done"
    embed = get_embed(title=title, description=description, color=discord.Color.dark_green())
    await channel.send(embed=embed)


async def send_commands_list(prefix, channel):
    title = "Command list"
    description = "Command list for Jailor Bot"
    embed = get_embed(title=title, description=description, color=discord.Colour.dark_green())
    embed.add_field(name=f"{prefix} help", value="Show this message", inline=False)
    embed.add_field(name=f"{prefix} config", value="Show the actual configuration for your server", inline=False)
    embed.add_field(name=f"{prefix} warn <user> <reason>", value="Warn user (role must be configured)", inline=False)
    embed.add_field(name=f"{prefix} mute <user> <reason>", value="Mute user (role must be configured)",
                    inline=False)
    embed.add_field(name=f"{prefix} unmute <user>", value="Unmute user and remove mute role",
                    inline=False)
    await channel.send(embed=embed)


async def send_configuration(configuration, channel):
    title = "Configuration"
    description = "Command usage"
    embed = get_embed(title=title, description=description, color=discord.Color.dark_gold())
    embed.add_field(name=f"{configuration.command_prefix} config role <@role | disable>",
                    value=f"Current: {configuration.role if configuration.role else 'unset'}\n"
                          f"Set or remove which role can use commands", inline=False)

    embed.add_field(name=f"{configuration.command_prefix} config command_prefix <prefix>",
                    value=f"Current: {configuration.command_prefix}\n"
                          f"Set a command prefix for your server", inline=False)

    embed.add_field(name=f"{configuration.command_prefix} config command_channel <#channel | disable>",
                    value=f"Current: {configuration.command_channel if configuration.command_channel else 'unset'}\n"
                          f"Set or remove which channel the bot will use to read commands", inline=False)

    embed.add_field(name=f"{configuration.command_prefix} config warning_role <@role>",
                    value=f"Current: {configuration.warning_role if configuration.warning_role else 'unset'}\n"
                          f"Set the role the user will gain upon calling the warn command", inline=False)

    embed.add_field(name=f"{configuration.command_prefix} config warning_role_timer <hours>",
                    value=f"Current: {configuration.warning_role_timer if configuration.warning_role_timer else 'unset'}\n"
                          f"Set the timer in hours after which a warned user will lose the role", inline=False)

    embed.add_field(name=f"{configuration.command_prefix} config mute_role <@role>",
                    value=f"Current: {configuration.mute_role if configuration.mute_role else 'unset'}\n"
                          f"Set the role the user will gain upon calling the mute command", inline=False)

    embed.add_field(name=f"{configuration.command_prefix} config mute_role_timer <hours>",
                    value=f"Current: {configuration.mute_role_timer if configuration.mute_role_timer else 'unset'}\n"
                          f"Set the timer in hours after which a muted user will lose the role", inline=False)
    await channel.send(embed=embed)


def get_channel(context, id):
    return [x for x in context.guild.channels if x.id == int(id)][0]


def get_user(context, id):
    return [x for x in context.guild.members if x.id == int(id)][0]


def get_role(guild, roleId):
    role = [x for x in guild.roles if x.id == int(clean_role_id(roleId))]
    if len(role) > 0:
        return role[0]
    else:
        return None


def get_embed(title, description, color):
    embed = discord.Embed(title=title,
                          description=description,
                          color=color)
    return embed


def clean_channel_id(channel_id):
    return channel_id.replace("<#", "").replace(">", "")


def clean_role_id(role_id):
    return role_id.replace("<@&", "").replace(">", "")


def clean_user_id(user_id):
    return user_id.replace("<@!", "").replace(">", "")
