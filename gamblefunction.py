import random
import discord
import pymongo
import asyncio


def roulette(channel, args, authinfo, dbpass):
    if len(args) == 3:
        embed = discord.Embed(title="룰렛", description="지휘관, 도박은 나빠...그래도 지휘관이 원한다면...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```", value="룰렛은 1회당 100 LP가 소모됩니다. 확률조작 안합니다. 포인트 잃어도 라피는 모릅니다.", inline=False)
        embed.add_field(name="```사용법 : !라피 도박 룰렛 (1~30/0/홀/짝)```",
                        value="가상의 룰렛을 돌립니다.(룰렛과 실제 룰이 같지 않습니다.)\n0은 홀/짝 어디에도 속하지 않습니다.\n당첨시 배당금은 다음과 같습니다." +
                              "\n홀/짝 : 200 LP\n1~30 : 3000 LP\n0 : 5000 LP", inline=False)
        return channel.send(embed=embed)
    if args[3] in "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 홀 짝" and len(args) == 4:
        if authinfo["POINTS"] < 100:
            return channel.send("지휘관...포인트가 모자라...")
        num = random.randint(0, 30)
        win = 0
        if args[3] == "홀":
            if num != 0 and num % 2 == 1:
                win = 200
        elif args[3] == "짝":
            if num != 0 and num % 2 == 0:
                win = 200
        elif args[3] == str(num):
            if str(num) == "0":
                win = 5000
            else:
                win = 3000
        authinfo["POINTS"] = authinfo["POINTS"] - 100 + win
        mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
        mclient.Laffey.Data.update_one({"ID": authinfo["ID"]}, {"$set": authinfo})
        embed = discord.Embed(title="룰렛 결과", description="베팅 : %s  / 나온 숫자 : %s\n당첨 포인트 : %d LP\n소지 포인트 : %d LP" % (args[3], str(num), win, authinfo["POINTS"]),
                              color=0xf8f5ff)
        return channel.send(embed=embed)
    return channel.send("지휘관...사용법이 틀렸어...")


def dicebattle(channel, args, authinfo, dbpass):
    if len(args) == 3:
        embed = discord.Embed(title="다이스배틀", description="지휘관, 도박은 나빠...그래도 지휘관이 원한다면...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```", value="다이스배틀은 주사위게임의 일종입니다. 베팅은 10~5000 LP만 가능합니다. 확률조작 안합니다. 포인트 잃어도 라피는 모릅니다.", inline=False)
        embed.add_field(name="```사용법 : !라피 도박 다이스배틀 (베팅금)```",
                        value="워리어스 라이즈 오브 글로리에 나온 여관 도박을 바탕으로 합니다.\n주사위를 굴릴 시 최대 5개까지 굴립니다." +
                              "\n주사위를 전부 소모하지 않아도 던지는걸 중단할 수 있습니다.\n최종적으로 상대보다 체력이 많으면 승리합니다.\n주사위의 눈은 다음과 같습니다." +
                              "\n🗡️ : 상대에게 1 피해 (x2)" +
                              "\n🛡 : 자신에게 1 보호막/최대 5중첩 (x1)" +
                              "\n☠ : 자신에게 1 피해 (x1)" +
                              "\n🎲 : 다시 주사위 칸으로 (x2)", inline=False)
        embed.add_field(name="```배당금```", value="승리 : x2.2 / 비김 : x1 / 패배 : x0", inline=False)
        return channel.send(embed=embed)
    if args[3].isdigit() and len(args) == 4 and int(args[3]) > 0:
        return dicegame(channel, int(args[3]), authinfo, dbpass)
    else:
        return channel.send("지휘관...베팅할 양을 제대로 입력해줘...")


def dicegame(channel, bet, authinfo, dbpass):
    if authinfo["POINTS"] < bet:
        return channel.send("지휘관...포인트가 모자라...")
    if not 10 <= bet <= 5000:
        return channel.send("지휘관...베팅은 10~5000 LP만 가능해...")
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    db = mclient.Laffey
    if db.Gamble.find_one({"GAME": "DICEBATTLE"})["PLAYING"] is True:
        return channel.send("지휘관...이미 누군가 다이스배틀을 진행중이야...")
    authinfo["POINTS"] -= bet
    db.Data.update_one({"ID": authinfo["ID"]}, {"$set": {"POINTS": authinfo["POINTS"], "ISONACT": True}})
    db.Gamble.update_one({"GAME": "DICEBATTLE"}, {"$set": {"PLAYING": True, "BET": bet, "USERID": authinfo["ID"], "USERNICK": authinfo["NAME"], "LAFFEYHP": 10, "USERHP": 10, "LAFFEYSHIELD": 0, "USERSHIELD": 0, "LAFFEYDICE": 10, "USERDICE": 10}})
    embed = discord.Embed(title="다이스배틀 시작!", description="[%s] 지휘관이 진행중! 배팅액 : %d LP" % (authinfo["NAME"], bet),
                          color=0xf8f5ff)
    embed.add_field(name="```현재 턴```", value="[%s]" % authinfo["NAME"], inline=False)
    embed.add_field(name="```라피```", value="HP : 10 / 방어도 : 0\n🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲\n", inline=False)
    embed.add_field(name="\u200b", value="\u200b\n\u200b", inline=False)
    embed.add_field(name="```[%s]```" % authinfo["NAME"], value="🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲\nHP : 10 / 방어도 : 0", inline=False)
    return channel.send(embed=embed)


async def dicegamefirstreact(message, client):
    if str(message.author.id) == str(client.user.id):
        if len(message.embeds) >= 1:
            if message.embeds[0].title == "다이스배틀 시작!":
                await message.add_reaction("🎲")
                await message.add_reaction('⏹')


async def dicegameonreact(reaction, user, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    game = mclient.Laffey.Gamble.find_one({"GAME": "DICEBATTLE"})
    if reaction.message.embeds[0].title == "다이스배틀 시작!" or reaction.message.embeds[0].title == "다이스배틀 진행중!":
        if user.id == game["USERID"] and game["PLAYING"] is True:
            # Basic Structure
            embed = discord.Embed(title="다이스배틀 진행중!", description="[%s] 지휘관이 진행중! 배팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                  color=0xf8f5ff)
            embed.add_field(name="```공격자```", value="[%s]" % game["USERNICK"], inline=False)
            embed.add_field(name="```라피```", value="HP : %d / 방어도 : %d\n%s\n\n\n" % (game["LAFFEYHP"], game["LAFFEYSHIELD"], "🎲" * game["LAFFEYDICE"]), inline=False)
            embed.add_field(name="\u200b", value="\u200b\n\u200b", inline=False)
            embed.add_field(name="```[%s]```" % game["USERNICK"], value="%s\nHP : %d / 방어도 : %d" % ("🎲" * game["USERDICE"], game["USERHP"], game["USERSHIELD"]), inline=False)
            # 지휘관 턴!
            if str(reaction.emoji) == "🎲":
                await reaction.message.clear_reactions()
                dice, game = diceturnresult(diceroll(game["USERDICE"]), game, True)
                dice_com = "  ".join(dice)
                embed = discord.Embed(title="다이스배틀 진행중!", description="[%s] 지휘관이 진행중! 배팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```공격자```", value="%s" % game["USERNICK"], inline=False)
                embed.add_field(name="```라피```", value="HP : %d / 방어도 : %d\n%s\n\n\n" % (game["LAFFEYHP"], game["LAFFEYSHIELD"], "🎲" * game["LAFFEYDICE"]), inline=False)
                embed.add_field(name="\u200b", value="%s\n\u200b" % dice_com, inline=False)
                embed.add_field(name="```[%s]```" % game["USERNICK"], value="%s\nHP : %d / 방어도 : %d" % ("🎲" * game["USERDICE"], game["USERHP"], game["USERSHIELD"]), inline=False)
                await reaction.message.edit(embed=embed)
                if game["USERHP"] > 0 and game["LAFFEYHP"] > 0:
                    await asyncio.sleep(3)
                    dice, game = diceturnresult(diceroll(game["LAFFEYDICE"]), game, False)
                    dice_com = "  ".join(dice)
                    embed = discord.Embed(title="다이스배틀 진행중!", description="[%s] 지휘관이 진행중! 배팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                          color=0xf8f5ff)
                    embed.add_field(name="```공격자```", value="라피", inline=False)
                    embed.add_field(name="```라피```", value="HP : %d / 방어도 : %d\n%s\n\n\n" % (game["LAFFEYHP"], game["LAFFEYSHIELD"], "🎲" * game["LAFFEYDICE"]), inline=False)
                    embed.add_field(name="\u200b", value="%s\n\u200b" % dice_com, inline=False)
                    embed.add_field(name="```[%s]```" % game["USERNICK"], value="%s\nHP : %d / 방어도 : %d" % ("🎲" * game["USERDICE"], game["USERHP"], game["USERSHIELD"]), inline=False)
                    await reaction.message.edit(embed=embed)
                    if game["USERHP"] <= 0 or game["LAFFEYHP"] <= 0:
                        await dicegameresult(reaction, game, dbpass)
                    else:
                        mclient.Laffey.Gamble.update_one({"GAME": "DICEBATTLE"}, {"$set": game})
                        if game["USERDICE"] > 0:
                            await reaction.message.add_reaction("🎲")
                        await reaction.message.add_reaction('⏹')
                else:
                    await dicegameresult(reaction, game, dbpass)
            # 난 더이상 주사위를 던지지 않겠다!
            if str(reaction.emoji) == '⏹':
                await reaction.message.clear_reactions()
                embed = discord.Embed(title="다이스배틀 진행중!", description="[%s] 지휘관이 진행중! 배팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```공격자```", value="라피(지휘관 더이상 턴 중단)", inline=False)
                embed.add_field(name="```라피```", value="HP : %d / 방어도 : %d\n%s\n\n\n" % (game["LAFFEYHP"], game["LAFFEYSHIELD"], "🎲" * game["LAFFEYDICE"]), inline=False)
                embed.add_field(name="\u200b", value="\u200b\n\u200b", inline=False)
                embed.add_field(name="```[%s]```" % game["USERNICK"], value="%s\nHP : %d / 방어도 : %d" % ("🎲" * game["USERDICE"], game["USERHP"], game["USERSHIELD"]), inline=False)
                await reaction.message.edit(embed=embed)
                await asyncio.sleep(1)
                while game["LAFFEYDICE"] > 0:
                    if game["USERHP"] > 0 and game["LAFFEYHP"] > 0:
                        dice, game = diceturnresult(diceroll(game["LAFFEYDICE"]), game, False)
                        dice_com = "  ".join(dice)
                        embed = discord.Embed(title="다이스배틀 진행중!", description="[%s] 지휘관이 진행중! 배팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                              color=0xf8f5ff)
                        embed.add_field(name="```공격자```", value="라피(지휘관 더이상 턴 중단)", inline=False)
                        embed.add_field(name="```라피```", value="HP : %d / 방어도 : %d\n%s\n\n\n" % (game["LAFFEYHP"], game["LAFFEYSHIELD"], "🎲" * game["LAFFEYDICE"]), inline=False)
                        embed.add_field(name="\u200b", value="%s\n\u200b" % dice_com, inline=False)
                        embed.add_field(name="```[%s]```" % game["USERNICK"], value="%s\nHP : %d / 방어도 : %d" % ("🎲" * game["USERDICE"], game["USERHP"], game["USERSHIELD"]), inline=False)
                        await reaction.message.edit(embed=embed)
                        await asyncio.sleep(2)
                    else:
                        await dicegameresult(reaction, game, dbpass)
                await dicegameresult(reaction, game, dbpass)


async def dicegameresult(reaction, game, dbpass):
    if game["USERHP"] < game["LAFFEYHP"]:
        iswin = "패배"
        game["BET"] *= 0
    elif game["USERHP"] > game["LAFFEYHP"]:
        iswin = "승리"
        game["BET"] = int(game["BET"] * 2.2)
    else:
        iswin = "비겼음"
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    userdata = mclient.Laffey.Data.find_one({"ID": game["USERID"]})
    mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"POINTS": userdata["POINTS"]+game["BET"], "ISONACT": False}})
    embed = discord.Embed(title="다이스배틀 종료!", description="[%s] 지휘관 %s! 배당금 : %d LP" % (game["USERNICK"], iswin, game["BET"]),
                          color=0xf8f5ff)
    embed.add_field(name="```공격자```", value="종료됨", inline=False)
    embed.add_field(name="```라피```", value="HP : %d / 방어도 : %d\n%s\n\n\n" % (game["LAFFEYHP"], game["LAFFEYSHIELD"], "🎲" * game["LAFFEYDICE"]), inline=False)
    embed.add_field(name="\u200b", value="배틀 종료!\n\u200b", inline=False)
    embed.add_field(name="```[%s]```" % game["USERNICK"], value="%s\nHP : %d / 방어도 : %d" % ("🎲" * game["USERDICE"], game["USERHP"], game["USERSHIELD"]), inline=False)
    await reaction.message.edit(embed=embed)
    mclient.Laffey.Gamble.update_one({"GAME": "DICEBATTLE"}, {"$set": {"PLAYING": False}})


def diceturnresult(nums, status, isuser):
    # Dice - 1,2:Re/3,4:Def/5:Atk/6:Sui
    strdice = []
    for i in range(0, len(nums)):
        if nums[i] <= 5:
            if nums[i] <= 4:
                if nums[i] <= 2:
                    strdice.append("🎲")
                    continue
                strdice.append("🛡")
                continue
            strdice.append("🗡️")
            continue
        strdice.append("☠")
    nums.sort()
    for i in range(0, len(nums)):
        if status["USERHP"] <= 0 or status["LAFFEYHP"] <= 0:
            break
        if nums[i] == 3 or nums[i] == 4:
            if isuser is True:
                status["USERDICE"] -= 1
                status["USERSHIELD"] += 1
                if status["USERSHIELD"] > 5:
                    status["USERSHIELD"] = 5
            else:
                status["LAFFEYDICE"] -= 1
                status["LAFFEYSHIELD"] += 1
                if status["LAFFEYSHIELD"] > 5:
                    status["LAFFEYSHIELD"] = 5
        elif nums[i] == 5:
            if isuser is True:
                status["USERDICE"] -= 1
                if status["LAFFEYSHIELD"] > 0:
                    status["LAFFEYSHIELD"] -= 1
                else:
                    status["LAFFEYHP"] -= 1
            else:
                status["LAFFEYDICE"] -= 1
                if status["USERSHIELD"] > 0:
                    status["USERSHIELD"] -= 1
                else:
                    status["USERHP"] -= 1
        elif nums[i] == 6:
            if isuser is True:
                status["USERDICE"] -= 1
                if status["USERSHIELD"] > 0:
                    status["USERSHIELD"] -= 1
                else:
                    status["USERHP"] -= 1
            else:
                status["LAFFEYDICE"] -= 1
                if status["LAFFEYSHIELD"] > 0:
                    status["LAFFEYSHIELD"] -= 1
                else:
                    status["LAFFEYHP"] -= 1
    return strdice, status


def diceroll(counts):
    # Dice - 1:Atk/2,3:Def/4,5:Re/6:Sui
    num = []
    if counts < 5:
        for i in range(0, counts):
            num.append(random.randint(1, 6))
    else:
        for i in range(0, 5):
            num.append(random.randint(1, 6))
    return num


def updown(channel, args, authinfo, dbpass):
    if len(args) == 3:
        embed = discord.Embed(title="업다운", description="지휘관, 도박은 나빠...그래도 지휘관이 원한다면...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```", value="업다운은 카드게임의 일종입니다. 베팅은 10~5000 LP만 가능합니다. 확률조작 안합니다. 포인트 잃어도 라피는 모릅니다.", inline=False)
        embed.add_field(name="```사용법 : !라피 도박 업다운 (베팅금)```",
                        value="말 그대로 다음 카드가 높은가 낮은가를 맞추는 게임입니다.\n최대 4중첩까지 가능합니다.\n동일하면 그냥 넘어갑니다." +
                              "\n적어도 두 번 이상 맞춰야 중단이 가능합니다.\n카드에 문양은 없습니다. A는 무조건 1입니다." +
                              "\n🔺 : UP / 🔻 : DOWN / ⏹ : STOP", inline=False)
        embed.add_field(name="```배당금```", value="맞출 때마다 : 베팅액의 x0.4 / 틀림 : x0", inline=False)
        return channel.send(embed=embed)
    if args[3].isdigit() and len(args) == 4 and int(args[3]) > 0:
        return updownstart(channel, int(args[3]), authinfo, dbpass)
    else:
        return channel.send("지휘관...베팅할 양을 제대로 입력해줘...")


def updownstart(channel, bet, authinfo, dbpass):
    if authinfo["POINTS"] < bet:
        return channel.send("지휘관...포인트가 모자라...")
    if not 10 <= bet <= 5000:
        return channel.send("지휘관...베팅은 10~5000 LP만 가능해...")
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    db = mclient.Laffey
    if db.Gamble.find_one({"GAME": "UPDOWN"})["PLAYING"] is True:
        return channel.send("지휘관...이미 누군가 UPDOWN을 진행중이야...")
    authinfo["POINTS"] -= bet
    updowncards = random.sample([1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13], 5)
    if updowncards[0] == 1:
        cards = "A"
    elif updowncards[0] == 11:
        cards = "J"
    elif updowncards[0] == 12:
        cards = "Q"
    elif updowncards[0] == 13:
        cards = "K"
    else:
        cards = str(updowncards[0])
    db.Data.update_one({"ID": authinfo["ID"]}, {"$set": {"POINTS": authinfo["POINTS"], "ISONACT": True}})
    db.Gamble.update_one({"GAME": "UPDOWN"}, {"$set": {"PLAYING": True, "BET": bet, "USERID": authinfo["ID"], "USERNICK": authinfo["NAME"], "STACK": 0, "WIN": bet, "C1": updowncards[0], "C2": updowncards[1], "C3": updowncards[2], "C4": updowncards[3], "C5": updowncards[4]}})
    embed = discord.Embed(title="UPDOWN 시작!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (authinfo["NAME"], bet),
                          color=0xf8f5ff)
    embed.add_field(name="```현재 : 진행 전```", value="베팅금 : %d LP / 배당금 : %d LP" % (bet, bet), inline=False)
    embed.add_field(name="```Cards```", value="\u200b\n%s  ⬜  ⬜  ⬜  ⬜\n\u200b" % cards, inline=False)
    return channel.send(embed=embed)


async def updownfirstreact(message, client):
    if str(message.author.id) == str(client.user.id):
        if len(message.embeds) >= 1:
            if message.embeds[0].title == "UPDOWN 시작!":
                await message.add_reaction("🔺")
                await message.add_reaction("🔻")


async def updownonreact(reaction, user, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    game = mclient.Laffey.Gamble.find_one({"GAME": "UPDOWN"})

    if reaction.message.embeds[0].title == "UPDOWN 시작!" or reaction.message.embeds[0].title == "UPDOWN 진행중!":
        if user.id == game["USERID"] and game["PLAYING"] is True:
            user = mclient.Laffey.Data.find_one({"ID": game["USERID"]})
            # Basic Structure
            embed = discord.Embed(title="UPDOWN 진행중!", description="[%s] 지휘관이 진행중! 배팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                  color=0xf8f5ff)
            embed.add_field(name="```결과 : 진행 전 / 베팅: 진행 전```", value="베팅금 : %d LP / 배당금 : %d LP" % (game["BET"], game["WIN"]), inline=False)
            embed.add_field(name="```Cards```", value="\u200b\n%s  ⬜  ⬜  ⬜  ⬜\n\u200b" % str(game["C1"]), inline=False)
            # 더 한다!
            if str(reaction.emoji) == "🔺" or str(reaction.emoji) == "🔻":
                await reaction.message.clear_reactions()
                status, game = updownresult(str(reaction.emoji), updowncheck(game), game)
                cards = []
                for i in range(0, game["STACK"]+1):
                    if game["C"+str(i+1)] == 1:
                        cards.append("A")
                    elif game["C"+str(i+1)] == 11:
                        cards.append("J")
                    elif game["C"+str(i+1)] == 12:
                        cards.append("Q")
                    elif game["C"+str(i+1)] == 13:
                        cards.append("K")
                    else:
                        cards.append(str(game["C"+str(i+1)]))
                for i in range(0, 4-game["STACK"]):
                    cards.append("⬜")
                cards_c = " ".join(cards)
                embed = discord.Embed(title="UPDOWN 진행중!", description="[%s] 지휘관이 진행중! 배팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```결과 : %s / 베팅 : %s```" % (status, str(reaction.emoji)), value="베팅금 : %d LP / 배당금 : %d LP" % (game["BET"], game["WIN"]), inline=False)
                embed.add_field(name="```Cards```", value="\u200b\n%s\n\u200b" % cards_c, inline=False)
                await reaction.message.edit(embed=embed)
                # 아이고 포인트를 날려먹었네.
                if game["WIN"] <= 0:
                    cards = []
                    for i in range(0, 5):
                        if game["C" + str(i + 1)] == 1:
                            cards.append("A")
                        elif game["C" + str(i + 1)] == 11:
                            cards.append("J")
                        elif game["C" + str(i + 1)] == 12:
                            cards.append("Q")
                        elif game["C" + str(i + 1)] == 13:
                            cards.append("K")
                        else:
                            cards.append(str(game["C" + str(i + 1)]))
                    await asyncio.sleep(1)
                    embed = discord.Embed(title="UPDOWN 종료!", description="[%s] 지휘관은 포인트를 날렸습니다! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                          color=0xf8f5ff)
                    embed.add_field(name="```결과 : %s / 베팅 : %s```" % (status, str(reaction.emoji)), value="베팅금 : %d LP / 배당금 : %d LP" % (game["BET"], game["WIN"]), inline=False)
                    embed.add_field(name="```카드 공개!```", value="\u200b\n%s %s %s %s %s\n\u200b" % (cards[0], cards[1], cards[2], cards[3], cards[4]), inline=False)
                    mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"ISONACT": False}})
                    mclient.Laffey.Gamble.update_one({"GAME": "UPDOWN"}, {"$set": {"PLAYING": False, "BET": 0, "USERID": 0, "USERNICK": "NOONE", "STACK": 0, "WIN": 0, "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0}})
                    await reaction.message.edit(embed=embed)
                # 게임 끝!
                elif game["STACK"] >= 4:
                    await asyncio.sleep(1)
                    embed = discord.Embed(title="UPDOWN 종료!", description="[%s] 지휘관이 포인트를 쓸어갑니다! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                          color=0xf8f5ff)
                    embed.add_field(name="```결과 : %s / 베팅 : %s```" % (status, str(reaction.emoji)), value="베팅금 : %d LP / 배당금 : %d LP" % (game["BET"], game["WIN"]), inline=False)
                    embed.add_field(name="```카드 공개!```", value="\u200b\n%s %s %s %s %s\n\u200b" % (cards[0], cards[1], cards[2], cards[3], cards[4]), inline=False)
                    await reaction.message.edit(embed=embed)
                    user = mclient.Laffey.Data.find_one({"ID": game["USERID"]})
                    mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"POINTS": user["POINTS"] + game["WIN"], "ISONACT": False}})
                    mclient.Laffey.Gamble.update_one({"GAME": "UPDOWN"}, {"$set": {"PLAYING": False, "BET": 0, "USERID": 0, "USERNICK": "NOONE", "STACK": 0, "WIN": 0, "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0}})
                else:
                    mclient.Laffey.Gamble.update_one({"GAME": "UPDOWN"}, {"$set": {"STACK": game["STACK"], "WIN": game["WIN"]}})
                    await reaction.message.add_reaction("🔺")
                    await reaction.message.add_reaction("🔻")
                    if game["STACK"] >= 2:
                        await reaction.message.add_reaction("⏹")
            # 그만!
            if str(reaction.emoji) == '⏹':
                await reaction.message.clear_reactions()
                cards = []
                for i in range(0, 5):
                    if game["C" + str(i + 1)] == 1:
                        cards.append("A")
                    elif game["C" + str(i + 1)] == 11:
                        cards.append("J")
                    elif game["C" + str(i + 1)] == 12:
                        cards.append("Q")
                    elif game["C" + str(i + 1)] == 13:
                        cards.append("K")
                    else:
                        cards.append(str(game["C" + str(i + 1)]))
                embed = discord.Embed(title="UPDOWN 종료!", description="[%s] 지휘관이 도전을 멈춥니다! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```결과 : 중단! / 베팅 : 중단!```", value="베팅금 : %d LP / 배당금 : %d LP" % (game["BET"], game["WIN"]), inline=False)
                embed.add_field(name="```카드 공개!```", value="\u200b\n%s %s %s %s %s\n\u200b" % (cards[0], cards[1], cards[2], cards[3], cards[4]), inline=False)
                mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"POINTS": user["POINTS"] + game["WIN"], "ISONACT": False}})
                mclient.Laffey.Gamble.update_one({"GAME": "UPDOWN"}, {"$set": {"PLAYING": False, "BET": 0, "USERID": 0, "USERNICK": "NOONE", "STACK": 0, "WIN": 0, "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0}})
                await reaction.message.edit(embed=embed)


def updowncheck(game):
    if game["STACK"] >= 4:
        return "⏹"
    if game["C"+str(game["STACK"]+1)] > game["C"+str(game["STACK"]+2)]:
        return "🔻"
    elif game["C"+str(game["STACK"]+1)] < game["C"+str(game["STACK"]+2)]:
        return "🔺"
    elif game["C"+str(game["STACK"]+1)] == game["C"+str(game["STACK"]+2)]:
        return "KEEP"
    else:
        return "ERROR"


def updownresult(emoji, check, game):
    if check == "ERROR":
        status = "ERROR"
        return status, game
    if check == "KEEP":
        status = check
        game["STACK"] += 1
        return status, game
    if emoji == check:
        status = check
        game["STACK"] += 1
        game["WIN"] += int(game["BET"] * 0.4)
        return status, game
    else:
        status = check
        game["WIN"] *= 0
        game["STACK"] += 1
        return status, game


def blackjack(channel, args, authinfo, dbpass):
    if len(args) == 3:
        embed = discord.Embed(title="블랙잭", description="지휘관, 도박은 나빠...그래도 지휘관이 원한다면...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```", value="블랙잭은 카드게임의 일종입니다. 베팅은 10~5000 LP 까지 가능합니다.\n확률조작 안합니다. 포인트 잃어도 라피는 모릅니다.", inline=False)
        embed.add_field(name="```사용법 : !라피 도박 블랙잭 (베팅금)```",
                        value="숫자 21에 최대한 가깝게 하는 것을 목표로 하며 더 가까운 측이 승리합니다.\n21이 넘어가면 Bust!가 됩니다.\n라피는 17 이상이 되지 않으면 계속 카드를 받아야 합니다." +
                              "\n처음 두장으로 21이 되면 Blackjack!으로 승리합니다.\n항복은 처음에만 가능합니다.\nJ,Q,K는 10이며 A는 1혹은 11로 턴마다 21에 가까운 쪽으로 적용됩니다." +
                              "\n 🃏 : HIT - 카드를 1장 더 받습니다." +
                              "\n 💵 : DOUBLE DOWN - 다음 카드를 마지막으로 받고 베팅액을 2배로 올립니다." +
                              "\n ⏹ : STAND - 더이상 카드를 받지 않습니다." +
                              "\n 🏳 : SURRENDER - 항복하고 베팅액의 절반을 받아갑니다.", inline=False)
        embed.add_field(name="```배당금```", value="블랙잭 : x3 / 승리 : x2 / 패배 : x0 / 항복 x0.5(소수점 버림)", inline=False)
        return channel.send(embed=embed)
    if args[3].isdigit() and len(args) == 4 and int(args[3]) > 0:
        return blackjackstart(channel, int(args[3]), authinfo, dbpass)
    else:
        return channel.send("지휘관...베팅할 양을 제대로 입력해줘...")


def blackjackstart(channel, bet, authinfo, dbpass):
    if authinfo["POINTS"] < bet:
        return channel.send("지휘관...포인트가 모자라...")
    if not 10 <= bet <= 5000:
        return channel.send("지휘관...베팅은 10~5000 LP만 가능해...")
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    db = mclient.Laffey
    if db.Gamble.find_one({"GAME": "BLACKJACK"})["PLAYING"] is True:
        return channel.send("지휘관...이미 누군가 블랙잭을 진행중이야...")
    authinfo["POINTS"] -= bet
    blackjackcards = ["A", "A", "A", "A", "2", "2", "2", "2", "3", "3", "3", "3", "4", "4", "4", "4", "5", "5", "5", "5", "6", "6", "6", "6", "7", "7", "7", "7", "8", "8", "8", "8", "9", "9", "9", "9", "10", "10", "10", "10", "J", "J", "J", "J", "Q", "Q", "Q", "Q", "K", "K", "K", "K"]
    gamecards = random.sample(blackjackcards, 20)
    db.Data.update_one({"ID": authinfo["ID"]}, {"$set": {"POINTS": authinfo["POINTS"], "ISONACT": True}})
    db.Gamble.update_one({"GAME": "BLACKJACK"}, {"$set": {"PLAYING": True, "BET": bet, "USERID": authinfo["ID"], "USERNICK": authinfo["NAME"], "CARDS": gamecards, "FIRSTTURN": True, "LAFFEY": {"ACE": 0, "COUNT": 0, "COUNT_A": 0, "CARDS": [], "STATUS": "0"}, "USER": {"ACE": 0, "COUNT": 0, "COUNT_A": 0, "CARDS": [], "STATUS": "0"}}})
    embed = discord.Embed(title="블랙잭 시작!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (authinfo["NAME"], bet),
                          color=0xf8f5ff)
    embed.add_field(name="```라피```", value="진행 전", inline=False)
    embed.add_field(name="\u200b", value="\u200b\n\u200b", inline=False)
    embed.add_field(name="```지휘관```", value="진행 전", inline=False)
    return channel.send(embed=embed)


async def blackjackfirstreact(message, client):
    if str(message.author.id) == str(client.user.id):
        if len(message.embeds) >= 1:
            if message.embeds[0].title == "블랙잭 시작!":
                await message.add_reaction("▶")


async def blackjackonreact(reaction, user, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    game = mclient.Laffey.Gamble.find_one({"GAME": "BLACKJACK"})
    userdata = mclient.Laffey.Data.find_one({"ID": game["USERID"]})
    if reaction.message.embeds[0].title == "블랙잭 시작!" or reaction.message.embeds[0].title == "블랙잭 진행중!":
        if user.id == game["USERID"] and game["PLAYING"] is True:
            # 처음 턴!
            if str(reaction.emoji) == "▶" and game["FIRSTTURN"] is True:
                await reaction.message.clear_reactions()
                game["FIRSTTURN"] = False
                game = bjcarddraw(game, True)
                game = bjcarddraw(game, False)
                game = bjcarddraw(game, True)
                game = bjcarddraw(game, False)
                game = blackjackcalculate(game, True)
                game = blackjackcalculate(game, False)
                embed = discord.Embed(title="블랙잭 진행중!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```라피```", value="지휘관 차례 진행중", inline=False)
                embed.add_field(name="%s ⬜" % str(game["LAFFEY"]["CARDS"][0]), value="\u200b\n**%s**" % " ".join(game["USER"]["CARDS"]), inline=False)
                embed.add_field(name="```지휘관```", value="%s" % str(game["USER"]["STATUS"]), inline=False)
                await reaction.message.edit(embed=embed)
                # 어라? 블랙잭이야?
                if game["USER"]["STATUS"] == "BLACKJACK":
                    await asyncio.sleep(1)
                    if game["LAFFEY"]["STATUS"] == "BLACKJACK":
                        await blackjackdraw(reaction, game, dbpass)
                    else:
                        await blackjackwin(reaction, game, dbpass)
                # 잉 운도 지지리 없지 시작부터 버스트라니.
                elif game["USER"]["STATUS"] == "BUST":
                    await asyncio.sleep(1)
                    if game["LAFFEY"]["STATUS"] == "BUST":
                        await blackjackdraw(reaction, game, dbpass)
                    else:
                        await blackjacklose(reaction, game, dbpass)
                else:
                    mclient.Laffey.Gamble.update_one({"GAME": "BLACKJACK"}, {"$set": game})
                    await reaction.message.add_reaction("🃏")
                    if userdata["POINTS"] >= game["BET"]:
                        await reaction.message.add_reaction("💵")
                    await reaction.message.add_reaction("⏹")
                    await reaction.message.add_reaction("🏳")
            # 두번째 턴부터!
            if str(reaction.emoji) == "🃏" and game["FIRSTTURN"] is False:
                await reaction.message.clear_reactions()
                game = bjcarddraw(game, True)
                game = blackjackcalculate(game, True)
                embed = discord.Embed(title="블랙잭 진행중!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```라피```", value="지휘관 차례 진행중", inline=False)
                embed.add_field(name="%s ⬜" % str(game["LAFFEY"]["CARDS"][0]), value="\u200b\n**%s**" % " ".join(game["USER"]["CARDS"]), inline=False)
                embed.add_field(name="```지휘관```", value="%s" % str(game["USER"]["STATUS"]), inline=False)
                await reaction.message.edit(embed=embed)
                if game["USER"]["STATUS"] == "BUST":
                    await asyncio.sleep(1)
                    await blackjacklose(reaction, game, dbpass)
                else:
                    mclient.Laffey.Gamble.update_one({"GAME": "BLACKJACK"}, {"$set": game})
                    await reaction.message.add_reaction("🃏")
                    if userdata["POINTS"] >= game["BET"]:
                        await reaction.message.add_reaction("💵")
                    await reaction.message.add_reaction("⏹")
            # 더블 다운!
            if userdata["POINTS"] >= game["BET"] and str(reaction.emoji) == "💵" and game["FIRSTTURN"] is False:
                await reaction.message.clear_reactions()
                game = bjcarddraw(game, True)
                game = blackjackcalculate(game, True)
                mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"POINTS": userdata["POINTS"] - game["BET"]}})
                game["BET"] *= 2
                embed = discord.Embed(title="블랙잭 진행중!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```라피```", value="지휘관 더블 다운!", inline=False)
                embed.add_field(name="%s ⬜" % str(game["LAFFEY"]["CARDS"][0]), value="\u200b\n**%s**" % " ".join(game["USER"]["CARDS"]), inline=False)
                embed.add_field(name="```지휘관```", value="%s" % str(game["USER"]["STATUS"]), inline=False)
                await reaction.message.edit(embed=embed)
                if game["USER"]["STATUS"] == "BUST":
                    if game["LAFFEY"]["STATUS"] != "BUST":
                        await asyncio.sleep(1)
                        await blackjacklose(reaction, game, dbpass)
                    else:
                        await asyncio.sleep(1)
                        await blackjackdraw(reaction, game, dbpass)
                elif game["LAFFEY"]["STATUS"] == "BLACKJACK":
                    await blackjacklose(reaction, game, dbpass)
                elif game["LAFFEY"]["STATUS"] == "BUST":
                    await blackjackwin(reaction, game, dbpass)
                else:
                    game = await blackjacklaffey(reaction, game)
                    if game["LAFFEY"]["STATUS"] == "BUST":
                        await blackjackwin(reaction, game, dbpass)
                    elif game["LAFFEY"]["STATUS"] == game["USER"]["STATUS"]:
                        await blackjackdraw(reaction, game, dbpass)
                    else:
                        await blackjacklose(reaction, game, dbpass)
            # 스탠드!
            if str(reaction.emoji) == "⏹" and game["FIRSTTURN"] is False:
                await reaction.message.clear_reactions()
                if game["LAFFEY"]["STATUS"] == "BLACKJACK":
                    await blackjacklose(reaction, game, dbpass)
                elif game["LAFFEY"]["STATUS"] == "BUST":
                    await blackjackwin(reaction, game, dbpass)
                else:
                    game = await blackjacklaffey(reaction, game)
                    if game["LAFFEY"]["STATUS"] == "BUST":
                        await blackjackwin(reaction, game, dbpass)
                    elif game["LAFFEY"]["STATUS"] == game["USER"]["STATUS"]:
                        await blackjackdraw(reaction, game, dbpass)
                    else:
                        await blackjacklose(reaction, game, dbpass)
            if str(reaction.emoji) == "🏳" and len(game["CARDS"]) == 16:
                await reaction.message.clear_reactions()
                game["BET"] = int(game["BET"] / 2.0)
                embed = discord.Embed(title="블랙잭 종료!", description="[%s] 지휘관은 도망갔다! 배당금 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```라피```", value="%s" % str(game["LAFFEY"]["STATUS"]), inline=False)
                embed.add_field(name="%s" % " ".join(game["LAFFEY"]["CARDS"]), value="\u200b\n**%s**" % " ".join(game["USER"]["CARDS"]), inline=False)
                embed.add_field(name="```지휘관```", value="%s" % str(game["USER"]["STATUS"]), inline=False)
                await reaction.message.edit(embed=embed)
                userdata = mclient.Laffey.Data.find_one({"ID": game["USERID"]})
                mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"POINTS": userdata["POINTS"] + game["BET"], "ISONACT": False}})
                mclient.Laffey.Gamble.update_one({"GAME": "BLACKJACK"}, {"$set": {"PLAYING": False, "BET": 0, "USERID": 0, "USERNICK": "Noone", "CARDS": [], "FIRSTTURN": True, "LAFFEY": {"ACE": 0, "COUNT": 0, "COUNT_A": 0, "CARDS": [], "STATUS": "0"}, "USER": {"ACE": 0, "COUNT": 0, "COUNT_A": 0, "CARDS": [], "STATUS": "0"}}})


def bjcarddraw(game, isuser):
    card = game["CARDS"].pop()
    if isuser is True:
        if card == "A":
            game["USER"]["ACE"] += 1
            game["USER"]["COUNT"] += 1
        elif card == "J" or card == "Q" or card == "K":
            game["USER"]["COUNT"] += 10
        else:
            game["USER"]["COUNT"] += int(card)
        game["USER"]["CARDS"].append(card)
    else:
        if card == "A":
            game["LAFFEY"]["ACE"] += 1
            game["LAFFEY"]["COUNT"] += 1
        elif card == "J" or card == "Q" or card == "K":
            game["LAFFEY"]["COUNT"] += 10
        else:
            game["LAFFEY"]["COUNT"] += int(card)
        game["LAFFEY"]["CARDS"].append(card)
    return game


def blackjackcalculate(game, isuser):
    if isuser is True:
        game["USER"]["COUNT_A"] = game["USER"]["COUNT"]
        for i in range(0, game["USER"]["ACE"]):
            if game["USER"]["COUNT_A"]+10 <= 21:
                game["USER"]["COUNT_A"] += 10
            else:
                break
        game["USER"]["STATUS"] = str(game["USER"]["COUNT_A"])
        if len(game["USER"]["CARDS"]) == 2 and game["USER"]["COUNT_A"] == 21:
            game["USER"]["STATUS"] = "BLACKJACK"
        if game["USER"]["COUNT"] > 21:
            game["USER"]["STATUS"] = "BUST"
    else:
        game["LAFFEY"]["COUNT_A"] = game["LAFFEY"]["COUNT"]
        for i in range(0, game["LAFFEY"]["ACE"]):
            if game["LAFFEY"]["COUNT_A"]+10 <= 21:
                game["LAFFEY"]["COUNT_A"] += 10
            else:
                break
        game["LAFFEY"]["STATUS"] = str(game["LAFFEY"]["COUNT_A"])
        if len(game["LAFFEY"]["CARDS"]) == 2 and game["LAFFEY"]["COUNT_A"] == 21:
            game["LAFFEY"]["STATUS"] = "BLACKJACK"
        if game["LAFFEY"]["COUNT"] > 21:
            game["LAFFEY"]["STATUS"] = "BUST"
    return game


async def blackjacklaffey(reaction, game):
    while game["LAFFEY"]["COUNT_A"] < 17:
        game = bjcarddraw(game, False)
        game = blackjackcalculate(game, False)
        embed = discord.Embed(title="블랙잭 진행중!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                              color=0xf8f5ff)
        embed.add_field(name="```라피```", value="%s" % str(game["LAFFEY"]["STATUS"]), inline=False)
        embed.add_field(name="%s" % " ".join(game["LAFFEY"]["CARDS"]), value="\u200b\n**%s**" % " ".join(game["USER"]["CARDS"]), inline=False)
        embed.add_field(name="```지휘관```", value="%s" % str(game["USER"]["STATUS"]), inline=False)
        await reaction.message.edit(embed=embed)
        await asyncio.sleep(1)
    while (game["LAFFEY"]["COUNT_A"] < game["USER"]["COUNT_A"]) and game["LAFFEY"]["COUNT"] <= 21:
        game = bjcarddraw(game, False)
        game = blackjackcalculate(game, False)
        embed = discord.Embed(title="블랙잭 진행중!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                              color=0xf8f5ff)
        embed.add_field(name="```라피```", value="%s" % str(game["LAFFEY"]["STATUS"]), inline=False)
        embed.add_field(name="%s" % " ".join(game["LAFFEY"]["CARDS"]), value="\u200b\n**%s**" % " ".join(game["USER"]["CARDS"]), inline=False)
        embed.add_field(name="```지휘관```", value="%s" % str(game["USER"]["STATUS"]), inline=False)
        await reaction.message.edit(embed=embed)
        await asyncio.sleep(1)
    return game


async def blackjacklose(reaction, game, dbpass):
    game["BET"] *= 0
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    embed = discord.Embed(title="블랙잭 종료!", description="[%s] 지휘관의 패배! 배당금 : %d LP" % (game["USERNICK"], game["BET"]),
                          color=0xf8f5ff)
    embed.add_field(name="```라피```", value="%s" % str(game["LAFFEY"]["STATUS"]), inline=False)
    embed.add_field(name="%s" % " ".join(game["LAFFEY"]["CARDS"]), value="\u200b\n**%s**" % " ".join(game["USER"]["CARDS"]), inline=False)
    embed.add_field(name="```지휘관```", value="%s" % str(game["USER"]["STATUS"]), inline=False)
    await reaction.message.edit(embed=embed)
    mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"ISONACT": False}})
    mclient.Laffey.Gamble.update_one({"GAME": "BLACKJACK"}, {"$set": {"PLAYING": False, "BET": 0, "USERID": 0, "USERNICK": "Noone", "CARDS": [], "FIRSTTURN": True, "LAFFEY": {"ACE": 0, "COUNT": 0, "COUNT_A": 0, "CARDS": [], "STATUS": "0"}, "USER": {"ACE": 0, "COUNT": 0, "COUNT_A": 0, "CARDS": [], "STATUS": "0"}}})


async def blackjackdraw(reaction, game, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    embed = discord.Embed(title="블랙잭 종료!", description="[%s] 지휘관과 라피는 비겼음! 배당금 : %d LP" % (game["USERNICK"], game["BET"]),
                          color=0xf8f5ff)
    embed.add_field(name="```라피```", value="%s" % str(game["LAFFEY"]["STATUS"]), inline=False)
    embed.add_field(name="%s" % " ".join(game["LAFFEY"]["CARDS"]), value="\u200b\n**%s**" % " ".join(game["USER"]["CARDS"]), inline=False)
    embed.add_field(name="```지휘관```", value="%s" % str(game["USER"]["STATUS"]), inline=False)
    await reaction.message.edit(embed=embed)
    userdata = mclient.Laffey.Data.find_one({"ID": game["USERID"]})
    mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"POINTS": userdata["POINTS"]+game["BET"], "ISONACT": False}})
    mclient.Laffey.Gamble.update_one({"GAME": "BLACKJACK"}, {"$set": {"PLAYING": False, "BET": 0, "USERID": 0, "USERNICK": "Noone", "CARDS": [], "FIRSTTURN": True, "LAFFEY": {"ACE": 0, "COUNT": 0, "COUNT_A": 0, "CARDS": [], "STATUS": "0"}, "USER": {"ACE": 0, "COUNT": 0, "COUNT_A": 0, "CARDS": [], "STATUS": "0"}}})


async def blackjackwin(reaction, game, dbpass):
    if game["USER"]["STATUS"] == "BLACKJACK":
        game["BET"] *= 3
    else:
        game["BET"] *= 2
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    embed = discord.Embed(title="블랙잭 종료!", description="[%s] 지휘관의 승리! 배당금 : %d LP" % (game["USERNICK"], game["BET"]),
                          color=0xf8f5ff)
    embed.add_field(name="```라피```", value="%s" % str(game["LAFFEY"]["STATUS"]), inline=False)
    embed.add_field(name="%s" % " ".join(game["LAFFEY"]["CARDS"]), value="\u200b\n**%s**" % " ".join(game["USER"]["CARDS"]), inline=False)
    embed.add_field(name="```지휘관```", value="%s" % str(game["USER"]["STATUS"]), inline=False)
    await reaction.message.edit(embed=embed)
    userdata = mclient.Laffey.Data.find_one({"ID": game["USERID"]})
    mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"POINTS": userdata["POINTS"]+game["BET"], "ISONACT": False}})
    mclient.Laffey.Gamble.update_one({"GAME": "BLACKJACK"}, {"$set": {"PLAYING": False, "BET": 0, "USERID": 0, "USERNICK": "Noone", "CARDS": [], "FIRSTTURN": True, "LAFFEY": {"ACE": 0, "COUNT": 0, "COUNT_A": 0, "CARDS": [], "STATUS": "0"}, "USER": {"ACE": 0, "COUNT": 0, "COUNT_A": 0, "CARDS": [], "STATUS": "0"}}})


def laffeyduel(channel, args, authinfo, dbpass):
    if len(args) == 3:
        embed = discord.Embed(title="일기토", description="지휘관, 도박은 나빠...그래도 지휘관이 원한다면...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```", value="일기토는 전략게임의 일종입니다. 적어도 300포인트의 베팅금이 필요합니다.\n확률조작 안합니다. 포인트 잃어도 라피는 모릅니다.", inline=False)
        embed.add_field(name="```사용법 : !라피 도박 일기토 (베팅금)```",
                        value="라피와의 대결을 벌입니다. 더 많은 턴에서 이길 경우 승리합니다.\n턴은 총 5턴으로 이루어집니다." +
                              "\n각 턴마다 공격/방어/도발/필살(1회)을 사용할 수 있습니다.\n 각 행동의 상성은 다음과 같습니다." +
                              "\n방어 > 공격 > 도발 > 방어\n 필살은 필살로만 상대할 수 있습니다.", inline=False)
        embed.add_field(name="```배당금```", value="승리 : x2.2 / 무승부 : x1 / 패배 : x0", inline=False)
        return channel.send(embed=embed)
    if args[3].isdigit() and len(args) == 4 and int(args[3]) > 0:
        return laffeyduelstart(channel, int(args[3]), authinfo, dbpass)
    else:
        return channel.send("지휘관...베팅할 양을 제대로 입력해줘...")


def laffeyduelstart(channel, bet, authinfo, dbpass):
    if authinfo["POINTS"] < bet or bet < 300:
        return channel.send("지휘관...포인트가 모자라...")
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    db = mclient.Laffey
    if db.Gamble.find_one({"GAME": "LAFFEYDUEL"})["PLAYING"] is True:
        return channel.send("지휘관...이미 누군가 일기토를 진행중이야...")
    authinfo["POINTS"] -= bet
    dolist = ["🗡", "🛡", "👎"]
    laffeyturn = [random.choice(dolist) for i in range(0, 5)]
    laffeyturn[random.randint(0, 4)] = "🔥"
    db.Data.update_one({"ID": authinfo["ID"]}, {"$set": {"POINTS": authinfo["POINTS"], "ISONACT": True}})
    db.Gamble.update_one({"GAME": "LAFFEYDUEL"}, {"$set": {"PLAYING": True, "BET": bet, "USERID": authinfo["ID"], "USERNICK": authinfo["NAME"], "LAFFEYTURN": laffeyturn, "TURN": 0, "LSTATUS": "NUL", "USTATUS": "NUL", "LAFFEYWIN": 0, "USERWIN": 0, "USEULT": False}})
    embed = discord.Embed(title="일기토 시작!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (authinfo["NAME"], bet),
                          color=0xf8f5ff)
    embed.add_field(name="```승리 수```", value="라피 0 vs 0 [%s]" % authinfo["NAME"], inline=False)
    embed.add_field(name="```라피```", value="진행 전", inline=False)
    embed.add_field(name="\u200b", value="\u200b\n\u200b", inline=False)
    embed.add_field(name="```지휘관```", value="진행 전", inline=False)
    return channel.send(embed=embed)


async def laffeyduelfirstreact(message, client):
    if str(message.author.id) == str(client.user.id):
        if len(message.embeds) >= 1:
            if message.embeds[0].title == "일기토 시작!":
                await message.add_reaction("🗡")
                await message.add_reaction("🛡")
                await message.add_reaction("👎")
                await message.add_reaction("🔥")


async def laffeyduelonreact(reaction, user, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    game = mclient.Laffey.Gamble.find_one({"GAME": "LAFFEYDUEL"})
    if reaction.message.embeds[0].title == "일기토 시작!" or reaction.message.embeds[0].title == "일기토 진행중!":
        if user.id == game["USERID"] and game["PLAYING"] is True:
            if str(reaction.emoji) in ["🗡", "🛡", "👎", "🔥"]:
                await reaction.message.clear_reactions()
                game = laffeyduelcheck(game, str(reaction.emoji))
                await asyncio.sleep(0.5)
                embed = discord.Embed(title="일기토 진행중!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```승리 수```", value="라피 %d vs %d [%s]" % (game["LAFFEYWIN"], game["USERWIN"], game["USERNICK"]), inline=False)
                embed.add_field(name="```라피```", value="%s" % game["LSTATUS"], inline=False)
                embed.add_field(name="%s" % game["LAFFEYTURN"][game["TURN"] - 1], value="Turn : %d\n%s" % (game["TURN"], str(reaction.emoji)), inline=False)
                embed.add_field(name="```지휘관```", value="%s" % game["USTATUS"], inline=False)
                await reaction.message.edit(embed=embed)
                if game["LAFFEYWIN"] >= 3 or game["USERWIN"] >= 3 or game["TURN"] >= 5:
                    if game["LAFFEYWIN"] > game["USERWIN"]:
                        comment1 = "지휘관의 패배!"
                        comment2 = "일기토 패배!"
                        win = game["BET"] * 0
                    elif game["LAFFEYWIN"] < game["USERWIN"]:
                        comment1 = "지휘관의 승리!"
                        comment2 = "일기토 승리!"
                        win = int(game["BET"] * 2.2)
                    else:
                        comment1 = "지휘관과 라피의 무승부!"
                        comment2 = "일기토 무승부!"
                        win = game["BET"] * 1
                    userdata = mclient.Laffey.Data.find_one({"ID": game["USERID"]})
                    mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"POINTS": userdata["POINTS"] + win, "ISONACT": False}})
                    mclient.Laffey.Gamble.update_one({"GAME": "LAFFEYDUEL"}, {"$set": {"PLAYING": False, "BET": 0, "USERID": 0, "USERNICK": "Noone", "LAFFEYTURN": [], "TURN": 0, "LSTATUS": "NUL", "USTATUS": "NUL", "LAFFEYWIN": 0, "USERWIN": 0, "USEULT": False}})
                    await asyncio.sleep(1)
                    embed = discord.Embed(title="일기토 종료!", description="[%s] %s 배당금 : %d LP" % (game["USERNICK"], comment1, win),
                                          color=0xf8f5ff)
                    embed.add_field(name="```승리 수```", value="라피 %d vs %d [%s]" % (game["LAFFEYWIN"], game["USERWIN"], game["USERNICK"]), inline=False)
                    embed.add_field(name="```라피```", value="종료", inline=False)
                    embed.add_field(name="\u200b", value="%s\n\u200b" % comment2, inline=False)
                    embed.add_field(name="```지휘관```", value="종료", inline=False)
                    await reaction.message.edit(embed=embed)

                else:
                    mclient.Laffey.Gamble.update_one({"GAME": "LAFFEYDUEL"}, {"$set": game})
                    await reaction.message.add_reaction("🗡")
                    await reaction.message.add_reaction("🛡")
                    await reaction.message.add_reaction("👎")
                    if game["USEULT"] is False:
                        await reaction.message.add_reaction("🔥")


def laffeyduelcheck(game, emoji):
    # 공격 : 1  "🗡" / 방어 : 2  "🛡" / 도발 : 3  "👎" / 필살 : 4 "🔥"
    if game["LAFFEYTURN"][game["TURN"]] == "🔥":
        if emoji != "🔥":
            game["LSTATUS"] = "승리"
            game["USTATUS"] = "패배"
            game["TURN"] += 1
            game["LAFFEYWIN"] += 1
        else:
            game["LSTATUS"] = "비김"
            game["USTATUS"] = "비김"
            game["TURN"] += 1
            game["USEULT"] = True
    elif game["LAFFEYTURN"][game["TURN"]] == "👎":
        if emoji == "👎":
            game["LSTATUS"] = "비김"
            game["USTATUS"] = "비김"
            game["TURN"] += 1
        elif emoji == "🔥":
            game["LSTATUS"] = "패배"
            game["USTATUS"] = "승리"
            game["TURN"] += 1
            game["USERWIN"] += 1
            game["USEULT"] = True
        elif emoji == "🗡":
            game["LSTATUS"] = "패배"
            game["USTATUS"] = "승리"
            game["TURN"] += 1
            game["USERWIN"] += 1
        elif emoji == "🛡":
            game["LSTATUS"] = "승리"
            game["USTATUS"] = "패배"
            game["TURN"] += 1
            game["LAFFEYWIN"] += 1
    elif game["LAFFEYTURN"][game["TURN"]] == "🛡":
        if emoji == "🛡":
            game["LSTATUS"] = "비김"
            game["USTATUS"] = "비김"
            game["TURN"] += 1
        elif emoji == "👎":
            game["LSTATUS"] = "패배"
            game["USTATUS"] = "승리"
            game["TURN"] += 1
            game["USERWIN"] += 1
        elif emoji == "🗡":
            game["LSTATUS"] = "승리"
            game["USTATUS"] = "패배"
            game["TURN"] += 1
            game["LAFFEYWIN"] += 1
        elif emoji == "🔥":
            game["LSTATUS"] = "패배"
            game["USTATUS"] = "승리"
            game["TURN"] += 1
            game["USERWIN"] += 1
            game["USEULT"] = True
    elif game["LAFFEYTURN"][game["TURN"]] == "🗡":
        if emoji == "🗡":
            game["LSTATUS"] = "비김"
            game["USTATUS"] = "비김"
            game["TURN"] += 1
        elif emoji == "🛡":
            game["LSTATUS"] = "패배"
            game["USTATUS"] = "승리"
            game["TURN"] += 1
            game["USERWIN"] += 1
        elif emoji == "👎":
            game["LSTATUS"] = "승리"
            game["USTATUS"] = "패배"
            game["TURN"] += 1
            game["LAFFEYWIN"] += 1
        elif emoji == "🔥":
            game["LSTATUS"] = "패배"
            game["USTATUS"] = "승리"
            game["TURN"] += 1
            game["USERWIN"] += 1
            game["USEULT"] = True
    return game


async def drawpoker(channel, args, authinfo, dbpass):
    if len(args) == 3:
        embed = discord.Embed(title="파이브 카드 드로우", description="지휘관, 도박은 나빠...그래도 지휘관이 원한다면...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```", value="드로우 포커는 카드 게임의 일종입니다. 베팅액은 최저 50, 최대 500 LP까지 가능합니다.\n확률조작 안합니다. 포인트 잃어도 라피는 모릅니다.", inline=False)
        embed.add_field(name="```사용법 : !라피 도박 드로우포커 (베팅금)```",
                        value="파이브 카드 드로우를 기반으로 합니다. 카드는 문양이 없습니다.\n먼저 카드를 5장 받습니다." +
                              "\n바꿀 카드를 0~5장 선택합니다.\n그 뒤 바꾼 카드의 족보에 따라 배당금을 받게 됩니다." +
                              "\n족보에 대한 정보는 다음 명령어로 알 수 있습니다.\n**!라피 도박 드로우포커 족보**", inline=False)
        embed.add_field(name="```배당금```",
                        value="노 페어 : x0 / 원 페어 : x1 / 투 페어 : x1.5\n" +
                              "트리플 : x 2 / 풀하우스 : x3 / 포카드 : x4\n" +
                              "스트레이트 : x2.5 / 백스트레이트 : x5", inline=False)
        embed.add_field(name="```사용법```",
                        value="1️⃣~5️⃣ : 해당 위치 카드 뒤집기\n" +
                              "⏹ : 뒤집은 카드 바꾸기\n", inline=False)
        await channel.send(embed=embed)
    elif len(args) == 4 and args[3] == "족보":
        await channel.send("족보!")
    elif len(args) == 4 and args[3].isdigit() and int(args[3]) > 0:
        await drawpokerstart(channel, int(args[3]), authinfo, dbpass)
    else:
        await channel.send("지휘관...사용법이 틀린 것 같아...")


# 문양 없는 카드를 원하는 수만큼 리턴해주는 공통 코드로 제작해둔다.
def listcard(count):
    cardlist = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K",
                "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K",
                "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K",
                "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    return random.sample(cardlist, count)


def drawpokerstart(channel, bet, authinfo, dbpass):
    if authinfo["POINTS"] < bet:
        return channel.send("지휘관...포인트가 모자라...")
    if not 50 <= bet <= 500:
        return channel.send("지휘관...50 ~ 500 포인트만 베팅이 가능해...")
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    db = mclient.Laffey
    if db.Gamble.find_one({"GAME": "LAFFEYDUEL"})["PLAYING"] is True:
        return channel.send("지휘관...이미 누군가 파이브 드로우 포커를 진행중이야...")
    authinfo["POINTS"] -= bet
    cards = listcard(10)
    usercards = {"C1": cards.pop(), "C2": cards.pop(), "C3": cards.pop(), "C4": cards.pop(), "C5": cards.pop()}
    db.Data.update_one({"ID": authinfo["ID"]}, {"$set": {"POINTS": authinfo["POINTS"], "ISONACT": True}})
    db.Gamble.update_one({"GAME": "FIVEDRAWPOKER"}, {"$set": {"PLAYING": True, "BET": bet, "WIN": 0, "USERID": authinfo["ID"], "USERNICK": authinfo["NAME"], "STATUS": "NONE", "CARDS": cards, "USERCARDS": usercards, "CHANGE": {"C1": False, "C2": False, "C3": False, "C4": False, "C5": False}}})
    embed = discord.Embed(title="파이브 카드 드로우 시작!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (authinfo["NAME"], bet),
                          color=0xf8f5ff)
    embed.add_field(name="```상태```", value="진행 전", inline=False)
    embed.add_field(name="\u200b", value="\u200b\n\u200b", inline=False)
    return channel.send(embed=embed)


async def drawpokerfirstreact(message, client):
    if str(message.author.id) == str(client.user.id):
        if len(message.embeds) >= 1:
            if message.embeds[0].title == "파이브 카드 드로우 시작!":
                await message.add_reaction("▶")


async def drawpokeronreact(reaction, user, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    game = mclient.Laffey.Gamble.find_one({"GAME": "FIVEDRAWPOKER"})
    if reaction.message.embeds[0].title == "파이브 카드 드로우 시작!":
        if user.id == game["USERID"] and game["PLAYING"] is True:
            if str(reaction.emoji) == "▶":
                await reaction.message.clear_reactions()
                game = drawpokercalc(game)
                embed = discord.Embed(title="파이브 카드 드로우 진행중!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```상태```", value="%s" % game["STATUS"], inline=False)
                embed.add_field(name="\u200b", value="%s %s %s %s %s\n\u200b" % (game["USERCARDS"]["C1"], game["USERCARDS"]["C2"], game["USERCARDS"]["C3"], game["USERCARDS"]["C4"], game["USERCARDS"]["C5"]), inline=False)
                await reaction.message.edit(embed=embed)
                mclient.Laffey.Gamble.update_one({"GAME": "FIVEDRAWPOKER"}, {"$set": game})
                await reaction.message.add_reaction("1️⃣")
                await reaction.message.add_reaction("2️⃣")
                await reaction.message.add_reaction("3️⃣")
                await reaction.message.add_reaction("4️⃣")
                await reaction.message.add_reaction("5️⃣")
                await reaction.message.add_reaction("⏹")
    elif reaction.message.embeds[0].title == "파이브 카드 드로우 진행중!":
        if user.id == game["USERID"] and game["PLAYING"] is True:
            if str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]:
                await reaction.message.remove_reaction(str(reaction.emoji), member=user)
                game["CHANGE"] = drawpokerflip(game["CHANGE"], str(reaction.emoji))
                embed = discord.Embed(title="파이브 카드 드로우 진행중!", description="[%s] 지휘관이 진행중! 베팅액 : %d LP" % (game["USERNICK"], game["BET"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```상태```", value="%s" % game["STATUS"], inline=False)
                embed.add_field(name="\u200b", value="%s\n\u200b" % drawpokerdisplay(game), inline=False)
                await reaction.message.edit(embed=embed)
                mclient.Laffey.Gamble.update_one({"GAME": "FIVEDRAWPOKER"}, {"$set": game})
            elif str(reaction.emoji) == "⏹":
                await reaction.message.clear_reactions()
                game = drawpokerchange(game)
                game = drawpokercalc(game)
                if game["STATUS"] == "원 페어":
                    game["WIN"] = int(game["BET"] * 1.0)
                elif game["STATUS"] == "투 페어":
                    game["WIN"] = int(game["BET"] * 1.5)
                elif game["STATUS"] == "트리플":
                    game["WIN"] = int(game["BET"] * 2.0)
                elif game["STATUS"] == "스트레이트":
                    game["WIN"] = int(game["BET"] * 2.5)
                elif game["STATUS"] == "풀하우스":
                    game["WIN"] = int(game["BET"] * 3.0)
                elif game["STATUS"] == "포카드":
                    game["WIN"] = int(game["BET"] * 4.0)
                elif game["STATUS"] == "백스트레이트":
                    game["WIN"] = int(game["BET"] * 5.0)
                embed = discord.Embed(title="파이브 카드 드로우 종료!", description="[%s] 지휘관이 진행하였음! 배당금 : %d LP" % (game["USERNICK"], game["WIN"]),
                                      color=0xf8f5ff)
                embed.add_field(name="```상태```", value="%s" % game["STATUS"], inline=False)
                embed.add_field(name="\u200b", value="%s %s %s %s %s\n\u200b" % (game["USERCARDS"]["C1"], game["USERCARDS"]["C2"], game["USERCARDS"]["C3"], game["USERCARDS"]["C4"], game["USERCARDS"]["C5"]), inline=False)
                await reaction.message.edit(embed=embed)
                userdata = mclient.Laffey.Data.find_one({"ID": game["USERID"]})
                mclient.Laffey.Data.update_one({"ID": game["USERID"]}, {"$set": {"POINTS": userdata["POINTS"]+game["WIN"], "ISONACT": False}})
                mclient.Laffey.Gamble.update_one({"GAME": "FIVEDRAWPOKER"}, {"$set": {"PLAYING": False}})


def drawpokercalc(game):
    # Card Replace & Sort
    acard = [game["USERCARDS"]["C1"],
             game["USERCARDS"]["C2"],
             game["USERCARDS"]["C3"],
             game["USERCARDS"]["C4"],
             game["USERCARDS"]["C5"]]
    ncard = []
    for alphabet in acard:
        number = alphabet.replace("A", "1")
        number = number.replace("J", "11")
        number = number.replace("Q", "12")
        number = number.replace("K", "13")
        ncard.append(int(number))
    ncard.sort()
    # Check Rank
    pairs = 0
    for i in range(0, 4):
        for j in range(i+1, 5):
            if ncard[i] == ncard[j]:
                pairs += 1
    if pairs == 1:
        game["STATUS"] = "원 페어"
    elif pairs == 2:
        game["STATUS"] = "투 페어"
    elif pairs == 3:
        game["STATUS"] = "트리플"
    elif pairs == 4:
        game["STATUS"] = "풀하우스"
    elif pairs == 6:
        game["STATUS"] = "포카드"
    else:
        # 기본 , A10JQK, A2JQK, A23QK, A234K
        if (ncard[4]-ncard[0] == 4) or (ncard[0] == 1 and ncard[1] == 10) or (ncard[1] == 2 and ncard[2] == 11) or (ncard[2] == 3 and ncard[3] == 12) or (ncard[2] == 3 and ncard[3] == 4 and ncard[4] == 13):
            if ncard[0] == 1 and ncard[4] == 5:
                game["STATUS"] = "백스트레이트"
            else:
                game["STATUS"] = "스트레이트"
        else:
            game["STATUS"] = "노 페어"
    return game


def drawpokerflip(isflip, emoji):
    if emoji == "1️⃣":
        if isflip["C1"] is False:
            isflip["C1"] = True
        else:
            isflip["C1"] = False
    elif emoji == "2️⃣":
        if isflip["C2"] is False:
            isflip["C2"] = True
        else:
            isflip["C2"] = False
    elif emoji == "3️⃣":
        if isflip["C3"] is False:
            isflip["C3"] = True
        else:
            isflip["C3"] = False
    elif emoji == "4️⃣":
        if isflip["C4"] is False:
            isflip["C4"] = True
        else:
            isflip["C4"] = False
    elif emoji == "5️⃣":
        if isflip["C5"] is False:
            isflip["C5"] = True
        else:
            isflip["C5"] = False
    return isflip


def drawpokerdisplay(game):
    string = []
    for i in range(1, 6):
        if game["CHANGE"]["C"+str(i)] is True:
            string.append("⬜")
        else:
            string.append(game["USERCARDS"]["C"+str(i)])
    string = " ".join(string)
    return string


def drawpokerchange(game):
    for i in range(1,6):
        if game["CHANGE"]["C"+str(i)] is True:
            game["USERCARDS"]["C"+str(i)] = game["CARDS"].pop()
    return game



