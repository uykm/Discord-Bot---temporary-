import discord
from googleapiclient.discovery import build

api_key = open("Youtube_api_key", "r").readline()

async def get_latest_meta():
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        part="snippet",
        q="PS표 티어리스트",
        maxResults=10,
        order="date",
        type="video"
    )
    response = request.execute()

    for item in response['items']:
        video_info = item['snippet']
        title = video_info['title']
        if "PS표 티어리스트" in title:  # "PS표 티어리스트" 라는 문구가 들어간 영상들 중 가장 최신 영상 탐색
            thumbnail_url = video_info['thumbnails']['high']['url']
            video_id = item['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            embed = discord.Embed(title=title, url=video_url)
            embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            embed.add_field(name="영상 링크", value=video_url, inline=False)
            embed.set_image(url=thumbnail_url) # 썸네일을 제목 아래에 세팅
            return embed

    return None
