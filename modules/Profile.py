from easy_pil import Editor, Canvas, Font, load_image_async

import json

import discord
from discord import File
from discord.commands import Option
from discord.ext import commands
from discord.ui import Select, View

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

# Fonts
font_50 = Font("assets/font.ttf", size=50)
font_60 = Font("assets/font.ttf", size=60)

font_bighaustitul_50 = Font("assets/font_bighaustitul.ttf", size=50)

class Profile(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()
        self.utils = Utils()

        try:
            with open("./assets/settings.json", "r", encoding="utf8") as settings:
                data = json.load(settings)

            self.settings_prices = data.get("prices")

            self.cost_theme_default_profile = self.settings_prices.get("theme_default_profile")

            logger.info("Настройки загружены.")

        except:
            logger.error("Не можем загрузить настройки :(")
            exit()

        self.inst_a = Editor("assets/profile/inst_a.png")
        self.inst_n = Editor("assets/profile/inst_n.png")
        self.tg_a = Editor("assets/profile/tg_a.png")
        self.tg_n = Editor("assets/profile/tg_n.png")
        self.vk_a = Editor("assets/profile/vk_a.png")
        self.vk_n = Editor("assets/profile/vk_n.png")
        self.tiktok_a = Editor("assets/profile/tiktok_a.png")
        self.tiktok_n = Editor("assets/profile/tiktok_n.png")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("/profile - start")

    async def generate_profile(self, member):
        canvas = Canvas((2000, 1000))
        editor = Editor(canvas)

        self.background = Editor(f"assets/profile/themes/{self.db.get_active_theme(member)}.png")

        editor.paste(self.background.image, (0, 0))

        social_networks = [
            ('inst', (54, 114), self.inst_a, self.inst_n),
            ('tg', (54, 321), self.tg_a, self.tg_n),
            ('vk', (54, 534), self.vk_a, self.vk_n),
            ('tiktok', (54, 746), self.tiktok_a, self.tiktok_n),
        ]

        for sn, coords, img_a, img_n in social_networks:
            social_id = self.db.get_social(member.id, sn)
            img = img_a if social_id and social_id != " " else img_n
            editor.paste(img.image, coords)

        money = self.db.get_balance(member.id)
        name = member.display_name

        member_name = (name[:9] + '...') if len(name) > 10 else name

        member_name += "#" + str(member.discriminator)

        # Ник
        editor.text((1461, 390), member_name, color="white", font=font_60, align="center")

        # Аватарка
        avatar = await load_image_async(str(member.display_avatar.url))
        avatar = Editor(avatar).resize((250, 250)).circle_image()
        editor.paste(avatar.image, (1337, 87))

        # Валюта
        editor.text((1068, 125), str(money), color="white", font=font_bighaustitul_50, align="left")

        # Голосовая активность
        editor.text((1068, 267), self.db.get_total_online(member.id), color="white", font=font_bighaustitul_50, align="left")

        # Количество сообщений
        editor.text((1740, 125), str(self.db.get_message_count(member)), color="white", font=font_bighaustitul_50, align="left")

        # Место в топе по голосовой активности
        editor.text((1740, 267), "0", color="white", font=font_bighaustitul_50, align="left")

        # Если есть брак то рисуем партнёра
        if self.db.is_marry(member.id):
            data = self.db.get_info_marriege(member)

            if data[1] == member.id:
                partner = self.bot.get_user(data[2])
            else:
                partner = self.bot.get_user(data[1])

            partner_name = (partner.display_name[:8] + '...') if len(partner.display_name) > 8 else partner.display_name

            avatar_partner = await load_image_async(str(partner.display_avatar.url))
            avatar_partner = Editor(avatar_partner).resize((200, 200)).circle_image()
            
            # Аватарка партнёра
            editor.paste(avatar_partner.image, (1085, 560))

            # Ник партнёра
            editor.text((1185, 822), partner_name, color="white", font=font_50, align="center")
        
        return editor

    # Profile
    @commands.slash_command(name="profile", description="Профиль пользователя.", guild_ids=[guild_id_cmd])
    async def profile(
        self,
        ctx: discord.ApplicationContext, 
        member: Option(discord.Member, name="пользователь", description="Выберите пуську.", required = False)
    ):
        await ctx.response.defer()
        globalself = self

        if (member):
            # Социальные сети пользователя
            id_vk = self.db.get_social(member.id, 'vk')
            id_inst = self.db.get_social(member.id, 'inst')
            id_tg = self.db.get_social(member.id, 'tg')
            id_tiktok = self.db.get_social(member.id, 'tiktok')

            # Генерируем изображение профиля
            profile = await self.generate_profile(member)

            file = File(fp=profile.image_bytes, filename="assets/profile/profile.png")
            await ctx.followup.send(file=file)
        else:
            self.db.write_new_user(ctx.author)

            # Социальные сети пользователя
            id_vk = self.db.get_social(ctx.author.id, 'vk')
            id_inst = self.db.get_social(ctx.author.id, 'inst')
            id_tg = self.db.get_social(ctx.author.id, 'tg')
            id_tiktok = self.db.get_social(ctx.author.id, 'tiktok')

            # Генерируем изображение профиля
            profile = await self.generate_profile(ctx.author)

            class ProfileSocials(discord.ui.Modal):
                def __init__(self, *args, **kwargs):
                    super().__init__(
                        discord.ui.InputText(
                            label="Instagram",
                            placeholder="id instagram",
                            value=globalself.db.get_social(ctx.author.id, 'inst'),
                            required=False
                        ),
                        discord.ui.InputText(
                            label="VK",
                            placeholder="id vk",
                            value=globalself.db.get_social(ctx.author.id, 'vk'),
                            required=False
                        ),
                        discord.ui.InputText(
                            label="Telegram",
                            placeholder="id telegram",
                            value=globalself.db.get_social(ctx.author.id, 'tg'),
                            required=False
                        ),
                        discord.ui.InputText(
                            label="TikTok",
                            placeholder="id tiktok",
                            value=globalself.db.get_social(ctx.author.id, 'tiktok'),
                            required=False
                        ),
                        *args,
                        **kwargs
                    )

                async def callback(self, interaction):
                    await interaction.response.defer()

                    globalself.db.set_social("inst", self.children[0].value, interaction.user.id)
                    globalself.db.set_social("vk", self.children[1].value, interaction.user.id)
                    globalself.db.set_social("telegram", self.children[2].value, interaction.user.id)
                    globalself.db.set_social("tiktok", self.children[3].value, interaction.user.id)

                    await interaction.followup.send("Соц.сети изменены!", ephemeral=True)

            class ProfilesShop(discord.ui.View):
                def __init__(self, page, timeout=120):
                    super().__init__(timeout=timeout)

                    self.page = page
                    self.buy_buttons = []
                    self.user_themes = globalself.db.get_themes(ctx.author)

                    for i in range(0, 4):
                        if f"theme_{(self.page-1)*4+i+1}" in self.user_themes:
                            if globalself.db.get_active_theme(ctx.author) == f"theme_{(self.page-1)*4+i+1}":
                                self.buy_buttons.append(discord.ui.Button(label=f"{(self.page-1)*4+i+1}", custom_id=f"{(self.page-1)*4+i+1}", style=discord.ButtonStyle.blurple, row=0))
                            else:
                                self.buy_buttons.append(discord.ui.Button(label=f"{(self.page-1)*4+i+1}", custom_id=f"{(self.page-1)*4+i+1}", style=discord.ButtonStyle.green, row=0))
                        else:
                            self.buy_buttons.append(discord.ui.Button(label=f"{(self.page-1)*4+i+1}", custom_id=f"{(self.page-1)*4+i+1}", row=0))

                        async def button_callback_buy_theme(interaction: discord.Interaction):
                            await interaction.response.defer()

                            if ctx.author.id == interaction.user.id:
                                cost = int(globalself.cost_theme_default_profile)
                                id_theme = int(interaction.data['custom_id'])
                                if f"theme_{id_theme}" in self.user_themes:
                                    if globalself.db.get_active_theme(ctx.author) == f"theme_{id_theme}":
                                        globalself.db.set_active_theme(ctx.author, "theme_default")

                                        embed = discord.Embed(title=f'Магазин профилей', description=f"**Вы** успешно **сбросили** тему профиля на **стандартную**", color=discord.Colour.green())
                                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        await ctx.edit(view=ProfilesShop(self.page))
                                        await interaction.followup.send(embed=embed, view=View(), ephemeral=True)
                                    else:
                                        globalself.db.set_active_theme(ctx.author, f"theme_{id_theme}")

                                        embed = discord.Embed(title=f'Магазин профилей', description=f"**Вы** успешно **установили** тему профиля **№{int(interaction.data['custom_id'])}**", color=discord.Colour.green())
                                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        await ctx.edit(view=ProfilesShop(self.page))
                                        await interaction.followup.send(embed=embed, view=View(), ephemeral=True)
                                else:
                                    if globalself.db.get_balance(ctx.author.id) >= cost:
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
                                                        embed = discord.Embed(title=f'Магазин профилей', description=f"У вас **уже** есть эта тема!", color=0x2f3136)
                                                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                        await interaction.followup.send(embed=embed, ephemeral=True)
                                                    else:
                                                        globalself.db.take_money(ctx.author.id, cost)
                                                        globalself.db.write_new_transactions(ctx.author, f"Покупка темы профиля №{id_theme}", -cost)
                                                        
                                                        globalself.db.give_theme(ctx.author, f"theme_{id_theme}")
                                                        globalself.db.set_active_theme(ctx.author, f"theme_{id_theme}")

                                                        embed = discord.Embed(title=f'Магазин профилей', description=f"**Вы** успешно **купили** тему профиля **№{id_theme}** за **{globalself.cost_theme_default_profile}** <:1016719860547469323:1098025516059070485>\n\nНовая тема **установлена**", color=discord.Colour.green())
                                                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                        await ctx.edit(view=ProfilesShop(page=self.page))
                                                        await message.edit(embed=embed, view=View())

                                            @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
                                            async def button_callback_no(self, button, interaction: discord.Interaction):
                                                await interaction.response.defer()

                                                if ctx.author.id == interaction.user.id:
                                                    await message.delete()

                                        embed = discord.Embed(title=f'Магазин профилей', description=f"**Вы** уверены что хотите **купить** тему профиля **№{id_theme}** за **{globalself.cost_theme_default_profile}** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        message = await interaction.followup.send(embed=embed, view=ViewVerify(self.page, self.user_themes), ephemeral=True)
                                    else:
                                        embed = discord.Embed(title='Упс...', description="У вас недостаточно средств! Для начала пополните свой баланс.", color=0x2f3136)
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
                            file = discord.File('assets/profile/profiles_1.png') # хуйня
                            await ctx.edit(file=file, view=ProfilesShop(page=1))

                @discord.ui.button(label="В профиль", row=1)
                async def button_callback_back_profile(self, button, interaction: discord.Interaction):
                    await interaction.response.defer()

                    if ctx.author.id == interaction.user.id:
                        profile = await globalself.generate_profile(ctx.author)

                        file = File(fp=profile.image_bytes, filename="assets/profile/profile.png")
                        await ctx.edit(file=file, view=ProfileMenu())

                @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple, row=1)
                async def button_callback_next_shop(self, button, interaction: discord.Interaction):
                    await interaction.response.defer()

                    if ctx.author.id == interaction.user.id:
                        if self.page == 1:
                            file = discord.File('assets/profile/profiles_2.png') # хуйня
                            await ctx.edit(file=file, view=ProfilesShop(page=2))

            class ProfileMenu(discord.ui.View):
                def __init__(self, *, timeout=120):
                    super().__init__(timeout=timeout)

                    if not member:
                        button_change_profile = discord.ui.Button(label="Изменить профиль", style=discord.ButtonStyle.blurple, custom_id="button_change_profile")

                        async def button_change_profile_callback(interaction):
                            await interaction.response.defer()
                            if ctx.author.id == interaction.user.id:
                                view_select = View()

                                select = Select(
                                    placeholder="Выберите тип изменений",
                                    options=[
                                        discord.SelectOption(
                                            label="Соц.Сети",
                                            description="Изменить социальные сети в профиле"
                                        ),
                                        discord.SelectOption(
                                            label="Магазин профилей",
                                            description="Магазин в котором вы можете купить новую тему профиля"
                                        )
                                    ]
                                )

                                async def select_callback(interaction: discord.Interaction):
                                    if ctx.author.id == interaction.user.id:
                                        if select.values[0] == "Соц.Сети":
                                            await interaction.response.send_modal(ProfileSocials(title="Изменение социальных сетей"))
                                        elif select.values[0] == "Магазин профилей":
                                            await interaction.response.defer()

                                            file = discord.File('assets/profile/profiles_1.png')

                                            await ctx.edit(file=file, view=ProfilesShop(page=1))

                                select.callback = select_callback

                                button_back = discord.ui.Button(label="Назад", style=discord.ButtonStyle.blurple)

                                async def button_back_callback(interaction):
                                    if ctx.author.id == interaction.user.id:
                                        profile = await globalself.generate_profile(ctx.author)

                                        file = File(fp=profile.image_bytes, filename="assets/profile/profile.png")
                                        await ctx.edit(file=file, view=ProfileMenu())

                                button_back.callback = button_back_callback

                                view_select.add_item(select)
                                view_select.add_item(button_back)

                                async def on_timeout():
                                    await ctx.edit(view=View())

                                view_select.timeout = 180   
                                view_select.on_timeout = on_timeout

                                await ctx.edit(view=view_select)
                        
                        button_change_profile.callback = button_change_profile_callback
                        self.add_item(button_change_profile)

                    social_media = {
                        'VKontakte': {'id': id_vk, 'url': f'https://vk.com/{id_vk}', 'emoji': '<:vk:1074071824465408121>'},
                        'Instagram': {'id': id_inst, 'url': f'https://instagram.com/{id_inst}', 'emoji': '<:inst:1074071790466367578>'},
                        'Telegram': {'id': id_tg, 'url': f'https://t.me/{id_tg}', 'emoji': '<:tg:1074071810099904622>'},
                        'TikTok': {'id': id_tiktok, 'url': f'https://www.tiktok.com/@{id_tiktok}', 'emoji': '<:tt:1074071771977883718>'}
                    }

                    for network, data in social_media.items():
                        if data['id'] not in [None, False, " "]:
                            button = discord.ui.Button(label='', url=data['url'], emoji=data['emoji'])
                            self.add_item(button)

            file = File(fp=profile.image_bytes, filename="assets/profile/profile.png")
            await ctx.followup.send(file=file, view=ProfileMenu())