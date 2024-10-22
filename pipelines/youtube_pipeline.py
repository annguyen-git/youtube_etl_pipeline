from etls.youtube_etl import connect_youtube,data_video_youtube, data_channel_youtube, transform_data, connect_to_db, insert_to_db
from utils.constants import API_KEY, MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD, OUTPUT_PATH
from utils.handles import handles

def youtube_pipline(file_name, db_table_name):
    # Retrieve, transform and save data as csv
    youtube = connect_youtube(API_KEY)
    channel_data = data_channel_youtube(youtube,handles)
    video_df = data_video_youtube(youtube,channel_data)
    youtube_df = transform_data(video_df)
    file_path = f'{OUTPUT_PATH}/{file_name}.csv'
    youtube_df.to_csv(file_path,index=False)
    #Save data to db
    connection, engine = connect_to_db(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
    insert_to_db(connection, youtube_df, engine, db_table_name ,MYSQL_DATABASE)
    return file_path