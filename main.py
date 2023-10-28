from app.youtube_data import YouTubeData

video_id = "oZIlIludZto"

dataset = YouTubeData(video_id)

print(dataset.get_video_info())
