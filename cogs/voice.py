import discord
from discord import app_commands
from discord.ext import commands  # Added import
import logging
from .utils import check_empty_channel_loop

logger = logging.getLogger('music_bot')

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="music", description="Join a voice channel to play music")
    @app_commands.describe(channel_id="ID of the voice channel")
    async def music(self, interaction: discord.Interaction, channel_id: str):
        try:
            channel_id = int(channel_id)
            channel = self.bot.get_channel(channel_id)
            if not channel or not isinstance(channel, discord.VoiceChannel):
                await interaction.response.send_message("Invalid voice channel ID!", ephemeral=True)
                return

            if interaction.user.voice is None or interaction.user.voice.channel.id != channel_id:
                await interaction.response.send_message("You must be in the channel to connect me!", ephemeral=True)
                return

            guild_id = interaction.guild.id
            data = self.bot.guild_data[guild_id]

            if data['voice_client'] and data['voice_client'].is_connected():
                current_channel = data['voice_client'].channel
                if current_channel.id != channel_id and data['permanent_channel'] != current_channel.id:
                    await interaction.response.send_message(f"I'm already in the channel {current_channel.name}! Disconnect me first using /leave.", ephemeral=True)
                    return

            if data['voice_client'] and data['voice_client'].is_connected():
                await data['voice_client'].move_to(channel)
            else:
                data['voice_client'] = await channel.connect()
                if not data['permanent_channel']:
                    if data['check_empty_task']:
                        data['check_empty_task'].cancel()
                    data['check_empty_task'] = self.bot.loop.create_task(check_empty_channel_loop(guild_id, self.bot))

            logger.info(f"Connected to voice channel: {channel.name}")
            await interaction.response.send_message(f"Connected to {channel.name}!")
        except Exception as e:
            logger.error(f"Error while connecting to the channel: {e}")
            await interaction.response.send_message(f"Error while connecting to the channel: {e}", ephemeral=True)

    @app_commands.command(name="music_permanent", description="Set a channel where the bot will stay 24/7 (admin only)")
    @app_commands.describe(channel_id="ID of the voice channel")
    async def music_permanent(self, interaction: discord.Interaction, channel_id: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("This command can only be used by an admin!", ephemeral=True)
            return

        try:
            channel_id = int(channel_id)
            channel = self.bot.get_channel(channel_id)
            if not channel or not isinstance(channel, discord.VoiceChannel):
                await interaction.response.send_message("Invalid voice channel ID!", ephemeral=True)
                return

            guild_id = interaction.guild.id
            data = self.bot.guild_data[guild_id]

            data['permanent_channel'] = channel_id
            logger.info(f"Permanent channel set to: {channel.name}")

            if data['voice_client'] and data['voice_client'].is_connected():
                await data['voice_client'].move_to(channel)
            else:
                data['voice_client'] = await channel.connect()

            if data['check_empty_task']:
                data['check_empty_task'].cancel()
                data['check_empty_task'] = None

            await interaction.response.send_message(f"Permanent channel set to {channel.name}! The bot will stay here 24/7.")
        except Exception as e:
            logger.error(f"Error while setting the permanent channel: {e}")
            await interaction.response.send_message(f"Error while setting the permanent channel: {e}", ephemeral=True)

    @app_commands.command(name="leave", description="Leave the voice channel")
    async def leave(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        data = self.bot.guild_data[guild_id]

        if not data['voice_client']:
            await interaction.response.send_message("I'm not in a voice channel!")
            return

        if data['permanent_channel']:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("This channel is permanent! Only an admin can disconnect me.", ephemeral=True)
                return

        data['queue'].clear()
        data['current_song'] = None
        if data['voice_client'].is_playing():
            data['voice_client'].stop()
        await data['voice_client'].disconnect()
        data['voice_client'] = None
        data['permanent_channel'] = None
        if data['check_empty_task']:
            data['check_empty_task'].cancel()
            data['check_empty_task'] = None
        logger.info("Left the voice channel")
        await interaction.response.send_message("I have left the voice channel!")

async def setup(bot):
    await bot.add_cog(Voice(bot))