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
import media
import youtube_dl
from discord.ext import commands, tasks


credentials = media.read_file("credentials.md", filter=True)
token = credentials[0]
allowed_users = credentials[1:]

channel_id = {
	"commands": 850041698921873428,
	"mod_commands": 850041698921873428,
	"spam": 592484793065930764,
}

ydl_opts = {
    "format": "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "96",
    }],
}

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
	print(f"{bot.user} successfuly connected!")
	await set_status("cool music 24/7!", discord.Status.online)


'''
Discord Commands
'''
@bot.command()
async def join(ctx):
	await ctx.message.delete()  # Deletes the invocation message
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
	await ctx.message.delete()  # Deletes the invocation message
	voice = discord.utils.get(bot.voice_clients)
	await voice.disconnect()
	# print("Bye-bye.")
	await ctx.send("Bye-bye.")  # sends message to the channel that the user typed in


'''
Other Functions
'''
async def set_status(activity, status=discord.Status.online):
	await bot.change_presence(status=status, activity=discord.Game(activity))

def run():
	return bot.run(token)


if __name__ == "__main__":
	run()
