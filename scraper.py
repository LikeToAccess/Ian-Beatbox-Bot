from threading import Thread
import youtube_dl
import stream


class Scraper:
	def __init__(self):
		self.ydl = youtube_dl.YoutubeDL({"outtmpl": "%(id)s.%(ext)s"})

	def get_metadata(self, url):  # url should be youtube link
		with self.ydl:
			result = self.ydl.extract_info(
				url,
				download=False # We just want to extract the info
			)

		if "entries" in result:
			# Can be a playlist or a list of videos
			video = result["entries"][0]
		else:
			# Just a video
			video = result

		# print(video)
		for result in video["formats"]:
			if result["fps"] is None:
				metadata = result
		# print(metadata)
		return metadata

	def download(self, url, filename):
		# Ensures that the link will be the direct download
		# url = self.get_metadata(url)["url"] if (not "googlevideo.com" in url and) else url
		threaded_download = Thread(target=stream.get_stream, args=(url, filename))
		threaded_download.start()


if __name__ == "__main__":
	scraper = Scraper()
	url = "https://youtu.be/cB4dYfFgaME"
	url = scraper.get_metadata(url)["url"] if "googlevideo.com" not in url else url
	print(url)
	scraper.download(url, filename="song.m4a")


# formats = [
# 	{
# 		"asr": 48000,
# 		"filesize": 59570,
# 		"format_id": "249",
# 		"tbr": 48.425,
# 		"ext": "webm",
# 		"acodec": "opus",
# 		"abr": 48.425,
# 		"container": "webm_dash",
# 		"format": "249 - audio only (tiny)"
# 	},
# 	{
# 		"asr": 48000,
# 		"filesize": 77899,
# 		"format_id": "250",
# 		"tbr": 63.326,
# 		"ext": "webm",
# 		"acodec": "opus",
# 		"abr": 63.326,
# 		"container": "webm_dash",
# 		"format": "250 - audio only (tiny)"
# 	},
# 	{
# 		"asr": 48000,
# 		"filesize": 142292,
# 		"format_id": "251",
# 		"tbr": 115.672,
# 		"ext": "webm",
# 		"acodec": "opus",
# 		"abr": 115.672,
# 		"container": "webm_dash",
# 		"format": "251 - audio only (tiny)"
# 	},
# 	{
# 		"asr": 44100,
# 		"filesize": 157753,
# 		"format_id": "140",
# 		"tbr": 127.58,
# 		"ext": "m4a",
# 		"acodec": "mp4a.40.2",
# 		"abr": 127.58,
# 		"container": "m4a_dash",
# 		"format": "140 - audio only (tiny)"
# 	}
# ]
