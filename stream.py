import requests

def get_stream(url, filename="song.webm"):
	resp = requests.get(url, headers=None, stream=True)
	print(f"HTTP Status: {resp.status_code}")

	with open(filename, "wb") as file:
		for chunk in resp.iter_content(chunk_size=524288):
			if chunk:
				file.write(chunk)
				# print(chunk)
				print("64kB written.")
	print("Download complete!")
