import discord
import modules.utilities as utilities
import modules.functions as functions
from classes.bot_configuration import BotConfiguration

import traceback


class JailorBot(discord.Client):
    async def on_error(self, event_method, *args, **kwargs):
        utilities.logger.error(f"Something went wrong: {event_method}")
        traceback.print_exc()

    async def on_message(self, message):
        utilities.logger.debug(message)
        if message.author == self.user:
            return

        conf = BotConfiguration.from_dict(functions.read_configuration(message.guild.id))

        if conf.command_channel:
            if int(clean_channel_id(conf.command_channel)) != message.channel.id:
                return

        if message.content.startswith(conf.command_prefix):
            args = message.content.split()

            if args[1] == "help":
                await send_commands_list(prefix=conf.command_prefix, channel=message.channel)
            elif args[1] == "config":
                await config_manager(args=args, configuration=conf, message=message)
            else:
                await send_error(message.channel)
        else:
            return

async def config_manager(args, configuration, message):
    utilities.logger.debug(args)
    if len(args) > 3:
        if args[2] == "command_channel":
            await update_channel(configuration=configuration, context=message,
                                 value_to_update=args[3])
            return
        elif args[2] == "command_prefix":
            await update_prefix(configuration=configuration, context=message,
                                value_to_update=args[3])
            return
        elif args[2] == "role":
            await update_role(configuration=configuration, context=message,
                              value_to_update=args[3])
            return
        elif args[2] == "warning_role":
            await update_warning_role(configuration=configuration, context=message,
                              value_to_update=args[3])
            return
        elif args[2] == "mute_role":
            await update_mute_role(configuration=configuration, context=message,
                              value_to_update=args[3])
            return

    await send_configuration(configuration=configuration, channel=message.channel)


def clean_channel_id(channel_id):
    return channel_id.replace("<#", "").replace(">", "")


def clean_role_id(role_id):
    return role_id.replace("<@&", "").replace(">", "")


async def update_channel(configuration, context, value_to_update):
    if value_to_update == "disable":
        configuration.command_channel = None
        functions.update_configuration(guildId=configuration.guildId, item="command_channel", value=None)
        await send_Done(channel=context.channel, description="Command channel disabled")
    else:
        if get_channel(context, clean_channel_id(value_to_update)):
            configuration.command_channel = value_to_update
            functions.update_configuration(guildId=configuration.guildId, item="command_channel", value=value_to_update)
            await send_Done(channel=context.channel, description="Command channel updated")


async def update_role(configuration, context, value_to_update):
    if value_to_update == "disable":
        configuration.role = None
        functions.update_configuration(guildId=configuration.guildId, item="role", value=None)
        await send_Done(channel=context.channel, description="Role check disabled")
    else:
        if get_role(context, clean_role_id(value_to_update)) in context.guild.roles:
            configuration.role = value_to_update
            functions.update_configuration(guildId=configuration.guildId, item="role", value=value_to_update)
            await send_Done(channel=context.channel, description="Role check updated")


async def update_warning_role(configuration, context, value_to_update):
    if get_role(context, clean_role_id(value_to_update)) in context.guild.roles:
        configuration.warning_role = value_to_update
        functions.update_configuration(guildId=configuration.guildId, item="warning_role", value=value_to_update)
        await send_Done(channel=context.channel, description="Role for warned users updated")


async def update_mute_role(configuration, context, value_to_update):
    if get_role(context, clean_role_id(value_to_update)) in context.guild.roles:
        configuration.mute_role = value_to_update
        functions.update_configuration(guildId=configuration.guildId, item="mute_role", value=value_to_update)
        await send_Done(channel=context.channel, description="Role for muted users updated")


async def update_prefix(configuration, context, value_to_update):
    configuration.command_prefix = value_to_update
    functions.update_configuration(guildId=configuration.guildId, item="command_prefix", value=value_to_update)
    await send_Done(channel=context.channel, description="Command prefix updated")


async def send_error(channel):
    title = f"Error"
    description = "Command not found"
    embed = get_embed(title=title, description=description, color=discord.Color.red())
    await channel.send(embed=embed)


async def send_Done(channel, description):
    title = f"Done"
    embed = get_embed(title=title, description=description, color=discord.Color.dark_green())
    await channel.send(embed=embed)


async def send_commands_list(prefix, channel):
    title = "Command list"
    description = "Command list for Jailor Bot"
    embed = get_embed(title=title, description=description, color=discord.Colour.dark_green())
    embed.add_field(name=f"{prefix} help", value="Show this message", inline=False)
    embed.add_field(name=f"{prefix} config", value="Show the actual configuration for your server", inline=False)
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

    await channel.send(embed=embed)


def get_channel(context, id):
    return [x for x in context.guild.channels if x.id == int(id)][0]

def get_role(context, id):
    return [x for x in context.guild.roles if x.id == int(id)][0]


def get_embed(title, description, color):
    embed = discord.Embed(title=title,
                          description=description,
                          color=color)
    return embed
