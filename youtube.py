import discord
import youtube_dl
from discord.ext import commands
import os
import asyncio
import media

# Suppress noise about console usage from errors
# youtube_dl.utils.bug_reports_message = lambda: ''


bot = commands.Bot(command_prefix=
	[
		"-",
	],
	help_command=None, case_insensitive=True)

ytdl_opts = {
	"format": "bestaudio/best",
	# "quiet": True,
	# "no_warnings": True,
	"default_search": "auto",
	"source_address": "0.0.0.0",
	"postprocessors": [{
		"key": "FFmpegExtractAudio",
		"preferredcodec": "mp3",
		"preferredquality": "96",
	}],
}

ffmpeg_options = {
	"options": "-vn"
}

ytdl = youtube_dl.YoutubeDL(ytdl_opts)

async def from_url(url, *, loop=None, stream=False):
	loop = loop or asyncio.get_event_loop()
	data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

	if "entries" in data:
		# take first item from a playlist
		data = data["entries"][0]

	filename = data["url"] if stream else ytdl.prepare_filename(data)
	return discord.FFmpegPCMAudio(filename, **ffmpeg_options), data

@bot.command()
async def volume(ctx, volume: int):
	"""Changes the player's volume"""
	if ctx.voice_client is None:
		return await ctx.send("Not connected to a voice channel.")

	ctx.voice_client.source.volume = volume / 100
	await ctx.send(f"Changed volume to {volume}%")


#youtube_dl directly streaming music
@bot.command(pass_context=True)
async def stream(ctx, *url):
	url = " ".join(url) if len(url[0]) > 1 else url
	print(url)
	"""Streams from a url (same as yt, but doesn't predownload)"""
	async with ctx.typing():
		player = await from_url(url, loop=bot.loop, stream=True)
		ctx.voice_client.play(player[0], after=lambda e: print("Player error: %s" % e) if e else None)
	title = player[1]["title"]
	await ctx.send(f"Now playing: {title}")

#end
def endSong(guild, path):
	os.remove(path)

@commands.command()
async def stop(self, ctx):
    """Stops and disconnects the bot from voice"""

    await ctx.voice_client.disconnect()

@bot.command(pass_context=True)
async def play(ctx, url):
	if not ctx.message.author.voice:
		await ctx.send("you are not connected to a voice channel")
		return
	else:
		channel = ctx.message.author.voice.channel
	voice_client = await channel.connect()
	guild = ctx.message.guild
	with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
		file = ydl.extract_info(url, download=False)
		path = str(file["title"]) + "-" + str(file["id"] + ".mp3")
	voice_client.play(discord.FFmpegPCMAudio(path), after=lambda x: endSong(guild, path))
	voice_client.source = discord.PCMVolumeTransformer(voice_client.source, 1)
	await ctx.send(f"**Music: **{url}")

'''
Discord Commands
'''
@bot.command()
async def join(ctx):
	# await ctx.message.delete()  # Deletes the invocation message
	if ctx.author.voice and ctx.author.voice.channel:
		voice_channel = ctx.author.voice.channel
		# voice_channel = discord.utils.get(ctx.guild.voice_channels, name="▶voice-chat")
		await voice_channel.connect()  # Connects to the voice channel
		print(f"Joined \"{voice_channel.name}\".")
	else:
		await ctx.send("You are not connected to a voice channel!")
		return

@bot.command()
async def leave(ctx):
	# await ctx.message.delete()  # Deletes the invocation message
	voice = discord.utils.get(bot.voice_clients)
	await voice.disconnect()
	# print("Bye-bye.")
	await ctx.send("Bye-bye.")  # sends message to the channel that the user typed in


@play.before_invoke
@stream.before_invoke
async def ensure_voice(ctx):
	if ctx.voice_client is None:
		if ctx.author.voice:
			await ctx.author.voice.channel.connect()
		else:
			await ctx.send("You are not connected to a voice channel.")
			raise commands.CommandError("Author not connected to a voice channel.")
	elif ctx.voice_client.is_playing():
		ctx.voice_client.stop()


if __name__ == "__main__":
	credentials = media.read_file("credentials.md", filter=True)
	token = credentials[0]
	bot.run(token)

# async def run():
# 	while voice_client.is_playing():
# 		await asyncio.sleep(1)
# 	else:
# 		await voice_client.disconnect()
# 		print("Disconnected")
