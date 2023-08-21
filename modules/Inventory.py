import discord
from discord.ext import commands
from discord.ui import Select, View

import json

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

class Inventory(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

        try:
            with open("./assets/settings.json", "r", encoding="utf8") as settings:
                data = json.load(settings)

            self.guild_id = data.get("guild_id")

            guild_id_cmd = self.guild_id

            self.settings_roles = data.get("roles")
            self.settings_prices = data.get("prices")

            logger.info("Настройки загружены.")

        except:
            logger.error("Не можем загрузить настройки :(")
            exit()

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = discord.utils.get(self.bot.guilds, id=self.guild_id)

        logger.info("/inventory - start")

    @commands.slash_command(name="inventory", description="Открыть инвентарь.", guild_ids=[guild_id_cmd])
    async def inventory(
        self,
        ctx: discord.ApplicationContext
    ):
        await ctx.response.defer()

        embed = discord.Embed(title=f"Инвентарь — {ctx.author.name}#{ctx.author.discriminator}", description=f"{ctx.author.mention}, в данный момент ваш инвентарь **пуст**.", color=0x2f3136)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        await ctx.followup.send(embed=embed)