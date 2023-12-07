import aiohttp
import discord
import asyncio
import sys
import time as t
import os

from teamBuild import checkID, teambuild
from commandInfo import commandInfo
from ingameAnalysis import get_summoner_id, get_puuid, get_current_game_info, get_strategy
from meta import get_latest_meta
from searchSummoner import search

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# 환경변수 값 가져오기
token = os.getenv('TOKEN')
api_key = os.getenv('YOUTUBE_API_KEY')

# intents 설정은 꼭 해줘야 한다!
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('분석'))
    print(f'{client.user}이 준비 과정을 성공적으로 마쳤습니다.')

def find_first_channel(channels):
    position_array = [i.position for i in channels]

    for i in channels:
        if i.position == min(position_array):
            return i

@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await guild.system_channel.send("\"" + guild.name + "\"" + " 서버 여러분 안녕하세요!")
            await guild.system_channel.send("저는 여러분이 롤을 편하게 즐길 수 있게 도와드리는 P.S 봇입니다.")
            await guild.system_channel.send("저를 사용하는 방법은 아래를 참고해주세요!")
            await guild.system_channel.send(embed=commandInfo())
            break

@client.event
async def on_member_join(member):
    await find_first_channel(member.guild.text_channels).send(member.name + "님 안녕하세요, 저는 P.S 봇입니다.")
    await find_first_channel(member.guild.text_channels).send("저를 사용하는 방법은 \"!명령어\" 를 입력하시면 확인하실 수 있습니다.")


@client.event
async def on_message(msg):
    if msg.author == client.user:
        return None

    if msg.content == ('!명령어'):
        await msg.delete()
        await msg.channel.send(embed=commandInfo())

    if msg.content == ('!메타정보'):
        temp_message = await msg.channel.send("자료 불러오는 중 ...")  # 임시 메시지 저장
        embed = await get_latest_meta()
        if embed:
            t1 = t.time()
            await msg.channel.send(embed=embed)
            await msg.delete()
            await temp_message.delete()  # 임시 메시지 삭제
            t2 = t.time()
            embed = discord.Embed(title="데이터 출처", description="[Youtube] 프로관전러 P.S", color=0x62c1cc)
            embed.add_field(name="소요시간", value="`" + str(round(t2 - t1, 3)) + "초`", inline=False)
            embed.set_footer(text="프로관전러 P.S 유튜브 자료를 가져왔습니다.",
                             icon_url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            await msg.channel.send(embed=embed)
        else:
            await msg.delete()
            await msg.channel.send("죄송합니다. 아직 현재 메타 정보가 준비되지 않았습니다.")


    if msg.content.startswith('!전적검색 '):
        parts = msg.content.split('#', 1)
        if len(parts) != 2:
            embed = discord.Embed(title="명령어 형식이 잘못되었습니다.",
                                  description="`!전적검색 닉네임#태그` 형식으로 입력해주세요.", color=0x62c1cc)
            embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            await msg.channel.send(embed=embed)
            return

        summoner_name = parts[0].replace('!전적검색 ', '')
        summoner_tag = parts[1]

        async with aiohttp.ClientSession() as session:
            file = await search(session, summoner_name, summoner_tag)
            if file == -1:
                embed = discord.Embed(title="해당 유저가 존재하지 않습니다.",
                                      description="닉네임을 다시 확인해주세요! (띄어쓰기, 영어 대소문자)", color=0x62c1cc)
                embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            else:
                temp_message = await msg.channel.send("전적 검색 중 ...")  # 임시 메시지 저장
                await msg.delete()
                t1 = t.time()
                await msg.channel.send(file=file)
                await temp_message.delete()  # 임시 메시지 삭제
                t2 = t.time()
                embed = discord.Embed(title="데이터 출처", description="Riot API / fow.kr / 나무위키", color=0x62c1cc)
                embed.add_field(name="소요시간", value="`" + str(round(t2 - t1, 3)) + "초`", inline=False)
                embed.set_footer(text="솔로 랭크 기준 티어입니다.", icon_url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            await msg.channel.send(embed=embed)

    if msg.content.startswith('!인게임분석 '):
        parts = msg.content.split('#', 1)
        if len(parts) != 2:
            embed = discord.Embed(title="명령어 형식이 잘못되었습니다.",
                                  description="`!인게임분석 닉네임#태그` 형식으로 입력해주세요.", color=0x62c1cc)
            embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            await msg.channel.send(embed=embed)
            return

        summoner_name = parts[0].replace('!인게임분석 ', '')
        summoner_tag = parts[1]

        async with aiohttp.ClientSession() as session:
            summoner_puuid = await get_puuid(session, summoner_name, summoner_tag)

            if summoner_puuid == -1:
                await msg.delete()
                embed = discord.Embed(title="해당 유저가 존재하지 않습니다.",
                                      description="정확한 닉네임이 맞는지 확인해주세요! (띄어쓰기, 영어 대/소문자)", color=0x62c1cc)
                embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                await msg.channel.send(embed=embed)
            else:
                summoner_id = await get_summoner_id(session, summoner_puuid)
                current_game = await get_current_game_info(session, summoner_id)

                if current_game == -1:
                    await msg.delete()
                    embed = discord.Embed(title="현재 게임 중이 아닙니다.",
                                          description="게임이 끝났나봐요! 아니면.. 혹시 닷지하셨나요?", color=0x62c1cc)
                    embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                    await msg.channel.send(embed=embed)
                else:
                    temp_message = await msg.channel.send("인게임 분석 중 ...")  # 임시 메시지 저장
                    t1 = t.time()
                    embed = await get_strategy(session, summoner_name, summoner_tag, summoner_puuid, current_game)
                    await msg.delete()
                    await msg.channel.send(embed=embed)
                    await temp_message.delete()  # 임시 메시지 삭제
                    t2 = t.time()
                    embed = discord.Embed(title="데이터 출처", description="Riot API", color=0x62c1cc)
                    embed.add_field(name="소요시간", value="`" + str(round(t2 - t1, 3)) + "초`", inline=False)
                    embed.set_footer(text="게임 내의 모든 플레이어들의 승률 지표를 기반으로 나타난 결과입니다.",
                                     icon_url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                    await msg.channel.send(embed=embed)

    if msg.content == '!내전팀빌딩':
        async with aiohttp.ClientSession() as session:
            await msg.delete()
            temp_message = await msg.channel.send("내전에 참여할 10명의 유저의 닉네임과 태그를 '중복되지 않도록' 3분 이내에 입력해주세요."
                                   "\n`ex.닉네임1#태그1/닉네임2#태그/...`")
            def check(m):
                return m.author == msg.author and m.channel == msg.channel

            try:
                response = await client.wait_for('message', timeout=180, check=check)
                await response.delete()
            except asyncio.TimeoutError:
                embed = discord.Embed(title="시간 초과입니다 ㅜㅜ ",
                                      description="저를 기다리고 계신 분들이 계시니.. 나중에 다시 시도해주세요!", color=0x62c1cc)
                embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                await msg.channel.send(embed=embed)
                return

            players = response.content.split('/')

            if len(players) != 10:
                embed = discord.Embed(title="10명의 유저를 입력하시지 않았거나 잘못된 형식으로 입력하신 것 같아요.",
                                      description="`ex) 닉네임1#태그1/닉네임2#태그/...`", color=0x62c1cc)
                embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                await temp_message.delete()
                await msg.channel.send(embed=embed)
                return

            await temp_message.delete()

            temp_message = await msg.channel.send("아이디 확인 중 ...")  # 임시 메시지 저장
            nametag_puuid = {}
            for player in players:
                player_name, player_tag = player.split('#')
                puuid = await checkID(session, player_name, player_tag)
                if puuid == -1:
                    embed = discord.Embed(title=f"'{player}' 라는 유저가 존재하지 않아요 ㅜㅜ 유저분들의 닉네임과 태그를 다시 확인해주세요! (띄어쓰기, 영어 대소문자)",
                                          description="`ex) 닉네임1#태그1/닉네임2#태그/...`", color=0x62c1cc)
                    embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                    await msg.channel.send(embed=embed)
                    await temp_message.delete()  # 임시 메시지 삭제
                    return
                nametag_puuid[player] = puuid
            await temp_message.delete()  # 임시 메시지 삭제

            puuid_list = list(nametag_puuid.values())
            player_wish_list = {puuid: [] for puuid in puuid_list}

            for puuid in puuid_list:
                name_tag = [name for name, p in nametag_puuid.items() if p == puuid][0]
                while True:
                    temp_message = await msg.channel.send(f"`{name_tag}`님이 원하시는 라인을 30초 내에 입력해주세요.\n`ex) 탑/정글/미드/원딜/서폿`")  # 임시 메시지 저장

                    try:
                        line_response = await client.wait_for('message', timeout=30, check=check)
                        await line_response.delete()
                    except asyncio.TimeoutError:
                        await temp_message.delete()
                        embed = discord.Embed(title="시간 초과입니다 ㅜㅜ ",
                                              description="저를 기다리고 계신 분들이 계시니.. 나중에 다시 시도해주세요!", color=0x62c1cc)
                        embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                        await msg.channel.send(embed=embed)
                        return

                    wish_lines = line_response.content.split('/')
                    valid_lines = ['탑', '정글', '미드', '원딜', '서폿']
                    valid = all(line in valid_lines for line in wish_lines)

                    await temp_message.delete()

                    if valid:
                        player_wish_list[puuid] = wish_lines
                        break
                    else:
                        await msg.channel.send("입력 형식을 다시 확인해주세요!\n`ex) 탑/미드/원딜`")

            temp_message = await msg.channel.send("팀 빌딩 중 ...")  # 임시 메시지 저장
            t1 = t.time()
            embed = await teambuild(session, nametag_puuid, player_wish_list)
            if embed == -1:
                await temp_message.delete()
                embed = discord.Embed(title="적절한 팀 구성을 찾을 수 없습니다.",
                                     description="각 라인당 중복되지 않은 최소 ' 2 '명의 플레이어가 입력되어야 합니다!")
                embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                await msg.channel.send(embed=embed)
                return
            await msg.channel.send(embed=embed)
            await temp_message.delete()  # 임시 메시지 삭제
            t2 = t.time()
            embed = discord.Embed(title="데이터 출처", description="Riot API / 나무위키", color=0x62c1cc)
            embed.add_field(name="소요시간", value="`" + str(round(t2 - t1, 3)) + "초`", inline=False)
            embed.set_footer(text="플레이어들의 티어를 분석하여 팀을 빌딩한 결과입니다.",
                             icon_url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            await msg.channel.send(embed=embed)

        '''
        for line in lines:
            while True:

                await msg.channel.send(f"{line}을 가고 싶은 유저들의 닉네임과 태그를 입력해주시고, 다른 라인과 중복 입력 가능합니다!"
                                       f"\n(ex. 닉네임1#태그1/닉네임2#태그2)")

                def check(m):
                    return m.author == msg.author and m.channel == msg.channel

                try:
                    response = await client.wait_for('message', timeout=300, check=check)
                except asyncio.TimeoutError:
                    await msg.delete()
                    embed = discord.Embed(title="시간 초과입니다 ㅜㅜ ",
                                          description="저를 기다리고 계신 분들이 계시니.. 나중에 다시 시도해주세요!", color=0x62c1cc)
                    embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                    await msg.channel.send(embed=embed)
                    return

                temp_message = await msg.channel.send("아이디 확인 중 ...")  # 임시 메시지 저장
                players = response.content.split('/')

                puuids = []
                valid = True
                for player in players:
                    parts = player.split('#', 1)
                    if len(parts) != 2:
                        await temp_message.delete()  # 임시 메시지 삭제
                        await msg.channel.send(f"`{player}`가 형식에 맞지 않아요 ㅜㅜ (ex. 닉네임1#태그1)")
                        valid = False
                        break

                    player_name = parts[0]
                    player_tag = parts[1]

                    puuid = await checkID(session, player_name, player_tag)
                    if puuid == -1:
                        await temp_message.delete()  # 임시 메시지 삭제
                        await msg.channel.send(f"'{player}'라는 유저가 존재하지 않아요 ㅜㅜ (ex. 닉네임1#태그1/닉네임2#태그2)")
                        valid = False
                        break

                    puuids.append(puuid)

                if valid:
                    await temp_message.delete()  # 임시 메시지 삭제
                    players_lists[line] = puuids
                    break

        temp_message = await msg.channel.send("팀 빌딩 중 ...")  # 임시 메시지 저장
        t1 = t.time()
        embed = await teambuild(session, top=players_lists['탑'], jungle=players_lists['정글'], mid=players_lists['미드'],
                  bottom=players_lists['원딜'], support=players_lists['서폿'])
        await msg.channel.send(embed=embed)
        await temp_message.delete()  # 임시 메시지 삭제
        t2 = t.time()
        embed = discord.Embed(title="데이터 출처", description="Riot API", color=0x62c1cc)
        embed.add_field(name="소요시간", value="`" + str(round(t2 - t1, 3)) + "초`", inline=False)
        embed.set_footer(text="플레이어들의 티어를 분석하여 팀을 빌딩한 결과입니다.",
                         icon_url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
        await msg.channel.send(embed=embed)
        '''


client.run(token)