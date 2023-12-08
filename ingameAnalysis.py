import asyncio
import aiohttp
import discord

# import request 방식으로 시도했지만 Discord 봇의 이벤트 루프가 블로킹(동기) HTTP 요청에 의해 차단되는 오류가 발생하기도 하고,
# 응답 속도를 높이기 위해 비동기 방식으로 변경했습니다.
from championDB import find_kor_name

import os
from dotenv import load_dotenv

riot_api_key = os.getenv('RIOT_API_KEY')
# riot_api_key = open("RIOT_API_KEY.txt", "r").readline()

champion_data_cache = None

async def get_champion_data(session):
    global champion_data_cache
    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"

    # 캐시된 데이터가 없는 경우, 새로운 데이터 요청
    latest_version = await fetch_json(version_url, session)
    if latest_version != -1:
        champion_data_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version[0]}/data/en_US/champion.json"
        # 챔피언 데이터를 캐시에 저장
        champion_data_cache = await fetch_json(champion_data_url, session)
        if champion_data_cache != -1:
            champion_data = {data['key']: data['id'] for _, data in champion_data_cache['data'].items()}
            return champion_data
    return {}

# aiohttp를 사용하여 비동기적인 HTTP 요청을 처리하고, 응답을 JSON 형식으로 파싱하는 공통 기능을 제공하기 위한 함수입니다.
async def fetch_json(url, session, headers=None):
    for attempt in range(5):
        async with session.get(url, headers=headers) as response:
            print(response.status)
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                # API 요청 횟수가 초과했을 경우 지연시키기
                if attempt < 6:
                    await asyncio.sleep(10)
                else:
                    return -1
            else:
                return -1
    return -1

async def get_champion_image(session, champion_id):
    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    async with session.get(version_url) as response:
        if response.status == 200:
            latest_version = await response.json()
            image_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version[0]}/img/champion/{champion_id}.png"

            # 이미지 URL의 유효성 확인
            async with session.get(image_url) as img_response:
                return image_url if img_response.status == 200 else None
        return None

async def get_puuid(session, summoner_name, summoner_tag):
    summoner_url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}"
    summoner_data = await fetch_json(summoner_url, session, {"X-Riot-Token": riot_api_key})
    if summoner_data == -1:
        return -1
    return summoner_data.get('puuid')

# puuid를 이용해 닉네임과 태그를 얻어온다.
async def get_summoner_name_and_tag_by_puuid(session, puuid):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
    headers = {"X-Riot-Token": riot_api_key}
    data = await fetch_json(url, session, headers)
    if data != -1:
        return data.get('gameName', '') + '#' + data.get('tagLine', '')
    else:
        return None

async def get_summoner_id(session, puuid):
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": riot_api_key}
    data = await fetch_json(url, session, headers)
    return data.get('id', -1) if data != None else -1

async def get_current_game_info(session, summonerId):
    if summonerId == -1:
        return -1
    url = f"https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summonerId}"
    headers = {"X-Riot-Token": riot_api_key}
    async with aiohttp.ClientSession() as session:
        return await fetch_json(url, session, headers)

async def get_ranked_data(session, summoner_id):
    ranked_url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    ranked_data = await fetch_json(ranked_url, session, {"X-Riot-Token": riot_api_key})
    if not ranked_data:
        return None
    # 솔로 랭크 정보만 필터링
    solo_rank_data = next((data for data in ranked_data if data["queueType"] == "RANKED_SOLO_5x5"), None)
    return solo_rank_data

async def get_strategy(session, input_name, input_tag, puuid, current_game):
    champion_data = await get_champion_data(session)

    # 팀별로 플레이어 분류
    blue = [player for player in current_game['participants'] if player['teamId'] == 100]
    red = [player for player in current_game['participants'] if player['teamId'] == 200]

    # 사용자가 속한 팀 확인
    summoner_team_id = 100 if any(player['puuid'] == puuid for player in blue) else 200

    # 팀별 랭크 정보 및 승률 가져오기
    blue_winrates = {player['puuid']: await get_ranked_data(session, player['summonerId']) for player in blue}
    red_winrates = {player['puuid']: await get_ranked_data(session, player['summonerId']) for player in red}

    # 팀별 가장 높은 승률을 가진 플레이어의 PUUID 찾기
    flag = False
    ace_puuid_blue = max(blue_winrates, key=lambda p: (blue_winrates[p]['wins'] / (blue_winrates[p]['wins'] + blue_winrates[p]['losses']) if blue_winrates[p] else 0))
    ace_puuid_red = max(red_winrates, key=lambda p: (red_winrates[p]['wins'] / (red_winrates[p]['wins'] + red_winrates[p]['losses']) if red_winrates[p] else 0))
    if ace_puuid_blue == puuid or ace_puuid_red == puuid:
        flag = True

    # 해당 플레이어(ace)의 챔피언 ID 찾기
    ace_champion_id_blue = next((player['championId'] for player in blue if player['puuid'] == ace_puuid_blue), None)
    ace_champion_id_red = next((player['championId'] for player in red if player['puuid'] == ace_puuid_red), None)

    # 챔피언 ID를 영어 이름으로 변환
    champion_eng_blue = champion_data[str(ace_champion_id_blue)]
    champion_eng_red = champion_data[str(ace_champion_id_red)]

    # puuid로 양팀(블루/레드) 스타 플레이어의 닉네임과 태그 찾기
    ace_name_and_tag_blue = await get_summoner_name_and_tag_by_puuid(session, ace_puuid_blue)
    ace_name_and_tag_red = await get_summoner_name_and_tag_by_puuid(session, ace_puuid_red)

    # 유저가 블루팀에 속한 경우
    if summoner_team_id == 100:
        our_ace_champion_eng = champion_eng_blue
        our_ace_name_and_tag = ace_name_and_tag_blue
        enemy_ace_champion_eng = champion_eng_red
        enemy_ace_name_and_tag = ace_name_and_tag_red
    # 유저가 레드팀에 속한 경우
    else:
        our_ace_champion_eng = champion_eng_red
        our_ace_name_and_tag = ace_name_and_tag_red
        enemy_ace_champion_eng = champion_eng_blue
        enemy_ace_name_and_tag = ace_name_and_tag_blue

    # 에이스 플레이어의 챔피언 한국어 이름 찾기
    our_kor_ace = find_kor_name(our_ace_champion_eng)
    enemy_kor_ace = find_kor_name(enemy_ace_champion_eng)

    # Embed 생성
    embed = discord.Embed(title=f"인게임 분석 결과", description="`" + input_name + "#" + input_tag + "님의 게임`", color=0x00ff00)
    # 우리 팀 챔피언 이미지와 메시지 추가
    our_ace_image = await get_champion_image(session, our_ace_champion_eng)

    if flag:
        our_team_message = f"우리 팀의 스타 플레이어는 \" 당신 \" 입니다. \n희생적인 플레이는 피하고 성장에 집중하세요!"
        embed.set_thumbnail(url=our_ace_image)
        embed.add_field(name="추천 코멘트 !", value=our_team_message, inline=False)
    else:
        our_team_message = (f"우리 팀의 스타 플레이어는 \" {our_kor_ace} \" 입니다. \n\" {our_kor_ace} \" 와(과) 함께 게임을 풀어나가는 것을 추천합니다!\n"
                            f"`{our_kor_ace} 정보:` ")
        embed.set_thumbnail(url=our_ace_image)
        embed.add_field(name="추천 코멘트 !", value=our_team_message + "`" + str(our_ace_name_and_tag) + "`", inline=False)

    # 적 팀 챔피언 이미지와 메시지 추가
    enemy_ace_image = await get_champion_image(session, enemy_ace_champion_eng)
    embed.set_image(url=enemy_ace_image)
    enemy_team_message = (f"적 팀에 있는 \"" + enemy_kor_ace + "\" 은(는) 조심할 필요가 있을 것 같습니다!\n"
                        f"`{enemy_kor_ace} 정보:` ")
    embed.add_field(name="주의 코멘트 !", value=enemy_team_message + "`" + str(enemy_ace_name_and_tag) + "`", inline=False)

    return embed
