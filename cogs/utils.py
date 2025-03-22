import discord
import yt_dlp
import asyncio
import logging

logger = logging.getLogger('music_bot')

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0'
    }
}

def search_youtube(query):
    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
        try:
            if not query.startswith('http'):
                query = f"ytsearch:{query}"
            info = ytdl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            logger.info(f"Found stream URL: {info['url']}")
            return info['url'], info['title']
        except Exception as e:
            logger.error(f"Error while searching for a song: {e}")
            return None, None

class YTDLAudioSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')

    @classmethod
    async def from_url(cls, url, *, loop=None, volume=0.5):
        loop = loop or asyncio.get_event_loop()
        ytdl = yt_dlp.YoutubeDL(ytdl_opts)
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        stream_url = data['url']
        logger.info(f"Streaming from URL: {stream_url}")
        try:
            source = discord.FFmpegPCMAudio(stream_url, options='-vn')
        except Exception as e:
            logger.error(f"Error while creating FFmpeg source: {e}")
            raise
        return cls(source, data=data, volume=volume)

async def check_empty_channel(guild_id, bot):
    data = bot.guild_data[guild_id]
    voice_client = data['voice_client']
    
    if data['permanent_channel']:
        return

    if voice_client and voice_client.is_connected():
        channel = voice_client.channel
        if len([member for member in channel.members if not member.bot]) == 0:
            logger.info(f"Channel {channel.name} is empty, disconnecting the bot")
            data['queue'].clear()
            data['current_song'] = None
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            data['voice_client'] = None
            if data['check_empty_task']:
                data['check_empty_task'].cancel()
                data['check_empty_task'] = None
            await channel.guild.system_channel.send("I disconnected because the channel was empty!")

async def check_empty_channel_loop(guild_id, bot):
    while True:
        await check_empty_channel(guild_id, bot)
        await asyncio.sleep(60)