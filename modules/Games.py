import discord
from discord import Option
from discord.ext import commands
from discord.ui import View

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

import random

determine_flip = ['Орёл', 'Решка']

class Games(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()
        self.utils = Utils()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("/games - start")

    @commands.slash_command(name="games", description="Игры на валюту.", guild_ids=[guild_id_cmd])
    async def games(
        self,
        ctx: discord.ApplicationContext,
        game: Option(str, "Выберите игру", name="игра", choices = ['Орёл или Решка', 'Казино'], required=True),
        amount: Option(int, name="ставка", description="Ставка для игры.", min_value = 50, max_value = 999999, required = True)
    ):
        globalself = self

        if globalself.utils.is_active_game(ctx.author.id):
            embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"У вас уже **есть** активная игра!", color=discord.Color.red())
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            await ctx.respond(embed=embed, ephemeral=True)
        else:
            if globalself.db.get_balance(ctx.author.id) >= amount:
                # Орёл или Решка
                if game == "Орёл или Решка":
                    globalself.utils.start_game(ctx.author.id)

                    embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"{ctx.author.mention}, выберите сторону на которую **хотите** поставить ваши **{amount}** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                    class ButtonsView(discord.ui.View):
                        def __init__(self, timeout=120):
                            super().__init__(timeout=timeout)

                        async def on_timeout(self):
                            embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"Время ожидания истекло!", color=discord.Color.red())
                            embed.set_thumbnail(url=ctx.author.display_avatar.url)
                            globalself.utils.stop_game(ctx.author.id)

                            await ctx.edit(embed=embed, view=View())

                        @discord.ui.button(label="Орёл", custom_id="button_orel")
                        async def button_callback_orel(self, button, interaction: discord.Interaction):
                            await interaction.response.defer()

                            if ctx.author.id == interaction.user.id:
                                globalself.db.take_money(interaction.user.id, amount)

                                random_win = random.choice(determine_flip)

                                embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"**Ставка:** {amount} <:1016719860547469323:1098025516059070485>\n**Выбранная сторона**: Орёл", color=0x2f3136)
                                
                                if random_win == 'Орёл':
                                    embed.set_image(url="https://cdn.discordapp.com/attachments/1026111017748533258/1046856198995054632/1.gif")
                                elif random_win == 'Решка':
                                    embed.set_image(url="https://cdn.discordapp.com/attachments/1026111017748533258/1046856199343194213/2.gif")

                                await ctx.edit(embed=embed, view=View())

                                await asyncio.sleep(4)

                                if random_win == 'Орёл':
                                    embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"{interaction.user.mention}, выпал **Орёл**, **Вы** выиграли **{amount}** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                    globalself.db.give_money(ctx.author.id, amount*2)
                                    globalself.db.write_new_transactions(ctx.author, "Победа в игре", amount)

                                    embed.set_footer(text=f"Ваш баланс — {globalself.db.get_balance(ctx.author.id)}")
                                elif random_win == 'Решка':
                                    embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"{interaction.user.mention}, выпала **Решка**, **Вы** проиграли **{amount}** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                    embed.set_footer(text=f"Ваш баланс — {globalself.db.get_balance(ctx.author.id)}")

                                    globalself.db.write_new_transactions(ctx.author, "Поражение в игре", -amount)

                                view = View(timeout=120)

                                button_repeat_game = discord.ui.Button(label="🔄 Сыграть с той же ставкой", custom_id="button_repeat_game", style=discord.ButtonStyle.blurple)

                                async def button_callback_repeat_game(interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        if globalself.utils.is_active_game(ctx.author.id):
                                            embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"У вас уже **есть** активная игра!", color=discord.Color.red())
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                            await ctx.edit(embed=embed, view=View())
                                        else:
                                            globalself.utils.start_game(ctx.author.id)

                                            embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"{ctx.author.mention}, выберите сторону на которую **хотите** поставить ваши **{amount}** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                            await ctx.edit(embed=embed, view=ButtonsView())

                                button_repeat_game.callback = button_callback_repeat_game

                                view.add_item(button_repeat_game)

                                globalself.utils.stop_game(ctx.author.id)

                                await ctx.edit(embed=embed, view=view)
                                self.stop()

                        @discord.ui.button(label="Решка", custom_id="button_reshka")
                        async def button_callback_reshka(self, button, interaction: discord.Interaction):
                            await interaction.response.defer()

                            if ctx.author.id == interaction.user.id:
                                globalself.db.take_money(interaction.user.id, amount)

                                random_win = random.choice(determine_flip)

                                embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"**Ставка:** {amount} <:1016719860547469323:1098025516059070485>\n**Выбранная сторона**: Решка", color=0x2f3136)
                                
                                if random_win == 'Орёл':
                                    embed.set_image(url="https://cdn.discordapp.com/attachments/1026111017748533258/1046856198995054632/1.gif")
                                elif random_win == 'Решка':
                                    embed.set_image(url="https://cdn.discordapp.com/attachments/1026111017748533258/1046856199343194213/2.gif")

                                await ctx.edit(embed=embed, view=View())

                                await asyncio.sleep(4)

                                if random_win == 'Решка':
                                    embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"{interaction.user.mention}, выпала **Решка**, **Вы** выиграли **{amount}** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                    globalself.db.give_money(ctx.author.id, amount*2)
                                    globalself.db.write_new_transactions(ctx.author, "Победа в игре", amount)

                                    embed.set_footer(text=f"Ваш баланс — {globalself.db.get_balance(ctx.author.id)}")
                                elif random_win == 'Орёл':
                                    embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"{interaction.user.mention}, выпал **Орёл**, **Вы** проиграли **{amount}** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                                    embed.set_footer(text=f"Ваш баланс — {globalself.db.get_balance(ctx.author.id)}")

                                    globalself.db.write_new_transactions(ctx.author, "Поражение в игре", -amount)

                                view = View(timeout=120)

                                button_repeat_game = discord.ui.Button(label="🔄 Сыграть с той же ставкой", custom_id="button_repeat_game", style=discord.ButtonStyle.blurple)

                                async def button_callback_repeat_game(interaction: discord.Interaction):
                                    await interaction.response.defer()

                                    if ctx.author.id == interaction.user.id:
                                        if globalself.utils.is_active_game(ctx.author.id):
                                            embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"У вас уже **есть** активная игра!", color=discord.Color.red())
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                            await ctx.edit(embed=embed, view=View())
                                        else:
                                            if globalself.db.get_balance(ctx.author.id) >= amount:
                                                globalself.utils.start_game(ctx.author.id)

                                                embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"{ctx.author.mention}, выберите сторону на которую **хотите** поставить ваши **{amount}** <:1016719860547469323:1098025516059070485>", color=0x2f3136)
                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                await ctx.edit(embed=embed, view=ButtonsView())
                                            else:
                                                embed = discord.Embed(title='Упс...', description="У вас недостаточно средств! Для начала пополните свой баланс.", color=discord.Color.red())
                                                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                                await interaction.followup.send(embed=embed, view=View(), ephemeral=True)  

                                button_repeat_game.callback = button_callback_repeat_game

                                view.add_item(button_repeat_game)

                                globalself.utils.stop_game(ctx.author.id)

                                await ctx.edit(embed=embed, view=view)
                                self.stop()

                    await ctx.respond(embed=embed, view=ButtonsView())
                elif game == "Казино":
                    random_number = random.randint(1, 100)

                    if random_number % 2 == 0:
                        embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', color=0x2f3136)
                        embed.add_field(name="> Ставка", value=f"```{amount}```")
                        embed.add_field(name="> Выпавшее число", value=f"```{random_number}```")
                        embed.add_field(name="> Ты проиграл", value=f"```{amount}```")
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                        globalself.db.take_money(ctx.author.id, amount)
                        globalself.db.write_new_transactions(ctx.author, "Поражение в игре", -amount)

                        embed.set_footer(text=f"Ваш баланс — {globalself.db.get_balance(ctx.author.id)}")
                    else:
                        embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', color=0x2f3136)
                        embed.add_field(name="> Ставка", value=f"```{amount}```")
                        embed.add_field(name="> Выпавшее число", value=f"```{random_number}```")
                        embed.add_field(name="> Ты выиграл", value=f"```{amount}```")
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                        globalself.db.give_money(ctx.author.id, amount)
                        globalself.db.write_new_transactions(ctx.author, "Победа в игре", amount)

                        embed.set_footer(text=f"Ваш баланс — {globalself.db.get_balance(ctx.author.id)}")

                    view = View(timeout=120)

                    button_repeat_game = discord.ui.Button(label="🔄 Сыграть с той же ставкой", custom_id="button_repeat_game", style=discord.ButtonStyle.blurple)

                    async def button_callback_repeat_game(interaction: discord.Interaction):
                        await interaction.response.defer()

                        if ctx.author.id == interaction.user.id:
                            if globalself.utils.is_active_game(ctx.author.id):
                                embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"У вас уже **есть** активная игра!", color=discord.Color.red())
                                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                await ctx.edit(embed=embed, view=View())
                            else:
                                random_number = random.randint(1, 500)

                                if globalself.utils.is_active_game(ctx.author.id):
                                    embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', description=f"У вас уже **есть** активная игра!", color=discord.Color.red())
                                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                    await ctx.edit(embed=embed, view=View())
                                else:
                                    if globalself.db.get_balance(ctx.author.id) >= amount:
                                        if random_number % 2 == 0:
                                            embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', color=0x2f3136)
                                            embed.add_field(name="> Ставка", value=f"```{amount}```")
                                            embed.add_field(name="> Выпавшее число", value=f"```{random_number}```")
                                            embed.add_field(name="> Ты проиграл", value=f"```{amount}```")
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                            globalself.db.take_money(ctx.author.id, amount)
                                            globalself.db.write_new_transactions(ctx.author, "Поражение в игре", -amount)

                                            embed.set_footer(text=f"Ваш баланс — {globalself.db.get_balance(ctx.author.id)}")
                                        else:
                                            embed = discord.Embed(title=f'{game} — {ctx.author.name}#{ctx.author.discriminator}', color=0x2f3136)
                                            embed.add_field(name="> Ставка", value=f"```{amount}```")
                                            embed.add_field(name="> Выпавшее число", value=f"```{random_number}```")
                                            embed.add_field(name="> Ты выиграл", value=f"```{amount}```")
                                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                            globalself.db.give_money(ctx.author.id, amount)
                                            globalself.db.write_new_transactions(ctx.author, "Победа в игре", amount)

                                            embed.set_footer(text=f"Ваш баланс — {globalself.db.get_balance(ctx.author.id)}")

                                        await ctx.edit(embed=embed, view=view)
                                    else:
                                        embed = discord.Embed(title='Упс...', description="У вас недостаточно средств! Для начала пополните свой баланс.", color=discord.Color.red())
                                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                                        await interaction.followup.send(embed=embed, view=View(), ephemeral=True)

                    button_repeat_game.callback = button_callback_repeat_game

                    view.add_item(button_repeat_game)

                    await ctx.respond(embed=embed, view=view)
            else:
                embed = discord.Embed(title='Упс...', description="У вас недостаточно средств! Для начала пополните свой баланс.", color=discord.Color.red())
                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                await ctx.respond(embed=embed, ephemeral=True)