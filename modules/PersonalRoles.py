import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
from discord.ui import Select, View

import json

from datetime import datetime, timedelta

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

class PersonalRoles(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

        try:
            with open("./assets/settings.json", "r", encoding="utf8") as settings:
                data = json.load(settings)

            self.settings_roles = data.get("roles")
            self.settings_prices = data.get("prices")

            self.cost_role_create = self.settings_prices.get("role_create")
            self.cost_role_change_name = self.settings_prices.get("role_change_name")
            self.cost_role_change_color = self.settings_prices.get("role_change_color")

            logger.info("Настройки загружены.")

        except:
            logger.error("Не можем загрузить настройки :(")
            exit()

    sub = discord.SlashCommandGroup("role")

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = discord.utils.get(self.bot.guilds, id=guild_id_cmd)
        
        logger.info("/role create - start")
        logger.info("/role manage - start")

    @sub.command(description="Создание личной роли.", guild_ids=[guild_id_cmd])
    async def create(
        self,
        ctx: discord.ApplicationContext,
        name: Option(str, "Введите название роли", name="название", required=True),
        color: Option(str, "Введите цвет роли в формате #FFFFFF", name="цвет", required=True)
    ):
        globalself = self

        if self.db.get_balance(ctx.author.id) >= self.cost_role_create:
            try:
                colour = await commands.ColourConverter().convert(ctx, color)
            except Exception as E:
                print(f'role_create command error: {E}')
                embed = discord.Embed(title=f"Создание роли", description=f"Введите **цвет** в корректном **HEX** формате.\nНапример: **#FFFFFF**", color=discord.Color.red())
                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                await ctx.respond(embed=embed, view=View(), ephemeral=True)
                return
            
            await ctx.response.defer()

            class ButtonsView(discord.ui.View):
                def __init__(self, timeout=120):
                    super().__init__(timeout=timeout)

                async def on_timeout(self):
                    embed = discord.Embed(title=f'Создание роли', description=f"Время ожидания истекло!", color=discord.Color.red())
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                    await ctx.edit(embed=embed, view=View())

                @discord.ui.button(label="Да", custom_id="button_yes", style=discord.ButtonStyle.green)
                async def button_callback_yes(self, button, interaction: discord.Interaction):
                    await interaction.response.defer()

                    if ctx.author.id == interaction.user.id:
                        role = await ctx.guild.create_role(name=name)
                        x = ctx.guild.get_role(globalself.settings_roles.get("personal_roles_sort"))

                        await role.edit(position=x.position - 1, colour = await commands.ColourConverter().convert(ctx, color))
                        await ctx.author.add_roles(role)

                        globalself.db.write_new_role(ctx.author, role)
                        globalself.db.take_money(ctx.author.id, globalself.cost_role_create)
                        globalself.db.write_new_transactions(ctx.author, "Создание личной роли", -globalself.cost_role_create)

                        embed = discord.Embed(title=f'Создание роли', description=f"**Вы** успешно создали свою **личную роль** {role.mention}\nДля управления ролью **/role manage**", color=discord.Color.green())
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                        self.stop()

                        await ctx.edit(embed=embed, view=View())

                @discord.ui.button(label="Нет", custom_id="button_no", style=discord.ButtonStyle.red)
                async def button_callback_no(self, button, interaction: discord.Interaction):
                    await interaction.response.defer()

                    if ctx.author.id == interaction.user.id:
                        self.stop()
                        await ctx.delete()

            embed = discord.Embed(title=f"Создание роли", description=f"**Вы** уверены что хотите создать роль **{name}** за **{self.cost_role_create}** <:1016719860547469323:1098025516059070485>?", color=0x2f3136)
            embed.set_footer(text="Роли создаются сроком на 30 дней после чего их необходимо оплатить.")
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            await ctx.followup.send(embed=embed, view=ButtonsView())
        else:
            embed = discord.Embed(title=f"Создание роли", description=f"{ctx.author.mention}, у Вас **недостаточно средств**.", color=discord.Color.red())
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            await ctx.respond(embed=embed, ephemeral=True)

    @sub.command(description="Управление личной ролью.", guild_ids=[guild_id_cmd])
    async def manage(
        self,
        ctx: discord.ApplicationContext
    ):
        globalself = self

        if self.db.is_exists_role(ctx.author):
            await ctx.defer()
            embed = discord.Embed(title=f"Личные роли", description=f"**Выберите** роль для **взаимодействия**", color=0x2f3136)
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            class SelectRoleView(discord.ui.View):
                def __init__(self, timeout=120):
                    super().__init__(timeout=timeout)

                    select = Select(
                        placeholder="Выберите личную роль",
                    )

                    roles = globalself.db.get_all_roles(ctx.author)

                    for role in roles:
                        x = discord.utils.get(globalself.guild.roles, id=int(role))
                        select.add_option(label=f"{x.name}", value=f"{x.id}")
                            
                    async def select_callback(interaction):
                        await interaction.response.defer()

                        if ctx.author.id == interaction.user.id:
                            select_role = discord.utils.get(globalself.guild.roles, id=int(select.values[0]))

                            role_created_at = f"{select_role.created_at.day:02}.{select_role.created_at.month:02}.{select_role.created_at.year}"

                            class ButtonBackSettings(discord.ui.View):
                                def __init__(self, timeout=120):
                                    super().__init__(timeout=timeout)

                                @discord.ui.button(label="⬅️ Вернуться к настройке роли", custom_id="button_back_settings", style=discord.ButtonStyle.blurple)
                                async def button_callback_back_settings(self, button, interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        time_create = datetime.fromtimestamp(globalself.db.get_time_to_pay(select_role))
                                        time_pay = time_create + timedelta(days=30)

                                        embed = discord.Embed(title=f'Управление личной ролью', description=f"**Выберите** операцию для **взаимодействия** с **личной ролью** {select_role.mention}\n\nДо оплаты — **{(time_pay - time_create).days}** дней", color=0x2f3136)
                                        embed.set_footer(text=f"Создана {role_created_at}")
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                                                                
                                        await ctx.edit(embed=embed, view=ButtonsEditView())

                            class ButtonsEditView(discord.ui.View):
                                def __init__(self, timeout=180):
                                    super().__init__(timeout=timeout)
                                        
                                @discord.ui.button(label="Изменить название", custom_id="button_change_name")
                                async def button_callback_change_name(self, button, interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        # Кнопка возврата к настройки роли
                                        view = View()
                                        button_back = discord.ui.Button(label="Отмена", custom_id="button_back", style=discord.ButtonStyle.red)

                                        async def button_callback_back(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                embed = discord.Embed(title=f'Управление личной ролью', description=f"**Выберите** операцию для **взаимодействия** с **личной ролью** {select_role.mention}", color=0x2f3136)
                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                        
                                                await ctx.edit(embed=embed, view=ButtonsEditView())

                                        button_back.callback = button_callback_back
                                        view.add_item(button_back)

                                        # Меняем сообщение на Изменение названия роли
                                        embed = discord.Embed(title=f'Изменение названия роли', description=f"**Напишите новое название** для вашей **личной роли** {select_role.mention}", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        await ctx.edit(embed=embed, view=view)

                                        # Ждём нового названия
                                        await interaction.followup.send("Напишите новое название роли.", ephemeral=True, delete_after=10)

                                        try:
                                            def check(message):
                                                return interaction.user == message.author

                                            message = await globalself.bot.wait_for("message", timeout=60.0, check=check)
                                        except asyncio.TimeoutError:
                                            embed = discord.Embed(title=f'Изменение названия роли', description=f"Время ожидания истекло!", color=discord.Color.red())
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                            await ctx.edit(embed=embed, view=View())

                                        # Получили новое название, теперь подтверждаем действие
                                        view_verify = View()

                                        embed = discord.Embed(title=f'Изменение названия роли — {ctx.author.name}#{ctx.author.discriminator}', description=f"{ctx.author.mention}, **Вы уверены** что хотите изменить **название** роли на **{message.content}** за **{globalself.cost_role_change_name}** <:1016719860547469323:1098025516059070485>?", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        button_yes_verify = discord.ui.Button(label="Да", custom_id="button_yes_verify", style=discord.ButtonStyle.green)
                                        button_no_verify = discord.ui.Button(label="Нет", custom_id="button_no_verify", style=discord.ButtonStyle.red)

                                        async def button_callback_yes_verify(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                if globalself.db.get_balance(ctx.author.id) >= globalself.cost_role_change_name:
                                                    embed = discord.Embed(title=f'Изменение названия роли', description=f"**Вы** успешно изменили **название** роли {select_role.mention}", color=discord.Colour.green())
                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                    globalself.db.take_money(ctx.author.id, globalself.cost_role_change_name)
                                                    globalself.db.write_new_transactions(ctx.author, "Личная роль", -globalself.cost_role_change_name)
                                                    await select_role.edit(name=f"{message.content}")

                                                    await ctx.edit(embed=embed, view=ButtonBackSettings())
                                                else:
                                                    embed = discord.Embed(title=f'Изменение названия роли', description=f"у **Вас** недостаточно **средств** для **изменения названия роли**", color=discord.Colour.red())
                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                    await ctx.edit(embed=embed, view=ButtonBackSettings())

                                        async def button_callback_no_verify(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                await ctx.edit(view=ButtonBackSettings())

                                        button_yes_verify.callback = button_callback_yes_verify
                                        button_no_verify.callback = button_callback_no_verify

                                        view_verify.add_item(button_yes_verify)
                                        view_verify.add_item(button_no_verify)

                                        await message.delete()
                                        await ctx.edit(embed=embed, view=view_verify)

                                @discord.ui.button(label="Изменить цвет", custom_id="button_change_color")
                                async def button_callback_change_color(self, button, interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        # Кнопка возврата к настройки роли
                                        view = View()
                                        button_back = discord.ui.Button(label="Отмена", custom_id="button_back", style=discord.ButtonStyle.red)

                                        async def button_callback_back(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                embed = discord.Embed(title=f'Управление личной ролью', description=f"**Выберите** операцию для **взаимодействия** с **личной ролью** {select_role.mention}", color=0x2f3136)
                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                        
                                                await ctx.edit(embed=embed, view=ButtonsEditView())

                                        button_back.callback = button_callback_back
                                        view.add_item(button_back)

                                        # Меняем сообщение на Изменение цвета роли
                                        embed = discord.Embed(title=f'Изменение цвета роли', description=f"**Напишите новый цвет** в формате **#FFFFFF** для вашей **личной роли** {select_role.mention}", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        await ctx.edit(embed=embed, view=view)

                                        # Ждём нового названия
                                        await interaction.followup.send("Напишите новый цвет роли.", ephemeral=True, delete_after=10)

                                        try:
                                            def check(message):
                                                return interaction.user == message.author

                                            while True:
                                                message = await globalself.bot.wait_for("message", timeout=60.0, check=check)

                                                try:
                                                    colour = await commands.ColourConverter().convert(ctx, message.content)
                                                    break
                                                except Exception as E:
                                                    print(f'role_change_color command error: {E}')
                                                    await interaction.followup.send("Введите цвет в формате: #FFFFFF", ephemeral=True, delete_after=5)
                                                    await message.delete()

                                        except asyncio.TimeoutError:
                                            embed = discord.Embed(title=f'Изменение цвета роли', description=f"Время ожидания истекло!", color=discord.Color.red())
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                            await ctx.edit(embed=embed, view=View())

                                        # Получили новое название, теперь подтверждаем действие
                                        view_verify = View()

                                        embed = discord.Embed(title=f'Изменение цвета роли', description=f"**Вы уверены** что хотите изменить **цвет** роли на **{message.content}** за **{globalself.cost_role_change_color}** <:1016719860547469323:1098025516059070485>?", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        button_yes_verify = discord.ui.Button(label="Да", custom_id="button_yes_verify", style=discord.ButtonStyle.green)
                                        button_no_verify = discord.ui.Button(label="Нет", custom_id="button_no_verify", style=discord.ButtonStyle.red)

                                        async def button_callback_yes_verify(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                if globalself.db.get_balance(ctx.author.id) >= globalself.cost_role_change_color:
                                                    embed = discord.Embed(title=f'Изменение цвета роли', description=f"**Вы** успешно изменили **цвет** роли {select_role.mention}", color=discord.Colour.green())
                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                    globalself.db.take_money(ctx.author.id, globalself.cost_role_change_color)
                                                    globalself.db.write_new_transactions(ctx.author, "Личная роль", -globalself.cost_role_change_color)
                                                    await select_role.edit(color=colour)

                                                    await ctx.edit(embed=embed, view=ButtonBackSettings())
                                                else:
                                                    embed = discord.Embed(title=f'Изменение цвета роли', description=f"у **Вас** недостаточно **средств** для **изменения цвета роли**", color=discord.Colour.red())
                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                    await ctx.edit(embed=embed, view=ButtonBackSettings())

                                        async def button_callback_no_verify(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                await ctx.edit(view=ButtonBackSettings())

                                        button_yes_verify.callback = button_callback_yes_verify
                                        button_no_verify.callback = button_callback_no_verify

                                        view_verify.add_item(button_yes_verify)
                                        view_verify.add_item(button_no_verify)

                                        await message.delete()
                                        await ctx.edit(embed=embed, view=view_verify)

                                @discord.ui.button(label="Выдать пользователям", custom_id="button_add_members")
                                async def button_callback_add_members(self, button, interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        # Кнопка возврата к настройки роли
                                        view = View()
                                        button_back = discord.ui.Button(label="Отмена", custom_id="button_back", style=discord.ButtonStyle.red)

                                        async def button_callback_back(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                embed = discord.Embed(title=f'Управление личной ролью', description=f"**Выберите** операцию для **взаимодействия** с **личной ролью** {select_role.mention}", color=0x2f3136)
                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                        
                                                await ctx.edit(embed=embed, view=ButtonsEditView())

                                        button_back.callback = button_callback_back
                                        view.add_item(button_back)

                                        # Меняем сообщение на Выдача роли
                                        embed = discord.Embed(title=f'Выдача роли', description=f"**Упомяните пользователей** которым хотите **выдать** вашу **личную роль** {select_role.mention}", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        await ctx.edit(embed=embed, view=view)

                                        # Ждём упоминания людей
                                        await interaction.followup.send("Упомяните пользователей которым хотите выдать вашу личную роль.", ephemeral=True, delete_after=10)

                                        try:
                                            def check(message):
                                                return interaction.user == message.author

                                            while True:
                                                message = await globalself.bot.wait_for("message", timeout=60.0, check=check)

                                                if len(message.mentions) > 0:
                                                    break
                                                else:
                                                    await interaction.followup.send("Упомяните пользователей которым хотите выдать вашу личную роль", ephemeral=True, delete_after=5)
                                                    await message.delete()

                                        except asyncio.TimeoutError:
                                            embed = discord.Embed(title=f'Выдача роли', description=f"Время ожидания истекло!", color=discord.Color.red())
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                            await ctx.edit(embed=embed, view=View())

                                        # Получили новое название, теперь подтверждаем действие
                                        view_verify = View()

                                        mention_members = ""

                                        for member in message.mentions:
                                            mention_members += f"<@{member.id}> "

                                        embed = discord.Embed(title=f'Выдача роли — {ctx.author.name}#{ctx.author.discriminator}', description=f"**Вы уверены** что хотите **выдать** вашу роль пользователям: {mention_members} ?", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        button_yes_verify = discord.ui.Button(label="Да", custom_id="button_yes_verify", style=discord.ButtonStyle.green)
                                        button_no_verify = discord.ui.Button(label="Нет", custom_id="button_no_verify", style=discord.ButtonStyle.red)

                                        async def button_callback_yes_verify(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                embed = discord.Embed(title=f'Выдача роли', description=f"**Вы** успешно **выдали** вашу роль пользователям: {mention_members}", color=discord.Colour.green())
                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                for member in message.mentions:
                                                    await member.add_roles(select_role)

                                                await ctx.edit(embed=embed, view=ButtonBackSettings())

                                        async def button_callback_no_verify(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                await ctx.edit(view=ButtonBackSettings())

                                        button_yes_verify.callback = button_callback_yes_verify
                                        button_no_verify.callback = button_callback_no_verify

                                        view_verify.add_item(button_yes_verify)
                                        view_verify.add_item(button_no_verify)

                                        await message.delete()
                                        await ctx.edit(embed=embed, view=view_verify)

                                @discord.ui.button(label="Забрать у пользователей", custom_id="button_remove_members")
                                async def button_callback_remove_members(self, button, interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        # Кнопка возврата к настройки роли
                                        view = View()
                                        button_back = discord.ui.Button(label="Отмена", custom_id="button_back", style=discord.ButtonStyle.red)

                                        async def button_callback_back(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                embed = discord.Embed(title=f'Управление личной ролью', description=f"**Выберите** операцию для **взаимодействия** с **личной ролью** {select_role.mention}", color=0x2f3136)
                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                        
                                                await ctx.edit(embed=embed, view=ButtonsEditView())

                                        button_back.callback = button_callback_back
                                        view.add_item(button_back)

                                        # Меняем сообщение на Забрать роль
                                        embed = discord.Embed(title=f'Забрать роль', description=f"**Упомяните пользователей** у которых хотите **забрать** вашу **личную роль** {select_role.mention}", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        await ctx.edit(embed=embed, view=view)

                                        # Ждём упоминания людей
                                        await interaction.followup.send("Упомяните пользователей у которых хотите забрать вашу личную роль.", ephemeral=True, delete_after=10)

                                        try:
                                            def check(message):
                                                return interaction.user == message.author

                                            while True:
                                                message = await globalself.bot.wait_for("message", timeout=60.0, check=check)

                                                if len(message.mentions) > 0:
                                                    break
                                                else:
                                                    await interaction.followup.send("Упомяните пользователей у которых хотите забрать вашу личную роль", ephemeral=True, delete_after=5)
                                                    await message.delete()

                                        except asyncio.TimeoutError:
                                            embed = discord.Embed(title=f'Забрать роль', description=f"Время ожидания истекло!", color=discord.Color.red())
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                            await ctx.edit(embed=embed, view=View())

                                        # Получили новое название, теперь подтверждаем действие
                                        view_verify = View()

                                        mention_members = ""

                                        for member in message.mentions:
                                            mention_members += f"<@{member.id}> "

                                        embed = discord.Embed(title=f'Забрать роль', description=f"**Вы уверены** что хотите **забрать** вашу роль у пользователей: {mention_members} ?", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        button_yes_verify = discord.ui.Button(label="Да", custom_id="button_yes_verify", style=discord.ButtonStyle.green)
                                        button_no_verify = discord.ui.Button(label="Нет", custom_id="button_no_verify", style=discord.ButtonStyle.red)

                                        async def button_callback_yes_verify(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                embed = discord.Embed(title=f'Забрать роль', description=f"**Вы** успешно **забрали** вашу роль у пользователей: {mention_members}", color=discord.Colour.green())
                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                for member in message.mentions:
                                                    await member.remove_roles(select_role)

                                                await ctx.edit(embed=embed, view=ButtonBackSettings())

                                        async def button_callback_no_verify(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                await ctx.edit(view=ButtonBackSettings())

                                        button_yes_verify.callback = button_callback_yes_verify
                                        button_no_verify.callback = button_callback_no_verify

                                        view_verify.add_item(button_yes_verify)
                                        view_verify.add_item(button_no_verify)

                                        await message.delete()
                                        await ctx.edit(embed=embed, view=view_verify)

                                @discord.ui.button(label="Удалить личную роль", custom_id="button_delete_role", style=discord.ButtonStyle.red, row=1)
                                async def button_callback_delete_role(self, button, interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        view_verify = View()

                                        embed = discord.Embed(title=f'Удалить личную роль', description=f"**Вы уверены** что хотите **удалить** вашу **личную роль** {select_role.mention} ?", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        button_yes_verify = discord.ui.Button(label="Да", custom_id="button_yes_verify", style=discord.ButtonStyle.green)
                                        button_no_verify = discord.ui.Button(label="Нет", custom_id="button_no_verify", style=discord.ButtonStyle.red)

                                        async def button_callback_yes_verify(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                embed = discord.Embed(title=f'Удалить личную роль', description=f"**Вы** успешно **удалили** вашу **личную роль**.", color=discord.Colour.green())
                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                globalself.db.delete_role(select_role)
                                                await select_role.delete()

                                                view_back_inventory = View()

                                                button_close = discord.ui.Button(label="Закрыть", custom_id="button_close", style=discord.ButtonStyle.red)

                                                async def button_callback_close(interaction: discord.Interaction):
                                                    await interaction.response.defer()

                                                    if ctx.author.id == interaction.user.id:
                                                        await ctx.delete()

                                                button_close.callback = button_callback_close

                                                view_back_inventory.add_item(button_close)

                                                await ctx.edit(embed=embed, view=view_back_inventory)

                                        async def button_callback_no_verify(interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                await ctx.edit(view=ButtonBackSettings())

                                        button_yes_verify.callback = button_callback_yes_verify
                                        button_no_verify.callback = button_callback_no_verify

                                        view_verify.add_item(button_yes_verify)
                                        view_verify.add_item(button_no_verify)

                                        await ctx.edit(embed=embed, view=view_verify)

                                @discord.ui.button(label="⬅️ Вернуться к выбору роли", custom_id="button_back_select_role", style=discord.ButtonStyle.blurple, row=1)
                                async def button_callback_back_select_role(self, button, interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        embed = discord.Embed(title=f"Личные роли", description=f"**Выберите** роль для **взаимодействия**", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        await ctx.edit(embed=embed, view=SelectRoleView())

                            time_create = datetime.fromtimestamp(globalself.db.get_time_to_pay(select_role))
                            time_pay = time_create + timedelta(days=30)

                            embed = discord.Embed(title=f'Управление личной ролью', description=f"**Выберите** операцию для **взаимодействия** с **личной ролью** {select_role.mention}\n\nДо оплаты — **{(time_pay - time_create).days}** дней", color=0x2f3136)
                            embed.set_footer(text=f"Создана {role_created_at}")
                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                            await ctx.edit(embed=embed, view=ButtonsEditView())

                    select.callback = select_callback
                    self.add_item(select)

            await ctx.followup.send(embed=embed, view=SelectRoleView())
        else:
            await ctx.respond("Нихуя нет", ephemeral=True)