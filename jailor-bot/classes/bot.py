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

        if message.content.startswith(conf.command_prefix):
            args = message.content.split()

            if args[1] == "help":
                await send_commands_list(prefix=conf.command_prefix, channel=message.channel)
            elif args[1] == "config":
                utilities.logger.debug(args)
                if len(args) > 2:
                    if args[2] == "command_channel":
                        if len(args) > 3:
                            await update_channel(configuration=conf, context=message,
                                                 value_to_update=args[3])
                            return

                await send_configuration(configuration=conf, channel=message.channel)
            else:
                await send_error(message.channel)
        else:
            return


async def update_channel(configuration, context, value_to_update):
    channel = get_channel(context, value_to_update.replace("#", "")
                          .replace("<", "").replace(">", ""))
    if channel:
        configuration.command_channel = channel.id
        functions.update_configuration(guildId=configuration.guildId, item="command_channel", value=value_to_update)
        await send_Done(channel=context.channel, description="command_channel updated")


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


def get_embed(title, description, color):
    embed = discord.Embed(title=title,
                          description=description,
                          color=color)
    return embed
