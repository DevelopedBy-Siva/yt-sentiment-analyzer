import pandas as pd
import os
from sklearn.feature_extraction.text import re
from googleapiclient.discovery import build

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
        raise InvalidYouTubeURL("Invalid URL. Please enter a valid YouTube URL.")


def clean_data(review):
    no_punc = re.sub(r'[^\w\s]', '', review)
    no_digits = ''.join([i for i in no_punc if not i.isdigit()])
    return no_digits


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

    def get_dataframes(self):
        """
        Retrieve comments and their replies for a YouTube video.

        Returns a tuple of two DataFrames: one for top-level comments and
        another for replies.

        Top-level comments DataFrame structure:
        {
            'id': '124',
            'text': 'comment text...',
            'likes': 123,
            'timestamp': '2023-10-28T12:36:00Z'
        }

        Replies DataFrame structure:
        {
            'id': '124',
            'text': 'reply text...',
            'likes': 45,
            'timestamp': '2023-10-28T12:36:00Z',
            'comment_id': '123'  # The corresponding top-level comment ID
        }

        Returns:
            tuple: Two DataFrames - one for top-level comments and another for replies.
        """
        comments_data = []
        replies_data = []

        # retrieve youtube video results
        video_response = self.youtube.commentThreads().list(
            part='snippet,replies',
            videoId=self.video_id
        ).execute()

        # iterate video response
        while video_response:
            for item in video_response['items']:
                # Extracting top-level comment
                top_level_comment_id = item['id']
                top_level_comment_text = item['snippet']['topLevelComment']['snippet']['textOriginal']
                top_level_comment_likes = item['snippet']['topLevelComment']['snippet']['likeCount']
                top_level_comment_timestamp = item['snippet']['topLevelComment']['snippet']['publishedAt']

                # Extracting replies
                if 'replies' in item and 'comments' in item['replies']:
                    for reply_item in item['replies']['comments']:
                        reply_id = reply_item['id']
                        reply_text = reply_item['snippet']['textOriginal']
                        reply_likes = reply_item['snippet']['likeCount']
                        reply_timestamp = reply_item['snippet']['publishedAt']

                        replies_data.append({
                            'id': reply_id,
                            'text': reply_text,
                            'likes': reply_likes,
                            'timestamp': reply_timestamp,
                            'comment_id': top_level_comment_id,
                        })

                comments_data.append({
                    'id': top_level_comment_id,
                    'comment': top_level_comment_text,
                    'likes': top_level_comment_likes,
                    'timestamp': top_level_comment_timestamp,
                })

            if 'nextPageToken' in video_response:
                video_response = self.youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=self.video_id,
                    pageToken=video_response['nextPageToken']
                ).execute()
            else:
                break

        comments_dataframe = pd.DataFrame(comments_data)
        comments_dataframe["timestamp"] = pd.to_datetime(comments_dataframe["timestamp"])

        replies_dataframe = pd.DataFrame(replies_data)
        replies_dataframe["timestamp"] = pd.to_datetime(replies_dataframe["timestamp"])

        return comments_dataframe, replies_dataframe

