import discord
from discord import Option
from discord.ext import commands
from discord.ui import View

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

class Give(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("/give - start")

    @commands.slash_command(name="give", description="Передать валюту.", guild_ids=[guild_id_cmd])
    async def give(
        self,
        ctx: discord.ApplicationContext, 
        member: Option(discord.Member, name="пользователь", description="Выберите пуську.", required = True),
        amount: Option(int, name="сумма", description="Сумма для передачи.", min_value = 50, max_value = 10000, required = True)
    ):
        balance = self.db.get_balance(ctx.author.id)

        if member.id != ctx.author.id:
            if (balance >= 50 and amount <= balance):
                self.db.transfer_money(ctx.author, member, amount)
                
                self.db.write_new_transactions(ctx.author, f"Перевод {member.mention}", -amount)
                self.db.write_new_transactions(member, f"Перевод от {ctx.author.mention}", amount)

                logger.info(f"{ctx.author.name} передал {member.name} {amount} валюты")

                embed = discord.Embed(title='Передача валюты', description=f"Вы успешно передали **{amount}** <:1016719860547469323:1098025516059070485> пользователю {member.mention}.", color=0x2f3136)
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                await ctx.respond(embed=embed)
            else:
                await ctx.respond("баланс проверь, дурак", ephemeral=True)
        else:
            await ctx.respond("самому себе нельзя!", ephemeral=True)