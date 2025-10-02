import discord
from discord.ext import commands
import json
from datetime import datetime
import calendar



from main import (
    guild_rules,
    ReactionRoles,
    REACTION_ROLES_FILE,
    SUGGESTIONS_CHANNEL,
    load_data,
    save_data,
    get_user_data,
)



class FoxaClausList(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name="foxa-claus-list",
        description="Check your position and details on the Fox'a Claus list"
    )
    async def foxa_claus_list(
            self,
            ctx,
            show_gift: discord.Option(bool, "Show the gift you selected")
    ):

        user = ctx.author
        data = load_data()
        user_data = get_user_data(data, str(user.id))

        position = user_data["foxa_claus_list_position"]
        gift = user_data["foxa_claus_list_gift"]
        gift_verified = user_data["foxa_claus_list_gift_verified"]

        if position == 0:

            embed = discord.Embed(
                title=":x: Not in list",
                description=f"{user.mention} you're not in the Fox'a Claus list!",
                color=discord.Color.red()
            )

            await ctx.respond(embed=embed)
            return


        if gift == "":

            gift = "No gift"

        embed = discord.Embed(
            title="Fox'a Claus List",
            description="",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Position",
            value=f"#{position}",
            inline=False
        )

        if show_gift:

            embed.add_field(
                name="Gift",
                value=f"{gift}",
                inline=False
            )

            if gift_verified:

                embed.add_field(
                    name="Gift Status",
                    value=":white_check_mark: Verified",
                    inline=False
                )

            else:
                embed.add_field(
                    name="Gift Status",
                    value=":x: Unverified",
                    inline=False
                )

        await ctx.respond(embed=embed)


    @commands.slash_command(
        name="foxa-claus-list-join",
        description="Enter the Fox'a Claus list with a gift of your choice"
    )
    async def foxa_claus_list_join(
            self,
            ctx,
            gift: discord.Option(str, "The gift you want")
    ):

        user = ctx.author
        data = load_data()
        user_data = get_user_data(data, str(user.id))

        position = user_data["foxa_claus_list_position"]

        if position != 0:

            embed = discord.Embed(
                title=":x: Already in list",
                description=f"{user.mention}, you are already in the Fox'a Claus list. Check your details with the command `/foxa-claus-list`",
                color=discord.Color.red()
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return

        last_position = 0
        for udata in data.values():
            pos = udata.get("foxa_claus_list_position", 0)
            if pos > last_position:
                last_position = pos

        user_data["foxa_claus_list_position"] = last_position + 1
        user_data["foxa_claus_list_gift"] = gift

        save_data(data)

        embed = discord.Embed(
            title="🎁 Added to Fox'a Claus List!",
            description=f"{user.mention}, you've been added to the list at position **#{last_position + 1}**!\n🎁 Gift: `{gift}`",
            color=discord.Color.green()
        )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(FoxaClausList(bot))
