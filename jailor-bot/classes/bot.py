import discord
import modules.utilities as utilities
import traceback


class JailorBot(discord.Client):
    async def on_error(self, event_method, *args, **kwargs):
        utilities.logger.error(f"Something went wrong: {event_method}")
        traceback.print_exc()

    async def on_message(self, message):
        utilities.logger.info(message)
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello World!')