import discord
from discord.ext import commands, tasks
from discord.ui import View

from modules.Logger import *
from modules.Database import Database
from modules.Utils import Utils

guild_id = Utils.get_guild_id()

class Economy(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()
        self.utils = Utils()

        self.messages.start()

   # Bot ready
    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(guild_id)
        members = guild.members

        for member in members:
            self.db.write_new_user(member)
            self.db.write_new_user_tracker(member)
            self.db.log_write_new_user(member)
            self.db.set_null_dates(member)

    # New member join -> write in db
    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.db.write_new_user(member)
        self.db.write_new_user_tracker(member)
        self.db.log_write_new_user(member)

    # Message counter
    @tasks.loop(seconds=30)
    async def messages(self):
        self.db.save_message_count(self.utils.get_messages())

    @commands.Cog.listener()
    async def on_message(self, ctx):
        author = ctx.author.id

        self.utils.write_message(author)
        
        await self.bot.process_commands(ctx)
    
    @commands.Cog.listener()
    async def on_application_command_error(
        self, ctx: commands.Context, error: discord.ext.commands.CommandError
    ):
        if isinstance(error, commands.NotOwner):
            await ctx.respond("гг")
        else:
            raise error