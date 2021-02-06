# jailor-discord-bot
## Discord bot

This is a discord bot which will help you manage your community. 
As the name implies it will reach users who does not respect your server rules and warning them (or soft banning in case of recidivist behaviour)

## Commands

The bot will answer to these commands:

Command | Description
--------|------------
j! help | Will show a help message that will list the bot commands
j! config | Will show a configuration recap
j! config <prefix> <value> | Will update a configuration to the passed value 
j! warn <user> <reason> | Will warn an user sending him a DM with the reason and giving them the warning role (if configured)
j! mute <user> <reason> | Will mute an user sending him a DM with the reason and giving them the mute role (if configured)
J! unmute <user> | Will revoke the muting directive and remove the mute role from the user

A second warning on the same user will automatically transform into a mute command.

## Configuration

So far you can customize these configurations for you discord server:

Prefix | Description
--------|------------
role <@role> | Specify the role the bot will listen to when searching for commands
command_prefix <value> | Change the command prefix (defaults to j!)
command_channel <#channel> | Specify the channel the bot will listen to (defaults to every channel the bot role can read)
warning_role <@role> | Specify the warning role the bot will assign to warned users
mute_role <@role> | Specify the mute role the bot will assign to muted users
warning_role_timer <value> | Specify the duration of the warning role assignement (defaults to 24)
mute_role_timer <value> | Specify the duration of the mute role assignement (defaults to 48)

## FAQ

**I want to invite this bot to my server**

Easy peasy, just click [here](https://discord.com/api/oauth2/authorize?client_id=804454621161848853&permissions=281111798&scope=bot) and follow the procedure for inviting the bot!

## Special Thanks

I'd like to thank the [Stadia Italia](https://discord.gg/jJcXhYYG) community for helping me test this bot and of course, giving me a caring home for my gaming sessions!