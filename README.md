# Discord Music Bot

A Discord bot designed to play music in voice channels. The bot supports commands for playing, pausing, skipping, and stopping music, as well as managing the queue and setting the volume. It also includes features for setting a permanent channel and automatically disconnecting when the channel is empty.

## Features

- **Play Music**: Play songs from YouTube by searching or providing a URL.
- **Queue Management**: Add songs to a queue and manage playback.
- **Volume Control**: Adjust the volume of the currently playing song.
- **Permanent Channel**: Set a permanent voice channel where the bot will stay 24/7.
- **Auto-Disconnect**: Automatically disconnect from the voice channel when it's empty.

## Commands

- `/music <channel_id>`: Join a voice channel to play music.
- `/play <song>`: Play a song or add it to the queue.
- `/pause`: Pause the current song.
- `/resume`: Resume the paused song.
- `/skip`: Skip the current song.
- `/stop`: Stop playback and clear the queue.
- `/volume <0-100>`: Set the volume for the bot.
- `/music_permanent <channel_id>`: Set a permanent voice channel for the bot (admin only).
- `/leave`: Disconnect the bot from the voice channel.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/discord-music-bot.git
   cd discord-music-bot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add your Discord bot token:
   ```env
   BOT_TOKEN=your-discord-bot-token
   ```

4. **Run the Bot**:
   ```bash
   python music_bot.py
   ```

## Requirements

- Python 3.8 or higher
- A Discord bot token
- FFmpeg installed and added to your system's PATH

## File Structure

- `music_bot.py`: Main entry point for the bot.
- `cogs/`: Contains the bot's functionality split into modules:
  - `music.py`: Handles music playback and queue management.
  - `voice.py`: Handles voice channel interactions.
  - `utils.py`: Utility functions for the bot.

## Troubleshooting

### FFmpeg Not Found
Ensure FFmpeg is installed and added to your system's PATH. You can download it from [FFmpeg.org](https://ffmpeg.org/).

### Bot Not Responding
- Verify that the bot token in the `.env` file is correct.
- Ensure the bot has the necessary permissions to join voice channels and send messages.

### Commands Not Working
- Make sure the bot is online and has synchronized its commands. Check the console output for any errors during startup.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
