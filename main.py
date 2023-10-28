from app.youtube_data import YouTubeData

url = "https://www.youtube.com/watch?v=oZIlIludZto"

dataset = YouTubeData(url)

print(dataset.get_video_info())
