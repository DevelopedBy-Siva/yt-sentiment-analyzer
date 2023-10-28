from googleapiclient.discovery import build
import os

API_KEY = os.environ.get("GOOGLE_API_KEY")


class VideoNotFoundError(Exception):
    pass


class YouTubeData:

    def __init__(self, url):
        self.youtube = build('youtube', 'v3', developerKey=API_KEY)
        self.video_id = url

    def get_video_info(self):
        video_info = self.youtube.videos().list(
            part='snippet,statistics',
            id=self.video_id
        ).execute()

        # throw VideoNotFoundError when video doesn't exist
        if 'items' not in video_info or not video_info['items']:
            raise VideoNotFoundError("Video not found.")

        # extract video details
        snippet = video_info['items'][0]['snippet']
        statistics = video_info['items'][0]['statistics']

        # get video information
        video_name = snippet.get('title', 'No Title')
        channel_title = snippet.get('channelTitle', 'Unknown Channel')
        like_count = int(statistics.get('likeCount', 0))
        dislike_count = int(statistics.get('dislikeCount', 0))

        return {
            'video_id': self.video_id,
            'video_name': video_name,
            'channel_title': channel_title,
            'likes': like_count,
            'dislikes': dislike_count
        }
