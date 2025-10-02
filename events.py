import discord
from discord.ext import commands
from datetime import datetime, timedelta

from main import (
    ReactionRoles,
    Roles,
    load_data,
    save_data,
    get_user_data,
    WELCOME_AND_GOODBYE_CHANNEL,
    LOGS_CHANNEL,
    LEVELS_CHANNEL,
    nia_id,
    cest,
)
from levels import xp_for_next_level
from tickets import load_tickets


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id in self.bot.reaction_roles_message_ids:
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return

            member = guild.get_member(payload.user_id)
            if not member:
                return

            role = None
            if str(payload.emoji.name) == ReactionRoles.HIM.emoji:
                role = guild.get_role(ReactionRoles.HIM.role_id)
            elif str(payload.emoji.name) == ReactionRoles.HER.emoji:
                role = guild.get_role(ReactionRoles.HER.role_id)
            elif str(payload.emoji.name) == ReactionRoles.THEY.emoji:
                role = guild.get_role(ReactionRoles.THEY.role_id)
            elif str(payload.emoji.name) == ReactionRoles.OTHER.emoji:
                role = guild.get_role(ReactionRoles.OTHER.role_id)
            elif str(payload.emoji.name) == ReactionRoles.PROMO_RULES_ACCEPTED.emoji:
                role = guild.get_role(ReactionRoles.PROMO_RULES_ACCEPTED.role_id)

            if role:
                await member.add_roles(role)
                print(f"ROLE ADDITION --> Role: {role.name} Member: {member.name}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id in self.bot.reaction_roles_message_ids:
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return

            member = guild.get_member(payload.user_id)
            if not member:
                return

            role = None
            if str(payload.emoji.name) == ReactionRoles.HIM.emoji:
                role = guild.get_role(ReactionRoles.HIM.role_id)
            elif str(payload.emoji.name) == ReactionRoles.HER.emoji:
                role = guild.get_role(ReactionRoles.HER.role_id)
            elif str(payload.emoji.name) == ReactionRoles.THEY.emoji:
                role = guild.get_role(ReactionRoles.THEY.role_id)
            elif str(payload.emoji.name) == ReactionRoles.OTHER.emoji:
                role = guild.get_role(ReactionRoles.OTHER.role_id)
            elif str(payload.emoji.name) == ReactionRoles.PROMO_RULES_ACCEPTED.emoji:
                role = guild.get_role(ReactionRoles.PROMO_RULES_ACCEPTED.role_id)

            if role:
                await member.remove_roles(role)
                print(f"ROLE REMOVAL --> Role: {role.name} Member: {member.name}")


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user}')
        load_tickets(self)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel = self.bot.get_channel(WELCOME_AND_GOODBYE_CHANNEL)

        embed = discord.Embed(
            title="Welcome!",
            description=f"Welcome {member.mention} to {guild.name}!",
            color=discord.Color.green()
        )
        embed.add_field(name="Join date", value=f"<t:{int(member.joined_at.timestamp())}:F>")
        embed.set_thumbnail(url=f"{member.avatar.url}")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        channel = self.bot.get_channel(WELCOME_AND_GOODBYE_CHANNEL)

        embed = discord.Embed(
            title="Goodbye!",
            description=f"{member.mention} left {guild.name}!",
            color=discord.Color.red()
        )
        embed.add_field(name="Join date", value=f"<t:{int(member.joined_at.timestamp())}:F>")
        embed.set_thumbnail(url=f"{member.avatar.url}")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        log_channel = self.bot.get_channel(LOGS_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="Message Deleted",
                description=f"**Author:** {message.author.mention}\n"
                            f"**Channel:** {message.channel.mention}\n"
                            f"**Content:** {message.content or 'No content'}",
                color=discord.Color.red()
            )

            if message.attachments:
                attachment_urls = "\n".join([attachment.url for attachment in message.attachments])
                embed.add_field(name="Attachments", value=attachment_urls, inline=False)

            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        channel = self.bot.get_channel(LOGS_CHANNEL)
        embed = discord.Embed(
            title="Message Edited",
            description=f"**User:** {before.author.mention}\n**Channel:** {before.channel.mention}",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Before", value=before.content or "No content", inline=False)
        embed.add_field(name="After", value=after.content or "No content", inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        levels_channel = self.bot.get_channel(LEVELS_CHANNEL)
        if message.author.bot:
            return

        user = message.author

        if isinstance(message.channel, discord.DMChannel):
            channel = self.bot.get_channel(1407222427263701127)
            if channel:
                embed = discord.Embed(
                    description=message.content,
                    color=discord.Color.blue()
                )
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                await channel.send(embed=embed)


        data = load_data()
        user_data = get_user_data(data, str(user.id))

        if user_data["username"] != user.name:
            user_data["username"] = user.name

        if user_data["napping"]:
            user_data["napping"] = False
            try:
                current_nick = user.nick or user.display_name or user.name
                new_nick = current_nick.replace("[NAP]", "").strip()
                await user.edit(nick=new_nick or None)
                user_data["nickname"] = new_nick
            except discord.Forbidden:
                print(f"❌ I don’t have permission to change {user.name}’s nickname.")
            except discord.HTTPException as e:
                print(f"⚠️ Failed to change {user.name}'s nickname: {e}")

            embed = discord.Embed(
                title="⏰ No longer napping",
                description=f"Welcome back {user.mention}, you're no longer napping and users can ping you now.",
                color=discord.Color.nitro_pink()
            )
            embed.set_footer(text=f"You can now ping {user.name} again!")
            await message.channel.send(embed=embed)

        current_nick = user.nick or user.display_name or user.name
        if user_data["nickname"] != current_nick:
            user_data["nickname"] = current_nick


        for mentioned in message.mentions:
            mentioned_data = get_user_data(data, str(mentioned.id))
            napping = mentioned_data["napping"]
            if napping:
                try:
                    user_data["warnings"]+=1
                    if user_data["warnings"]>=3:
                        until = discord.utils.utcnow() + timedelta(hours=1)
                        await message.author.timeout(until, reason="Ping while napping")
                    await message.channel.send(
                        f"{message.author.mention} please do not ping {mentioned.name} right now as they are napping. You have been warned or punished with a 1 hour mute."
                    )
                except discord.Forbidden:
                    await message.channel.send("I don't have permission to timeout this user.")
                except discord.HTTPException as e:
                    await message.channel.send(f"Failed to timeout: {e}")

        if message.content == user_data["last_message"]:
            return

        xp_to_add = 1 * user_data["xp_multiplier"]

        user_data["last_message"] = message.content
        user_data["xp"] += xp_to_add

        while user_data["xp"] >= xp_for_next_level(user_data["level"]):
            levels_to_add = 1 * user_data["level_multiplier"]
            user_data["level"] += levels_to_add
            user_data["xp"] = 0
            embed = discord.Embed(
                title="New level!",
                description=f"{user.mention} leveled up to **Level {user_data['level']}**!",
                color=discord.Color.blue()
            )
            await levels_channel.send(embed=embed)

            if user_data["level"] >= 10:
                level_role = message.guild.get_role(Roles.YOUNG_FOX.role_id)
                await user.add_roles(level_role)
            elif user_data["level"] >= 25:
                level_role = message.guild.get_role(Roles.ADULT_FOX.role_id)
                await user.add_roles(level_role)
            elif user_data["level"] >= 50:
                level_role = message.guild.get_role(Roles.SENIOR_FOX.role_id)
                await user.add_roles(level_role)

        save_data(data)

        await self.bot.process_commands(message)



def setup(bot):
    bot.add_cog(Events(bot))
