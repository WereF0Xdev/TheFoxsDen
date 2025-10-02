import discord
from discord.ext import commands
import json
import os
import aiofiles

from main import TICKETS_FILE, ticket_channels, save_data
from main import Roles


def load_tickets(self):
    self.load_tickets()

class OpenTicketButton(discord.ui.Button):
    def __init__(self, cog):
        super().__init__(label="Open a ticket", style=discord.ButtonStyle.primary)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await self.cog.open_ticket(interaction)


class OpenTicketView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.add_item(OpenTicketButton(cog))


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ticket_channels = {}
        self.ensure_ticket_file()
        self.load_tickets()


    def ensure_ticket_file(self):
        if not os.path.exists(TICKETS_FILE):
            with open(TICKETS_FILE, "w") as f:
                json.dump({}, f)

    def load_tickets(self):
        self.ensure_ticket_file()
        with open(TICKETS_FILE, "r") as f:
            self.ticket_channels = json.load(f)

    def save_tickets(self):
        with open(TICKETS_FILE, "w") as f:
            json.dump(self.ticket_channels, f)


    @commands.slash_command(name="ticket-open", description="Open a ticket")
    async def ticket_open(self, ctx):
        view = OpenTicketView(self)
        embed = discord.Embed(
            title="Tickets",
            description="Click the button to open a Ticket.",
            color=discord.Color.blue()
        )
        await ctx.respond(embed=embed, view=view)

    @commands.slash_command(name="ticket-close", description="Close a ticket")
    async def ticket_close(self, ctx):
        await self.close_ticket(ctx)

    @commands.slash_command(name="ticket-export", description="Export this ticket as an HTML file")
    async def ticket_export(self, ctx):
        if ctx.channel.id not in self.ticket_channels.values():
            await ctx.respond("This is not a ticket channel.")
            return

        await ctx.respond("Exporting ticket...", ephemeral=True)

        messages = await ctx.channel.history(limit=100).flatten()
        messages.reverse()

        html_lines = []
        for msg in messages:
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
            username = msg.author.display_name
            avatar = msg.author.avatar.url if msg.author.avatar else msg.author.default_avatar.url
            content = msg.clean_content.replace("\n", "<br>")

            html_lines.append(f"""
            <div class="message">
                <img src="{avatar}" class="avatar">
                <div class="msg-content">
                    <span class="username">{username}</span>
                    <span class="timestamp">{timestamp}</span>
                    <div class="text">{content}</div>
                </div>
            </div>
            """)

        html_content = f"""
        <html>
        <head>
            <link href="https://fonts.googleapis.com/css2?family=Whitney:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{
                    background-color: #313338;
                    color: #dcddde;
                    font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    padding: 0;
                    margin: 0;
                }}
                .header {{
                    background-color: #2b2d31;
                    padding: 20px;
                    display: flex;
                    align-items: center;
                    border-bottom: 1px solid #1e1f22;
                }}
                .header-logo {{
                    width: 200px;
                    height: auto;
                    margin-right: 10px;
                }}
                .header-text {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #fff;
                }}
                .server-info {{
                    padding: 15px 20px;
                    background-color: #2b2d31;
                    display: flex;
                    align-items: center;
                    border-bottom: 1px solid #1e1f22;
                }}
                .server-icon {{
                    width: 40px;
                    height: 40px;
                    border-radius: 8px;
                    margin-right: 10px;
                }}
                .server-name {{
                    font-weight: bold;
                    color: #fff;
                    font-size: 16px;
                }}
                .channel-name {{
                    font-size: 14px;
                    color: #aaa;
                    margin-left: 6px;
                }}
                .content {{
                    padding: 20px;
                }}
                .message {{
                    display: flex;
                    margin-bottom: 18px;
                }}
                .avatar {{
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    margin-right: 12px;
                }}
                .msg-content {{
                    max-width: 700px;
                }}
                .username {{
                    font-weight: 600;
                    color: #fff;
                    display: inline-block;
                    margin-right: 10px;
                }}
                .timestamp {{
                    font-size: 12px;
                    color: #aaa;
                }}
                .text {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    margin-top: 2px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <img src="https://1000logos.net/wp-content/uploads/2021/06/Discord-logo.png" class="header-logo">
            </div>
            <div class="server-info">
                <img src="{ctx.guild.icon.url if ctx.guild.icon else 'https://cdn.discordapp.com/embed/avatars/0.png'}" class="server-icon">
                <span class="server-name">{ctx.guild.name}</span>
                <span class="channel-name">- #{ctx.channel.name}</span>
            </div>
            <div class="content">
                {''.join(html_lines)}
            </div>
        </body>
        </html>
        """

        async with aiofiles.open("ticket.html", "w", encoding="utf-8") as f:
            await f.write(html_content)

        await ctx.send(f"HTML export of ticket requested by {ctx.author.mention}:")
        await ctx.send(file=discord.File("ticket.html"))


    async def open_ticket(self, interaction):
        guild = interaction.guild
        author = interaction.user
        if str(author.id) in self.ticket_channels:
            await interaction.response.send_message(
                "You already have an open ticket. Please close the other one first with `/ticket-close`.",
                ephemeral=True
            )
            return

        category = discord.utils.get(guild.categories, name="Tickets")
        if category is None:
            category = await guild.create_category("Tickets")

        ticket_channel = await guild.create_text_channel(
            f"ticket-{author.name}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                author: discord.PermissionOverwrite(read_messages=True),
                guild.get_role(Roles.MODERATOR.role_id): discord.PermissionOverwrite(read_messages=True)
            }
        )

        self.ticket_channels[str(author.id)] = ticket_channel.id
        self.save_tickets()

        embed = discord.Embed(
            title="Ticket Created",
            description=f"{author.mention} Your ticket has been created. A staff member will be with you shortly.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed)
        await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

    async def close_ticket(self, ctx):
        if ctx.channel.id not in self.ticket_channels.values():
            await ctx.respond("This is not a ticket channel.")
            return

        await ctx.channel.delete()
        ticket_creator_id = next((k for k, v in self.ticket_channels.items() if v == ctx.channel.id), None)
        if ticket_creator_id:
            del self.ticket_channels[ticket_creator_id]
            self.save_tickets()


def setup(bot):
    bot.add_cog(Tickets(bot))
