import discord

from PIL import ImageDraw, ImageFont
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image

from championDB import championsName

api_key = open("C:/Users/who/Desktop/SeoulTech/2023_2/OSS/Riot_api_key.txt", "r").readline()

async def fetch_json(url, session, headers=None):
    async with session.get(url, headers=headers) as response:
        print(response.status)
        if response.status == 200:
            return await response.json()
        return None


async def fetch_html(url, session, headers=None):
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.text()
        return None


def get_color(tier):
    color = (0, 0, 0)
    color2 = (0, 0, 0)

    if tier.startswith('UNRANKED'):
        color = (230, 230, 230)  # 밝은 회색
        color2 = (110, 110, 110)  # 더 어두운 회색
    elif tier.startswith('IRON'):
        color = (160, 157, 156)  # 밝은 철색
        color2 = (70, 50, 47)  # 더 어두운 철색
    elif tier.startswith('BRONZE'):
        color = (145, 112, 89)  # 밝은 청동색
        color2 = (70, 68, 68)  # 더 어두운 청동색
    elif tier.startswith('SILVER'):
        color = (185, 195, 203)  # 밝은 은색
        color2 = (90, 73, 57)  # 더 어두운 은색
    elif tier.startswith('GOLD'):
        color = (229, 191, 86)  # 밝은 금색
        color2 = (41, 83, 44)  # 더 어두운 금색
    elif tier.startswith('PLATINUM'):
        color = (50, 208, 146)  # 밝은 플래티넘색
        color2 = (0, 62, 31)  # 더 어두운 플래티넘색
    elif tier.startswith('EMERALD'):
        color = (136, 235, 170)  # 밝은 에메랄드색
        color2 = (27, 97, 70)  # 더 어두운 에메랄드색
    elif tier.startswith('DIAMOND'):
        color = (137, 123, 222)  # 밝은 다이아몬드색
        color2 = (157, 88, 191)  # 더 어두운 다이아몬드색
    elif tier.startswith('MASTER'):
        color = (200, 118, 221)  # 밝은 마스터색
        color2 = (194, 59, 187)  # 더 어두운 마스터색
    elif tier.startswith('GRANDMASTER'):
        color = (134, 109, 109)  # 밝은 그랜드마스터색
        color2 = (202, 31, 37)  # 더 어두운 그랜드마스터색
    elif tier.startswith('CHALLENGER'):
        color = (52, 185, 255)  # 밝은 챌린저색
        color2 = (182, 173, 130)  # 더 어두운 챌린저색

    return color, color2


async def get_player_info(session, summoner_name, summoner_tag):
    # 소환사 정보 가져오기
    summoner_url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}"
    summoner_data = await fetch_json(summoner_url, session, {"X-Riot-Token": api_key})
    if not summoner_data:
        return -1

    # puuid를 사용하여 랭크 정보 가져오기
    summoner_id_url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{summoner_data.get('puuid')}"
    summoner_id = await fetch_json(summoner_id_url, session, {"X-Riot-Token": api_key})
    rank_url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id.get('id')}"
    rank_data = await fetch_json(rank_url, session, {"X-Riot-Token": api_key})
    if not rank_data:
        return -1

    # 필요한 랭크 정보 추출
    tier_info = next((tier for tier in rank_data if tier["queueType"] == "RANKED_SOLO_5x5"), None)
    if not tier_info:
        return "언랭입니다."

    # 티어 이미지 URL 생성
    tier = tier_info["tier"].lower()  # 티어 이름을 소문자로 변환
    tier_image_url = f"https://z.fow.kr/img/emblem/{tier}.png"

    # 현 시즌 승리, 패배 횟수 및 승률 계산
    wins = tier_info["wins"]
    losses = tier_info["losses"]
    winrate = wins / (wins + losses) * 100

    return {
        'level': summoner_id["summonerLevel"],
        'image': tier_image_url,
        'tier': tier_info["tier"] + " " + tier_info["rank"],
        'lp': tier_info["leaguePoints"],
        'wins': wins,
        'losses': losses,
        'winrate': winrate
    }


async def get_most_champions(session, url):
    html = await fetch_html(url, session)
    soup = BeautifulSoup(html, 'html.parser')

    # 모스트 챔피언 정보를 담는 리스트
    most_champions = []

    # 모스트 챔피언 정보를 포함하는 테이블을 찾습니다.
    table = soup.find("table", {"class": "tablesorter"})
    if table:
        # 테이블의 모든 행(tr 태그)을 찾습니다.
        rows = table.find_all("tr")[1:4]  # 첫 번째 행은 헤더이므로 제외하고, 다음 3개의 행을 가져옵니다.

        for row in rows:
            cols = row.find_all("td")
            champion_name = cols[0].get_text(strip=True)
            games_played = cols[1].get_text(strip=True)
            win_rate = cols[2].get_text(strip=True)
            kda = cols[3].get_text(strip=True)

            # 추출한 정보를 리스트에 추가합니다.
            most_champions.append({
                "champion_name": champion_name,
                "games_played": games_played,
                "win_rate": win_rate,
                "kda": kda
            })

    return most_champions


async def get_tier_image(session, tier_image_url):
    async with session.get(tier_image_url) as response:
        if response.status == 200:
            # 응답으로부터 바이트 데이터를 가져옴
            image_data = await response.read()
            # BytesIO를 사용하여 바이트 데이터를 이미지로 변환
            im = Image.open(BytesIO(image_data))
            # 이미지 크기 조정
            return im.resize((180, 180))
        else:
            return None


async def get_champion_image(session, champion_name):
    # Riot API로부터 최신 버전 정보 가져오기
    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    latest_version = await fetch_json(version_url, session)
    if not latest_version:
        return None

    if champion_name:
        image_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version[0]}/img/champion/{champion_name}.png"
        async with session.get(image_url) as response:
            if response.status == 200:
                image_data = await response.read()
                image = Image.open(BytesIO(image_data))
                image = image.resize((45,45))
                return image
    return None


async def search(session, summoner_name, summoner_tag):
    user_info = await get_player_info(session, summoner_name, summoner_tag)
    if user_info == -1 or user_info == "언랭입니다.":
        # 오류 메시지 반환 또는 적절한 처리
        return -1

    fow_url = "https://fow.kr/find/" + summoner_name + "-" + summoner_tag
    most_champions = await get_most_champions(session, fow_url)

    # 숫자 값들을 문자열로 변환
    level_str = str(user_info.get('level'))
    wins_str = str(user_info.get('wins'))
    losses_str = str(user_info.get('losses'))
    winrate_str = f"{user_info.get('winrate'):.2f}%"

    temp = [summoner_name + "#" + summoner_tag, level_str, user_info.get('image'), user_info.get('tier'),
            wins_str + " " + losses_str + "  " + winrate_str, most_champions]

    im = Image.new("RGB", (400, 580), get_color(temp[3])[0])
    im2 = Image.new("RGB", (360, 540), (0, 0, 0))
    im3 = Image.new("RGB", (380, 560), get_color(temp[3])[1])
    table = Image.new("RGB", (360, 315), (30, 32, 44))
    table2 = Image.new("RGB", (340, 90), (54, 54, 61))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("malgunbd.ttf", 17)
    font2 = ImageFont.truetype("malgunbd.ttf", 15)
    im.paste(im3, (10, 10))
    im.paste(im2, (20, 20))
    draw.text((40, 35), temp[0], font=font, fill=(255, 255, 255))
    draw.text((40, 60), "레벨", font=font2, fill=(140, 140, 140))
    draw.text((80, 60), temp[1], font=font2, fill=(140, 140, 140))
    im.paste(await get_tier_image(session, temp[2]), (110, 60)) # 티어 이미지

    im.paste(table, (20, 240))
    draw.text((40, 257), "티어 정보", font=font2, fill=(255, 255, 255))
    draw.text((40, 285), temp[3], font=font2, fill=(140, 140, 140))
    draw.text((40, 320), "승/패 | 승률", font=font2, fill=(255, 255, 255))
    draw.text((40, 347), temp[4], font=font2, fill=(140, 140, 140))
    draw.text((40, 383), "모스트 챔피언", font=font2, fill=(255, 255, 255))
    for i, champion in enumerate(most_champions[:3]):  # 최대 3개의 챔피언 이미지
        print(championsName[champion['champion_name']])
        champion_image = await get_champion_image(session, championsName[champion['champion_name']])
        if champion_image:
            im.paste(champion_image, (40 + i * 60, 407))

    im.paste(table2, (30, 460))
    for i, champion in enumerate(most_champions):
        champ_text = f"{champion['champion_name']} | {champion['games_played']}게임 | 승률 {champion['win_rate']} | KDA {champion['kda']}"
        draw.text((40, 468 + i * 26), champ_text, font=font2, fill=(160, 160, 160))

    with BytesIO() as image_binary:
        im.save(image_binary, "png")
        image_binary.seek(0)
        out = discord.File(fp=image_binary, filename="image.png")

    return out
