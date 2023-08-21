from easy_pil import Editor, Canvas, Font, load_image_async

import discord
from discord import File
from discord import Option
from discord.ext import commands
from discord.ui import View

import json

from datetime import datetime, timedelta

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

# Fonts
font_40 = Font("assets/font.ttf", size=40)
font_50 = Font("assets/font.ttf", size=50)
font_80 = Font("assets/font.ttf", size=80)

font_bighaustitul_50 = Font("assets/font_bighaustitul.ttf", size=50)

class LoveProfile(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

        try:
            with open("./assets/settings.json", "r", encoding="utf8") as settings:
                data = json.load(settings)

            self.guild_id = data.get("guild_id")

            self.settings_roles = data.get("roles")
            self.settings_prices = data.get("prices")

            self.cost_room_change_name = self.settings_prices.get("change_name_love_room")
            self.cost_theme_default_lprofile = self.settings_prices.get("theme_default_lprofile")

            logger.info("Настройки загружены.")

        except:
            logger.error("Не можем загрузить настройки :(")
            exit()

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = discord.utils.get(self.bot.guilds, id=self.guild_id)

        self.marry_role = discord.utils.get(self.guild.roles, id=self.settings_roles.get("marry_role"))

        logger.info("/lprofile - start")

    async def generate_lprofile(self, member):
        canvas = Canvas ((1920, 1000))

        background = Editor(f"assets/marry/themes/{self.db.get_active_theme_lprofile(member)}.png")

        editor = Editor(canvas)

        editor.paste(background.image, (0, 0))

        if (member):
            data = self.db.get_info_marriege(member)

            partner_1 = self.bot.get_user(data[1])
            partner_2 = self.bot.get_user(data[2])

            reg_date = datetime.fromtimestamp(int(data[4]))
            reg_days = datetime.now() - reg_date
            end = datetime.fromtimestamp(int(data[4])) + timedelta(days=30)

            a_partner_1 = await load_image_async(str(partner_1.display_avatar.url))
            a_partner_1 = Editor(a_partner_1).resize((200, 200)).circle_image()

            a_partner_2 = await load_image_async(str(partner_2.display_avatar.url))
            a_partner_2 = Editor(a_partner_2).resize((200, 200)).circle_image()

            # 1 партнёр
            background.paste(a_partner_1, (966, 70))
            name_partner_1 = (partner_1.display_name[:6] + '...') if len(partner_1.display_name) > 6 else partner_1.display_name

            background.text((1066, 330), name_partner_1 + "#" + partner_1.discriminator, color="white", font=font_40, align="center")

            # 2 партнёр
            background.paste(a_partner_2, (1548, 70))
            name_partner_2 = (partner_2.display_name[:6] + '...') if len(partner_2.display_name) > 6 else partner_2.display_name

            background.text((1648, 330), name_partner_2 + "#" + partner_2.discriminator, color="white", font=font_40, align="center")

            # Количество дней
            background.text((1358, 115), str(reg_days.days), color="#A482AB", font=font_80, align="center")

            # Дни
            background.text((1356, 183), "Дней", color="#A482AB", font=font_40, align="center")

            # Баланс
            background.text((960, 605), str(data[3]), color="white", font=font_bighaustitul_50, align="left")

            # Голосовая активность
            background.text((960, 808), f"{self.db.get_data_loveRoom(member)['total_hours']} ч.", color="white", font=font_bighaustitul_50, align="left")

            # Дата регистрации брака
            background.text((1685, 605), f"{reg_date.day:02}.{reg_date.month:02}.{reg_date.year}", color="white", font=font_bighaustitul_50, align="center")

            # Дата оплаты
            background.text((1685, 808), f"{end.day:02}.{end.month:02}.{end.year}", color="white", font=font_bighaustitul_50, align="center")
        
            return background

    # Love profile
    @commands.slash_command(name="lprofile", description="Любовный профиль.", guild_ids=[guild_id_cmd])
    async def lprofile(
        self,
        ctx: discord.ApplicationContext, 
        member: Option(discord.Member, name="пользователь", description="Выберите пуську.", required=False)
    ):
        globalself = self

        if member:
            if self.db.is_marry(member.id):
                lprofile = await self.generate_lprofile(member)
                data = self.db.get_info_marriege(member)

                file = discord.File(fp=lprofile.image_bytes, filename="image.png")
                await ctx.respond(file=file)
            else:
                embed = discord.Embed(title=f'Любовный профиль', description="Этот человек ещё не состоит в браке! Может это твоя судьба?", color=0x2f3136)
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                await ctx.respond(embed=embed, ephemeral=True)
        else:
            if self.db.is_marry(ctx.author.id):
                await ctx.defer()
                
                lprofile = await self.generate_lprofile(ctx.author)
                data = self.db.get_info_marriege(ctx.author)
                
                partner_1 = self.guild.get_member(data[1])
                partner_2 = self.guild.get_member(data[2])

                file = discord.File(fp=lprofile.image_bytes, filename="image.png")
                embed = discord.Embed(title=f'Любовный профиль — {ctx.author.name}#{ctx.author.discriminator}', color=0x2f3136)
                embed.set_image(url="attachment://image.png")

                class ButtonsView(discord.ui.View):
                    def __init__(self, *, timeout=120):
                        super().__init__(timeout=timeout)

                    @discord.ui.button(label="Пополнить баланс", style=discord.ButtonStyle.blurple, custom_id="button_balance_lprofile")
                    async def button_callback_balance(self, button, interaction: discord.Interaction):

                        if ctx.author.id == interaction.user.id:
                            class AddBalance(discord.ui.Modal):
                                def __init__(self, *args, **kwargs):
                                    super().__init__(
                                        discord.ui.InputText(
                                            label="Введите сумму пополнения",
                                            placeholder="100",
                                            required=True
                                        ),
                                        *args,
                                        **kwargs
                                    )

                                async def callback(self, interaction):
                                    await interaction.response.defer()

                                    try:
                                        if int(self.children[0].value) <= 0:
                                            embed = discord.Embed(title='Пополнение баланса пары', description="Введите корректную сумму пополнения.", color=0x2f3136)
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                            await interaction.followup.send(embed=embed, ephemeral=True)
                                        else:
                                            embed = discord.Embed(title='Пополнение баланса пары', description="Вы успешно пополнили баланс пары.", color=0x2f3136)
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                            globalself.db.give_balance_marry(ctx.author, int(self.children[0].value))

                                            await interaction.followup.send(embed=embed, ephemeral=True)

                                            lprofile = await globalself.generate_lprofile(ctx.author)

                                            file = discord.File(fp=lprofile.image_bytes, filename="image.png")

                                            await ctx.edit(file=file)
                                    except Exception:
                                        embed = discord.Embed(title='Пополнение баланса пары', description="Введите корректную сумму пополнения.", color=0x2f3136)
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                        await interaction.followup.send(embed=embed, ephemeral=True)
                            await interaction.response.send_modal(AddBalance(title="Пополнение баланса пары"))

                    @discord.ui.button(label="Настройки", style=discord.ButtonStyle.blurple, custom_id="button_settings_lprofile")
                    async def button_callback_settings(self, button, interaction: discord.Interaction):
                        await interaction.response.defer()

                        if ctx.author.id == interaction.user.id:
                            class SettingsMarry(discord.ui.View):
                                def __init__(self, *, timeout=120):
                                    super().__init__(timeout=timeout)

                                # Вернуться в лав профиль
                                @discord.ui.button(label="⬅️ Назад", custom_id="button_back_settings_lprofile")
                                async def button_callback_back_settings(self, button, interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        await ctx.edit(view=ButtonsView())

                                # Магазин тем для лав профиля
                                @discord.ui.button(label="Магазин профилей", style=discord.ButtonStyle.blurple, custom_id="button_shop_settings_lprofile")
                                async def button_callback_shop_settings(self, button, interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        class ProfilesShop(discord.ui.View):
                                            def __init__(self, page, timeout=120):
                                                super().__init__(timeout=timeout)

                                                self.page = page
                                                self.buy_buttons = []
                                                self.user_themes = globalself.db.get_themes_lprofile(ctx.author)

                                                for i in range(0, 4):
                                                    if f"theme_{(self.page-1)*4+i+1}" in self.user_themes:
                                                        if globalself.db.get_active_theme_lprofile(ctx.author) == f"theme_{(self.page-1)*4+i+1}":
                                                            self.buy_buttons.append(discord.ui.Button(label=f"{(self.page-1)*4+i+1}", custom_id=f"{(self.page-1)*4+i+1}", style=discord.ButtonStyle.blurple, row=0))
                                                        else:
                                                            self.buy_buttons.append(discord.ui.Button(label=f"{(self.page-1)*4+i+1}", custom_id=f"{(self.page-1)*4+i+1}", style=discord.ButtonStyle.green, row=0))
                                                    else:
                                                        self.buy_buttons.append(discord.ui.Button(label=f"{(self.page-1)*4+i+1}", custom_id=f"{(self.page-1)*4+i+1}", row=0))

                                                    async def button_callback_buy_theme(interaction: discord.Interaction):
                                                        await interaction.response.defer()

                                                        if ctx.author.id == interaction.user.id:
                                                            cost = int(globalself.cost_theme_default_lprofile)
                                                            id_theme = int(interaction.data['custom_id'])
                                                            if f"theme_{id_theme}" in self.user_themes:
                                                                if globalself.db.get_active_theme_lprofile(ctx.author) == f"theme_{id_theme}":
                                                                    globalself.db.set_active_theme_lprofile(ctx.author, "theme_default")

                                                                    embed = discord.Embed(title=f'Магазин любовных профилей', description=f"**Вы** успешно **сбросили** тему профиля на **стандартную**", color=discord.Colour.green())
                                                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                                    await ctx.edit(view=ProfilesShop(self.page))
                                                                    await interaction.followup.send(embed=embed, view=View(), ephemeral=True)
                                                                else:
                                                                    globalself.db.set_active_theme_lprofile(ctx.author, f"theme_{id_theme}")

                                                                    embed = discord.Embed(title=f'Магазин любовных профилей', description=f"**Вы** успешно **установили** тему профиля **№{int(interaction.data['custom_id'])}**", color=discord.Colour.green())
                                                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                                    await ctx.edit(view=ProfilesShop(self.page))
                                                                    await interaction.followup.send(embed=embed, view=View(), ephemeral=True)
                                                            else:
                                                                if globalself.db.get_balance_marry(ctx.author) >= cost:
                                                                    class ViewVerify(discord.ui.View):
                                                                        def __init__(self, page, user_themes, timeout=60):
                                                                            super().__init__(timeout=timeout)\
                                                                            
                                                                            self.page = page
                                                                            self.user_themes = user_themes

                                                                        async def on_timeout(self):
                                                                            await ctx.delete()

                                                                        @discord.ui.button(label="Да", style=discord.ButtonStyle.green)
                                                                        async def button_callback_yes(self, button, interaction: discord.Interaction):
                                                                            await interaction.response.defer()

                                                                            if ctx.author.id == interaction.user.id:
                                                                                if f"theme_{id_theme}" in self.user_themes:
                                                                                    embed = discord.Embed(title=f'Магазин любовных профилей', description=f"У вас **уже** есть эта тема!", color=0x2f3136)
                                                                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                                                    await interaction.followup.send(embed=embed, ephemeral=True)
                                                                                else:
                                                                                    globalself.db.take_money_marry(ctx.author, cost)
                                                                                    
                                                                                    globalself.db.give_theme_lprofile(ctx.author, f"theme_{id_theme}")
                                                                                    globalself.db.set_active_theme_lprofile(ctx.author, f"theme_{id_theme}")

                                                                                    embed = discord.Embed(title=f'Магазин профилей', description=f"**Вы** успешно **купили** тему профиля **№{id_theme}** за **{globalself.cost_theme_default_lprofile}** <:1016719860547469323:1098025516059070485>\n\nНовая тема **установлена**", color=discord.Colour.green())
                                                                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                                                    await ctx.edit(view=ProfilesShop(page=self.page))
                                                                                    await message.edit(embed=embed, view=View())

                                                                        @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
                                                                        async def button_callback_no(self, button, interaction: discord.Interaction):
                                                                            await interaction.response.defer()

                                                                            if ctx.author.id == interaction.user.id:
                                                                                await message.delete()

                                                                    embed = discord.Embed(title=f'Магазин любовных профилей', description=f"**Вы** уверены что хотите **купить** тему профиля **№{id_theme}** за **{globalself.cost_theme_default_lprofile}** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                                                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                                    message = await interaction.followup.send(embed=embed, view=ViewVerify(self.page, self.user_themes), ephemeral=True)
                                                                else:
                                                                    embed = discord.Embed(title='Упс...', description="На балансе пары недостаточно средств! Для начала пополните баланс.", color=0x2f3136)
                                                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                                    await interaction.followup.send(embed=embed, view=View(), ephemeral=True)

                                                    self.buy_buttons[i].callback = button_callback_buy_theme

                                                    self.add_item(self.buy_buttons[i])

                                            @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple, row=1)
                                            async def button_callback_back_shop(self, button, interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    if self.page == 2:
                                                        file = discord.File('assets/marry/profiles_1.png') # хуйня
                                                        await ctx.edit(file=file, view=ProfilesShop(page=1))

                                            @discord.ui.button(label="В профиль", row=1)
                                            async def button_callback_back_profile(self, button, interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    profile = await globalself.generate_lprofile(ctx.author)

                                                    file = File(fp=profile.image_bytes, filename="assets/marry/profile.png")
                                                    await ctx.edit(file=file, view=ButtonsView())

                                            @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple, row=1)
                                            async def button_callback_next_shop(self, button, interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    if self.page == 1:
                                                        file = discord.File('assets/marry/profiles_2.png') # хуйня
                                                        await ctx.edit(file=file, view=ProfilesShop(page=2))

                                        file = discord.File('assets/marry/profiles_1.png')

                                        await ctx.edit(file=file, view=ProfilesShop(page=1))

                                # Настроить лав руму
                                @discord.ui.button(label="Настройки комнаты", style=discord.ButtonStyle.blurple, custom_id="button_room_settings_lprofile")
                                async def button_callback_room_settings(self, button, interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        class SettingsRoom(discord.ui.View):
                                            def __init__(self, *, timeout=120):
                                                super().__init__(timeout=timeout)
                                            
                                            # Вернуться к настройкам брака
                                            @discord.ui.button(label="⬅️ Назад", custom_id="button_back_room_lprofile")
                                            async def button_callback_back_room(self, button, interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    await ctx.edit(view=SettingsMarry())

                                            # Изменить название лав румы
                                            @discord.ui.button(label="Изменить название", style=discord.ButtonStyle.blurple, custom_id="button_name_room_lprofile")
                                            async def button_callback_name_room(self, button, interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    # Ждём нового названия
                                                    embed = discord.Embed(title="Название любовной комнаты", description="Укажите новое название вашей любовной комнаты.", color=0x2f3136)
                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                                    message = await interaction.followup.send(embed=embed, ephemeral=True)

                                                    try:
                                                        def check(message):
                                                            return interaction.user == message.author

                                                        user_message = await globalself.bot.wait_for("message", timeout=120.0, check=check)
                                                    except asyncio.TimeoutError:
                                                        embed = discord.Embed(title="Название любовной комнаты", description="К сожалению ваше время ожидания истекло. Попробуйте вновь повторить действие, а может и не стоит, вдруг это судьба.", color=0x2f3136)
                                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                                        await interaction.message.edit(embed=embed, view=View())

                                                    view_verify = View()

                                                    embed = discord.Embed(title="Название любовной комнаты", description=f"Вы уверены что хотите установить **{user_message.content}** новым названием вашей любовной комнаты, это будет стоить **{globalself.cost_room_change_name}** <:1016719860547469323:1098025516059070485>.\nЛучше посоветуйтесь с вашей второй половинкой.", color=0x2f3136)
                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                                    button_yes_verify = discord.ui.Button(label="Да", custom_id="button_yes_verify", style=discord.ButtonStyle.green)

                                                    async def button_callback_yes_verify(interaction: discord.Interaction):
                                                        await interaction.response.defer()
                                                        if ctx.author.id == interaction.user.id:
                                                            loveRoom_data = globalself.db.get_data_loveRoom(ctx.author)
                                                            data = globalself.db.get_info_marriege(ctx.author)

                                                            partner_1 = globalself.bot.get_user(data[1])
                                                            partner_2 = globalself.bot.get_user(data[2])

                                                            old_name = ""

                                                            if loveRoom_data['name'] == 0:
                                                                old_name = f"{partner_1.display_name} 💕 {partner_2.display_name}"
                                                            else:
                                                                old_name = loveRoom_data['name']

                                                            if globalself.db.get_balance_marry(ctx.author) >= globalself.cost_room_change_name:
                                                                embed = discord.Embed(title=f"Название любовной комнаты", description=f"Ух, было не столь легко. Но вы успешно изменили название вашей любовной комнаты с **{old_name}** на название **{user_message.content}**.", color=0x2f3136)
                                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                                                loveRoom_voice = globalself.guild.get_channel(loveRoom_data['id'])

                                                                if loveRoom_voice:
                                                                    await loveRoom_voice.edit(name=f"{user_message.content}")

                                                                globalself.db.write_data_loveRoom(ctx.author, 'name', str(user_message.content))

                                                                globalself.db.take_money_marry(ctx.author, globalself.cost_room_change_name)
                                                                
                                                                await message.edit(embed=embed)
                                                            else:
                                                                embed = discord.Embed(title="Упс...", description="У вас недостаточно средств! Для начала пополните свой баланс.", color=0x2f3136)
                                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                                                await message.edit(embed=embed)

                                                    button_no_verify = discord.ui.Button(label="Нет", custom_id="button_no_verify", style=discord.ButtonStyle.red)

                                                    async def button_callback_no_verify(interaction: discord.Interaction):
                                                        await interaction.response.defer()
                                                        if ctx.author.id == interaction.user.id:
                                                            await message.delete()

                                                    button_yes_verify.callback = button_callback_yes_verify
                                                    button_no_verify.callback = button_callback_no_verify

                                                    view_verify.add_item(button_yes_verify)
                                                    view_verify.add_item(button_no_verify)

                                                    view_verify.timeout=60 

                                                    await user_message.delete()
                                                    await message.edit(embed=embed, view=view_verify)

                                            # Сброс названия лав румы
                                            @discord.ui.button(label="Сбросить название", custom_id="button_reset_name_room_lprofile")
                                            async def button_callback_reset_name_room(self, button, interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    embed = discord.Embed(title="Название любовной комнаты", description="Вы успешно **сбросили название** любовной комнаты.", color=0x2f3136)
                                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                                    globalself.db.write_data_loveRoom(ctx.author, 'name', 0)

                                                    loveRoom_data = globalself.db.get_data_loveRoom(ctx.author)
                                                    data = globalself.db.get_info_marriege(ctx.author)

                                                    partner_1 = globalself.bot.get_user(data[1])
                                                    partner_2 = globalself.bot.get_user(data[2])

                                                    loveRoom_voice = globalself.guild.get_channel(loveRoom_data['id'])

                                                    if loveRoom_voice:
                                                        await loveRoom_voice.edit(f"{partner_1.display_name} 💕 {partner_2.display_name}")

                                                    await interaction.followup.send(embed=embed, ephemeral=True)

                                            # Скрыть/Показать лав руму
                                            @discord.ui.button(label="Скрыть/Показать комнату", style=discord.ButtonStyle.blurple, custom_id="button_hide_room_lprofile")
                                            async def button_callback_hide_room(self, button, interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    loveRoom_data = globalself.db.get_data_loveRoom(ctx.author)

                                                    if loveRoom_data['id'] and loveRoom_data['id'] != 0:
                                                        loveRoom_voice = globalself.guild.get_channel(loveRoom_data['id'])

                                                        old_overwrites = loveRoom_voice.overwrites_for(globalself.guild.default_role)

                                                        overwrite = discord.PermissionOverwrite()
                                                        overwrite.view_channel = False

                                                        if old_overwrites.view_channel:
                                                            embed = discord.Embed(title='Изменение любовной комнаты', description="Вы успешно **скрыли** вашу комнату от лишних глаз!", color=0x2f3136)
                                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                                            await loveRoom_voice.set_permissions(globalself.guild.default_role, overwrite=overwrite)
                                                        else:
                                                            embed = discord.Embed(title='Изменение любовной комнаты', description="Вы успешно **показали** вашу комнату для всех!", color=0x2f3136)
                                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                                            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                                            overwrite.view_channel = True
                                                            await loveRoom_voice.set_permissions(globalself.guild.default_role, overwrite=overwrite)

                                                        await interaction.followup.send(embed=embed, ephemeral=True)

                                        await ctx.edit(view=SettingsRoom())

                            await ctx.edit(view=SettingsMarry())

                    @discord.ui.button(label="Развестись", style=discord.ButtonStyle.red, custom_id="button_divorce")
                    async def button_callback_divorce(self, button, interaction: discord.Interaction):
                        await interaction.response.defer()

                        if ctx.author.id == interaction.user.id:
                            globalself.db.divorce_marriege(data[1], data[2])

                            await partner_1.remove_roles(globalself.marry_role)
                            await partner_2.remove_roles(globalself.marry_role)

                            globalself.db.write_log_in_history(partner_1, partner_2, 'divorce')

                            if ctx.author.id == partner_1.id:
                                embed = discord.Embed(title='', description=f"Ваш брак был расторгнут по инициативе {partner_1.mention}. Наверное тому послужило что данный человек к вам остыл, но помните что у нас на сервере вы можете найти себе другую вторую половинку.", color=0x2f3136)
                                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                await partner_2.send(embed=embed)
                            elif ctx.author.id == partner_2.id:
                                embed = discord.Embed(title='', description=f"Ваш брак был расторгнут по инициативе {partner_2.mention}. Наверное тому послужило что данный человек к вам остыл, но помните что у нас на сервере вы можете найти себе другую вторую половинку.", color=0x2f3136)
                                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                                await partner_1.send(embed=embed)

                            embed = discord.Embed(title='Расторжение брака', description="Вы успешно развелись. Надеемся вы найдёте того самого человека с которым будете счастливы.", color=0x2f3136)
                            embed.set_thumbnail(url=ctx.author.display_avatar.url)
                            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                            await interaction.followup.send(embed=embed, ephemeral=True) # вебхук на развод
                            await ctx.edit(view=View())
                            
                await ctx.followup.send(file=file, view=ButtonsView())

            else:
                embed = discord.Embed(title='Любовный профиль', description="У вас отсутствует пара! Для её создания используйте команду: `/marry @member`.\nСтоимость создания традиционной пары - **1500** <:1016719860547469323:1098025516059070485>\nСтоимость создания нетрадиционной пары - **3000** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                await ctx.respond(embed=embed, ephemeral=True)