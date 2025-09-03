import csv
import os
import requests
from googleapiclient.discovery import build
import pandas as pd

# YouTube Data APIキーを設定
api_key = '自分のAPIキーを設定'  # 自分のAPIキーを設定
youtube = build('youtube', 'v3', developerKey=api_key)

# 特定のチャンネルIDを設定
channel_id = 'UC2dXx-3RXeeP8hA5AGt8vuw'  # 調査対象のチャンネルIDを設定

# 出力ディレクトリの設定
output_dir = 'output'
if not os.path.exists(output_dir):  # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir)

# サムネイルをダウンロードする関数
def download_thumbnail(url, video_id):
    response = requests.get(url)
    if response.status_code == 200:  # リクエストが成功した場合
        with open(f"{output_dir}/{video_id}.jpg", 'wb') as f:
            f.write(response.content)  # サムネイル画像を保存

# チャンネルの動画リストを取得
def get_videos_from_channel(channel_id):
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=100,
        order='date'
    )
    response = request.execute()  # APIリクエストを実行
    videos = []

    for item in response['items']:  # 各動画アイテムについて処理
        # 'videoId' キーが存在するか確認
        if 'videoId' in item['id']:
            video_id = item['id']['videoId']  # 動画IDを取得
            video_title = item['snippet']['title']  # 動画タイトルを取得
            video_url = f"https://www.youtube.com/watch?v={video_id}"  # 動画URLを作成
            video_description = item['snippet']['description']  # 動画説明を取得
            video_thumbnail = item['snippet']['thumbnails']['high']['url']  # 高解像度のサムネイルURLを取得

            # 動画の詳細情報を取得
            video_request = youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            )
            video_response = video_request.execute()  # 動画詳細情報のAPIリクエストを実行
            view_count = video_response['items'][0]['statistics']['viewCount']  # 再生回数を取得
            tags = video_response['items'][0]['snippet'].get('tags', [])  # タグを取得（存在しない場合は空リスト）

            # サムネイルをダウンロード
            download_thumbnail(video_thumbnail, video_id)  # サムネイル画像をダウンロード

            # 取得した動画情報をリストに追加
            videos.append({
                'title': video_title,
                'url': video_url,
                'description': video_description,
                'thumbnail_path': f"{output_dir}/{video_id}.jpg",
                'view_count': view_count,
                'tags': ','.join(tags)  # タグをカンマ区切りの文字列に変換
            })

    return videos

# 動画情報を取得してCSVに書き出す
videos = get_videos_from_channel(channel_id)  # 動画情報を取得
df = pd.DataFrame(videos)  # データフレームに変換
csv_filename = f"{output_dir}/videos_{channel_id}.csv"  # CSVファイル名にチャンネルIDを含める
df.to_csv(csv_filename, index=False, encoding='utf-8-sig')  # 日本語対応のエンコーディングでCSVに書き出し

print(f"Data extraction and CSV creation completed. CSV file saved as {csv_filename}")  # 処理完了メッセージを表示

