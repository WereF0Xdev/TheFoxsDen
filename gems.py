import os
import discord
from discord import Option, option
from discord.ext import commands, tasks
import random
from dotenv import load_dotenv
import math
import json

from main import (
    guild_rules,
    ReactionRoles,
    REACTION_ROLES_FILE,
    SUGGESTIONS_CHANNEL,
    load_data,
    save_data,
    get_user_data,
    gems_file,
    canUseModeratorCommands,
)

def format_number(n):
    if n >= 1_000_000_000_000_000_000_000_000_000_000_000_000_000:
        return f"{n / 1_000_000_000_000_000_000_000_000_000_000_000_000_000:.2f}Duo"
    elif n >= 1_000_000_000_000_000_000_000_000_000_000_000_000:
        return f"{n / 1_000_000_000_000_000_000_000_000_000_000_000_000:.2f}Un"
    elif n >= 1_000_000_000_000_000_000_000_000_000_000_000:
        return f"{n / 1_000_000_000_000_000_000_000_000_000_000_000:.2f}Dec"
    elif n >= 1_000_000_000_000_000_000_000_000_000_000:
        return f"{n / 1_000_000_000_000_000_000_000_000_000_000:.2f}Non"
    elif n >= 1_000_000_000_000_000_000_000_000_000:
        return f"{n / 1_000_000_000_000_000_000_000_000_000:.2f}Oct"
    elif n >= 1_000_000_000_000_000_000_000_000:
        return f"{n / 1_000_000_000_000_000_000_000_000:.2f}Sep"
    elif n >= 1_000_000_000_000_000_000_000:
        return f"{n / 1_000_000_000_000_000_000_000:.2f}Six"
    elif n >= 1_000_000_000_000_000_000:
        return f"{n / 1_000_000_000_000_000_000:.2f}Qui"
    elif n >= 1_000_000_000_000_000:
        return f"{n / 1_000_000_000_000_000:.2f}Qua"
    elif n >= 1_000_000_000_000:
        return f"{n / 1_000_000_000_000:.2f}T"
    elif n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.2f}K"
    else:
        return str(n)

class Gems(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
    name="gems-stats",
    description="Check how many gems you have"
    )
    async def gems_stats(
            self,
            ctx,
            user: discord.Option(discord.Member, "Member to get the Gems Stats of", required=False)
    ):
        if user is None:
            user = ctx.author

        data = load_data()
        user_data = get_user_data(data, str(user.id))

        gems = user_data["gems"]
        second_chance = user_data["second_chance"]
        roulette_dexterity = user_data["roulette_dexterity"]

        embed = discord.Embed(
             title=f"{user.display_name}'s Gems",
            description="\n",
            color=discord.Color.blue()
        )

        embed.add_field(
            name=":gem: Gems",
            value=f"{format_number(int(gems))}",
            inline=False
        )

        embed.add_field(
            name=":cyclone: Second Chance",
            value=f"{second_chance}",
            inline=False
        )

        embed.add_field(
            name=":slot_machine: Roulette Dexterity",
            value=f"Level {roulette_dexterity}",
            inline=False
        )

        embed.set_thumbnail(url=user.avatar.url or user.default_avatar.url)

        await ctx.respond(embed=embed)


    @commands.slash_command(
        name="gamble",
        description="Gamble Gems to win or lose more"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def gamble(
            self,
            ctx,
            amount: discord.Option(str, "Amount to gamble. You can use formatting.")
    ):

        suffixes = {
            "k": 1_000,
            "m": 1_000_000,
            "b": 1_000_000_000,
            "t": 1_000_000_000_000,
            "qua": 1_000_000_000_000_000,
            "qui": 1_000_000_000_000_000_000,
            "six": 1_000_000_000_000_000_000_000,
            "sep": 1_000_000_000_000_000_000_000_000,
            "oct": 1_000_000_000_000_000_000_000_000_000,
            "non": 1_000_000_000_000_000_000_000_000_000_000,
            "dec": 1_000_000_000_000_000_000_000_000_000_000_000,
            "un": 1_000_000_000_000_000_000_000_000_000_000_000_000,
            "duo": 1_000_000_000_000_000_000_000_000_000_000_000_000_000
        }

        amount = amount.lower().strip()
        multiplier = 1

        for suffix, factor in sorted(suffixes.items(), key=lambda x: -len(x[0])):
            if amount.endswith(suffix):
                multiplier = factor
                amount = amount[:-len(suffix)]
                break

        try:
            amount = int(amount) * multiplier
        except ValueError:
            await ctx.respond(
                "❌ Invalid amount! Use a number with optional k/m/b/t/qua/qui/six/sep/oct/non/dec/un/duo suffix.",
                ephemeral=True
            )
            return


        if amount <= 0:
            embed = discord.Embed(
                title=":x: Invalid values",
                description="You must gamble an amount > 0!",
                color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return

        data = load_data()
        user_data = get_user_data(data, str(ctx.author.id))

        gems = user_data["gems"]

        if gems < amount:
            missing_gems = amount - gems
            embed = discord.Embed(
                title=":x: Not enough Gems!",
                description=f"You need another {format_number(missing_gems)} :gem: to gamble this amount.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url="https://f0xmods.com/media/empty_wallet.png")
            embed.set_footer(text=f"Gems: {format_number(int(gems))}")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        second_chance = user_data["second_chance"]

        chance = user_data["gamble_luck"]
        roll = random.randint(1, 100)

        if roll > chance:
            if second_chance:
                roll = random.randint(1, 100)

        if roll <= chance:
            won_gems = amount
            user_data["gems"] += won_gems
            gems = user_data["gems"]
            embed = discord.Embed(
                title="You won!",
                description=f"{ctx.author.mention} you gambled and won {format_number(int(won_gems))} :gem:",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Gems: {format_number(int(gems))}")
            await ctx.respond(embed=embed)
        else:
            lost_gems = amount
            user_data["gems"] -= lost_gems
            gems = user_data["gems"]
            embed = discord.Embed(
                title="You lost!",
                description=f"{ctx.author.mention} you gambled and lost {format_number(int(lost_gems))} :gem:",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Gems: {format_number(int(gems))}")
            await ctx.respond(embed=embed)

        save_data(data)

    @gamble.error
    async def gamble_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):

            embed = discord.Embed(
                title="⏳ Slow down!",
                description=f"{ctx.author.mention}, please wait **1 second** before gambling again!",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)


    @commands.slash_command(
        name="welcome-claim",
        description="Claim your welcome gift in Gems"
    )
    async def welcome_claim(self, ctx):

        welcome_gift = 100

        data = load_data()

        user_data = get_user_data(data, str(ctx.author.id))

        welcome_claimed = user_data["welcome_claimed"]

        if not welcome_claimed:
            user_data["gems"] += welcome_gift
            user_data["welcome_claimed"] = True
            save_data(data)
            embed = discord.Embed(
                title=":star: Welcome claimed!",
                description=f"{ctx.author.mention} thank you for claiming your welcome gift!",
                color=discord.Color.yellow()
            )
            embed.add_field(
                name="Gift",
                value=f"{welcome_gift} :gem:",
                inline=False
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title=":x: Welcome already claimed!",
                description=f"{ctx.author.mention}, you already claimed your welcome gift!",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)


    @commands.slash_command(
        name="daily",
        description="Claim your daily reward"
    )
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):

        data = load_data()

        user_data = get_user_data(data, str(ctx.author.id))

        gems = user_data["gems"]


        if int(gems)<=0:
            gems = 1

        jackpot_percentage = 40
        jackpot_roll = random.randint(1, 100)
        jackpot_chance = 7


        if jackpot_roll <= jackpot_chance:
            win = (gems * jackpot_percentage)/100
            user_data["gems"] += win
            save_data(data)
            embed = discord.Embed(
                title=":coin: Jackpot!",
                description=f"{ctx.author.mention}, you hit the JACKPOT!",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="Daily Reward",
                value=f"{format_number(int(win))} :gem:"
            )
            await ctx.respond(embed=embed)
            return


        daily_percentage = random.randint(10, 25)
        daily_reward = (gems * daily_percentage)/100


        user_data["gems"] += daily_reward
        save_data(data)

        embed = discord.Embed(
            title=":alarm_clock: Daily reward claimed!",
            description=f"{ctx.author.mention}, you claimed your daily reward!",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="Daily Reward",
            value=f"{format_number(int(daily_reward))} :gem:"
        )

        if daily_reward < 1:
            embed.set_footer(text="The reward may seem nothing, but it's based on how many Gems you have. Get more to unlock more rewards!")
        await ctx.respond(embed=embed)

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):

            retry_after = math.ceil(error.retry_after)
            hours, remainder = divmod(retry_after, 3600)
            minutes, seconds = divmod(remainder, 60)

            time_left = (
                f"{hours}h {minutes}m {seconds}s"
                if hours
                else f"{minutes}m {seconds}s"
            )

            embed = discord.Embed(
                title="⏳ Daily Already Claimed!",
                description=f"{ctx.author.mention}, you can claim again in **{time_left}**.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="gems-leaderboard",
        description="Get the richest users on the server"
    )
    async def gems_leaderboard(
            self,
            ctx,
            entries: discord.Option(int, "How many places of the leaderboard you want to see", default=10)
    ):
        data = load_data()

        sorted_gems = sorted(
            data.items(),
            key=lambda item: item[1]["gems"],
            reverse=True
        )

        embed = discord.Embed(
            title="💎 Gems Leaderboard",
            description="Top users with the most gems",
            color=discord.Color.gold()
        )

        count = 0
        for user_id, user_data in sorted_gems:
            if count >= entries:
                break

            gems = int(user_data.get("gems", 0))
            if gems <= 0:
                continue

            user = ctx.guild.get_member(int(user_id))
            if not user:
                continue

            embed.add_field(
                name=f"#{count + 1} - {user.display_name}",
                value=f"**{format_number(gems)}** 💎",
                inline=False
            )

            count += 1

        if count == 0:
            embed.description = "No users with gems found in this server."

        await ctx.respond(embed=embed)



    @commands.slash_command(
        name="gem-modify",
        description="Modify Gem stats"
    )
    async def gem_modify(
            self,
            ctx,
            mode: discord.Option(
                str,
                "What action do you want to do?",
                autocomplete=lambda ctx: ["Add", "Remove", "Modify"]),
            member: discord.Option(discord.Member, "Member to commit the action to"),
            amount: discord.Option(int, "Amount of Gems")
    ):

        if await canUseModeratorCommands(ctx):

            if amount<=0:
                await ctx.respond("Please insert a value > 0", ephemeral=True)
                return

            data = load_data()

            user_data = get_user_data(data, str(member.id))

            if mode == "Add":

                user_data["gems"] += amount

                embed = discord.Embed(
                    title=":white_check_mark: Gems Added",
                    description=f"Added {format_number(amount)} :gem: to {member.mention}",
                    color=discord.Color.green()
                )
                await ctx.respond(embed=embed)

            elif mode == "Remove":

                gems = user_data["gems"]

                if gems<amount:
                    embed = discord.Embed(
                        title=":x: Error",
                        description=f"Unable to remove {format_number(amount)} :gem: from {member.mention}",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Reason", value="Final value would be < 0", inline=False)
                    await ctx.respond(embed=embed)
                    return

                user_data["gems"] -= amount

                embed = discord.Embed(
                    title=":white_check_mark: Gems Removed",
                    description=f"Removed {format_number(amount)} :gem: from {member.mention}",
                    color=discord.Color.green()
                )
                await ctx.respond(embed=embed)

            elif mode == "Modify":

                user_data["gems"] = amount

                embed = discord.Embed(
                    title=":white_check_mark: Gems Modified",
                    description=f"Set {member.mention}'s Gems to {format_number(amount)} :gem:",
                    color=discord.Color.green()
                )
                await ctx.respond(embed=embed)
            
            save_data(data)


def setup(bot):
    bot.add_cog(Gems(bot))