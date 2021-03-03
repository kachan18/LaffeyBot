import random
import discord
import datetime
import pymongo
import asyncio
import gamblefunction
import gachafunction

def noargs():
    rand = random.randint(0, 100)
    if rand <= 35:
        return "우우...... 지휘관, 흔들지 마......"
    elif rand < 65:
        return "응? 응. 라피의 기분 좋음 어필..."
    elif rand <= 95:
        return "라피는 지휘관이 상대해주길 바라거나 하지 않아. 응, 바라지 않아...(틱틱)"
    else:
        return "Zzzzzzzzz......지휘관, 불렀어?"


def bothelp(channel, args):
    if len(args) == 3 and args[2] == "2":
        embedhelp = discord.Embed(title="지휘관, 궁금한거 있어...?", description="궁금한거 다 봤으면 같이 코~할래?",
                                  color=0xf8f5ff)
        embedhelp.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        return channel.send(embed=embedhelp)
    else:
        embedhelp = discord.Embed(title="지휘관, 궁금한거 있어...?", description="궁금한거 다 봤으면 같이 코~할래?",
                                  color=0xf8f5ff)
        embedhelp.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embedhelp.add_field(name="!라피", value="지휘관, 지휘관. 라피, 무서워?", inline=False)
        embedhelp.add_field(name="!라피 정보", value="봇에 대한 정보를 열람합니다.", inline=False)
        embedhelp.add_field(name="!라피 도움말", value="도움말을 열람합니다.", inline=False)
        embedhelp.add_field(name="!라피 출석체크", value="출석체크를 수행합니다.", inline=False)
        embedhelp.add_field(name="!라피 포인트", value="포인트 관련 명령어를 확인합니다.", inline=False)
        embedhelp.add_field(name="!라피 도박", value="지휘관, 지휘관. 도박은 나빠...", inline=False)
        embedhelp.add_field(name="!라피 가챠", value="가챠는 나쁜 문명!", inline=False)
        embedhelp.add_field(name="!라피 저금", value="지휘관, 포인트를 저금하려고...?", inline=False)
        embedhelp.add_field(name="!라피 포인트벌이", value="지휘관에게 포인트를 벌 수 있도록 일거리를 줄게...", inline=False)
        return channel.send(embed=embedhelp)


def botinfo(channel):
    embed = discord.Embed(title="라피봇 v.0.4",
                          description="라피봇 v.0.4\n기본 기능 완료! 기능들 추가중!\n졸려... 응... 다시 자자......",
                          color=0xf8f5ff)
    embed.set_image(
        url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
    embed.add_field(name="```제작자```", value="Admiral. 레이나", inline=False)
    return channel.send(embed=embed)


# 제작중
def attendcheck(channel, authinfo, dbpass):
    if authinfo["DCTime"] < int(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y%m%d")):
        if authinfo["DCTime"] == int((datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))-datetime.timedelta(days=1)).strftime("%Y%m%d")):
            authinfo["DCStimul"] += 1
        else:
            authinfo["DCStimul"] = 1
        authinfo["DCTotal"] += 1
        authinfo["POINTS"] += 300
        authinfo["DCTime"] = int(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y%m%d"))

        mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
        mclient.Laffey.Data.update_one({"ID": authinfo["ID"]}, {"$set": authinfo})

        embed = discord.Embed(title="출석체크", description="지휘관, 잘 지냈어? 라피는 잘 지냈어, 아마도.\n응, 300 LP도 보너스로 받았어.",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```출석자```", value="[ %s ] 지휘관" % authinfo["NAME"], inline=False)
        embed.add_field(name="```출석일자```", value="%s" % datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y / %m / %d"), inline=False)
        embed.add_field(name="```연속 출석일수```", value="%d 일" % authinfo["DCStimul"], inline=False)
        embed.add_field(name="```총 출석일수```", value="%d 일" % authinfo["DCTotal"], inline=False)
        return channel.send(embed=embed)
    else:
        return channel.send("```[%s] 지휘관, 오늘은 벌써 출석체크를 했어...```" % authinfo["NAME"])


def gamble(message, args, authinfo, dbpass):
    channel = message.channel
    if len(args) == 2:
        embed = discord.Embed(title="도박", description="지휘관, 도박은 나빠...그래도 지휘관이 원한다면...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```", value="!라피 도박 (종류) : 해당 도박을 열람합니다.", inline=False)
        embed.add_field(name="```종류```",
                        value="'룰렛', '다이스배틀', '업다운', '블랙잭', '일기토', '드로우포커'", inline=False)
        return channel.send(embed=embed)
    if args[2] == "룰렛":
        return gamblefunction.roulette(channel, args, authinfo, dbpass)
    elif args[2] == "다이스배틀":
        return gamblefunction.dicebattle(channel, args, authinfo, dbpass)
    elif args[2] == "업다운":
        return gamblefunction.updown(channel, args, authinfo, dbpass)
    elif args[2] == "블랙잭":
        return gamblefunction.blackjack(channel, args, authinfo, dbpass)
    elif args[2] == "일기토":
        return gamblefunction.laffeyduel(channel, args, authinfo, dbpass)
    elif args[2] == "드로우포커":
        return gamblefunction.drawpoker(channel, args, authinfo, dbpass)
    return channel.send("지휘관, 그건 못해...")


async def gacha(message, args, authinfo, dbpass):
    channel = message.channel
    if len(args) == 2:
        embed = discord.Embed(title="가챠", description="역시 가챠는 나쁜 문명! 분쇄한다!",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```!라피 가챠 뽑기```", value="가챠! 가챠! 가챠 돌릴꼬얌!", inline=False)
        embed.add_field(name="```!라피 가챠 검색 (번호)```", value="해당 번호의 함선 카드를 검색합니다.", inline=False)
        embed.add_field(name="```!라피 가챠 확인```", value="소지하고 있는 카드들을 확인합니다.", inline=False)
        embed.add_field(name="```!라피 가챠 판매 (번호) (개수)```", value="소지하고 있는 카드를 팝니다.", inline=False)
        await channel.send(embed=embed)
    else:
        if args[2] == "뽑기":
            await gachafunction.letsgacha(message, args, authinfo, dbpass)
        elif args[2] == "확인":
            await gachafunction.gachacheck(message, args, authinfo, dbpass)
        elif args[2] == "판매":
            await gachafunction.gachasell(message, args, authinfo, dbpass)
        elif args[2] == "검색":
            await gachafunction.gachasearch(message, args, authinfo, dbpass)
        else:
            await channel.send("지휘관, 그건 할 수 없어...")


async def debug(message, args, authinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    dev = mclient.Laffey.Data.find_one({"DEVELOPER": "KAIRI"})
    if authinfo["ID"] == dev["ID"]:
        if len(args) == 2:
            embed = discord.Embed(title="디버그 권한 승인", description="관리자용 디버그 커맨드 목록",
                                  color=0xf8f5ff)
            embed.set_thumbnail(
                url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
            embed.add_field(name="```!라피 디버그 도박 (코드)```", value="해당 코드의 도박을 리로드합니다.", inline=False)
            embed.add_field(name="```!라피 디버그 포인트 (대상) (수량)```", value="해당 대상의 포인트를 설정합니다.", inline=False)
            embed.add_field(name="```!라피 디버그 가챠```", value="가챠를 리로드합니다.", inline=False)
            await message.channel.send(embed=embed)
        elif args[2] == "도박":
            if len(args) != 4:
                await message.channel.send("커맨드 사용법 불일치.")
                return
            target = mclient.Laffey.Gamble.find_one({"GAME": args[3]})
            if target is None:
                await message.channel.send("대상 검색 실패")
                return
            mclient.Laffey.Data.update_one({"GAME": target["GAME"]}, {"$set": {"PLAYING": False}})
            await message.channel.send("리로드 완료. ( TARGET : %s )" % target["GAME"])
        elif args[2] == "포인트":
            if len(args) != 5 or not args[4].isdigit():
                await message.channel.send("커맨드 사용법 불일치.")
                return
            target = mclient.Laffey.Data.find_one({"NAME": args[3]})
            if target is None:
                await message.channel.send("대상 검색 실패")
                return
            mclient.Laffey.Data.update_one({"ID": target["ID"]}, {"$set": {"POINTS": int(args[4])}})
            await message.channel.send("설정 완료. 대상 : %s / 수량 : %d LP" % (target["NAME"], int(args[4])))
        elif args[2] == "가챠":
            mclient.Gacha.System.update_one({"SYSTEM": "GACHA"}, {"$set": {"PLAYING": False, "USERID": 0, "USERNAME": "LAFFEY", "CURRENTMACHINE": 0}})
            await message.channel.send("가챠 리로드 완료.")
        else:
            await message.channel.send("커맨드 인식 불가.")
    else:
        await message.channel.send("디버그 권한 확인 실패.")



