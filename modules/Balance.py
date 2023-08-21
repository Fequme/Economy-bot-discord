import discord
from discord.ext import commands
from discord import Option
from discord.ui import View

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

import math
from datetime import datetime

guild_id_cmd = Utils.get_guild_id()

class Balance(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("/balance - start")

    async def make_page_transactions(self, page, total_pages, transactions):
        # Создание списка пользователей для текущей страницы
        page_transactions = transactions[(page-1)*10:page*10]

        embed = discord.Embed(title="История транзакций", color=0x2f3136)
        description = ""
        for user_id, category, value, time in page_transactions:
            date = datetime.fromtimestamp(time)
            months = ['янв.', 'фев.', 'мар.', 'апр.', 'май', 'июн.', 'июл.', 'авг.', 'сен.', 'окт.', 'ноя.', 'дек.']

            # Добавление информации о транзакции в embed
            description += f"<:dot2:1078804345119842464> {category} **[{date.day:02} {months[date.month - 1]}, {date.hour:02}:{date.minute:02}]**\nСумма: **{value}** <:1016719860547469323:1098025516059070485>\n\n"

        embed.description = description
        embed.set_footer(text=f"Страница {page} из {total_pages}")
        return embed

    #balance
    @commands.slash_command(name="balance", description="Посмотреть баланс.", guild_ids=[guild_id_cmd])
    async def balance(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member, name="пользователь", description="Выберите пуську.", required=False)
    ):
        await ctx.defer()

        globalself = self

        if member:
            embed = discord.Embed(title=f'Текущий баланс — {member.name}#{member.discriminator}', color=0x2f3136)
            embed.add_field(name="> Монеты <:1016719860547469323:1098025516059070485>", value=f"```{self.db.get_balance(member.id)}```")
            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
            embed.set_thumbnail(url=member.display_avatar.url)

            await ctx.followup.send(embed=embed)
        else:
            class Balance(discord.ui.View):
                def __init__(self, timeout=120):
                    super().__init__(timeout=timeout)

                @discord.ui.button(label="Транзакции", style=discord.ButtonStyle.blurple, custom_id="button_transactions_balance")
                async def button_callback_transactions(self, button, interaction: discord.Interaction):
                    await interaction.response.defer()

                    if ctx.author.id == interaction.user.id:
                        transactions = globalself.db.get_user_transactions(ctx.author)
                        total_pages = math.ceil(len(transactions)/10)
                        page = 1

                        class ButtonsView(discord.ui.View):
                            def __init__(self, page, total_pages, timeout=120):
                                super().__init__(timeout=timeout)
                                self.page = page
                                self.total_pages = total_pages

                            @discord.ui.button(label="Назад")
                            async def button_callback_back_balance(self, button, interaction: discord.Interaction):
                                await interaction.response.defer()

                                if ctx.author.id == interaction.user.id:
                                    embed = discord.Embed(title=f'Текущий баланс — {ctx.author.name}#{ctx.author.discriminator}', color=0x2f3136)
                                    embed.add_field(name="> Монеты <:1016719860547469323:1098025516059070485>", value=f"```{globalself.db.get_balance(ctx.author.id)}```")
                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                    await ctx.edit(embed=embed, view=Balance())

                            @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple)
                            async def button_callback_back(self, button, interaction: discord.Interaction):
                                await interaction.response.defer()

                                if ctx.author.id == interaction.user.id:
                                    self.page -= 1

                                    await self.update_embed(interaction)

                            @discord.ui.button(label="🗑️", style=discord.ButtonStyle.red)
                            async def button_callback_delete(self, button, interaction: discord.Interaction):
                                await interaction.response.defer()

                                if ctx.author.id == interaction.user.id:
                                    await ctx.delete()

                            @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple)
                            async def button_callback_next(self, button, interaction: discord.Interaction):
                                await interaction.response.defer()

                                if ctx.author.id == interaction.user.id:
                                    self.page += 1

                                    await self.update_embed(interaction)

                            async def update_embed(self, interaction: discord.Interaction):
                                self.page = max(min(self.page, self.total_pages), 1)
                                embed = await globalself.make_page_transactions(self.page, self.total_pages, transactions)
                                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                await interaction.message.edit(embed=embed, view=self)

                        embed = await globalself.make_page_transactions(page, total_pages, transactions)
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                        await ctx.edit(embed=embed, view=ButtonsView(page, total_pages))

                @discord.ui.button(label="🗑️", style=discord.ButtonStyle.red, custom_id="button_delete_balance")
                async def button_callback_delete(self, button, interaction: discord.Interaction):
                    await interaction.response.defer()

                    if ctx.author.id == interaction.user.id:
                        await ctx.delete()

            embed = discord.Embed(title=f'Текущий баланс — {ctx.author.name}#{ctx.author.discriminator}', color=0x2f3136)
            embed.add_field(name="> Монеты <:1016719860547469323:1098025516059070485>", value=f"```{self.db.get_balance(ctx.author.id)}```")
            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
            await ctx.followup.send(embed=embed, view=Balance())