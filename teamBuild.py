import discord
import itertools
import os

riot_api_key = os.getenv('RIOT_API_KEY')
# riot_api_key = open("RIOT_API_KEY.txt", "r").readline()

async def fetch_json(url, session, headers=None):
    async with session.get(url, headers=headers) as response:
        print(response.status)
        if response.status == 200:
            return await response.json()
        return None


async def checkID(session, summoner_name, summoner_tag):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}"
    headers = {"X-Riot-Token": riot_api_key}
    data = await fetch_json(url, session, headers)
    return data.get('puuid', -1) if data != None else -1

async def get_rank(session, puuid):
    # puuid를 사용하여 랭크 정보 가져오기
    summoner_id_url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    summoner_id = await fetch_json(summoner_id_url, session, {"X-Riot-Token": riot_api_key})
    if not summoner_id or 'id' not in summoner_id:
        return None  # summoner_id가 없거나 유효하지 않은 경우

    rank_url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id.get('id')}"
    rank_data = await fetch_json(rank_url, session, {"X-Riot-Token": riot_api_key})
    if not rank_data:
        return None  # 랭크 데이터가 없는 경우

    # 필요한 랭크 정보 추출
    tier_info = next((tier for tier in rank_data if tier["queueType"] == "RANKED_SOLO_5x5"), None)
    if not tier_info:
        return None  # tier_info가 없는 경우

    return {
        'level': summoner_id.get("summonerLevel", 0),
        'tier': tier_info.get("tier", "UNRANKED"),
        'rank': tier_info.get("rank", ""),
        'lp': tier_info.get("leaguePoints", 0)
    }


def calculate_score(rank_info):
    tier_points = {
        'IRON': 5,
        'BRONZE': 10,
        'SILVER': 25,
        'GOLD': 40,
        'PLATINUM': 60,
        'EMERALD': 100,
        'DIAMOND': 150,
        'MASTER': 500,
        'GRANDMASTER': 1000,
        'CHALLENGER': 2000
    }

    # Unranked
    if rank_info is None or 'tier' not in rank_info or rank_info['tier'] == 'UNRANKED':
        level = rank_info.get('level', 0) if rank_info is not None else 0
        return level / 3

    tier = rank_info.get('tier')
    rank = rank_info.get('rank')
    lp = rank_info.get('lp')

    if tier in ['MASTER', 'GRANDMASTER', 'CHALLENGER']:
        return tier_points[tier] + lp
    elif tier in ['DIAMOND']:
        rank_value = {'I': 2, 'II': 1.5, 'III': 1.2, 'IV': 1}.get(rank, 4)  # 기본값으로 IV를 사용
        return tier_points[tier] * rank_value
    else: # ['BRONZE', 'SILVER', 'GOLD', 'PLATINUM']:
        rank_value = {'I': 10, 'II': 7, 'III': 4, 'IV': 0}.get(rank, 4)  # 기본값으로 IV를 사용
        return tier_points[tier] + rank_value


# 각자 가고 싶었던 라인에 배치될 수 있는지 체크하는 함수
async def is_valid_combination(combination, player_wish_list):
    lines = {'탑', '정글', '미드', '원딜', '서폿'}
    assigned_lines = set()

    for puuid in combination:
        for line in player_wish_list[puuid]:
            if line in lines and line not in assigned_lines:
                assigned_lines.add(line)
                break

    return len(assigned_lines) == len(lines)


async def find_lineup(team, player_wish_list):
    line_ups = {line: [] for line in ['탑', '정글', '미드', '원딜', '서폿']}
    for puuid in team:
        for line in player_wish_list[puuid]:
            if line in line_ups:
                line_ups[line].append(puuid)

    # 가능한 라인업 찾기 (단순하게 최초로 발견되는 조합을 선택)
    possible_lineup = {}
    for line, players in line_ups.items():
        for player in players:
            if player not in possible_lineup.values():
                possible_lineup[line] = player
                break

    return possible_lineup


async def teambuild(session, nametag_puuid, player_wish_list):
    # 플레이어(puuid) 별 점수 계산
    puuid_scores = {}
    for puuid in nametag_puuid.values():
        rank_info = await get_rank(session, puuid)
        score = calculate_score(rank_info)  # rank_info에 따라 점수 계산하는 함수
        puuid_scores[puuid] = score


    all_puuids = list(puuid_scores.keys())
    min_score = 100000
    best_combination = (None, None)

    # 블루팀과 레드팀에 해당하는 5인 조합 생성
    for combination in itertools.combinations(all_puuids, 5):
        blueteam = set(combination)
        redteam = set(all_puuids) - blueteam

        # 각자 가고 싶었던 라인에 중복되는 사람 없이 배치될 수 있는지 체크
        if await is_valid_combination(blueteam, player_wish_list) and await is_valid_combination(redteam, player_wish_list):
            if len(blueteam.union(redteam)) == 10:
                score_diff = abs(sum(puuid_scores[p] for p in blueteam) - sum(puuid_scores[p] for p in redteam))

                if score_diff < min_score:
                    min_score = score_diff
                    best_combination = (blueteam, redteam)
    print(best_combination)

    # 결과 Embed 생성
    if best_combination[0] is not None and best_combination[1] is not None:
        embed = discord.Embed(title="내전 팀 빌딩 결과")
        for team_name, team in zip(["블루 팀", "레드 팀"], best_combination):
            lineup = await find_lineup(team, player_wish_list)
            team_fields_value = "\n".join(f"{line}: `{[name for name, p in nametag_puuid.items() if p == puuid][0]}`"
                                          for line, puuid in lineup.items())
            embed.add_field(name=team_name, value=team_fields_value, inline=False)

        return embed
    else:
        return -1

