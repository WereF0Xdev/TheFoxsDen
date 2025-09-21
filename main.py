import discord
from discord.ext import commands
import json
import os
from enum import Enum
import discord
import emoji
from dotenv import load_dotenv
import pytz


# Startup and checks

load_dotenv()

TOKEN = os.getenv("TOKEN")
WELCOME_AND_GOODBYE_CHANNEL = int(os.getenv("WELCOME_AND_GOODBYE_CHANNEL"))
SUGGESTIONS_CHANNEL = int(os.getenv("SUGGESTIONS_CHANNEL"))
LOGS_CHANNEL = int(os.getenv("LOGS_CHANNEL"))
CURSEFORGE_API_KEY = os.getenv("CURSEFORGE_API_KEY")
CF_API_KEY = os.getenv("CURSEFORGE_API_KEY")
TICKETS_FILE = os.getenv("TICKETS_FILE")
XP_FILE = os.getenv("XP_FILE")
LEVELS_CHANNEL = int(os.getenv("LEVELS_CHANNEL"))

guild_rules = "**\n\nServer guidelines**\n**N.1** - You must agree to [Discord's Terms of Service](<https://discord.com/terms>).\n**N.2** - Be respectful to others.\n**N.3** - No spamming.\n**N.4** - English only.\n**N.5** - No NSFW content.\n**N.6** - Follow moderators' instructions.\n**N.7** - Here we respect all members of the LGBT community and marginalized communities and this is a safe space for everyone. No hate towards anyone will be tolerated.\n**N.8** - Please do **not** ping Fox or Nia past 10 pm CEST."

guild_ids = [os.getenv("GUILD_IDS")]

promo_rules_message_id = os.getenv("PROMO_MESSAGE_ID")

reaction_roles_message_ids = [promo_rules_message_id]

cest = pytz.timezone("Europe/Paris")

nia_id = 1289656707445686386

skin_skull_url = ""

ticket_channels = {}

REACTION_ROLES_FILE = "reaction_roles.json"

if os.path.exists(REACTION_ROLES_FILE):
    with open(REACTION_ROLES_FILE, "r") as file:
        try:
            reaction_roles_message_ids = json.load(file)
        except json.JSONDecodeError:
            reaction_roles_message_ids = []
else:
    reaction_roles_message_ids = []

data_file = "data.json"

def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    return {}


def save_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)


def get_user_data(data, user_id):
    if user_id not in data:
        data[user_id] = {"level": 1, "xp": 0, "last_message": "", "xp_multiplier": 1, "level_multiplier": 1, "gems": 0, "welcome_claimed": False, "second_chance": False, "roulette_dexterity": 0, "gamble_luck": 35, "roulette_luck": 40, "napping": False, "warnings": 0}
    return data[user_id]

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

class Roles(Enum):
    FOX_PUPPY = 1387834989302780047,
    YOUNG_FOX = 1387836091968524288,
    ADULT_FOX = 1387836335091486730,
    SENIOR_FOX = 1387836710666371093,
    CONTRIBUTOR = 1387836898076135577,
    MODERATOR = 1387838055469154415,
    FOX_FAMILY = 1387846237331521598,
    LITTLE_GREMLIN = 1387838679204106240,
    FOX = 1387838830215692399,
    BOT = 1388069960231682048,
    ANNOUNCEMENTS_NOTIFICATIONS = 1387869225816690698,
    EVENTS_NOTIFICATIONS = 1387869372088848484,
    CERTIFIED_GAMBLER = 1390055313767399484,
    ELIGIBLE_FOR_FOXA_CLAUS = 1404044259015004261,
    SILLY_ANNOUNCEMENTS_NOTIFICATIONS = 1398048543964532817,
    FRIENDS = 1404564517123260447,
    CERTIFIED_CREATOR = 1388457039008628858

    def __init__(self, role_id):
        self.role_id = role_id

class ReactionRoles(Enum):
    HIM = 1408825573748375572, "He/Him", f"{emoji.emojize(':male_sign:', language='alias')}",
    HER = 1408825691406995568, "She/Her", f"{emoji.emojize(':female_sign:', language='alias')}",
    THEY = 1408825737699659837, "They/Them", f"{emoji.emojize(':purple_heart:', language='alias')}",
    OTHER = 1408825881023090718, "Other", f"{emoji.emojize(':green_heart:', language='alias')}",
    PROMO_RULES_ACCEPTED = 1388454108893286471, "Promotion Rules Accepted", f"{emoji.emojize(':bell:', language='alias')}"

    def __init__(self, role_id, display_name, emoji):
        self.role_id = role_id
        self.display_name = display_name
        self.emoji = emoji

REACTION_ROLES_FILE = "reaction_roles.json"

if os.path.exists(REACTION_ROLES_FILE):
    with open(REACTION_ROLES_FILE, "r") as file:
        try:
            reaction_roles_message_ids = json.load(file)
        except json.JSONDecodeError:
            reaction_roles_message_ids = []
else:
    reaction_roles_message_ids = []


def isModerator(user):
    if any(role.id == Roles.MODERATOR.role_id for role in user.roles):
        return True
    else:
        return False


async def canUseModeratorCommands(ctx):
    if isModerator(ctx.author):
        return True
    else:
        embed = discord.Embed(
            title="No permissions",
            description="You do not have permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed, ephemeral=True)
        return False



# Run

bot.reaction_roles_message_ids = reaction_roles_message_ids
bot.load_extension("events")
bot.load_extension("levels")
bot.load_extension("minecraft_commands")
bot.load_extension("moderator_commands")
bot.load_extension("tickets")
bot.load_extension("user_commands")

bot.run(TOKEN)
