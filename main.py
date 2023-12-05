import aiohttp
import discord
import asyncio
import sys
import time as t

from commandInfo import commandInfo
from coach import get_summoner_id, get_puuid, get_current_game_info, get_strategy
from meta import get_latest_meta
from searchSummoner import search

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TOKEN = open("Discord_token", "r").readline()
Youtube_api_key = open("Youtube_api_key", "r").readline()

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
        embed = await get_latest_meta()
        if embed:
            t1 = t.time()
            await msg.channel.send(embed=embed)
            temp_message = await msg.channel.send("잠시만 기다려주세요!")  # 임시 메시지 저장
            await msg.delete()
            await temp_message.delete()  # 임시 메시지 삭제
            t2 = t.time()
            embed = discord.Embed(title="데이터 출처", description="[Youtube] 프로관전러 P.S", color=0x62c1cc)
            embed.add_field(name="소요시간", value="`" + str(round(t2 - t1, 3)) + "초`", inline=False)
            embed.set_footer(text="프로관전러 P.S 유튜브 자료를 가져왔습니다..",
                             icon_url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            await msg.channel.send(embed=embed)
        else:
            await msg.delete()
            await msg.channel.send("죄송합니다. 아직 현재 메타 정보가 준비되지 않았습니다.")


    if msg.content.startswith('!전적검색'):
        parts = msg.content.split('#', 1)
        if len(parts) != 2:
            embed = discord.Embed(title="명령어 형식이 잘못되었습니다.",
                                  description="'!전적검색 닉네임#태그' 형식으로 입력해주세요.", color=0x62c1cc)
            embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            await msg.channel.send(embed=embed)
            return

        summoner_name = parts[0].replace('!전적검색 ', '')
        summoner_tag = parts[1]

        async with aiohttp.ClientSession() as session:
            file = await search(session, summoner_name, summoner_tag)
            if file == -1:
                embed = discord.Embed(title="해당 유저가 존재하지 않습니다.",
                                      description="닉네임을 다시 확인해주세요!", color=0x62c1cc)
                embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            else:
                temp_message = await msg.channel.send("잠시만 기다려주세요!")  # 임시 메시지 저장
                await msg.delete()
                t1 = t.time()
                await msg.channel.send(file=file)
                await temp_message.delete()  # 임시 메시지 삭제
                t2 = t.time()
                embed = discord.Embed(title="데이터 출처", description="Riot API / fow.kr", color=0x62c1cc)
                embed.add_field(name="소요시간", value="`" + str(round(t2 - t1, 3)) + "초`", inline=False)
                embed.set_footer(text="솔로랭크 기준 티어입니다. | 랭크 정보가 없을 시 출력되지 않습니다.", icon_url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
            await msg.channel.send(embed=embed)

    if msg.content.startswith('!인게임분석 '):
        parts = msg.content.split('#', 1)
        if len(parts) != 2:
            embed = discord.Embed(title="명령어 형식이 잘못되었습니다.",
                                  description="'!인게임분석 닉네임#태그' 형식으로 입력해주세요.", color=0x62c1cc)
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
                                      description="정확한 닉네임이 맞는지 확인해주세요!", color=0x62c1cc)
                embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                await msg.channel.send(embed=embed)
            else:
                summoner_id = await get_summoner_id(session, summoner_puuid)
                current_game = await get_current_game_info(session, summoner_id)

                if current_game == -1:
                    await msg.delete()
                    embed = discord.Embed(title="현재 게임 중이 아닙니다.", description="게임이 끝났나봐요! 아니면.. 혹시 닷지하셨나요?", color=0x62c1cc)
                    embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                    await msg.channel.send(embed=embed)
                else:
                    temp_message = await msg.channel.send("잠시만 기다려주세요!")  # 임시 메시지 저장
                    t1 = t.time()
                    await msg.delete()
                    embed = await get_strategy(session, summoner_name, summoner_tag, summoner_puuid, current_game)
                    await msg.channel.send(embed=embed)
                    await temp_message.delete()  # 임시 메시지 삭제
                    t2 = t.time()
                    embed = discord.Embed(title="데이터 출처", description="Riot API", color=0x62c1cc)
                    embed.add_field(name="소요시간", value="`" + str(round(t2 - t1, 3)) + "초`", inline=False)
                    embed.set_footer(text="게임 내의 모든 플레이어들의 승률 지표를 기반으로 나타난 결과입니다.",
                                     icon_url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
                    await msg.channel.send(embed=embed)

# 봇 토큰으로 봇 실행
client.run(TOKEN)