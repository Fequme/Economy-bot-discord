import discord
from discord import Option
from discord.ext import commands
from discord.ui import View, Select

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

import json

guild_id_cmd = Utils.get_guild_id()

class AdminPanel(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()
        self.utils = Utils()

        try:
            with open("./assets/settings.json", "r", encoding="utf8") as settings:
                data = json.load(settings)

            self.settings_roles = data.get("roles")

            logger.info("Настройки загружены.")

        except:
            logger.error("Не можем загрузить настройки :(")
            exit()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("/apanel - start")

    @commands.slash_command(name="apanel", description="Панель разработчика.", guild_ids=[guild_id_cmd])
    @commands.is_owner()
    async def casino(
        self,
        ctx: discord.ApplicationContext, 
        member: Option(discord.Member, name="пользователь", description="Выберите пуську..", required = True)
    ):
        await ctx.response.defer()
        globalself = self

        if not member.bot:
            embed = discord.Embed(title=f'Управление пользователем', description=f"{ctx.author.mention}, **Выберите** операцию для **взаимодействия** с {member.mention}", color=0x2f3136)
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            class ButtonsManipulate(discord.ui.View):
                def __init__(self, timeout=120):
                    super().__init__(timeout=timeout)

                async def on_timeout(self):
                    await ctx.edit(view=View())
                
                @discord.ui.button(label="Валюта", custom_id="button_manipulate_balance", style=discord.ButtonStyle.blurple)
                async def button_callback_manipulate_balance(self, button, interaction: discord.Interaction):
                    await interaction.response.defer()

                    if ctx.author.id == interaction.user.id:
                        self.stop()

                        class ButtonsManipulateBalance(discord.ui.View):
                            def __init__(self, timeout=120):
                                super().__init__(timeout=timeout)

                            async def on_timeout(self):
                                await ctx.edit(view=View())

                            @discord.ui.button(label="Выдать валюту", custom_id="button_balance_give")
                            async def button_callback_balance_give(self, button, interaction: discord.Interaction):
                                #await interaction.response.defer()

                                if ctx.author.id == interaction.user.id:
                                    class BalanceGiveModal(discord.ui.Modal):
                                        def __init__(self, *args, **kwargs):
                                            super().__init__(
                                                discord.ui.InputText(
                                                    label="Выдать валюту",
                                                    placeholder="Например: 1000",
                                                    min_length=1,
                                                    max_length=15,
                                                    required=True
                                                ),
                                                *args,
                                                **kwargs
                                            )

                                        async def callback(self, interaction):
                                            await interaction.response.defer()
                                            
                                            amount = int(self.children[0].value)

                                            globalself.db.give_money(member.id, amount)
                                            #сделать проверку на число

                                            view = View()

                                            button_balance_back_manipulate = discord.ui.Button(label="⬅️ Вернуться к управлению балансом", custom_id="button_balance_back_manipulate", style=discord.ButtonStyle.blurple)

                                            async def button_callback_balance_back_manipulate(interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    embed = discord.Embed(title=f'Валюта', description=f"{ctx.author.mention}, **Выберите** операцию для **взаимодействия** с **балансом** {member.mention}\n\n> **Баланс пользователя**\n```{globalself.db.get_balance(member.id)}```", color=0x2f3136)
                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                    await ctx.edit(embed=embed, view=ButtonsManipulateBalance())

                                            button_balance_back_manipulate.callback = button_callback_balance_back_manipulate
                                            view.add_item(button_balance_back_manipulate)

                                            embed = discord.Embed(title=f'Выдать валюту', description=f"{ctx.author.mention}, Вы **успешно выдали** пользователю {member.mention}, **{amount}** валюты", color=discord.Colour.green())
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url) 

                                            await interaction.message.edit(embed=embed, view=view)
                                    
                                    await interaction.response.send_modal(BalanceGiveModal(title="Выдача валюты"))

                            @discord.ui.button(label="Снять валюту", custom_id="button_balance_remove")
                            async def button_callback_balance_remove(self, button, interaction: discord.Interaction):
                                #await interaction.response.defer()

                                if ctx.author.id == interaction.user.id:
                                    class BalanceGiveModal(discord.ui.Modal):
                                        def __init__(self, *args, **kwargs):
                                            super().__init__(
                                                discord.ui.InputText(
                                                    label="Снятие валюты",
                                                    placeholder="Например: 1000",
                                                    min_length=1,
                                                    max_length=15,
                                                    required=True
                                                ),
                                                *args,
                                                **kwargs
                                            )

                                        async def callback(self, interaction):
                                            await interaction.response.defer()
                                            
                                            amount = int(self.children[0].value)

                                            globalself.db.take_money(member.id, amount)
                                            #сделать проверку на число

                                            view = View()

                                            button_balance_back_manipulate = discord.ui.Button(label="⬅️ Вернуться к управлению балансом", custom_id="button_balance_back_manipulate", style=discord.ButtonStyle.blurple)

                                            async def button_callback_balance_back_manipulate(interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    embed = discord.Embed(title=f'Валюта', description=f"{ctx.author.mention}, **Выберите** операцию для **взаимодействия** с **балансом** {member.mention}\n\n> **Баланс пользователя**\n```{globalself.db.get_balance(member.id)}```", color=0x2f3136)
                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                    await ctx.edit(embed=embed, view=ButtonsManipulateBalance())

                                            button_balance_back_manipulate.callback = button_callback_balance_back_manipulate
                                            view.add_item(button_balance_back_manipulate)

                                            embed = discord.Embed(title=f'Снять валюту', description=f"{ctx.author.mention}, Вы **забрали** у пользователя {member.mention}, **{amount}** валюты", color=discord.Colour.green())
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url) 

                                            await interaction.message.edit(embed=embed, view=view)
                                    
                                    await interaction.response.send_modal(BalanceGiveModal(title="Снятие валюты"))

                            @discord.ui.button(label="⬅️ Вернуться к управлению", custom_id="button_balance_back", style=discord.ButtonStyle.blurple)
                            async def button_callback_balance_back(self, button, interaction: discord.Interaction):
                                await interaction.response.defer()

                                if ctx.author.id == interaction.user.id:
                                    embed = discord.Embed(title=f'Управление пользователем', description=f"{ctx.author.mention}, **Выберите** операцию для **взаимодействия** с {member.mention}", color=0x2f3136)
                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                    await ctx.edit(embed=embed, view=ButtonsManipulate())

                        embed = discord.Embed(title=f'Валюта', description=f"{ctx.author.mention}, **Выберите** операцию для **взаимодействия** с **балансом** {member.mention}\n\n> **Баланс пользователя**\n```{globalself.db.get_balance(member.id)}```", color=0x2f3136)
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                        await ctx.edit(embed=embed, view=ButtonsManipulateBalance())

                @discord.ui.button(label="Личные комнаты", custom_id="button_manipulate_rooms", style=discord.ButtonStyle.blurple)
                async def button_callback_manipulate_rooms(self, button, interaction: discord.Interaction):
                    await interaction.response.defer()

                    if ctx.author.id == interaction.user.id:
                        self.stop()

                        class ButtonsManipulateRooms(discord.ui.View):
                            def __init__(self, timeout=120):
                                super().__init__(timeout=timeout)

                            async def on_timeout(self):
                                await ctx.edit(view=View())

                            @discord.ui.button(label="Создать комнату", custom_id="button_rooms_create")
                            async def button_callback_balance_give(self, button, interaction: discord.Interaction):
                                #await interaction.response.defer()

                                if ctx.author.id == interaction.user.id:
                                    class RoomCreateModal(discord.ui.Modal):
                                        def __init__(self, *args, **kwargs):
                                            super().__init__(
                                                discord.ui.InputText(
                                                    label="1. Название комнаты и роли",
                                                    placeholder="Например: хуеплеты",
                                                    required=True
                                                ),
                                                discord.ui.InputText(
                                                    label="2. Цвет роли",
                                                    placeholder="Например: #FFFFFF",
                                                    required=True
                                                ),
                                                *args,
                                                **kwargs
                                            )

                                        async def callback(self, interaction):
                                            await interaction.response.defer()
                                            
                                            globalself.db.write_new_personal_room(member, self.children[0].value)
                                            
                                            role = await ctx.guild.create_role(name=self.children[0].value)
                                            x = ctx.guild.get_role(globalself.settings_roles.get("personal_rooms_sort"))

                                            await role.edit(position=x.position - 1, colour = await commands.ColourConverter().convert(ctx, self.children[1].value))
                                            await member.add_roles(role)

                                            view = View()

                                            button_balance_back_manipulate = discord.ui.Button(label="⬅️ Вернуться к управлению комнатами", custom_id="button_rooms_back_manipulate", style=discord.ButtonStyle.blurple)

                                            async def button_callback_rooms_back_manipulate(interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    embed = discord.Embed(title="Личные комнаты", description=f"{ctx.author.mention}, **Выберите** операцию для **взаимодействия** с {member.mention}", color=0x2f3136)
                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                    await ctx.edit(embed=embed, view=ButtonsManipulateRooms())

                                            button_balance_back_manipulate.callback = button_callback_rooms_back_manipulate
                                            view.add_item(button_balance_back_manipulate)

                                            embed = discord.Embed(title="Создание личной комнаты", description=f"{ctx.author.mention}, Вы **успешно создали** пользователю {member.mention} личную комнату {role.mention}", color=discord.Colour.green())
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url) 

                                            await interaction.message.edit(embed=embed, view=view)
                                    
                                    await interaction.response.send_modal(RoomCreateModal(title="Создание личной комнаты"))

                            @discord.ui.button(label="⬅️ Вернуться к управлению", custom_id="button_balance_back", style=discord.ButtonStyle.blurple)
                            async def button_callback_balance_back(self, button, interaction: discord.Interaction):
                                await interaction.response.defer()

                                if ctx.author.id == interaction.user.id:
                                    embed = discord.Embed(title=f'Управление пользователем', description=f"{ctx.author.mention}, **Выберите** операцию для **взаимодействия** с {member.mention}", color=0x2f3136)
                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                    await ctx.edit(embed=embed, view=ButtonsManipulate())

                        embed = discord.Embed(title="Личные комнаты", description=f"{ctx.author.mention}, **Выберите** операцию для **взаимодействия** с {member.mention}", color=0x2f3136)
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                        await ctx.edit(embed=embed, view=ButtonsManipulateRooms())


                @discord.ui.button(label="Закрыть", custom_id="button_manipulate_close", style=discord.ButtonStyle.red)
                async def button_callback_manipulate_close(self, button, interaction: discord.Interaction):
                    await interaction.response.defer()

                    if ctx.author.id == interaction.user.id:
                        self.stop()

                        await ctx.delete()
                        
            await ctx.followup.send(embed=embed, view=ButtonsManipulate())
        else:
            pass # Выберите корректного пользователя.
