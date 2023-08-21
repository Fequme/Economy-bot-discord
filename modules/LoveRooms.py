import discord
from discord.ext import commands
from discord.ui import View

import json

from modules.Logger import *
from modules.Database import Database

class LoveRooms(commands.Cog, View):

    def __init__(self, bot):

        self.bot = bot
        self.db = Database()

        try:
            with open("./assets/settings.json", "r", encoding="utf8") as settings:
                data = json.load(settings)

            self.guild_id = data.get("guild_id")

            self.settings_roles = data.get("roles")
            self.settings_channels = data.get("channels")

            logger.info("Настройки загружены.")

        except:
            logger.error("Не можем загрузить настройки :(")
            exit()

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = discord.utils.get(self.bot.guilds, id=self.guild_id)
            
        self.entry_love_room = discord.utils.get(self.guild.voice_channels, id=self.settings_channels.get("entry_love_room"))
        self.love_category = discord.utils.get(self.guild.channels, id=self.settings_channels.get("love_category"))
        
        logger.info("LoveRooms - start")

        await self.check_love_rooms()

    # Love rooms
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Проверяем подключен ли пользователь к комнате "ВХОДА"
        if(before.channel != self.entry_love_room and after.channel == self.entry_love_room):

            # Если вторая половинка уже создала комнату
            loveRoom_data = self.db.get_data_loveRoom(member)

            if loveRoom_data['id'] != 0:
                channel = discord.utils.get(self.guild.channels, id=loveRoom_data['id'])
                await member.edit(voice_channel=channel)

                return
            
            # Создаём новую приватную комнату
            
            bitrates = [96000, 128000, 256000, 384000]
            bitrate = bitrates[self.guild.premium_tier]

            data = self.db.get_info_marriege(member)

            partner_1 = self.bot.get_user(data[1])
            partner_2 = self.bot.get_user(data[2])

            overwrites = {
                self.guild.default_role : discord.PermissionOverwrite(connect=False, view_channel=True),
                partner_1 : discord.PermissionOverwrite(connect=True, view_channel=True),
                partner_2 : discord.PermissionOverwrite(connect=True, view_channel=True),
            }

            custom_name = self.db.get_data_loveRoom(member)['name']

            if custom_name != 0 and custom_name != None:
                channel_name = f"{custom_name}"
            else:
                channel_name = f"{partner_1.display_name} 💕 {partner_2.display_name}"
            channel = await self.guild.create_voice_channel(channel_name, bitrate=bitrate, overwrites=overwrites, category=self.love_category)

            self.db.write_data_loveRoom(member, 'id', channel.id)

            # Перемещаем чела в его комнату
            await member.edit(voice_channel=channel)

            logger.info(f"Создана любовная комната {channel.name}")

    async def check_love_rooms(self):

        while True:
            channels_in_category = self.love_category.voice_channels
            for channel in channels_in_category:

                if channel != self.entry_love_room and not channel.members:
                    self.db.update_data_loveRoom(channel.id)
                    await channel.delete(reason="Пустой канал.")
                    
                    logger.info(f"Удалён пустой канал {channel.name}")
    
            await asyncio.sleep(5)