import discord
from discord.commands import Option
from discord.ext import commands
from discord.ui import View

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

import math

guild_id_cmd = Utils.get_guild_id()

class Top(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("/top - start")

    async def make_page_balance(self, page, total_pages, users):
        # Создание списка пользователей для текущей страницы
        page_users = users[(page-1)*10:page*10]

        embed = discord.Embed(title="Топ 30 пользователей по балансу", color=0x2f3136)
        description = ""
        for i, (user_id, balance) in enumerate(page_users):
            # Получение имени пользователя по user_id
            user = self.bot.get_user(user_id)
            if user is None:
                username = f"Пользователь {user_id}"
            else:
                username = user.mention
            
            # Добавление информации о пользователе в embed
            description += f"**{(page-1)*10+i+1}.** {username} — **{balance} <:1016719860547469323:1098025516059070485>**\n"

        embed.description = description
        embed.set_footer(text=f"Страница {page} из {total_pages}")
        return embed
    
    async def make_page_online(self, page, total_pages, users):
        # Создание списка пользователей для текущей страницы
        page_users = users[(page-1)*10:page*10]

        embed = discord.Embed(title="Топ 30 пользователей по онлайну", color=0x2f3136)
        description = ""
        for i, (user_id, hours, minutes) in enumerate(page_users):
            # Получение имени пользователя по user_id
            user = self.bot.get_user(user_id)
            if user is None:
                username = f"Пользователь {user_id}"
            else:
                username = user.mention

            # Добавление информации о пользователе в embed
            description += f"**{(page-1)*10+i+1}.** {username} — **{hours} ч. {minutes} мин.**\n"

        embed.description = description
        embed.set_footer(text=f"Страница {page} из {total_pages}")
        return embed
    
    async def make_page_messages(self, page, total_pages, users):
        # Создание списка пользователей для текущей страницы
        page_users = users[(page-1)*10:page*10]

        embed = discord.Embed(title="Топ 30 пользователей по сообщениям", color=0x2f3136)
        description = ""
        for i, (user_id, count) in enumerate(page_users):
            # Получение имени пользователя по user_id
            user = self.bot.get_user(user_id)
            if user is None:
                username = f"Пользователь {user_id}"
            else:
                username = user.mention

            # Добавление информации о пользователе в embed
            description += f"**{(page-1)*10+i+1}.** {username} — **{count} шт.**\n"

        embed.description = description
        embed.set_footer(text=f"Страница {page} из {total_pages}")
        return embed

    #Top users online, balance
    @commands.slash_command(name="top", description="Топ пользователей.", guild_ids=[guild_id_cmd])
    async def top(
        self,
        ctx: discord.ApplicationContext,
        action:Option(str, "Выберите показатель", name="показатель", choices = ['Баланс', 'Онлайн', 'Сообщения','Лав Онлайн','Лав баланс'], required=True)
    ):
        await ctx.defer()

        globalself = self

        if (action == 'Баланс'):
            users = self.db.get_top_users_balance()
            total_pages = math.ceil(len(users)/10)
            page = 1

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
                    embed = await globalself.make_page_balance(self.page, self.total_pages, users)
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    await interaction.message.edit(embed=embed, view=self)

            embed = await self.make_page_balance(page, total_pages, users)
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

        elif (action == 'Онлайн'):
            users = self.db.get_top_users_online()
            total_pages = math.ceil(len(users)/10)
            page = 1

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
                    embed = await globalself.make_page_online(self.page, self.total_pages, users)
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    await interaction.message.edit(embed=embed, view=self)

            embed = await self.make_page_online(page, total_pages, users)
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
        elif (action == 'Сообщения'):
            users = self.db.get_top_users_messages()
            total_pages = math.ceil(len(users)/10)
            page = 1

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
                    embed = await globalself.make_page_messages(self.page, self.total_pages, users)
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    await interaction.message.edit(embed=embed, view=self)

            embed = await self.make_page_messages(page, total_pages, users)
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            

        await ctx.followup.send(embed=embed, view=ButtonsView(page, total_pages))