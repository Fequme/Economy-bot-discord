import discord
from discord import Option
from discord.ext import commands
from discord.ui import View

import json

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

class Marry(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

        try:
            with open("./assets/settings.json", "r", encoding="utf8") as settings:
                data = json.load(settings)

            self.guild_id = data.get("guild_id")

            self.settings_roles = data.get("roles")
            self.settings_prices = data.get("prices")

            logger.info("Настройки загружены.")

        except:
            logger.error("Не можем загрузить настройки :(")
            exit()

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = discord.utils.get(self.bot.guilds, id=self.guild_id)

        self.marry_role = discord.utils.get(self.guild.roles, id=self.settings_roles.get("marry_role"))
        self.male = discord.utils.get(self.guild.roles, id=self.settings_roles.get("gender_male"))
        self.female = discord.utils.get(self.guild.roles, id=self.settings_roles.get("gender_female"))

        logger.info("/marry - start")

    # Marry
    @commands.slash_command(name="marry", description="Заключить брак.", guild_ids=[guild_id_cmd])
    async def marry(
        self,
        ctx: discord.ApplicationContext, 
        member: Option(discord.Member, name="пользователь", description="Выберите пуську.")
    ):
        globalself = self

        cost_marry_standart = self.settings_prices.get("marry_create_standart")
        cost_marry_nonstandart = self.settings_prices.get("marry_create_nonstandart")

        cost_marry = 0

        if self.male in ctx.author.roles and self.female in member.roles:
            cost_marry = cost_marry_standart
        elif self.female in ctx.author.roles and self.male in member.roles:
            cost_marry = cost_marry_standart
        elif self.male in ctx.author.roles and self.male in member.roles:
            cost_marry = cost_marry_nonstandart
        elif self.female in ctx.author.roles and self.female in member.roles:
            cost_marry = cost_marry_nonstandart

        class ButtonsView(discord.ui.View):
            def __init__(self, *, timeout=120):
                super().__init__(timeout=timeout)

            async def on_timeout(self):
                embed = discord.Embed(title='Упс...', description=f"К сожалению {member.mention} не решился принять ваше предложение. Надеемся что в ближайшее время он одумается и вы сможете заключить полноценный брак.", color=0x2f3136)
                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")

                await ctx.edit(embed=embed, view=View())
            
            @discord.ui.button(label="Принять", custom_id="button_1", style=discord.ButtonStyle.green)
            async def button_callback_yes(self, button, interaction: discord.Interaction):
                await interaction.response.defer()

                if member.id == interaction.user.id:
                    if not globalself.db.is_marry(member.id):
                        globalself.db.write_new_marry(ctx.author, member)

                        await ctx.author.add_roles(globalself.marry_role)
                        await member.add_roles(globalself.marry_role)

                        globalself.db.take_money(ctx.author.id, cost_marry)
                        globalself.db.write_new_transactions(ctx.author, "Создание брака", -cost_marry)
                        globalself.db.write_log_in_history(ctx.author, member, 'creature')

                        logger.info(f"Создан брак между {ctx.author.name} и {member.name}")

                        embed = discord.Embed(title='Горько, горько, горько...', description=f"Сегодня мы празднуем бракосочетание {ctx.author.mention} и {member.mention}. Никогда не предавайте свою любовь, верьте в нее и друг в друга. Уверенно стройте совместные планы и смело их воплощайте. Пусть горько вам будет только сегодня, а каждый день семейной жизни дарит только счастье и успех!", color=0x2f3136)
                        embed.set_image(url="https://media.tenor.com/3OYmSePDSVUAAAAC/black-clover-licht.gif")

                        if member.id == interaction.user.id:
                            await ctx.edit(view=View())
                            await ctx.edit(content="", embed=embed, view=View())
                    else:
                        embed = discord.Embed(title='Создание пары', description="Вы уже состоите в браке! На два фронта не получится...", color=0x2f3136)
                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                        embed.set_thumbnail(url=member.display_avatar.url)
                        await interaction.followup.send(embed=embed, ephemeral=True)
                    self.stop()
                    
            @discord.ui.button(label="Отказаться", custom_id="button_2", style=discord.ButtonStyle.red)
            async def button_callback_no(self, button, interaction: discord.Interaction):
                await interaction.response.defer()
                if member.id == interaction.user.id:
                    if globalself.male in ctx.author.roles and globalself.female in member.roles:
                        embed = discord.Embed(title='У нас плохие новости...', description=f"Уважаемый {ctx.author.mention}, хотим оповестить вас о том что {member.mention} не захотела вступать с вами в брак. Мы искренне надеемся что вы найдёте ту самую милфочку!", color=0x2f3136)
                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    elif globalself.female in ctx.author.roles and globalself.male in member.roles:
                        embed = discord.Embed(title='У нас плохие новости...', description=f"Уважаемая {ctx.author.mention}, хотим оповестить вас о том что {member.mention} не захотел вступать с вами в брак. Мы искренне надеемся что вы найдёте того самого папика!", color=0x2f3136)
                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    elif globalself.male in ctx.author.roles and globalself.male in member.roles:
                        embed = discord.Embed(title='У нас плохие новости...', description=f"Уважаемый {ctx.author.mention}, хотим оповестить вас о том что {member.mention} не захотел вступать с вами в брак. Может наступило время стать натуралом?", color=0x2f3136)
                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    elif globalself.female in ctx.author.roles and globalself.female in member.roles:
                        embed = discord.Embed(title='У нас плохие новости...', description=f"Уважаемая {ctx.author.mention}, хотим оповестить вас о том что {member.mention} не захотела вступать с вами в брак. Может наступило время стать натуралкой?", color=0x2f3136)
                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                    self.stop()
                    await ctx.edit(content="", embed=embed, view=View())

        if member.id != ctx.author.id:
            if not self.db.is_marry(ctx.author.id):
                if not self.db.is_marry(member.id):
                    if self.db.get_balance(ctx.author.id) >= cost_marry:
                        embed = None

                        if self.male in ctx.author.roles and self.female in member.roles:
                            embed = discord.Embed(title='Создание пары', description=f"Дорогая {member.mention}, я предлагаю тебе свою руку и свое сердце. Знай, моя рука всегда будет крепко держать твою и никогда не даст тебе упасть, а мое сердце всегда будет биться, чтобы делать тебя счастливой. Ты согласна?", color=0x2f3136)
                            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                            embed.set_thumbnail(url=ctx.author.display_avatar.url)
                        elif self.female in ctx.author.roles and self.male in member.roles:
                            embed = discord.Embed(title='Создание пары', description=f"Дорогой {member.mention}, все закаты и восходы солнца я хочу встречать с тобой! Так хочется окунуться в твои объятия и почувствовать все твое тепло. Вечность — это долго, но я бы хотела провести ее рядом с тобой. Ты согласен?", color=0x2f3136)
                            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                            embed.set_thumbnail(url=ctx.author.display_avatar.url)
                        elif self.male in ctx.author.roles and self.male in member.roles:
                            embed = discord.Embed(title='Создание пары', description=f"Дорогой {member.mention}, ты очень много для меня значишь, и я очень ценю, что ты появился в моей жизни. Я всё больше и больше хочу проводить времени рядом с тобой. Ты согласен?", color=0x2f3136)
                            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                            embed.set_thumbnail(url=ctx.author.display_avatar.url)
                        elif self.female in ctx.author.roles and self.female in member.roles:
                            embed = discord.Embed(title='Создание пары', description=f"Девочка моя {member.mention}, я испытываю к тебе невероятно большое и воистину прекрасное чувство – это любовь. Солнышко, я хочу чтобы мы всегда были вместе. Ты согласна?", color=0x2f3136)
                            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                        await ctx.respond(member.mention, embed=embed, view=ButtonsView())
                    else:
                        embed = discord.Embed(title='Создание пары', description=f"На вашем счету недостаточно средств! Для создание пары вам нужно ещё **{cost_marry - globalself.db.get_balance(ctx.author.id)}** <:coin:1074339571992641616>", color=0x2f3136)
                        embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                        embed.set_thumbnail(url=ctx.author.display_avatar.url)

                        await ctx.respond(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(title='Создание пары', description="Этот человек уже состоит в браке! Нам очень жаль...", color=0x2f3136)
                    embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)

                    await ctx.respond(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title='Создание пары', description="Вы уже состоите в браке! На два фронта не получится...", color=0x2f3136)
                embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title='Создание пары', description="Вы не можете создать брак с самим собой. Заходите когда найдёте пару...", color=0x2f3136)
            embed.set_image(url="https://cdn.discordapp.com/attachments/992883178362642453/1029462389130792970/-1.png")
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            await ctx.respond(embed=embed, ephemeral=True)