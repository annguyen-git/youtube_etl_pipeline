import pandas as pd
from itertools import chain
import googleapiclient.discovery
from dateutil import parser
import isodate
from sqlalchemy import create_engine
import pymysql

# Function that gets channel stats
def get_channel_stats(youtube, handles):
    all_data = []
    for i in handles:
        try:
            request = youtube.channels().list(
                part='snippet,contentDetails,statistics',
                maxResults=1,
                forHandle=i  # Replace 'forHandle' with 'forUsername' or another appropriate parameter
            )
            response = request.execute()
            if 'items' in response and len(response['items']) > 0:
                item = response['items'][0]
                data = dict(
                    channelname=item['snippet']['title'],
                    subscribers=item['statistics'].get('subscriberCount', 'N/A'),
                    views=item['statistics'].get('viewCount', 'N/A'),
                    totalVideos=item['statistics'].get('videoCount', 'N/A'),
                    uploads=item['contentDetails']['relatedPlaylists']['uploads']
                )
                all_data.append(data)
        except Exception as e:
            print(f"Error fetching data for {i}: {e}")

    return pd.DataFrame(all_data)

# Function that get videos' IDs from uploads
def get_video_ids(youtube, playlist_id):
    request_vi = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=50)
    response_vi = request_vi.execute()
    video_ids = [item['contentDetails']['videoId'] for item in response_vi['items']]

    # Get more ids if there is more pages
    next_page_token = response_vi.get('nextPageToken')

    more_pages = True
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request_vi = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token)
            response_vi = request_vi.execute()
            video_ids = list(chain(video_ids, [item['contentDetails']['videoId'] for item in response_vi['items']]))
            next_page_token = response_vi.get('nextPageToken')
    return video_ids

#Function that gets all videos details
def get_video_details(youtube, video_ids):
    videos_info = []  # List to store information for each video
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i + 50])
        )
        response = request.execute()

        for video in response['items']:
            stats_to_keep = {
                'id': ['id'],  # Top-level key for video ID
                'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                'statistics': ['viewCount', 'likeCount', 'favoriteCount', 'commentCount'],
                'contentDetails': ['duration', 'definition', 'caption']
            }

            video_info = {}  # Dictionary for storing information for one video

            # Iterate over the top-level keys (e.g., snippet, statistics)
            for k, v_list in stats_to_keep.items():
                for v in v_list:
                    try:
                        # Special handling for 'id' since it's at the top level
                        if k == 'id':
                            video_info[v] = video.get(v)
                        else:
                            video_info[v] = video[k].get(v, None)  # Use .get to avoid KeyError
                    except KeyError:
                        video_info[v] = None

            if 'tags' in video_info and isinstance(video_info['tags'], list):
                video_info['tags'] = ', '.join(video_info['tags'])
            else:
                video_info['tags'] = None  # Handle case where tags are missing or not a list

            videos_info.append(video_info)  # Append this video's information to the list

        # video_info now contains the last processed video
    videos_details = pd.DataFrame(videos_info)  # This contains all processed video data
    return videos_details


# Create an API client using the API key
def connect_youtube(api_key):
    youtube = googleapiclient.discovery.build(
        'youtube', 'v3', developerKey=api_key)
    return youtube

def data_channel_youtube(youtube,handles):
    channel_data = get_channel_stats(youtube, handles)
    numeric_cols = ['subscribers', 'views', 'totalVideos']
    channel_data[numeric_cols] = channel_data[numeric_cols].apply(pd.to_numeric, errors='coerce')
    return channel_data

def data_video_youtube(youtube,channel_data):
    video_df = pd.DataFrame()
    for c in channel_data['channelname'].unique():
        print("Getting video information from channel: " + c)
        playlist_id = channel_data.loc[channel_data['channelname']== c, 'uploads'].iloc[0]
        video_ids = get_video_ids(youtube, playlist_id)
        video_data = get_video_details(youtube, video_ids)
        video_df = pd.concat([video_df, video_data], ignore_index=True)
    return video_df

def transform_data(video_df):
    video_df2 = video_df.copy()  # Create a copy of the DataFrame
    cols = ['viewCount', 'likeCount', 'favoriteCount', 'commentCount']
    video_df2[cols] = video_df[cols].apply(pd.to_numeric, errors='coerce', axis=1)
    video_df2['publishedAt'] = video_df['publishedAt'].apply(lambda x: parser.parse(x))
    video_df2['publishedOn'] = video_df2['publishedAt'].apply(lambda x: x.strftime("%A"))
    video_df2['duration'] = video_df2['duration'].apply(lambda x: isodate.parse_duration(x))
    video_df2['duration'] = video_df2['duration'].dt.total_seconds()
    video_df2['datepublished'] = video_df2['publishedAt'].dt.date
    video_df2['timepublished'] = video_df2['publishedAt'].dt.time
    video_df2.drop(columns = ['publishedAt'], inplace = True)
    return video_df2


def connect_to_db(host, user, password, database):
    try:
        # Create a pymysql connection for executing raw SQL
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            port=3307,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        # Create an SQLAlchemy engine for DataFrame operations
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:3307/{database}?charset=utf8mb4")
        print("Connection established")
        if connection.open:
            print("Connection is open")
        else:
            print("Connection is closed")
        return connection, engine
    except pymysql.MySQLError as err:
        print("An error occurred:", err)
        return None, None

def insert_to_db(connection, youtube_df, engine, table_name, database):
    try:
        # Use the pymysql connection to alter the database
        with connection.cursor() as cursor:
            alter_database_sql = f"ALTER DATABASE `{database}` CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;"
            cursor.execute(alter_database_sql)
        connection.commit()  # Commit the changes
        print("Database and table charset changed to utf8mb4 successfully.")
        youtube_df.to_sql(table_name, engine, if_exists='replace', index=False)
        print("Data written to table.")
    except pymysql.MySQLError as err:
        print("An error occurred:", err)
    finally:
        if connection and connection.open:
            connection.close()
            print("Connection closed.")
