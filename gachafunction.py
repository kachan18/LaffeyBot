import random
import discord
import datetime
import pymongo
import asyncio


async def letsgacha(message, args, authinfo, dbpass):
    channel = message.channel
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Gacha?retryWrites=true&w=majority" % dbpass)
    gachasystem = mclient.Gacha.System
    machineinfo = gachasystem.find_one({"SYSTEM": "GACHA"})
    if machineinfo["PLAYING"] is True:
        await channel.send("지휘관...이미 누군가 가챠를 진행중이야...")
    else:
        gachasystem.update_one({"SYSTEM": "GACHA"}, {"$set": {"PLAYING": True, "USERID": authinfo["ID"], "USERNAME": authinfo["NAME"]}})
        embed = discord.Embed(title="가챠 대기중!", description="가챠는 나쁜 문명!",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```가챠 머신```", value="%s" % machineinfo["ALLMACHINENAME"][machineinfo["CURRENTMACHINE"]], inline=False)
        embed.add_field(name="```비용```", value="%d LP" % int(machineinfo["COSTS"][machineinfo["CURRENTMACHINE"]]), inline=False)
        embed.add_field(name="```획득 가능```", value="%s" % machineinfo["PRIZE"][machineinfo["CURRENTMACHINE"]], inline=False)
        embed.add_field(name="```코멘트```", value="힘내요!", inline=False)
        embed.add_field(name="```사용법```", value="⬅/➡ : 이전/다음 머신으로 이동\n💎 : 가챠!\n❌ : 가챠 종료", inline=False)
        await channel.send(embed=embed)


async def letsgachaaddreact(message, client):
    if str(message.author.id) == str(client.user.id):
        if len(message.embeds) >= 1:
            if message.embeds[0].title == "가챠 대기중!" and message.embeds[0].description == "가챠는 나쁜 문명!":
                await message.add_reaction("⬅")
                await message.add_reaction("💎")
                await message.add_reaction("➡")
                await message.add_reaction("❌")


async def letsgachaonreact(reaction, user, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Gacha?retryWrites=true&w=majority" % dbpass)
    gachasystem = mclient.Gacha.System
    machineinfo = gachasystem.find_one({"SYSTEM": "GACHA"})

    if reaction.message.embeds[0].title == "가챠 대기중!" or reaction.message.embeds[0].title == "가챠 진행중!":
        if user.id == machineinfo["USERID"] and machineinfo["PLAYING"] is True:
            if str(reaction.emoji) == "⬅":
                await letsgachamachinemove(reaction, machineinfo, dbpass, False)
                await reaction.message.remove_reaction("⬅", member=user)
            elif str(reaction.emoji) == "➡":
                await letsgachamachinemove(reaction, machineinfo, dbpass, True)
                await reaction.message.remove_reaction("➡", member=user)
            elif str(reaction.emoji) == "💎":
                await reaction.message.remove_reaction("💎", member=user)
                await letsgachagacha(reaction, machineinfo, dbpass)
            elif str(reaction.emoji) == "❌":
                await reaction.message.clear_reactions()
                gachasystem.update_one({"SYSTEM": "GACHA"}, {"$set": {"PLAYING": False, "USERID": 0, "USERNAME": "LAFFEY","CURRENTMACHINE": 0}})
                embed = discord.Embed(title="가챠 종료!", description="가챠는 나쁜 문명!",
                                      color=0xf8f5ff)
                embed.add_field(name="```지휘관, 원하는 건 뽑았어...?```", value="다음에 또 와...", inline=False)
                await reaction.message.edit(embed=embed)


async def letsgachamachinemove(reaction, machineinfo, dbpass, isright):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Gacha?retryWrites=true&w=majority" % dbpass)
    gachasystem = mclient.Gacha.System
    if isright is True:
        if machineinfo["CURRENTMACHINE"] + 1 >= machineinfo["MACHINENUMS"]:
            embed = discord.Embed(title="가챠 대기중!", description="가챠는 나쁜 문명!",
                                  color=0xf8f5ff)
            embed.set_thumbnail(
                url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
            embed.add_field(name="```가챠 머신```", value="%s" % machineinfo["ALLMACHINENAME"][machineinfo["CURRENTMACHINE"]], inline=False)
            embed.add_field(name="```비용```", value="%d LP" % int(machineinfo["COSTS"][machineinfo["CURRENTMACHINE"]]), inline=False)
            embed.add_field(name="```획득 가능```", value="%s" % machineinfo["PRIZE"][machineinfo["CURRENTMACHINE"]], inline=False)
            embed.add_field(name="```코멘트```", value="현재 머신이 마지막 머신입니다.", inline=False)
            await reaction.message.edit(embed=embed)
        else:
            machineinfo["CURRENTMACHINE"] += 1
            embed = discord.Embed(title="가챠 대기중!", description="가챠는 나쁜 문명!",
                                  color=0xf8f5ff)
            embed.set_thumbnail(
                url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
            embed.add_field(name="```가챠 머신```", value="%s" % machineinfo["ALLMACHINENAME"][machineinfo["CURRENTMACHINE"]], inline=False)
            embed.add_field(name="```비용```", value="%d LP" % int(machineinfo["COSTS"][machineinfo["CURRENTMACHINE"]]), inline=False)
            embed.add_field(name="```획득 가능```", value="%s" % machineinfo["PRIZE"][machineinfo["CURRENTMACHINE"]], inline=False)
            embed.add_field(name="```코멘트```", value="다음 머신으로 이동했습니다.", inline=False)
            await reaction.message.edit(embed=embed)
            gachasystem.update_one({"SYSTEM": "GACHA"}, {"$set": machineinfo})
    else:
        if machineinfo["CURRENTMACHINE"] - 1 < 0:
            embed = discord.Embed(title="가챠 대기중!", description="가챠는 나쁜 문명!",
                                  color=0xf8f5ff)
            embed.set_thumbnail(
                url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
            embed.add_field(name="```가챠 머신```", value="%s" % machineinfo["ALLMACHINENAME"][machineinfo["CURRENTMACHINE"]], inline=False)
            embed.add_field(name="```비용```", value="%d LP" % int(machineinfo["COSTS"][machineinfo["CURRENTMACHINE"]]), inline=False)
            embed.add_field(name="```획득 가능```", value="%s" % machineinfo["PRIZE"][machineinfo["CURRENTMACHINE"]], inline=False)
            embed.add_field(name="```코멘트```", value="현재 머신이 처음 머신입니다.", inline=False)
            await reaction.message.edit(embed=embed)
        else:
            machineinfo["CURRENTMACHINE"] -= 1
            embed = discord.Embed(title="가챠 대기중!", description="가챠는 나쁜 문명!",
                                  color=0xf8f5ff)
            embed.set_thumbnail(
                url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
            embed.add_field(name="```가챠 머신```", value="%s" % machineinfo["ALLMACHINENAME"][machineinfo["CURRENTMACHINE"]], inline=False)
            embed.add_field(name="```비용```", value="%d LP" % int(machineinfo["COSTS"][machineinfo["CURRENTMACHINE"]]), inline=False)
            embed.add_field(name="```획득 가능```", value="%s" % machineinfo["PRIZE"][machineinfo["CURRENTMACHINE"]], inline=False)
            embed.add_field(name="```코멘트```", value="이전 머신으로 이동했습니다.", inline=False)
            await reaction.message.edit(embed=embed)
            gachasystem.update_one({"SYSTEM": "GACHA"}, {"$set": machineinfo})


async def letsgachagacha(reaction, machineinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Gacha?retryWrites=true&w=majority" % dbpass)
    machinedata = mclient.Gacha.System.find_one({"MACHINEID": machineinfo["CURRENTMACHINE"]})
    userdata = mclient.Laffey.Data.find_one({"ID": machineinfo["USERID"]})
    if userdata["POINTS"] >= machinedata["COST"]:
        userdata["POINTS"] -= machinedata["COST"]
        mclient.Laffey.Data.update_one({"ID": userdata["ID"]}, {"$set": {"POINTS": userdata["POINTS"]}})
        embed = discord.Embed(title="가챠 진행중!", description="가챠는 나쁜 문명!",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```가챠 머신```", value="%s" % machinedata["MACHINENAME"], inline=False)
        embed.add_field(name="```획득 가능```", value="%s" % machineinfo["PRIZE"][machinedata["MACHINEID"]], inline=False)
        embed.add_field(name="```비용```", value="%d LP" % int(machinedata["COST"]), inline=False)
        embed.add_field(name="```코멘트```", value="가챠 도전! 과연 결과는?", inline=False)
        await reaction.message.edit(embed=embed)
        await asyncio.sleep(2)
        prize = randomgacha(machinedata["PRIZE"])
        embed = discord.Embed(title="가챠 진행중!", description="가챠는 나쁜 문명!",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.set_image(
            url="%s" % prize["IMAGE"])
        embed.add_field(name="```가챠 머신```", value="%s" % machinedata["MACHINENAME"], inline=False)
        embed.add_field(name="```획득 가능```", value="%s" % machineinfo["PRIZE"][machinedata["MACHINEID"]], inline=False)
        embed.add_field(name="```비용```", value="%d LP" % int(machinedata["COST"]), inline=False)
        embed.add_field(name="```코멘트```", value="[%s] 획득!" % prize["NAME"], inline=False)
        await reaction.message.edit(embed=embed)
        prizesave(userdata["ID"], userdata["NAME"], prize, dbpass)
    else:
        embed = discord.Embed(title="가챠 진행중!", description="가챠는 나쁜 문명!",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```가챠 머신```", value="%s" % machinedata["MACHINENAME"], inline=False)
        embed.add_field(name="```획득 가능```", value="%s" % machineinfo["PRIZE"][machinedata["MACHINEID"]], inline=False)
        embed.add_field(name="```비용```", value="%d LP" % int(machinedata["COST"]), inline=False)
        embed.add_field(name="```코멘트```", value="지휘관, %d LP 밖에 없는데..?" % userdata["POINTS"], inline=False)
        await reaction.message.edit(embed=embed)
        return


def randomgacha(prize):
    num = random.randint(0, len(prize)-1)
    return prize[num]


def prizesave(uid, name, prize, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Gacha?retryWrites=true&w=majority" % dbpass)
    gachacount = mclient.Gacha.System.find_one({"SYSTEM": "GACHA"})
    userdata = mclient.Gacha.Userdata
    target = userdata.find_one({"ID": uid})
    if target is None:
        arrhave = []
        arrcount = []
        for i in range(0, gachacount["TOTALPRIZENUM"]+1):
            arrhave.append(False)
            arrcount.append(0)
        mclient.Gacha.Userdata.insert_one({"ID": uid, "NAME": name, "PRIZE": {"HAVE": arrhave, "COUNT": arrcount}})
    target = userdata.find_one({"ID": uid})
    target["NAME"] = name
    for i in range(0, gachacount["TOTALPRIZENUM"]-len(target["PRIZE"]["HAVE"])):
        target["PRIZE"]["HAVE"].append(False)
    for i in range(0, gachacount["TOTALPRIZENUM"] - len(target["PRIZE"]["COUNT"])):
        target["PRIZE"]["COUNT"].append(0)
    target["PRIZE"]["HAVE"][int(prize["ID"])] = True
    if target["PRIZE"]["COUNT"][int(prize["ID"])] == 0:
        target["PRIZE"]["COUNT"][int(prize["ID"])] = 1
    else:
        target["PRIZE"]["COUNT"][int(prize["ID"])] += 1
    userdata.update_one({"ID": uid}, {"$set": target})


async def gachacheck(message, args, authinfo, dbpass):
    channel = message.channel
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Gacha?retryWrites=true&w=majority" % dbpass)
    prizedata = mclient.Gacha.System.find_one({"SYSTEM": "PRIZELIST"})
    userdata = mclient.Gacha.Userdata.find_one({"ID": authinfo["ID"]})

    if userdata is None:
        arrhave = []
        arrcount = []
        for i in range(0, len(prizedata["NAME"])+1):
            arrhave.append(False)
            arrcount.append(0)
        mclient.Gacha.Userdata.insert_one({"ID": authinfo["ID"], "NAME": authinfo["NAME"], "PRIZE": {"HAVE": arrhave, "COUNT": arrcount}})
    userdata = mclient.Gacha.Userdata.find_one({"ID": authinfo["ID"]})
    userdata["NAME"] = authinfo["NAME"]
    for i in range(0, len(prizedata["NAME"])-len(userdata["PRIZE"]["HAVE"])):
        userdata["PRIZE"]["HAVE"].append(False)
    for i in range(0, len(prizedata["NAME"]) - len(userdata["PRIZE"]["COUNT"])):
        userdata["PRIZE"]["COUNT"].append(0)
    mclient.Gacha.Userdata.update_one({"ID": authinfo["ID"]}, {"$set": userdata})

    if len(args) == 3:
        embed = discord.Embed(title="지휘관...그동안 얼마나 모았는지 알려줄게...", description="!라피 가챠 확인 (페이지)",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        printlist = []
        for i in range(0, 11):
            if i >= len(userdata["PRIZE"]["HAVE"]):
                break
            if userdata["PRIZE"]["HAVE"][i] is True:
                printlist.append(prizedata["NAME"][i] + " x" + str(userdata["PRIZE"]["COUNT"][i]) + " - " + str(prizedata["PRICE"][i]) + " LP")
            else:
                printlist.append("No.?? ??? x 0")
        printlist = "\n".join(printlist)
        embed.add_field(name="```보유 목록```", value="%s" % printlist)
        embed.add_field(name="```페이지```", value="1 of %d" % int(1+((len(prizedata["NAME"])-1) / 10)), inline=False)
        await channel.send(embed=embed)
    elif args[3].isdigit() and int((len(prizedata["NAME"]) - 1) / 10) >= int(args[3]) > 0:
        embed = discord.Embed(title="지휘관...그동안 얼마나 모았는지 알려줄게...", description="!라피 가챠 확인 (페이지)",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        printlist = []
        for i in range(((int(args[3])-1)*10)+1, ((int(args[3])-1)*10)+11):
            if i >= len(userdata["PRIZE"]["HAVE"]):
                break
            if userdata["PRIZE"]["HAVE"][i] is True:
                printlist.append(prizedata["NAME"][i] + " x" + str(userdata["PRIZE"]["COUNT"][i]) + " - " + str(prizedata["PRICE"][i]) + " LP")
            else:
                printlist.append("No.?? ??? x 0")
        printlist = "\n".join(printlist)
        embed.add_field(name="```보유 목록```", value="%s" % printlist)
        embed.add_field(name="```페이지```", value=str(args[3])+" of %d" % int(1+((len(prizedata["NAME"])-1) / 10)), inline=False)
        await channel.send(embed=embed)
    else:
        await channel.send("지휘관...없는 페이지야...")


async def gachasell(message, args, authinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Gacha?retryWrites=true&w=majority" % dbpass)
    prizedata = mclient.Gacha.System.find_one({"SYSTEM": "PRIZELIST"})
    userdata = mclient.Gacha.Userdata.find_one({"ID": authinfo["ID"]})

    if userdata is None:
        arrhave = []
        arrcount = []
        for i in range(0, len(prizedata["NAME"])+1):
            arrhave.append(False)
            arrcount.append(0)
        mclient.Gacha.Userdata.insert_one({"ID": authinfo["ID"], "NAME": authinfo["NAME"], "PRIZE": {"HAVE": arrhave, "COUNT": arrcount}})
    userdata = mclient.Gacha.Userdata.find_one({"ID": authinfo["ID"]})
    userdata["NAME"] = authinfo["NAME"]
    for i in range(0, len(prizedata["NAME"])-len(userdata["PRIZE"]["HAVE"])):
        userdata["PRIZE"]["HAVE"].append(False)
    for i in range(0, len(prizedata["NAME"]) - len(userdata["PRIZE"]["COUNT"])):
        userdata["PRIZE"]["COUNT"].append(0)
    mclient.Gacha.Userdata.update_one({"ID": authinfo["ID"]}, {"$set": userdata})

    if len(args) == 3:
        embed = discord.Embed(title="가챠", description="지휘관, 팔러 온거야...? 라피가 아카시한테 가져다줄게...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```", value="이 명령어를 통해 가챠에서 나온 카드를 판매가 가능합니다.", inline=False)
        embed.add_field(name="```사용법```", value="!라피 가챠 판매 (번호) (개수)", inline=False)
        embed.add_field(name="```판매가```", value="No.0 흑우 : 100 LP\nNo.0를 제외한 모든 번호 : 가챠 비용의 절반", inline=False)
        await message.channel.send(embed=embed)
    elif len(args) == 5 and args[3].isdigit() and args[4].isdigit() and int(args[4]) > 0:
        if userdata["PRIZE"]["COUNT"][int(args[3])] >= int(args[4]):
            userdata["PRIZE"]["COUNT"][int(args[3])] -= int(args[4])
            authinfo["POINTS"] = authinfo["POINTS"] + (prizedata["PRICE"][int(args[3])] * int(args[4]))
            mclient.Laffey.Data.update_one({"ID": authinfo["ID"]}, {"$set": authinfo})
            embed = discord.Embed(title="[%s] 지휘관, 판매 완료다냥. 늘 고맙다냥! - 아카시 -" % authinfo["NAME"], description="판매 대금 : %d LP\n소지 포인트 : %d LP" % ((prizedata["PRICE"][int(args[3])] * int(args[4])), int(authinfo["POINTS"])),
                                  color=0xf8f5ff)
            await message.channel.send(embed=embed)
            mclient.Gacha.Userdata.update_one({"ID": authinfo["ID"]}, {"$set": userdata})
        else:
            await message.channel.send("지휘관, 팔기에는 그 수가 모자라...")
    else:
        await message.channel.send("지휘관, 사용법이 틀린 것 같아...")


async def gachasearch(message, args, authinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Gacha?retryWrites=true&w=majority" % dbpass)
    prizedata = mclient.Gacha.System.find_one({"SYSTEM": "PRIZELIST"})
    userdata = mclient.Gacha.Userdata.find_one({"ID": authinfo["ID"]})

    if userdata is None:
        arrhave = []
        arrcount = []
        for i in range(0, len(prizedata["NAME"])+1):
            arrhave.append(False)
            arrcount.append(0)
        mclient.Gacha.Userdata.insert_one({"ID": authinfo["ID"], "NAME": authinfo["NAME"], "PRIZE": {"HAVE": arrhave, "COUNT": arrcount}})
    userdata = mclient.Gacha.Userdata.find_one({"ID": authinfo["ID"]})
    userdata["NAME"] = authinfo["NAME"]
    for i in range(0, len(prizedata["NAME"])-len(userdata["PRIZE"]["HAVE"])):
        userdata["PRIZE"]["HAVE"].append(False)
    for i in range(0, len(prizedata["NAME"]) - len(userdata["PRIZE"]["COUNT"])):
        userdata["PRIZE"]["COUNT"].append(0)
    mclient.Gacha.Userdata.update_one({"ID": authinfo["ID"]}, {"$set": userdata})

    if len(args) == 3:
        embed = discord.Embed(title="가챠", description="지휘관...? 궁금한게 있다면 라피가 찾아와줄게...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```", value="이 명령어를 통해 카드에 대한 정보 열람이 가능합니다.", inline=False)
        embed.add_field(name="```사용법```", value="!라피 가챠 검색 (번호)\n단, 한 번이라도 소지했던 적이 있던 카드만 확인이 가능합니다.", inline=False)
        await message.channel.send(embed=embed)
    elif len(args) == 4 and args[3].isdigit():
        if 0 <= int(args[3]) < (len(prizedata["NAME"]) - 1):
            if userdata["PRIZE"]["HAVE"][int(args[3])] is True:
                embed = discord.Embed(title="가챠", description="찾았어 지휘관...라피는 칭찬해줘 칭찬해줘 포즈, 안 했어...... 응, 안 했어.",
                                      color=0xf8f5ff)
                embed.set_thumbnail(
                    url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
                embed.set_image(
                    url="%s" % prizedata["IMAGE"][int(args[3])])
                embed.add_field(name="```No.%d```" % int(args[3]), value="%s" % prizedata["NAME"][int(args[3])], inline=False)
                embed.add_field(name="```판매가```", value="%d" % int(prizedata["PRICE"][int(args[3])]), inline=False)
                embed.add_field(name="```정보```", value="%s" % prizedata["DATA"][int(args[3])], inline=False)
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="가챠", description="지휘관...이전에 얻은 적이 없는 카드인 것 같아...",
                                      color=0xf8f5ff)
                embed.set_thumbnail(
                    url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
                embed.add_field(name="```No.%d```" % int(args[3]), value="???", inline=False)
                embed.add_field(name="```판매가```", value="???", inline=False)
                embed.add_field(name="```정보```", value="???", inline=False)
                await message.channel.send(embed=embed)
        else:
            message.channel.send("지휘관...그런 번호는 없는 것 같아...")
    else:
        await message.channel.send("지휘관...사용법이 틀린 것 같아...")