# -*- coding: utf-8 -*-
# filename          : test.py
# description       :
# author            : Ian Ault
# email             : liketoaccess@protonmail.com
# date              : 02-21-2023
# version           : v1.0
# usage             : python test.py
# notes             :
# license           : MIT
# py version        : 3.11.1
#==============================================================================
import os
# import json
import asyncio
# import requests

import discord
import yt_dlp as youtube_dl

from youtube_search import YoutubeSearch
from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""


ytdl_format_options = {
	"format": "bestaudio/best",
	"outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
	"restrictfilenames": True,
	"noplaylist": True,
	"nocheckcertificate": True,
	"ignoreerrors": False,
	"logtostderr": False,
	"quiet": True,
	"no_warnings": True,
	"default_search": "auto",
	"source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
	"options": "-vn",
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)

		self.data = data

		self.title = data.get("title")
		self.url = data.get("url")

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		if "entries" in data:
			# take first item from a playlist
			data = data["entries"][0]

		filename = data["url"] if stream else ytdl.prepare_filename(data)
		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
	def __init__(self, bot_instance):
		self.bot = bot_instance

	async def start_stream(self, ctx, url: str) -> None:
		"""Starts a stream from a given url

		Args:
			url (str): The url of the stream

		"""
		async with ctx.typing():
			player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
			ctx.voice_client.play(
				player,
				after=lambda e: print(f"Player error: {e}") if e else None
			)

		await ctx.send(f"Now playing: {player.title}")

	async def wait_for_song(self, ctx) -> None:
		"""Waits for the current song to finish

		"""
		while ctx.voice_client.is_playing():
			await asyncio.sleep(1)

	def start_search(self, query) -> str:
		"""Searches for a video and returns the first result

		Args:
			query (str): The search query

		Returns:
			str: The url of the first result

		"""
		# with ctx.typing():
		# with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
		# 	try:
		# 		requests.get(query, timeout=3)
		# 		print(query)
		# 	except requests.exceptions.MissingSchema:
		# 		video = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
		# 	else:
		# 		video = ydl.extract_info(query, download=False)

		# print(video["webpage_url"])
		# await ctx.send(f"Found: {video[0]['webpage_url']}")


		results = YoutubeSearch(query, max_results=1).to_dict()[0]
		video = f"https://youtube.com{results['url_suffix']}"

		return video

	@commands.command(aliases=["s", "find"])
	async def search(self, ctx, *, query) -> None:
		"""Searches for a video and returns the first result

		Args:
			query (str): The search query

		"""
		print(f"DEBUG: {query=}")
		async with ctx.typing():
			video = self.start_search(query)

		await ctx.send(f"Found: {video}")

	@commands.command(alises=["unpause"])
	async def resume(self, ctx) -> None:
		"""Resumes the current song

		"""
		if not ctx.voice_client.is_playing():
			ctx.voice_client.resume()
			await ctx.send("Resumed")
		else:
			await ctx.send("Already playing")

	@commands.command()
	async def pause(self, ctx) -> None:
		"""Pauses the current song

		"""
		if ctx.voice_client.is_playing():
			ctx.voice_client.pause()
			await ctx.send("Paused")
		else:
			ctx.voice_client.resume()
			await ctx.send("Resumed")

	@commands.command()
	async def join(self, ctx, *, channel: discord.VoiceChannel=None) -> None:
		"""Joins a voice channel

		Args:
			channel (discord.VoiceChannel): The voice channel to join

		"""
		if ctx.author.voice and ctx.author.voice.channel and channel is None:
			channel = ctx.author.voice.channel
		if ctx.voice_client is not None:
			return await ctx.voice_client.move_to(channel)

		await channel.connect()
		await ctx.send("Joined")

	@commands.command(aliases=["p", "add"])
	async def play(self, ctx, *, query) -> None:
		"""Plays a file from the local filesystem

		Args:
			query (str): The file path to the audio file or url to stream

		"""
		if query.startswith("http"):
			print("Switching to stream")
			return await self.start_stream(ctx, url=query)

		if not os.path.isfile(query):
			print("Local file not found, switching to stream with search")
			return await self.start_stream(ctx, url=self.start_search(query))

		source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
		ctx.voice_client.play(source, after=lambda e: print(f"Player error: {e}") if e else None)

		await ctx.send(f"Now playing: {query}")
		await self.wait_for_song(ctx)
		print("Song finished")

	@commands.command(aliases=["preload", "preadd", "youtube"])
	async def yt(self, ctx, *, url) -> None:
		"""Plays from a url (almost anything youtube_dl supports)

		Args:
			url (str): The url to play

		"""
		async with ctx.typing():
			player = await YTDLSource.from_url(url, loop=self.bot.loop)
			ctx.voice_client.play(
				player,
				after=lambda e: print(f"Player error: {e}") if e else None
			)

		await ctx.send(f"Now playing: {player.title}")

	@commands.command()
	async def stream(self, ctx, *, url) -> None:
		"""Streams from a url (same as yt, but doesn't predownload)

		Args:
			url (str): The url to stream

		"""
		print(f"DEBUG: {url=}")
		await self.start_stream(ctx, url)
		await self.wait_for_song(ctx)
		print("Song finished")

	@commands.command()
	async def volume(self, ctx, volume: int) -> None:
		"""Changes the player's volume

		Args:
			volume (int): Volume to set player to (0-100)

		"""
		if ctx.voice_client is None:
			return await ctx.send("Not connected to a voice channel.")

		ctx.voice_client.source.volume = volume / 100
		await ctx.send(f"Changed volume to {volume}%")

	@commands.command()
	async def stop(self, ctx) -> None:
		"""Stops and disconnects the bot from voice

		"""
		await ctx.voice_client.disconnect()

	@play.before_invoke
	@yt.before_invoke
	@stream.before_invoke
	async def ensure_voice(self, ctx):
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				await ctx.send("You are not connected to a voice channel.")
				raise commands.CommandError("Author not connected to a voice channel.")
		elif ctx.voice_client.is_playing():
			ctx.voice_client.stop()


async def set_status(activity, status=discord.Status.online):
	await bot.change_presence(status=status, activity=discord.Game(activity))


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
	command_prefix=commands.when_mentioned_or("-"),
	description="Relatively simple music bot example",
	intents=intents,
)


@bot.event
async def on_ready():
	print(f"Logged in as {bot.user} (ID: {bot.user.id})")
	print("------")
	await set_status("cool music 24/7!", discord.Status.online)


async def main():
	async with bot:
		await bot.add_cog(Music(bot))
		await bot.start("TOKEN")


asyncio.run(main())
