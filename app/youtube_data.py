from googleapiclient.discovery import build
import os

API_KEY = os.environ.get("GOOGLE_API_KEY")


class YouTubeData:

    def __init__(self, video_id):
        self.youtube = build('youtube', 'v3', developerKey=API_KEY)
        self.video_id = video_id

    def get_video_info(self):

        video_info = self.youtube.videos().list(
            part='snippet,statistics',
            id=self.video_id
        ).execute()

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

