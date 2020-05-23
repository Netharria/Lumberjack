from datetime import datetime

import discord
from discord.ext import commands

from database import get_log_by_id
from helpers import return_time_delta_string, get_invite, update_invite, format_date


class MemberLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        gld = get_log_by_id(member.guild.id)
        logs = self.bot.get_channel(gld[1])
        account_age = datetime.utcnow() - member.created_at
        invite_used = "Vanity URL"
        invite_uses = ""
        inviter = ""
        for invite in await gld.invites():
            before_invite = get_invite(invite.id)
            if before_invite.uses != invite.uses:
                invite_used = invite.url
                invite_uses = f"{invite.uses} uses"
                inviter = invite.inviter
                update_invite(invite)
        if account_age.days < 7:
            color = 0xFFC704
        else:
            color = 0x008000
        if logs is None:
            pass
        else:
            embed = discord.Embed(
                title=f"**User Joined**",
                description=f"""**Name:** {member.mention}
    **Created on:** {member.created_at.strftime(format_date)}
    **Account age:** {account_age.days} days old
    **Invite used:** {invite_used} {invite_uses}
    **Created By:** {inviter}""",
                color=color,
            )
            new_account_string = return_time_delta_string(account_age)
            if len(new_account_string) > 0:
                embed.add_field(
                    name="**New Account**",
                    value=f"Created {new_account_string}ago",
                    inline=False,
                )
            embed.set_author(name=f"{member.name}#{member.discriminator} ({member.id})")
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Total Members: {member.guild.member_count}")
            embed.timestamp = datetime.utcnow()
            await logs.send(embed=embed)
            stat_channel = self.bot.get_channel(gld[9])
            if stat_channel is None:
                pass
            else:
                await stat_channel.edit(name=f"Members: {member.guild.member_count}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        gld = get_log_by_id(member.guild.id)
        logs = self.bot.get_channel(gld[2])
        if logs is None:
            pass
        else:
            account_age = datetime.utcnow() - member.created_at
            time_on_server = datetime.utcnow() - member.joined_at
            embed = discord.Embed(
                title=f"**User Left**",
                description=f"""**Name:** {member.mention}
    **Created on:** {member.created_at.strftime(format_date)}
    **Account age:** {account_age.days} days old
    **Joined on:** {member.joined_at.strftime(format_date)} ({time_on_server.days} days ago)""",
                color=0xD90000,
            )
            embed.set_author(name=f"{member.name}#{member.discriminator} ({member.id})")
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Total Members: {member.guild.member_count}")
            embed.timestamp = datetime.utcnow()
            roles = [f"<@&{role.id}>" for role in member.roles[1:]]
            roles_str = " ".join(roles)
            if len(roles) < 1:
                embed.add_field(name=f"**Roles[{len(roles)}]**", value="None", inline=False)
            else:
                embed.add_field(
                    name=f"**Roles[{len(roles)}]**", value=f"{roles_str}", inline=False
                )
            await logs.send(embed=embed)
            stat_channel = self.bot.get_channel(gld[9])
            if stat_channel is None:
                pass
            else:
                await stat_channel.edit(name=f"Members: {member.guild.member_count}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        gld = get_log_by_id(after.guild.id)
        logs = self.bot.get_channel(gld[7])
        if before.nick == after.nick:
            pass
        elif logs is None:
            pass
        else:
            embed = discord.Embed(
                title=f"**User Nickname Updated**",
                description=f"""**User:** <@!{after.id}>\n
    **Before:** {before.nick}
    **After:** {after.nick}""",
                color=0x22FFC2,
            )
            embed.set_author(name=f"{after.name}#{after.discriminator} ({after.id})")
            embed.set_thumbnail(url=after.avatar_url)
            embed.set_footer(text=f"")
            embed.timestamp = datetime.utcnow()
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        for guild in self.bot.guilds:
            if after in guild.members:
                gld = get_log_by_id(guild.id)
                if before.name != after.name or before.discriminator != after.discriminator:
                    logs = self.bot.get_channel(gld[6])
                    if logs is None:
                        pass
                    else:
                        embed = discord.Embed(
                            title=f"**Username Updated**",
                            description=f"""**User:** <@!{after.id}>\n
    **Before:** {before.name}#{before.discriminator}
    **After:** {after.name}#{after.discriminator}""",
                            color=0x22FFC2,
                        )
                        embed.set_author(
                            name=f"{after.name}#{after.discriminator} ({after.id})"
                        )
                        embed.set_thumbnail(url=after.avatar_url)
                        embed.set_footer(text=f"")
                        embed.timestamp = datetime.utcnow()
                        await logs.send(embed=embed)
                if before.avatar != after.avatar:
                    logs = self.bot.get_channel(gld[8])
                    if logs is None:
                        pass
                    else:
                        embed = discord.Embed(
                            title=f"**User avatar Updated**",
                            description=f"""**User:** <@!{after.id}>\n
    Old avatar in thumbnail. New avatar down below""",
                            color=0x8000FF,
                        )
                        embed.set_author(
                            name=f"{after.name}#{after.discriminator} ({after.id})"
                        )
                        embed.set_thumbnail(url=before.avatar_url)
                        embed.set_footer(text=f"")
                        embed.set_image(url=after.avatar_url_as(size=128))
                        embed.timestamp = datetime.utcnow()
                        await logs.send(embed=embed)