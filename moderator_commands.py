import asyncio
import discord
from discord.ext import commands
from datetime import datetime, timedelta

from main import canUseModeratorCommands, load_data, save_data, get_user_data


class Moderator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.slash_command(
        name="clear",
        description="Mass remove a certain amount of messages from this channel."
    )
    async def clear(self, ctx, amount: discord.Option(int, "Amount of messages to remove")):
        if await canUseModeratorCommands(ctx):
            if amount < 1:
                await ctx.respond("Please specify a number greater than 0.", ephemeral=True)
                return

            deleted = await ctx.channel.purge(limit=amount)
            await ctx.respond(f"Deleted {len(deleted)} messages.", ephemeral=True)


    @commands.slash_command(
        name="schedule",
        description="Schedule a message to be sent after waiting a specific time."
    )
    async def schedule(
        self,
        ctx,
        seconds: discord.Option(int, "How many seconds to wait before sending"),
        message: discord.Option(str, "The message you want to schedule"),
        channel: discord.Option(discord.TextChannel, "Send the message in a specific channel", required=False)
    ):
        if await canUseModeratorCommands(ctx):
            scheduled_channel = channel or ctx.channel
            await ctx.respond(
                f"Message scheduled to send in {seconds} seconds in {scheduled_channel.mention}",
                ephemeral=True
            )

            await asyncio.sleep(seconds)
            await scheduled_channel.send(message)


    @commands.slash_command(
        name="schedule-embed",
        description="Schedule an embed message to be sent after waiting a specific time."
    )
    async def schedule_embed(
        self,
        ctx,
        seconds: discord.Option(int, "How many seconds to wait"),
        color: discord.Option(str, "Hex code of the embed color"),
        channel: discord.Option(discord.TextChannel, "Channel to send the embed", required=False),
        title: discord.Option(str, "Title of the embed", required=False),
        description: discord.Option(str, "Description of the embed", required=False)
    ):
        if await canUseModeratorCommands(ctx):
            scheduled_channel = channel or ctx.channel
            await ctx.respond(
                f"Embed scheduled to send in {seconds} seconds in {scheduled_channel.mention}",
                ephemeral=True
            )

            embed = discord.Embed(
                title=title or "",
                description=description or "",
                color=int(color.strip("#"), 16)
            )

            await asyncio.sleep(seconds)
            await scheduled_channel.send(embed=embed)


    @commands.slash_command(
        name="role",
        description="Assign a role to a user or remove it if they already have it."
    )
    async def role(
        self,
        ctx,
        user: discord.Option(discord.Member, "Member to give/take the role"),
        chosen_role: discord.Option(discord.Role, "The role to assign/remove")
    ):
        if await canUseModeratorCommands(ctx):
            if any(role.id == chosen_role.id for role in user.roles):
                await user.remove_roles(chosen_role)
                embed = discord.Embed(
                    title="Role removed",
                    description=f"Removed {chosen_role.mention} from {user.mention}.",
                    color=discord.Color.dark_green()
                )
            else:
                await user.add_roles(chosen_role)
                embed = discord.Embed(
                    title="Role added",
                    description=f"Added {chosen_role.mention} to {user.mention}.",
                    color=discord.Color.green()
                )
            await ctx.respond(embed=embed, ephemeral=True)


    @commands.slash_command(
        name="ban",
        description="Ban a member"
    )
    async def ban(
        self,
        ctx,
        user: discord.Option(discord.Member, "Member to ban"),
        reason: discord.Option(str, "Reason")
    ):
        if await canUseModeratorCommands(ctx):
            await user.ban(reason=reason)
            embed = discord.Embed(
                title=f"{user.name} has been banned.",
                description=f"Reason: {reason}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)


    @commands.slash_command(
        name="kick",
        description="Kick a member"
    )
    async def kick(
        self,
        ctx,
        user: discord.Option(discord.Member, "Member to kick"),
        reason: discord.Option(str, "Reason")
    ):
        if await canUseModeratorCommands(ctx):
            await user.kick(reason=reason)
            embed = discord.Embed(
                title=f"{user.name} has been kicked.",
                description=f"Reason: {reason}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)


    @commands.slash_command(
        name="timeout",
        description="Timeout a member"
    )
    async def timeout(
        self,
        ctx,
        user: discord.Option(discord.Member, "Member to timeout"),
        duration: discord.Option(int, "Duration in seconds"),
        reason: discord.Option(str, "Reason")
    ):
        if await canUseModeratorCommands(ctx):
            try:
                until_time = datetime.utcnow() + timedelta(seconds=duration)
                await user.timeout(until=until_time, reason=reason)

                embed = discord.Embed(
                    title=f"{user.name} has been timed out for {duration} seconds.",
                    description=f"**Reason:** {reason}",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=embed)
            except Exception as e:
                await ctx.respond(f"❌ Failed to timeout member: {e}", ephemeral=True)


    @commands.slash_command(
        name="find-user",
        description="Find everything about a member"
    )
    async def find_user(
        self,
        ctx,
        member: discord.Option(discord.Member, "Member to get information about")
    ):
        if await canUseModeratorCommands(ctx):

            data = load_data()
            user_data = get_user_data(data, str(member.id))

            embed = discord.Embed(
                title="User information",
                color=discord.Color.random()
            )

            avatar = member.avatar or member.default_avatar
            embed.set_thumbnail(url=avatar.url)

            author_avatar = ctx.author.avatar or ctx.author.default_avatar
            embed.set_footer(icon_url=author_avatar.url, text=f"Requested by {ctx.author.name}")

            embed.add_field(name="Username", value=member.name)
            embed.add_field(name="Display Name", value=member.display_name)
            embed.add_field(name="Joined Guild", value=member.joined_at)
            embed.add_field(
                name="Roles list",
                value="\n".join(role.mention for role in member.roles if role.name != "@everyone"),
            )
            embed.add_field(name="Status", value=member.status)

            if member.activities:
                activity_list = []
                for activity in member.activities:
                    if activity.type.name.lower() == "playing":
                        activity_list.append(f"🎮 Playing **{activity.name}**")
                    elif activity.type.name.lower() == "listening":
                        activity_list.append(f"🎵 Listening to **{activity.name}**")
                    elif activity.type.name.lower() == "streaming":
                        activity_list.append(f"📺 Streaming **{activity.name}**")
                    elif activity.type.name.lower() == "watching":
                        activity_list.append(f"📺 Watching **{activity.name}**")
                    else:
                        activity_list.append(f"{activity.type.name.title()} **{activity.name}**")

                activity_text = "\n".join(activity_list)
            else:
                activity_text = "No activity"

            embed.add_field(name="Activity", value=activity_text)
            embed.add_field(name="Mention", value=member.mention)
            embed.add_field(name="User ID", value=member.id)
            embed.add_field(name="Created at", value=member.created_at)

            if member.voice:
                embed.add_field(name="Voice channel", value="The user is in a voice channel")
            if member.bot:
                embed.add_field(name="Bot", value="This user is a bot")

            embed.add_field(name="Level", value=user_data["level"])
            embed.add_field(name="XP", value=user_data["xp"])
            embed.add_field(name="Level Multiplier", value=user_data["level_multiplier"])
            embed.add_field(name="XP Multiplier", value=user_data["xp_multiplier"])
            embed.add_field(name="Warnings", value=user_data["warnings"])
            embed.add_field(name="Gems", value=user_data["gems"])
            embed.add_field(name="Welcome Claimed", value=user_data["welcome_claimed"])
            embed.add_field(name="Second Chance", value=user_data["second_chance"])
            embed.add_field(name="Roulette Dexterity", value=user_data["roulette_dexterity"])
            embed.add_field(name="Gambling luck", value=user_data["gamble_luck"])
            embed.add_field(name="Roulette luck", value=user_data["roulette_luck"])
            embed.add_field(name="Napping", value=user_data["napping"])

            await ctx.respond(embed=embed)


    @commands.slash_command(
        name="dm",
        description="Send a DM to a member"
    )
    async def dm(
        self,
        ctx,
        member: discord.Option(discord.Member, "Member to DM"),
        message: discord.Option(str, "Message to send")
    ):
        if await canUseModeratorCommands(ctx):
            try:
                user = await self.bot.fetch_user(member.id)
                await user.send(message)
                await ctx.respond("✅ Sent!")
            except discord.Forbidden:
                await ctx.respond("❌ I can't DM this user (they might have DMs closed).")
            except discord.NotFound:
                await ctx.respond("❌ User not found.")
            except Exception as e:
                await ctx.respond(f"⚠️ Error: {e}")

    @commands.slash_command(
        name="force-nap",
        description="Force a nap to a member and avoid them getting pings"
    )
    async def force_nap(self, ctx, member: discord.Option(discord.Member, "Member to force a nap to")):

        if await canUseModeratorCommands(ctx):

            data = load_data()
            user_data = get_user_data(data, str(member.id))

            napping = user_data["napping"]

            if napping:
                user_data["napping"] = False
                embed = discord.Embed(
                    title=":alarm_clock: No longer napping",
                    description=f"Welcome back {member.mention}, you're no longer napping and users can ping you now.",
                    color=discord.Color.nitro_pink()
                )
                embed.set_footer(text=f"You can now ping {member.name} again!")
            else:
                user_data["napping"] = True
                embed = discord.Embed(
                    title=":crescent_moon: Napping",
                    description=f"{member.name}, have a good nap! Users will now be warned/punished if they try to ping you.",
                    color=discord.Color.dark_blue()
                )
                embed.set_footer(text=f"Don't ping {member.name}!")

            save_data(data)
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Moderator(bot))
