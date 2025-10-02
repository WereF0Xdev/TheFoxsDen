import discord
from discord.ext import commands
import aiohttp
import io
from mcstatus import JavaServer


class DownloadSkinButton(discord.ui.Button):
    def __init__(self, skin_download_url):
        super().__init__(label="Download Skin", style=discord.ButtonStyle.success)
        self.skin_download_url = skin_download_url

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            description="Here is your skin file for download:",
            color=discord.Color.orange()
        )
        embed.set_image(url=self.skin_download_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class DownloadSkinButtonView(discord.ui.View):
    def __init__(self, skin_download_url):
        super().__init__()
        self.add_item(DownloadSkinButton(skin_download_url))


async def get_uuid(username: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['id']
                return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


class Minecraft(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.skin_skull_url = ""

    @commands.slash_command(
        name="skin",
        description="Get a player's Minecraft skin."
    )
    async def skin(self, ctx, username: discord.Option(str, "Username of the player")):
        uuid = await get_uuid(username)
        if uuid:
            skin_url = f"https://crafthead.net/armor/body/{uuid}"
            skin_download_url = f"https://crafthead.net/skin/{uuid}"
            skin_head_url = f"https://crafthead.net/cube/{uuid}"
            self.skin_skull_url = skin_head_url

            async with aiohttp.ClientSession() as session:
                async with session.get(skin_url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        skin_file = discord.File(io.BytesIO(data), filename=f"{username}.png")
                        embed = discord.Embed(
                            title=f"{username}'s skin",
                            color=discord.Color.orange()
                        )
                        await ctx.respond(embed=embed, file=skin_file, view=DownloadSkinButtonView(skin_download_url))


    @commands.slash_command(
        name="server-lookup",
        description="Look up information about a Minecraft server."
    )
    async def find_server(self, ctx, ip: discord.Option(str, "IP of the server")):
        try:
            server = JavaServer.lookup(ip)
            status = server.status()

            embed = discord.Embed(
                title="**🌐 Server Lookup**",
                description="Here's information about the requested server",
                color=discord.Color.random()
            )
            embed.add_field(name="IP", value=ip, inline=False)
            embed.add_field(name="Players", value=f"{status.players.online}/{status.players.max}", inline=False)
            embed.add_field(name="Latency", value=f"{int(status.latency)} ms", inline=False)
            embed.add_field(name="Version", value=f"{status.version.name}", inline=False)

            if status.players.sample:
                player_names = ", ".join(player.name for player in status.players.sample)
                embed.add_field(name="Online Players", value=player_names, inline=False)

            await ctx.respond(embed=embed)

        except Exception:
            await ctx.respond(
                "There was an error retrieving information about the server. Is the IP correct?",
                ephemeral=True
            )


def setup(bot):
    bot.add_cog(Minecraft(bot))
