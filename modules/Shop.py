import discord
from discord.commands import Option
from discord.ext import commands
from discord.ui import View

import math

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

class Shop(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = discord.utils.get(self.bot.guilds, id=guild_id_cmd)

        logger.info("/shop - start")

    async def get_user(self, user_id):
        user = self.bot.get_user(user_id)
        if user is None:
            return f"Пользователь {user_id}"
        return user.mention

    async def make_page_shop(self, page, total_pages, roles):
        # Создание списка ролей для текущей страницы
        page_roles = roles[(page-1)*5:page*5]

        embed = discord.Embed(title="Магазин личных ролей", color=0x2f3136)
        description = ""

        for i, (owner_id, role_id, price, count) in enumerate(page_roles):
            owner = await self.get_user(owner_id)
            role = discord.utils.get(self.guild.roles, id=role_id)
            
            # Добавляем информацию о роли в embed
            description += f"**{(page-1)*5+i+1}.** {role.mention} \n<:dot2:1078804345119842464> Продавец: {owner}\n<:dot2:1078804345119842464> Стоимость: **{price}** <:1016719860547469323:1098025516059070485>\n<:dot2:1078804345119842464> Куплена раз: **{count}**\n\n"

        embed.description = description
        embed.set_footer(text=f"Страница {page} из {total_pages}")
        return embed

    @commands.slash_command(name="shop", description="Магазин личных ролей.", guild_ids=[guild_id_cmd])
    async def shop(
        self,
        ctx: discord.ApplicationContext
    ):
        await ctx.response.defer()

        globalself = self

        roles = self.db.get_shop_roles()

        total_pages = math.ceil(len(roles)/5)
        page = 1

        # Кнопки управления магазином
        class ButtonsView(discord.ui.View):
            def __init__(self, page, total_pages, timeout=120):
                super().__init__(timeout=timeout)
                self.page = page
                self.total_pages = total_pages

                self.page_roles = roles[(self.page-1)*5:self.page*5]
                self.buy_buttons = []

                for i, (owner_id, role_id, price, count) in enumerate(self.page_roles):
                    self.buy_buttons.append(discord.ui.Button(label=f"{(self.page-1)*5+i+1}", custom_id=f"{(self.page-1)*5+i+1}", row=0))

                    async def button_callback_buy_role(interaction: discord.Interaction):
                        await interaction.response.defer()

                        if ctx.author.id == interaction.user.id:
                            role = discord.utils.get(globalself.guild.roles, id=int(roles[int(interaction.data['custom_id'])-1][1]))
                            seller = discord.utils.get(globalself.guild.members, id=int(roles[int(interaction.data['custom_id'])-1][0]))

                            cost = int(roles[int(interaction.data['custom_id'])-1][2])

                            if role in ctx.author.roles:
                                embed = discord.Embed(title=f'Магазин личных ролей', description=f"У **Вас** уже есть роль {role.mention}", color=discord.Colour.red())
                                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                await interaction.followup.send(embed=embed, view=View(), ephemeral=True)
                            else:
                                if globalself.db.get_balance(ctx.author.id) >= cost:
                                    class ViewVerify(discord.ui.View):
                                        def __init__(self, timeout=60):
                                            super().__init__(timeout=timeout)

                                        async def on_timeout(self):
                                            await ctx.delete()

                                        @discord.ui.button(label="Да", style=discord.ButtonStyle.green)
                                        async def button_callback_yes(self, button, interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                await ctx.author.add_roles(role)

                                                globalself.db.take_money(ctx.author.id, cost)
                                                globalself.db.give_money(seller.id, cost * 0.3)
                                                globalself.db.write_new_transactions(ctx.author, f"Покупка роли {role.mention}", -cost)
                                                globalself.db.write_new_transactions(seller, "Продажа личной роли", cost * 0.3)
                                                globalself.db.give_purchase(role)

                                                embed = discord.Embed(title=f'Магазин личных ролей', description=f"**Вы** успешно **купили** роль {role.mention} у {seller.mention}", color=discord.Colour.green())
                                                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                await message.edit(embed=embed, view=View())

                                        @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
                                        async def button_callback_no(self, button, interaction: discord.Interaction):
                                            await interaction.response.defer()

                                            if ctx.author.id == interaction.user.id:
                                                await message.delete()

                                    embed = discord.Embed(title=f'Магазин личных ролей', description=f"**Вы** уверены что хотите **купить** роль {role.mention} за **{cost}** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                    message = await interaction.followup.send(embed=embed, view=ViewVerify(), ephemeral=True)
                                else:
                                    embed = discord.Embed(title='Упс...', description="У вас недостаточно средств! Для начала пополните свой баланс.", color=0x2f3136)
                                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                    await interaction.followup.send(embed=embed, view=View(), ephemeral=True)

                    self.buy_buttons[i].callback = button_callback_buy_role

                    self.add_item(self.buy_buttons[i])

            @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple, row=1)
            async def button_callback_back(self, button, interaction: discord.Interaction):
                await interaction.response.defer()

                if ctx.author.id == interaction.user.id:
                    self.page -= 1

                    await self.update_embed(interaction)

            @discord.ui.button(label="🗑️", style=discord.ButtonStyle.red, row=1)
            async def button_callback_delete(self, button, interaction: discord.Interaction):
                await interaction.response.defer()

                if ctx.author.id == interaction.user.id:
                    await ctx.delete()

            @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple, row=1)
            async def button_callback_next(self, button, interaction: discord.Interaction):
                await interaction.response.defer()

                if ctx.author.id == interaction.user.id:
                    self.page += 1

                    await self.update_embed(interaction)

            async def update_embed(self, interaction: discord.Interaction):
                self.page = max(min(self.page, self.total_pages), 1)
                embed = await globalself.make_page_shop(self.page, self.total_pages, roles)
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await interaction.message.edit(embed=embed, view=ButtonsView(self.page, self.total_pages))

        embed = await self.make_page_shop(page, total_pages, roles)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

        await ctx.followup.send(embed=embed, view=ButtonsView(page, total_pages))