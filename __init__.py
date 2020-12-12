import discord
from discord.ext import commands

from Helpers.database import (
    init_db,
    delete_old_db_messages,
    get_old_lumberjack_messages,
    delete_lumberjack_messages_from_db, add_all_guilds, add_guild,
)
from Helpers.helpers import add_invite, remove_invite, add_all_invites, add_all_guild_invites, remove_all_guild_invites
from Cogs.logger import Logger
from Cogs.member_log import MemberLog
from Cogs.tracker import Tracker

import logging

logs = logging.getLogger("Lumberjack")
logs.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="Logs/lj.log", encoding="utf-8", mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logs.addHandler(handler)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="bum.", intents=intents, activity=discord.Activity(
            type=discord.ActivityType.watching, name="with ten thousand eyes."
        ))


if __name__ == "__main__":
    bot.add_cog(MemberLog(bot, logs))
    bot.add_cog(Tracker(bot, logs))
    bot.add_cog(Logger(bot, logs))
    init_db()
    add_all_guilds(bot)


@bot.event
async def on_ready():
    print("Bot is ready.")
    await add_all_invites(bot)


@bot.event
async def on_guild_join(guild):
    await add_all_guild_invites(guild)
    add_guild(guild)


@bot.event
async def on_guild_remove(guild):
    await remove_all_guild_invites(guild)


@bot.event
async def on_invite_create(invite):
    add_invite(invite)


@bot.event
async def on_invite_delete(invite):
    remove_invite(invite)


@bot.event
async def on_message_delete(message):
    delete_old_db_messages()
    db_messages = get_old_lumberjack_messages()
    for message_id in db_messages:
        channel = bot.get_channel(message_id[1])
        try:
            lum_message = await channel.fetch_message(message_id[0])
            await lum_message.delete()
        except discord.NotFound:
            pass
        delete_lumberjack_messages_from_db(message_id[0])


@bot.command()
async def ping(ctx):
    embed = discord.Embed(
        title="**Ping**", description=f"Pong! {round(bot.latency * 1000)}ms"
    )
    embed.set_author(name=f"{bot.user.name}", icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)


bot.remove_command("help")


@bot.command(aliases=["help"])
async def _help(ctx):
    await ctx.send(
        "`lum.ping` to check bot responsiveness\n"
        '`lum.log <log type> <"here" or channel mention/id>` will change what channel a log appears in\n'
        "`lum.clear <log type>` will disable a log\n"
        "`lum.track <user mention/id> <time in d h or m> <channel mention/id>` "
        "to place a tracker on someone\n"
        "`lum.untrack <user mention/id>` will remove a tracker"
    )


with open("token", "r") as f:
    bot.run(f.readline().strip())
