from googleapiclient.discovery import build
import os
import re

API_KEY = os.environ.get("GOOGLE_API_KEY")


class VideoNotFoundError(Exception):
    pass


class InvalidYouTubeURL(Exception):
    pass


def extract_video_id(url):
    pattern = re.compile(
        r'^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*'
    )
    match = pattern.match(url)
    if match and len(match.group(7)) == 11:
        return match.group(7)
    else:
        raise InvalidYouTubeURL("Invalid YouTube URL")


class YouTubeData:

    def __init__(self, url):
        """
        :param url: YouTube Video URL
        """
        self.youtube = build('youtube', 'v3', developerKey=API_KEY)
        self.video_id = extract_video_id(url)

    def get_video_info(self):
        """
        Get details for a YouTube video.

        :return: A dictionary containing video information.
            Keys:
            - 'video_id': The ID of the video.
            - 'video_name': The title of the video.
            - 'channel_title': The title of the channel that uploaded the video.
            - 'likes': The number of likes on the video.
            - 'dislikes': The number of dislikes on the video.
            - 'views': The number of views on the video.

        :raises VideoNotFoundError: If the video does not exist.
        """
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
        view_count = int(statistics.get('viewCount', 0))

        return {
            'video_id': self.video_id,
            'video_name': video_name,
            'channel_title': channel_title,
            'likes': like_count,
            'dislikes': dislike_count,
            'views': view_count
        }

    def get_comments(self):
        comments_data = []

        # retrieve youtube video results
        video_response = self.youtube.commentThreads().list(
            part='snippet,replies',
            videoId=self.video_id
        ).execute()

        # iterate video response
        while video_response:
            for item in video_response['items']:
                # Extracting top-level comment
                top_level_comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                # Extracting replies
                replies = []
                if 'replies' in item and 'comments' in item['replies']:
                    for reply_item in item['replies']['comments']:
                        reply = reply_item['snippet']['textDisplay']
                        replies.append(reply)

                comments_data.append({
                    'comment': top_level_comment,
                    'replies': replies
                })

            if 'nextPageToken' in video_response:
                video_response = self.youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=self.video_id,
                    pageToken=video_response['nextPageToken']
                ).execute()
            else:
                break

        return comments_data

