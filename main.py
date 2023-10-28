from app.youtube_data import YouTubeData

url = "https://www.youtube.com/watch?v=hXdLpnvbixs"

dataset = YouTubeData(url)

print(dataset.get_video_info())
print(dataset.get_comments())
