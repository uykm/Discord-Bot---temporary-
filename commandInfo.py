import discord

def commandInfo():
    embed = discord.Embed(title="기능 설명", description="저는 현재 아래와 같은 기능들을 지원하고 있습니다!", color=0xf3bb76)
    # url 주소가 너무 길면 오류가 발생해 이미지를 직접 포스팅한 주소로 받아왔습니다.
    embed.set_thumbnail(url="https://i.ibb.co/4f1nw7T/P-S.webp?type=w800")
    embed.add_field(name="!전적검색", value="`!전적검색 닉네임#태그 (ex. !전적검색 민규#TAG)`"
                                        "\n해당 유저의 정보를 확인해볼 수 있습니다.", inline=False)
    embed.add_field(name="!인게임분석", value="`!인게임분석 닉네임#태그 (ex. !인게임분석 민규#TAG)`"
                                         "\n해당 게임에서 누구와 게임을 풀어나가야 할지, 적팀에서 누구를 조심해야 할지를 승률에 기반해서 알려줍니다.", inline=False)
    embed.set_footer(text="버그 제보 및 문의\nhttps://github.com/uykm/P.Sbot-Discord")
    return embed
