# -*- coding: utf-8 -*-
# filename          : bot.py
# description       : Main bot stuff
# author            : LikeToAccess
# email             : liketoaccess@protonmail.com
# date              : 06-20-2021
# version           : v1.0
# usage             : python bot.py
# notes             :
# license           : MIT
# py version        : 3.8.2 (must run on 3.6 or higher)
#==============================================================================
import discord
from discord.errors import *
from discord.ext import commands#, tasks
# import youtube_dl
import media
import scraper


credentials = media.read_file("credentials.md", filter=True)
token = credentials[0]
allowed_users = credentials[1:]
scraper = scraper.Scraper()

# channel_id = {
# 	"commands": 776367990560129066,
# 	"log": 776354053222826004,
# 	"spam": 780948981299150888,
# 	"voice-chat": 841891161920241705,
# }

channel_id = {
	"spam": 547119582565892131,
	"voice-chat": 790742242376941599
}

# ydl_opts = {
#     "format": "bestaudio/best",
#     "postprocessors": [{
#         "key": "FFmpegExtractAudio",
#         "preferredcodec": "mp3",
#         "preferredquality": "96",
#     }],
# }

bot = commands.Bot(command_prefix=
	[
		"-",
	],
	help_command=None, case_insensitive=True)



'''
Discord Functions
'''
@bot.event
async def on_ready():
	media.remove_file("song.m4a")
	print(f"{bot.user} successfuly connected!")
	await set_status("cool music 24/7!", discord.Status.online)


'''
Discord Commands
'''
@bot.command()
async def join(ctx, auto_rejoin=True):
	# await ctx.message.delete()  # Deletes the invocation message
	if ctx.author.voice and ctx.author.voice.channel:
		voice_channel = ctx.author.voice.channel
		user_is_currently_in_voice_channel = True
	else:
		voice_channel = bot.get_channel(channel_id["voice-chat"])
		user_is_currently_in_voice_channel = False
	feedback = await join_status_feedback(voice_channel, user_is_currently_in_voice_channel, auto_rejoin=auto_rejoin)
	await send(feedback, silent=False)

@bot.command(aliases=["disconnect", "bye", "exit"])
async def leave(ctx):
	# await ctx.message.delete()  # Deletes the invocation message
	voice = discord.utils.get(bot.voice_clients)
	try:
		await voice.disconnect()
		print("Left VC.")
		await send("Bye-bye.")
	except AttributeError:
		await send("I am not in a VC.")

@bot.command(aliases=["p", "add"])
async def play(ctx, *song_name):
	await join(ctx, auto_rejoin=False)
	song_name = " ".join(song_name)
	filename = "song.m4a"
	if song_name.split("://", maxsplit=1)[0] in ["http", "https"]:
		await send("Playing song via direct link...", silent=False)
		print(song_name)
		url = scraper.get_metadata(song_name)["url"]
		print(f"DEBUG: {url}")
		# scraper.download(url, filename=filename)
		await play_audio_file(filename)
	else:
		await send("Searching for matches...", silent=False)

	# voice = discord.utils.get(bot.voice_clients)
	# voice.play(discord.FFmpegPCMAudio("sample.mp3"), after=lambda e: print('done', e))


# TODO: vvv Not working vvv
# @bot.command()
# async def volume(ctx, volume: int):
# 	try:
# 		ctx.voice_client.source.volume = volume / 100
# 		await send(f"Changed volume to {volume}%.")
# 	except AttributeError:
# 		await send("I am not in a VC.")

@bot.command()
async def test(ctx):
	await join(ctx, auto_rejoin=False)
	await send("Playing test tones...", silent=False)
	await play_audio_file("sample.mp3")

'''
Other Functions
'''
async def join_status_feedback(
		voice_channel,
		user_is_currently_in_voice_channel,
		auto_rejoin=True):
	bot_was_reconnected = await join_channel(voice_channel, auto_rejoin=auto_rejoin)
	if bot_was_reconnected:
		join_status = "Joined"
	else:
		join_status = "Rejoined"
	if auto_rejoin or join_status == "Joined":
		if user_is_currently_in_voice_channel:
			message = f"{join_status} in \"{voice_channel.name}\"."
		else:
			message = f"You are not connected to a voice channel!\n{join_status} default channel \"{voice_channel.name}\""
		return message
		# await send(f"{join_status} in \"{voice_channel.name}\".", silent=False)
		# await send(f"You are not connected to a voice channel!\n{join_status} default channel \"{voice_channel.name}\"")
	return False

async def play_audio_file(filename, after=None):
	voice = discord.utils.get(bot.voice_clients)
	voice.play(discord.FFmpegPCMAudio(filename), after=after)  # TODO: 

async def set_status(activity, status=discord.Status.online):
	await bot.change_presence(status=status, activity=discord.Game(activity))

async def join_channel(target_voice_channel, auto_rejoin=True):
	try:
		await target_voice_channel.connect()  # Connects to the voice channel
		return True  # bot connected for the first time.
	except ClientException:  # bot is already in the channel
		if auto_rejoin:
			current_voice = discord.utils.get(bot.voice_clients)
			await current_voice.disconnect()
			await target_voice_channel.connect()
			return False  # bot was DC'd then reconnected.
	return False  # bot is already in a channel

async def send(msg, channel="spam", silent=True):
	if not msg:
		return
	channel = bot.get_channel(channel_id[channel])
	await channel.send(msg)
	if not silent: print(msg)

def run():
	return bot.run(token)


if __name__ == "__main__":
	run()
