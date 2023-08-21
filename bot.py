import asyncio
from dotenv import load_dotenv
import os

import discord
from discord.ext import commands
from discord.utils import *

from modules.Logger import *
from modules.Economy import Economy
from modules.Marry import Marry
from modules.Profile import Profile
from modules.Give import Give
from modules.LoveRooms import LoveRooms
from modules.Top import Top
from modules.LoveProfile import LoveProfile
from modules.Timely import Timely
from modules.Balance import Balance
from modules.Games import Games
from modules.MarriesHistory import Marries

from modules.PersonalRoles import PersonalRoles
from modules.Inventory import Inventory

from modules.AdminPanel import AdminPanel

from modules.Tracker import Tracker

from modules.TestCommand import TestCommand

from modules.Shop import Shop

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None,  case_insensitive=True)

bot.add_cog(Economy(bot))

bot.add_cog(Marry(bot))
bot.add_cog(Profile(bot))
bot.add_cog(Give(bot))
bot.add_cog(LoveRooms(bot))
bot.add_cog(LoveProfile(bot))
bot.add_cog(Timely(bot)) # Готово
bot.add_cog(Balance(bot)) # Готово
bot.add_cog(Top(bot)) # Пофиксить
bot.add_cog(Games(bot))
bot.add_cog(Marries(bot))

bot.add_cog(PersonalRoles(bot))
bot.add_cog(Inventory(bot))
bot.add_cog(Shop(bot))

bot.add_cog(AdminPanel(bot))

bot.add_cog(Tracker(bot))

bot.add_cog(TestCommand(bot))

load_dotenv()

bot.run("MTEyNTMzNTA4MzYwODQ0OTAzNQ.GnveWg.A9F7HcZ4jsuzIjD1KH6Eo2R8IaW8B4JGTjcStw")