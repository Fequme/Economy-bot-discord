from asyncio.tasks import sleep
import asyncio
from logging import LoggerAdapter, exception

import discord
from discord.ext import commands
from discord.utils import *

from datetime import datetime

from modules.Logger import *
from modules.Database import Database

from modules.Utils import Utils

guild_id_cmd = Utils.get_guild_id()

class Tracker(commands.Cog):
    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_ready(self):

        self.guild = discord.utils.get(self.bot.guilds, id=guild_id_cmd)

        logger.info("Tracker - start")

    def leave_channel(self, member):
        self.db.user_set_action_channel(member, "left")

        row = self.db.get_data(member)

        if int(row[0]) != 0:
            join_time = datetime.fromtimestamp(int(row[0]))
            left_time = datetime.fromtimestamp(int(row[1]))

            new_time = left_time - join_time

            hours, remainder = divmod(new_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
                    
            total_hours = hours + (new_time.days * 24)
            total_hours += row[2]

            total_minutes = minutes + row[3]

            if total_minutes >= 60:
                total_minutes-=60
                total_hours+=1
                        
            self.db.update_data(member, 'default', abs(total_hours), abs(total_minutes))
            
        self.db.set_null_dates(member)

    def leave_loveRoom_channel(self, member):
        if int(self.db.get_data_loveRoom(member)['joined_at']) != 0:
            join_time = datetime.fromtimestamp(int(self.db.get_data_loveRoom(member)['joined_at']))
            left_time = datetime.fromtimestamp(int(datetime.timestamp(datetime.now())))

            new_time = left_time - join_time

            hours, remainder = divmod(new_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
                                
            total_hours = hours + (new_time.days * 24)
            total_hours += self.db.get_data_loveRoom(member)['total_hours']

            total_minutes = minutes + self.db.get_data_loveRoom(member)['total_minutes']

            if total_minutes >= 60:
                total_minutes-=60
                total_hours+=1
                                    
            self.db.update_data(member, 'love', abs(total_hours), abs(total_minutes))

        self.db.write_data_loveRoom(member, 'joined_at', 0)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # user joined channel
        if before.channel is None and after.channel is not None:
            self.db.user_set_action_channel(member, "join")

            if self.db.is_marry(member.id):
                if after.channel.id == self.db.get_data_loveRoom(member)['id']:
                    verify = False

                    data = self.db.get_info_marriege(member)
                    
                    partner_1 = self.guild.get_member(data[1])
                    partner_2 = self.guild.get_member(data[2])

                    for member_in in after.channel.members:
                        if partner_1.id == member.id:
                            if member_in.id == partner_2.id:
                                verify = True
                        elif partner_2.id == member.id:
                            if member_in.id == partner_1.id:
                                verify = True
                    if verify:
                        self.db.write_data_loveRoom(member, 'joined_at', int(datetime.timestamp(datetime.now())))

            logger.info(f"[{datetime.now()}] {member.name} зашёл в {after.channel.name}")

        # user left channel
        elif before.channel is not None and after.channel is None:
            self.leave_channel(member)

            if self.db.is_marry(member.id):
                if before.channel.id == self.db.get_data_loveRoom(member)['id']:
                    self.leave_loveRoom_channel(member)

            logger.info(f"[{datetime.now()}] {member.name} вышел с {before.channel.name}")

        # user switched channel
        elif before.channel is not None and after.channel is not None:
            logger.info(f"[{datetime.now()}] {member.name} поменял канал с {before.channel.name} на {after.channel.name}")

            if self.db.is_marry(member.id):
                if after.channel.id == self.db.get_data_loveRoom(member)['id']:
                    verify = False

                    data = self.db.get_info_marriege(member)
                    
                    partner_1 = self.guild.get_member(data[1])
                    partner_2 = self.guild.get_member(data[2])

                    for member_in in after.channel.members:
                        if partner_1.id == member.id:
                            if member_in.id == partner_2.id:
                                verify = True
                        elif partner_2.id == member.id:
                            if member_in.id == partner_1.id:
                                verify = True

                    if verify:
                        self.db.write_data_loveRoom(member, 'joined_at', int(datetime.timestamp(datetime.now())))
                elif after.channel.id != self.db.get_data_loveRoom(member)['id']:
                    self.leave_loveRoom_channel(member)