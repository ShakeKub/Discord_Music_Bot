import discord
from discord import app_commands
from discord.ext import commands  # Added import
import logging
from .utils import search_youtube, YTDLAudioSource, check_empty_channel_loop

logger = logging.getLogger('music_bot')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def play_next(self, guild_id):
        data = self.bot.guild_data[guild_id]
        voice_client = data['voice_client']
        
        if not voice_client or not voice_client.is_connected():
            logger.warning("Voice client is not connected")
            return

        if not data['queue']:
            data['current_song'] = None
            logger.info("Queue is empty, stopping playback")
            return

        song_url, song_title, user_id = data['queue'].pop(0)
        data['current_song'] = (song_url, song_title, user_id)

        try:
            source = await YTDLAudioSource.from_url(song_url, loop=self.bot.loop, volume=data['volume'])
            voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(guild_id)))
            logger.info(f"Now playing: {song_title}")
            await self.bot.get_guild(guild_id).get_channel(voice_client.channel.id).send(f"Now playing: {song_title}")
        except Exception as e:
            logger.error(f"Error while playing the song: {e}")
            await self.bot.get_guild(guild_id).get_channel(voice_client.channel.id).send("Error while playing the song.")
            await self.play_next(guild_id)

    @app_commands.command(name="play", description="Play a song or add it to the queue")
    async def play(self, interaction: discord.Interaction, song: str):
        await interaction.response.defer()
        guild_id = interaction.guild.id
        data = self.bot.guild_data[guild_id]

        if not data['voice_client'] or not data['voice_client'].is_connected():
            await interaction.followup.send("I'm not in a voice channel! Use /music to connect me.")
            return

        song_url, song_title = search_youtube(song)
        if not song_url:
            await interaction.followup.send("I couldn't find that song!")
            return

        data['queue'].append((song_url, song_title, interaction.user.id))
        await interaction.followup.send(f"Added to queue: {song_title}")

        if not data['voice_client'].is_playing() and not data['current_song']:
            await self.play_next(guild_id)

    @app_commands.command(name="skip", description="Skip the current song")
    async def skip(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        data = self.bot.guild_data[guild_id]

        if not data['voice_client'] or not data['voice_client'].is_playing():
            await interaction.response.send_message("Nothing is playing!")
            return

        data['voice_client'].stop()
        logger.info("Skipped the current song")
        await interaction.response.send_message("Skipped!")

    @app_commands.command(name="pause", description="Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        data = self.bot.guild_data[guild_id]

        if not data['voice_client'] or not data['voice_client'].is_playing():
            await interaction.response.send_message("Nothing is playing!")
            return

        data['voice_client'].pause()
        logger.info("Playback paused")
        await interaction.response.send_message("Paused!")

    @app_commands.command(name="resume", description="Resume the paused song")
    async def resume(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        data = self.bot.guild_data[guild_id]

        if not data['voice_client'] or not data['voice_client'].is_paused():
            await interaction.response.send_message("Nothing is paused!")
            return

        data['voice_client'].resume()
        logger.info("Playback resumed")
        await interaction.response.send_message("Resumed!")

    @app_commands.command(name="stop", description="Stop playback and clear the queue")
    async def stop(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        data = self.bot.guild_data[guild_id]

        if not data['voice_client']:
            await interaction.response.send_message("I'm not in a voice channel!")
            return

        data['queue'].clear()
        data['current_song'] = None
        if data['voice_client'].is_playing():
            data['voice_client'].stop()
        logger.info("Playback stopped and queue cleared")
        await interaction.response.send_message("Playback stopped and queue cleared!")

    @app_commands.command(name="volume", description="Set the volume (0-100) for your song")
    @app_commands.describe(level="Volume level from 0 to 100")
    async def volume(self, interaction: discord.Interaction, level: int):
        guild_id = interaction.guild.id
        data = self.bot.guild_data[guild_id]

        if not data['voice_client']:
            await interaction.response.send_message("I'm not in a voice channel!")
            return

        if not 0 <= level <= 100:
            await interaction.response.send_message("Volume must be between 0 and 100!")
            return

        if data['current_song']:
            _, _, song_user_id = data['current_song']
            if song_user_id != interaction.user.id:
                await interaction.response.send_message("You can only change the volume for the song you added!", ephemeral=True)
                return

        data['volume'] = level / 100
        if data['voice_client'].source:
            data['voice_client'].source.volume = data['volume']
        logger.info(f"Volume set to {level}%")
        await interaction.response.send_message(f"Volume set to {level}%")

async def setup(bot):
    await bot.add_cog(Music(bot))