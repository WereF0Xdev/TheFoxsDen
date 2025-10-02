import discord
from discord.ext import commands

from main import load_data, get_user_data


def xp_for_next_level(level):
    return level * 10


class Levels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name="level",
        description="Check your leveling progress."
    )
    async def level(self, ctx, member: discord.Option(discord.Member, "Member to check", required=False)):
        if not member:
            member = ctx.author

        data = load_data()
        user_data = get_user_data(data, str(member.id))

        next_level_xp = xp_for_next_level(user_data["level"])
        xp_multiplier = user_data["xp_multiplier"]
        level_multiplier = user_data["level_multiplier"]

        embed = discord.Embed(
            title=f"{member.display_name}'s Level",
            color=discord.Color.blue()
        )
        embed.add_field(name="Level", value=f"{user_data['level']}", inline=False)
        embed.add_field(name="XP", value=f"{user_data['xp']}/{next_level_xp}", inline=False)
        embed.add_field(name="XP Multiplier", value=f"{xp_multiplier}x", inline=False)
        embed.add_field(name="Level Multiplier", value=f"{level_multiplier}x", inline=False)
        embed.set_thumbnail(url=member.avatar.url)

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Levels(bot))