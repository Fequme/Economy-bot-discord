import discord
from discord.ext import commands
from discord.ui import View

from datetime import datetime, timedelta
import random

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

class Timely(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("/timely - start")

    #timely
    @commands.slash_command(name="timely", description="Временная награда.", guild_ids=[guild_id_cmd])
    async def timely(
        self,
        ctx
    ):
        need = datetime.fromtimestamp(int(self.db.get_daily_award(ctx.author.id)))
        time = datetime.now()

        money = random.randint(50, 100)
        
        if len(str(need)) < 2 or time >= need:
            embed = discord.Embed(title='Ежедневная награда', description=f"Вы успешно получили ваши **{money}** <:1016719860547469323:1098025516059070485>\nВозвращайтесь через 24 часа!", color=0x2f3136)
            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            await ctx.respond(embed=embed)

            self.db.give_money(ctx.author.id, money)
            self.db.write_new_transactions(ctx.author, "Временная награда", money)
            self.db.update_daily_award(ctx.author.id, int(datetime.timestamp(time + timedelta(hours=24))))
        else:
            embed = discord.Embed(title='Ежедневная награда', description=f"Вы уже забрали свои монетки.\nВозвращайтесь через 24 часа!", color=0x2f3136)
            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            await ctx.respond(embed=embed, ephemeral=True)