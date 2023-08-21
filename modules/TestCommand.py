import discord
from discord.ext import commands
from discord.ui import View

import math
import time
import json

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

class TestCommand(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()
        self.utils = Utils()

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = discord.utils.get(self.bot.guilds, id=guild_id_cmd)

        logger.info("TestCommand - start")

    @commands.slash_command(name="test", description="Тестовая комманда.", guild_ids=[guild_id_cmd])
    async def test(
        self,
        ctx: discord.ApplicationContext
    ):
        await ctx.response.defer()

        self.db.give_theme(ctx.author, "theme_1")
            
        await ctx.followup.send("Успешно!")