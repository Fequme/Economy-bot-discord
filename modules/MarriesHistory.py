import discord
from discord.ext import commands
from discord import Option, SlashCommandGroup
from discord.ui import View

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

import math
from datetime import datetime

guild_id_cmd = Utils.get_guild_id()

class Marries(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

    sub = discord.SlashCommandGroup("marries")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("/marries history - start")

    async def get_user(self, user_id):
        user = self.bot.get_user(user_id)
        if user is None:
            return f"Пользователь {user_id}"
        return user.mention

    async def make_page_history(self, page, total_pages, users):
        # Создание списка пользователей для текущей страницы
        page_users = users[(page-1)*5:page*5]

        embed = discord.Embed(title="История браков", color=0x2f3136)
        description = ""
        for partner_1, partner_2, type, time in page_users:
            date = datetime.fromtimestamp(time)
            months = ['янв.', 'фев.', 'мар.', 'апр.', 'май', 'июн.', 'июл.', 'авг.', 'сен.', 'окт.', 'ноя.', 'дек.']

            # Получение имени пользователя по user_id
            user_1 = self.bot.get_user(partner_1)
            user_2 = self.bot.get_user(partner_2)

            username_1 = await self.get_user(partner_1)
            username_2 = await self.get_user(partner_2)
            
            # Добавление информации о пользователе в embed
            if type == 'creature':
                description += f"<:dot2:1078804345119842464> **Создан**\n{username_1} и {username_2} — **{date.day:02} {months[date.month - 1]}, {date.hour:02}:{date.minute:02}**\n\n"
            elif type == 'divorce':
                description += f"<:dot2:1078804345119842464> **Развод**\n{username_1} и {username_2} — **{date.day:02} {months[date.month - 1]}, {date.hour:02}:{date.minute:02}**\n\n"

        embed.description = description
        embed.set_footer(text=f"Страница {page} из {total_pages}")
        return embed

    @sub.command(description="История браков.", guild_ids=[guild_id_cmd])
    async def history(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member, name="пользователь", description="Выберите пуську.", required=False)
    ):
        await ctx.defer()

        globalself = self

        if member:
            history = self.db.get_marries_history(member)
        else:
            history = self.db.get_marries_history(ctx.author)

        total_pages = math.ceil(len(history)/5)
        page = 1

        if len(history) == 0:
            embed = discord.Embed(title="История браков", description="История чиста...", color=0x2f3136)
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            await ctx.followup.send(embed=embed)
        else:
            class ButtonsView(discord.ui.View):
                def __init__(self, page, total_pages, timeout=120):
                    super().__init__(timeout=timeout)
                    self.page = page
                    self.total_pages = total_pages

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
                    embed = await globalself.make_page_history(self.page, self.total_pages, history)
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    await interaction.message.edit(embed=embed, view=self)

            embed = await self.make_page_history(page, total_pages, history)
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            if member:
                embed.title = f"История браков — {member.name}#{member.discriminator}"

            await ctx.followup.send(embed=embed, view=ButtonsView(page, total_pages))

        