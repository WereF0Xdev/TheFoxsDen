import discord
from discord.ext import commands
import json

from main import (
    guild_rules,
    ReactionRoles,
    REACTION_ROLES_FILE,
    SUGGESTIONS_CHANNEL,
    load_data,
    save_data,
    get_user_data,
)


class User(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reaction_roles_message_ids = []


    @commands.slash_command(
        name="suggest",
        description="Submit a suggestion to the forum channel."
    )
    async def suggest(
        self,
        ctx,
        title: discord.Option(str, "Title of your suggestion"),
        description: discord.Option(str, "Detailed suggestion")
    ):
        await ctx.defer(ephemeral=True)

        forum_channel = ctx.guild.get_channel(SUGGESTIONS_CHANNEL)
        if not isinstance(forum_channel, discord.ForumChannel):
            return await ctx.respond("❌ Suggestions channel not found or invalid.", ephemeral=True)

        try:
            thread = await forum_channel.create_thread(
                name=title,
                content=description + f"\n\nSuggestion by: {ctx.author.mention}",
            )
            await ctx.respond(f"✅ Your suggestion was posted [here]({thread.jump_url})!", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Failed to post suggestion: `{e}`", ephemeral=True)


    @commands.slash_command(
        name="rules",
        description="Send the server rules"
    )
    async def guidelines(self, ctx):
        embed = discord.Embed(
            title="Rules and Guidelines",
            description=guild_rules,
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)

    @commands.slash_command(
        name="nap",
        description="Take a nap and avoid getting pings"
    )
    async def nap(self, ctx):
        data = load_data()
        user_data = get_user_data(data, str(ctx.author.id))

        napping = user_data["napping"]
        current_nick = ctx.author.nick or ctx.author.display_name or ctx.author.name
        original_nick = user_data["nickname"]

        if napping:
            try:
                new_nick = current_nick.replace("[NAP]", "").strip()
                await ctx.author.edit(nick=new_nick or None)
                user_data["nickname"] = new_nick
            except discord.Forbidden:
                print(f"❌ I don’t have permission to change {ctx.author.name}’s nickname.")
            except discord.HTTPException as e:
                print(f"⚠️ Failed to change {ctx.author.name}'s nickname: {e}")

            user_data["napping"] = False
            embed = discord.Embed(
                title="⏰ No longer napping",
                description=f"Welcome back {ctx.author.mention}, you're no longer napping and users can ping you now.",
                color=discord.Color.nitro_pink()
            )
            embed.set_footer(text=f"You can now ping {ctx.author.name} again!")

        else:
            try:
                if original_nick != current_nick:
                    user_data["nickname"] = current_nick

                base_nick = user_data["nickname"].replace("[NAP]", "").strip()
                new_nick = f"[NAP] {base_nick}"

                await ctx.author.edit(nick=new_nick)
            except discord.Forbidden:
                print(f"❌ I don’t have permission to change {ctx.author.name}’s nickname.")
            except discord.HTTPException as e:
                print(f"⚠️ Failed to change {ctx.author.name}'s nickname: {e}")

            user_data["napping"] = True
            embed = discord.Embed(
                title="🌙 Napping",
                description=f"{ctx.author.mention}, have a good nap! Users will now be warned/punished if they try to ping you.",
                color=discord.Color.dark_blue()
            )
            embed.set_footer(text=f"Don't ping {ctx.author.name}!")

        save_data(data)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(User(bot))
