import random
import discord
import datetime
import pymongo
import asyncio


# 포인트 함수
async def botpoint(channel, args, authinfo, dbpass):
    if len(args) == 2:
        embed = discord.Embed(title="(빤히)...지휘관한테 얼마나 있는지, 생각하고 있었어.",
                              description="!라피 포인트 보내기 (대상) (수량) : 포인트를 보낼 수 있습니다.\n!라피 포인트 확인 (대상) : 대상의 포인트 확인이 가능합니다." +
                                          "\n!라피 포인트 구제 : 포인트가 없으면 100 LP를 받습니다.\n!라피 포인트 기부 : 기부 기능을 열람합니다.",
                              color=0xf8f5ff)
        embed.add_field(name="```%s 지휘관의 소지 포인트```" % authinfo["NAME"], value="```%d LP```" % authinfo["POINTS"], inline=False)
        if authinfo["DEBT"] > 0:
            embed.add_field(name="```%s 지휘관의 남은 빚```" % authinfo["NAME"], value="```cs\n%d LP```" % authinfo["DEBT"], inline=False)
        await channel.send(embed=embed)
    elif args[2] == "확인":
        await pointcheck(channel, args, dbpass)
    elif args[2] == "보내기":
        if authinfo["DEBT"] > 0:
            await channel.send("지휘관, 빚이 있으면 다른 지휘관한테 포인트를 보낼 수 없어...")
        await pointsend(channel, args, authinfo, dbpass)
    elif args[2] == "구제":
        await pointsavior(channel, authinfo, dbpass)
    elif args[2] == "기부":
        await pointdonate(channel, args, authinfo, dbpass)
    else:
        await channel.send("지휘관, 알 수 없는 명령어야...")


def pointcheck(channel, args, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    info = mclient.Laffey.Data.find_one({"NAME": args[3]})
    if info is None:
        return channel.send("그런 이름의 지휘관은 없어...")
    embed = discord.Embed(title="Zzz...(!)...그 지휘관한테 얼마나 있는지, 생각하고 있었어.",
                          description="!라피 포인트 보내기 (대상) (수량) : 포인트를 보낼 수 있습니다.\n!라피 포인트 확인 (대상) : 대상의 포인트 확인이 가능합니다.",
                          color=0xf8f5ff)
    embed.add_field(name="```%s 지휘관의 소지 포인트```" % info["NAME"], value="```%d LP```" % info["POINTS"], inline=False)
    if info["DEBT"] > 0:
        embed.add_field(name="```%s 지휘관의 남은 빚```" % info["NAME"], value="```cs\n%d LP```" % info["DEBT"], inline=False)
    return channel.send(embed=embed)


def pointsend(channel, args, authinfo, dbpass):
    if len(args) != 5:
        return channel.send("지휘관, 사용 방법이 틀렸어...(!라피 포인트 보내기 (지휘관) (수량)")
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    info = mclient.Laffey.Data.find_one({"NAME": args[3]})
    if info is None:
        return channel.send("그런 이름의 지휘관은 없어...")
    if info["NAME"] == authinfo["NAME"]:
        return channel.send("지휘관, 자기 자신한테 보내는건 안돼...")
    if int(args[4]) <= 0:
        return channel.send("지휘관, 0 LP 이하는 보낼 수 없어...")
    if authinfo["POINTS"] < int(args[4]):
        return channel.send("지휘관, 포인트가 모자라...")
    else:
        info["POINTS"] += int(args[4])
        authinfo["POINTS"] -= int(args[4])
        mclient.Laffey.Data.update_one({"ID": authinfo["ID"]}, {"$set": authinfo})
        mclient.Laffey.Data.update_one({"ID": info["ID"]}, {"$set": info})
        embed = discord.Embed(title="이 정도쯤, 아무렇지도 않아...",
                              description="성공적으로 %s 포인트를 전달하였습니다." % args[4],
                              color=0xf8f5ff)
        embed.add_field(name="```%s 지휘관의 남은 포인트```" % authinfo["NAME"], value="```%d LP```" % authinfo["POINTS"], inline=False)
        embed.add_field(name="```%s 지휘관의 남은 포인트```" % info["NAME"], value="```%d LP```" % info["POINTS"], inline=False)
        return channel.send(embed=embed)


def pointsavior(channel, authinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    info = mclient.Laffey.Data.find_one({"ID": authinfo["ID"]})
    if info["POINTS"] <= 0:
        mclient.Laffey.Data.update_one({"ID": authinfo["ID"]}, {"$set": {"POINTS": info["POINTS"] + 100}})
        tempvar = mclient.Laffey.Data.find_one({"ID": 1004})
        mclient.Laffey.Data.update_one({"ID": 1004}, {"$set": {"COUNT": tempvar["COUNT"]+1, "SAVING": tempvar["SAVING"]-100}})
        if int(tempvar["SAVING"]) <= 0:
            return channel.send("누군가 라피의 용돈을 전부 빌려가버렸어...이제 남은 용돈이 없어...")
        embed = discord.Embed(title="지휘관...... 혹시, 빈털털이...?",
                              description="힘내 지휘관...작지만 이거라도 줄게...(+ 100 LP)\n 현재까지 누군가 받아간 수 : %d\n라피의 남은 용돈 : %d LP" % (int(tempvar["COUNT"]+1), int(tempvar["SAVING"]-100)),
                              color=0xf8f5ff)
        return channel.send(embed=embed)
    else:
        embed = discord.Embed(title="지휘관...?",
                              description="빈털털이가 아니잖아...",
                              color=0xf8f5ff)
        return channel.send(embed=embed)


async def pointdonate(channel, args, authinfo, dbpass):
    if len(args) == 3:
        mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
        tempvar = mclient.Laffey.Data.find_one({"ID": 1004})
        donateid = -1
        for i in range(0, len(tempvar["DONATELIST"]["ID"])):
            if authinfo["ID"] == tempvar["DONATELIST"]["ID"][i]:
                donateid = i
                break
        if donateid == -1:
            tempvar["DONATELIST"]["ID"].append(authinfo["ID"])
            tempvar["DONATELIST"]["NAME"].append(authinfo["NAME"])
            tempvar["DONATELIST"]["TOTAL"].append(0)
            mclient.Laffey.Data.update_one({"ID": 1004}, {"$set": tempvar})
        else:
            tempvar["DONATELIST"]["NAME"][donateid] = authinfo["NAME"]
        embed = discord.Embed(title="지휘관, 지금까지 얼마나 기부했는지 알려줄게...",
                              description="!라피 포인트 기부 (수량) : 지정한 양의 포인트를 기부합니다.",
                              color=0xf8f5ff)
        embed.add_field(name="```%s 지휘관의 총 기부액```" % tempvar["DONATELIST"]["NAME"][donateid], value="```%d LP```" % tempvar["DONATELIST"]["TOTAL"][donateid], inline=False)
        embed.add_field(name="```라피의 남은 용돈```", value="```%d LP```" % tempvar["SAVING"], inline=False)
        await channel.send(embed=embed)
    elif len(args) == 4:
        if (not args[3].isdigit()) or int(args[3]) <= 0:
            await channel.send("지휘관, 기부할 양을 제대로 적어줘...")
            return
        if authinfo["POINTS"] < int(args[3]):
            await channel.send("지휘관, 포인트가 모자라...")
            return
        mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
        tempvar = mclient.Laffey.Data.find_one({"ID": 1004})
        tempvar["SAVING"] += int(args[3])
        authinfo["POINTS"] -= int(args[3])
        donateid = -1
        for i in range(0, len(tempvar["DONATELIST"]["ID"])):
            if authinfo["ID"] == tempvar["DONATELIST"]["ID"][i]:
                donateid = i
                break
        if donateid == -1:
            tempvar["DONATELIST"]["ID"].append(authinfo["ID"])
            tempvar["DONATELIST"]["NAME"].append(authinfo["NAME"])
            tempvar["DONATELIST"]["TOTAL"].append(int(args[3]))
        else:
            tempvar["DONATELIST"]["NAME"][donateid] = authinfo["NAME"]
            tempvar["DONATELIST"]["TOTAL"][donateid] += int(args[3])
        mclient.Laffey.Data.update_one({"ID": authinfo["ID"]}, {"$set": authinfo})
        mclient.Laffey.Data.update_one({"ID": 1004}, {"$set": tempvar})
        embed = discord.Embed(title="지휘관, 기부 고마워...",
                              description="성공적으로 %s 포인트를 기부하였습니다." % args[3],
                              color=0xf8f5ff)
        embed.add_field(name="```%s 지휘관의 남은 포인트```" % authinfo["NAME"], value="```%d LP```" % authinfo["POINTS"], inline=False)
        embed.add_field(name="```%s 지휘관의 총 기부액```" % tempvar["DONATELIST"]["NAME"][donateid], value="```%d LP```" % tempvar["DONATELIST"]["TOTAL"][donateid], inline=False)
        embed.add_field(name="```라피의 남은 용돈```", value="```%d LP```" % tempvar["SAVING"], inline=False)
        await channel.send(embed=embed)
    else:
        await channel.send("지휘관, 사용법이 틀린 것 같아...")


# 포인트벌이 함수
async def pointearning(message, args, authinfo, dbpass):
    channel = message.channel
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    earndata = mclient.Laffey.Pointearning.find_one({"ID": authinfo["ID"]})
    if earndata is None:
        mclient.Laffey.Pointearning.insert_one({"ID": authinfo["ID"], "EARNING": 0, "STRING": "letsearnpoints"})
        earndata = mclient.Laffey.Pointearning.find_one({"ID": authinfo["ID"]})
    if len(args) == 2:
        embed = discord.Embed(title="포인트 벌이", description="지휘관에게 포인트를 벌 수 있도록 일거리를 줄게...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```현재 저장된 포인트```", value="%d LP" % earndata["EARNING"], inline=False)
        embed.add_field(name="```!라피 포인트벌이 타이핑 ```", value="타이핑을 통해 포인트를 벌 수 있습니다.", inline=False)
        embed.add_field(name="```!라피 포인트벌이 수령 ```", value="저장된 포인트를 수령합니다.", inline=False)
        await channel.send(embed=embed)
    else:
        if args[2] == "타이핑":
            await earningtyping(message, args, authinfo, dbpass)
        elif args[2] == "수령":
            mclient.Laffey.Pointearning.update_one({"ID": authinfo["ID"]}, {"$set": {"EARNING": 0}})
            await earningtake(message, earndata["EARNING"], authinfo, dbpass)
        else:
            await channel.send("지휘관, 그건 할 수 없어...")


async def earningtake(message, points, authinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    mclient.Laffey.Data.update_one({"ID": authinfo["ID"]}, {"$set": {"POINTS": authinfo["POINTS"] + points}})
    embed = discord.Embed(title="포인트 수령", description="지휘관...저장되어 있던 포인트를 수령했어...",
                          color=0xf8f5ff)
    embed.set_thumbnail(
        url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
    embed.add_field(name="```수령액```", value="%d LP" % points, inline=False)
    embed.add_field(name="```[%s] 지휘관의 현재 LP```" % authinfo["NAME"], value="%d LP" % int(authinfo["POINTS"] + points), inline=False)
    await message.channel.send(embed=embed)


async def earningtyping(message, args, authinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    typedata = mclient.Laffey.Pointearning.find_one({"ID": authinfo["ID"]})
    if typedata is None:
        mclient.Laffey.Pointearning.insert_one({"ID": authinfo["ID"], "EARNING": 0, "STRING": "letsearnpoints"})
    if len(args) == 3:
        embed = discord.Embed(title="포인트 벌이", description="지휘관에게 포인트를 벌 수 있도록 일거리를 줄게...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```방법```", value="!라피 포인트벌이 타이핑 (타이핑내용)", inline=False)
        embed.add_field(name="```도움말```", value="지정된 랜덤한 문자열을 타이핑하여 LP를 벌 수 있습니다. 매 1회마다 50 LP 가 지급됩니다.\n틀릴 경우 보상은 지급되지 않습니다.", inline=False)
        embed.add_field(name="```[%s] 지휘관의 현재 지정 문자열```" % authinfo["NAME"], value="%s" % typedata["STRING"], inline=False)
        await message.channel.send(embed=embed)
    elif len(args) == 4:
        if args[3] == typedata["STRING"]:
            nextstring = makerandomstring()
            mclient.Laffey.Pointearning.update_one({"ID": authinfo["ID"]}, {"$set": {"EARNING": typedata["EARNING"] + 50, "STRING": nextstring}})
            await message.channel.send("제대로 입력했어, 지휘관. 다음 문자열은 이거야...\n[%s] 지휘관의 다음 문자열```%s```" % (authinfo["NAME"], nextstring))
        else:
            await message.channel.send("지휘관, 입력한 문자열이 틀린 것 같아... 문자열을 다시 확인해봐...\n[%s] 지휘관의 현재 문자열```%s```" % (authinfo["NAME"], typedata["STRING"]))


def makerandomstring():
    stringlist = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                  "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                  "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    res = []
    for i in range(0, random.randint(5, 15)):
        res.append(random.choice(stringlist))
    res = "".join(res)
    return res


# 저금 부분 함수
async def pointsaving(message, args, authinfo, dbpass):
    channel = message.channel
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    savedata = mclient.Laffey.Data.find_one({"ID": authinfo["ID"]})

    if len(args) == 2:
        embed = discord.Embed(title="저금", description="지휘관, 꽃, 장식해볼래?",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```",
                        value="!라피 저금 입금 (수량) : 입력한 수량만큼 포인트를 저금합니다.\n" +
                              "!라피 저금 출금 (수량) : 입력한 수량만큼 포인트를 출금합니다.\n" +
                              "!라피 저금 대출 : 아카시론에 포인트 대출에 대해 상담합니다.", inline=False)
        embed.add_field(name="```주의사항```",
                        value="```cs\n출금은 하루에 '1회'만 가능합니다!```", inline=False)
        embed.add_field(name="```[ %s ] 지휘관의 현재 잔고```" % authinfo["NAME"],
                        value="```%d LP```" % savedata["SAVING"], inline=False)
        if savedata["DEBT"] > 0:
            embed = discord.Embed(title="아카시론", description="빚은 나쁜거다냥.",
                                  color=0xf8f5ff)
            embed.set_thumbnail(
                url="https://images2.imgbox.com/07/42/r545TkU2_o.png")
            embed.add_field(name="```도움말```",
                            value="!라피 저금 청산 (수량) : 입력한 수량만큼 빚을 청산한다냐.", inline=False)
            embed.add_field(name="```주의사항```",
                            value="```cs\n# 빚을 갚아야 은행 이용이 가능하다냥! -아카시-```", inline=False)
            embed.add_field(name="```[ %s ] 지휘관의 현재 빚```" % savedata["NAME"],
                            value="```cs\n%d LP```" % savedata["DEBT"], inline=False)
        await channel.send(embed=embed)
    elif args[2] == "입금":
        if savedata["DEBT"] > 0:
            await channel.send("지휘관...빚을 먼저 갚아야 해...")
            return
        await deposit(message, args, savedata, dbpass)
    elif args[2] == "출금":
        if savedata["DEBT"] > 0:
            await channel.send("지휘관...빚을 먼저 갚아야 해...")
            return
        await withdrawl(message, args, savedata, dbpass)
    elif args[2] == "대출":
        await loan(message, args, savedata, dbpass)
    elif args[2] == "청산":
        if savedata["DEBT"] <= 0:
            await channel.send("지휘관...진 빚이 없는데...")
            return
        await debtpayoff(message, args, savedata, dbpass)
    else:
        await channel.send("지휘관, 그건 못해...")


async def deposit(message, args, saveinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    if len(args) != 4 or not args[3].isdigit():
        await message.channel.send("지휘관 사용법이 틀린 것 같아...")
    elif int(args[3]) <= 0:
        await message.channel.send("지휘관...0LP 이하는 저금할 수 없어...")
    elif int(args[3]) > saveinfo["POINTS"]:
        await message.channel.send("지휘관...포인트가 모자라...")
    else:
        saveinfo["POINTS"] -= int(args[3])
        saveinfo["SAVING"] += int(args[3])
        embed = discord.Embed(title="저금", description="지휘관, 포인트를 보관하려고...? 라피가 잘 보관하고 있을게...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```도움말```",
                        value="!라피 저금 입금 (수량) : 입력한 수량만큼 포인트를 저금합니다.\n" +
                              "!라피 저금 출금 (수량) : 입력한 수량만큼 포인트를 출금합니다.", inline=False)
        embed.add_field(name="```[ %s ] 지휘관의 보유 포인트```" % saveinfo["NAME"],
                        value="```%d LP```" % saveinfo["POINTS"], inline=False)
        embed.add_field(name="```[ %s ] 지휘관의 현재 잔고```" % saveinfo["NAME"],
                        value="```%d LP```" % saveinfo["SAVING"], inline=False)
        await message.channel.send(embed=embed)
        mclient.Laffey.Data.update_one({"ID": saveinfo["ID"]}, {"$set": saveinfo})


async def withdrawl(message, args, saveinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    if len(args) != 4 or not args[3].isdigit():
        await message.channel.send("지휘관 사용법이 틀린 것 같아...")
    elif int(args[3]) <= 0:
        await message.channel.send("지휘관...0LP 이하는 저금할 수 없어...")
    elif int(args[3]) > saveinfo["SAVING"]:
        await message.channel.send("지휘관...%d LP밖에 저금하지 않았어..." % saveinfo["SAVING"])
    else:
        if saveinfo["BANKDATE"] < int(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y%m%d")):
            saveinfo["BANKDATE"] = int(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y%m%d"))
            saveinfo["POINTS"] += int(args[3])
            saveinfo["SAVING"] -= int(args[3])
            embed = discord.Embed(title="저금", description="지휘관, 포인트를 가져가려고...? 여기있어...",
                                  color=0xf8f5ff)
            embed.set_thumbnail(
                url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
            embed.add_field(name="```도움말```",
                            value="!라피 저금 입금 (수량) : 입력한 수량만큼 포인트를 저금합니다.\n" +
                                  "!라피 저금 출금 (수량) : 입력한 수량만큼 포인트를 출금합니다.", inline=False)
            embed.add_field(name="```[ %s ] 지휘관의 보유 포인트```" % saveinfo["NAME"],
                            value="```%d LP```" % saveinfo["POINTS"], inline=False)
            embed.add_field(name="```[ %s ] 지휘관의 현재 잔고```" % saveinfo["NAME"],
                            value="```%d LP```" % saveinfo["SAVING"], inline=False)
            await message.channel.send(embed=embed)
            mclient.Laffey.Data.update_one({"ID": saveinfo["ID"]}, {"$set": saveinfo})
        else:
            await message.channel.send("지휘관 이미 오늘은 포인트를 가져갔어...")


async def loan(message, args, saveinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    if len(args) == 3:
        embed = discord.Embed(title="아카시론", description="지휘관 포인트가 없어서 온거냥? 아카기가 '조금' 이자를 추가해서 빌려줄 수 있다냐.",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/07/42/r545TkU2_o.png")
        embed.add_field(name="```도움말```",
                        value="!라피 저금 대출 (수량) : 지정한 수량만큼 포인트를 대출합니다.\n빚이 존재하는 동안 지휘관의 계좌는 동결됩니다.\n대출 시 '대출액'의 '0.5배'가 '이자'로 추가됩니다.\n대출 한도는 5000 LP 입니다.", inline=False)
        embed.add_field(name="```[ %s ] 지휘관의 보유 포인트```" % saveinfo["NAME"],
                        value="```%d LP```" % saveinfo["POINTS"], inline=False)
        embed.add_field(name="```[ %s ] 지휘관의 남은 빛```" % saveinfo["NAME"],
                        value="```cs\n%d LP```" % saveinfo["DEBT"], inline=False)
        await message.channel.send(embed=embed)
        return
    if len(args) != 4 or not args[3].isdigit():
        await message.channel.send("지휘관, 사용법이 틀렸다냐 -아카시-")
    elif int(args[3]) <= 0:
        await message.channel.send("지금 장난하는거냥? 0 LP 를 빌릴수는 없다냐! -아카시-")
    elif (int(args[3]) + saveinfo["DEBT"]) > 5000:
        await message.channel.send("대출 한도 초과다냐. -아카시-")
    elif not saveinfo["DEBTDATE"] < int(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y%m%d")):
        await message.channel.send("이미 오늘 빌렸다냐. -아카시-")
    else:
        saveinfo["DEBTDATE"] = int(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y%m%d"))
        saveinfo["POINTS"] += int(args[3])
        saveinfo["DEBT"] += int(int(args[3]) * 1.5)
        embed = discord.Embed(title="아카시론", description="매번 고맙다냥~",
                              color=0xf8f5ff)
        if saveinfo["DEBT"] >= 5000:
            embed = discord.Embed(title="아카시론", description="이제 대출 한도다냐. 더이상 빌려줄 수는 없다냐.",
                                  color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/07/42/r545TkU2_o.png")
        embed.add_field(name="```도움말```",
                        value="!라피 저금 청산 (수량) : 입력한 수량만큼 빚을 청산합니다.\n빚이 존재하는 동안 지휘관의 계좌는 동결됩니다.\n대출 시 '대출액'의 '0.5배'가 '이자'로 추가됩니다.\n대출 한도는 5000 LP 입니다.", inline=False)
        embed.add_field(name="```[ %s ] 지휘관의 보유 포인트```" % saveinfo["NAME"],
                        value="```%d LP```" % saveinfo["POINTS"], inline=False)
        embed.add_field(name="```[ %s ] 지휘관의 남은 빛```" % saveinfo["NAME"],
                        value="```cs\n%d LP```" % saveinfo["DEBT"], inline=False)
        await message.channel.send(embed=embed)
        mclient.Laffey.Data.update_one({"ID": saveinfo["ID"]}, {"$set": saveinfo})


async def debtpayoff(message, args, saveinfo, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    if len(args) != 4 or not args[3].isdigit():
        await message.channel.send("지휘관, 사용법이 틀렸다냐")
    elif int(args[3]) <= 0:
        await message.channel.send("지금 장난하는거냥? 0 LP 갚는게 갚는거냥!")
    elif int(args[3]) > saveinfo["POINTS"]:
        await message.channel.send("포인트가 모자라다냐.")
    elif int(args[3]) > saveinfo["DEBT"]:
        await message.channel.send("물론 더 주면 좋지만, 아카시는 그정도로 가난하진 않다냐")
    else:
        saveinfo["POINTS"] -= int(args[3])
        saveinfo["DEBT"] -= int(args[3])
        embed = discord.Embed(title="아카시론", description="매번 고맙다냥~",
                              color=0xf8f5ff)
        if saveinfo["DEBT"] <= 0:
            embed = discord.Embed(title="아카시론", description="빚을 전부 다 갚았다냐. 수고했다냐.",
                                  color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/07/42/r545TkU2_o.png")
        embed.add_field(name="```도움말```",
                        value="!라피 저금 청산 (수량) : 입력한 수량만큼 빚을 청산합니다.", inline=False)
        embed.add_field(name="```[ %s ] 지휘관의 보유 포인트```" % saveinfo["NAME"],
                        value="```%d LP```" % saveinfo["POINTS"], inline=False)
        embed.add_field(name="```[ %s ] 지휘관의 남은 빛```" % saveinfo["NAME"],
                        value="```cs\n%d LP```" % saveinfo["DEBT"], inline=False)
        await message.channel.send(embed=embed)
        laffey = mclient.Laffey.Data.find_one({"ID": 1004})
        mclient.Laffey.Data.update_one({"ID": 1004}, {"$set": {"SAVING": laffey["SAVING"]+int(int(args[3])/10.0)}})
        mclient.Laffey.Data.update_one({"ID": saveinfo["ID"]}, {"$set": saveinfo})


# 투자 기능 함수
async def pointinvest(message, args, authinfo, dbpass):
    channel = message.channel
    if len(args) == 2:
        embed = discord.Embed(title="투자", description="지휘관, 지휘관. 라피, 무서워?",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```명령어```",
                        value="!라피 투자 [목록|종류] : 투자가 가능한 종목을 열람합니다.\n" +
                              "!라피 투자 정보 (이름) : 해당 종목에 대한 자세한 정보를 열람합니다.\n" +
                              "!라피 투자 [확인|보유] : 현재 보유 중인 종목을 열람합니다.\n" +
                              "!라피 투자 [구매|매수] (이름) (수량) : 해당 번호의 종목을 수량 만큼 매수합니다.\n" +
                              "!라피 투자 [판매|매도] (이름) (수량) : 해당 번호의 종목을 수량 만큼 매도합니다.", inline=False)
        embed.add_field(name="```도움말```",
                        value="```cs\n1. 매수/매도가의 경우 매 10 분 정도마다 갱신됩니다." +
                              "\n2. 떡락하던 떡상하던 라피는 모릅니다." +
                              "\n3. 거래 수수료는 다행히도 아직 받지 않습니다." +
                              "\n4. 해당 종목의 가격이 10 LP 보다 떨어지면 상장폐지되어 휴지조각이 됩니다.```", inline=False)
        await channel.send(embed=embed)
    elif args[2] in ["목록", "종류"]:
        await investlist(channel, dbpass)
    elif args[2] in ["정보"]:
        await investinfo(channel, args, dbpass)
    elif args[2] in ["확인", "보유"]:
        await investcheck(channel, authinfo["ID"], dbpass)
    elif args[2] in ["구매", "매수"]:
        await investbuy(channel, args, authinfo, dbpass)
    elif args[2] in ["판매", "매도"]:
        await investsell(channel, args, authinfo, dbpass)
    else:
        await channel.send("지휘관, 알 수 없는 명령어야...")


async def investlist(channel, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Invest?retryWrites=true&w=majority" % dbpass)
    investdata = mclient.Invest.System.find_one({"SYSTEM": "INVEST"})
    investpre = mclient.Invest.System.find_one({"SYSTEM": "INVESTPRE"})
    invlist = []
    for i in range(0, len(investdata["NAME"])):
        if investdata["PRICE"][i] <= 0:
            invlist.append(str(i + 1) + ". " + investdata["NAME"][i] +
                           " : 상장폐지" +
                           "\n  변화량 : 휴지조각이 되었음.")
            continue
        invlist.append(str(i+1) + ". " + investdata["NAME"][i] +
                       " : 개당 " + str(investdata["PRICE"][i]) +
                       " LP\n  변화량 : "+str(investdata["PRICE"][i] - investpre["PRICE"][i])+" LP")
    invlist = "\n".join(invlist)
    embed = discord.Embed(title="투자", description="지휘관, 지휘관. 라피, 무서워?",
                          color=0xf8f5ff)
    embed.set_thumbnail(
        url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
    embed.add_field(name="```현재 매수/매도가```",
                    value="```cs\n%s```" % invlist, inline=False)
    await channel.send(embed=embed)


async def investinfo(channel, args, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Invest?retryWrites=true&w=majority" % dbpass)
    investdata = mclient.Invest.System.find_one({"SYSTEM": "INVEST"})
    if args[3] in investdata["NAME"]:
        for i in range(0, len(investdata["NAME"])):
            if args[3] == investdata["NAME"][i]:
                args[3] = i
                break
        embed = discord.Embed(title="투자", description="해당 종목에 대해 정보를 가져왔어...",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```종목명```",
                        value="%s" % investdata["NAME"][int(args[3])], inline=False)
        embed.add_field(name="```초기 상장가```",
                        value="%d LP" % investdata["FIRSTPRICE"][int(args[3])], inline=False)
        embed.add_field(name="```현재 상장가```",
                        value="%d LP" % investdata["PRICE"][int(args[3])], inline=False)
        embed.add_field(name="```등락폭```",
                        value="%d" % investdata["VARIANCE"][int(args[3])], inline=False)
        embed.add_field(name="```종합평가```",
                        value="%s" % investdata["COMMENT"][int(args[3])], inline=False)
        await channel.send(embed=embed)
    else:
        await channel.send("지휘관, 그런 이름의 투자처는 없어...")


async def investcheck(channel, uid, dbpass):
    investdata, userdata = investdbload(uid, dbpass)
    invlist = []
    for i in range(0, len(investdata["NAME"])):
        invlist.append(str(i+1)+". "+investdata["NAME"][i]+" : "+str(userdata["HAVE"][i])+" 개\n  최근 구매가 : "+str(userdata["BUYPRICE"][i])+" LP")
    invlist = "\n".join(invlist)
    embed = discord.Embed(title="투자", description="지휘관, 지휘관. 라피, 무서워?",
                          color=0xf8f5ff)
    embed.set_thumbnail(
        url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
    embed.add_field(name="```현재 보유 종목```",
                    value="```cs\n%s```" % invlist, inline=False)
    await channel.send(embed=embed)


async def investbuy(channel, args, authinfo, dbpass):
    investdata, userdata = investdbload(authinfo["ID"], dbpass)
    if len(args) != 5 or (not args[4].isdigit()) or (args[4].isdigit() and int(args[4]) <= 0):
        await channel.send("지휘관 사용법이 틀린 것 같아...")
    elif args[3] in investdata["NAME"]:
        for i in range(0, len(investdata["NAME"])):
            if args[3] == investdata["NAME"][i]:
                args[3] = i
                break
        if investdata["PRICE"][int(args[3])] == 0:
            await channel.send("해당 투자 대상은 상장폐지가 된 상태야...")
            return
        if investdata["PRICE"][int(args[3])] * int(args[4]) <= authinfo["POINTS"]:
            authinfo["POINTS"] -= investdata["PRICE"][int(args[3])] * int(args[4])
            embed = discord.Embed(title="투자", description="지휘관, 성공적으로 매수를 완료했어...",
                                  color=0xf8f5ff)
            embed.set_thumbnail(
                url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
            embed.add_field(name="```매수 정보```",
                            value="매수 종목 : %s\n매수량 : %d\n매수가 : %d LP" % (investdata["NAME"][int(args[3])], int(args[4]), investdata["PRICE"][int(args[3])]), inline=False)
            await channel.send(embed=embed)
            mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Invest?retryWrites=true&w=majority" % dbpass)
            mclient.Laffey.Data.update_one({"ID": authinfo["ID"]}, {"$set": authinfo})
            userdata["HAVE"][int(args[3])] += int(args[4])
            userdata["BUYPRICE"][int(args[3])] = investdata["PRICE"][int(args[3])]
            investuserdbsave(userdata, dbpass)
        else:
            await channel.send("지휘관, 소지 포인트가 모자란 것 같아...")
    else:
        await channel.send("지휘관, 그런 이름의 투자처는 없어...")


async def investsell(channel, args, authinfo, dbpass):
    investdata, userdata = investdbload(authinfo["ID"], dbpass)
    if len(args) != 5 or (args[4].isdigit() and int(args[4]) <= 0):
        await channel.send("지휘관 사용법이 틀린 것 같아...")
    elif args[3] in investdata["NAME"]:
        for i in range(0, len(investdata["NAME"])):
            if args[3] == investdata["NAME"][i]:
                args[3] = i
                break
        if int(args[4]) <= userdata["HAVE"][int(args[3])]:
            authinfo["POINTS"] += investdata["PRICE"][int(args[3])] * int(args[4])
            embed = discord.Embed(title="투자", description="지휘관, 성공적으로 매도를 완료했어...",
                                  color=0xf8f5ff)
            embed.set_thumbnail(
                url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
            embed.add_field(name="```매도 정보```",
                            value="매도 종목 : %s\n매도량 : %d\n매도가 : %d LP" % (investdata["NAME"][int(args[3])], int(args[4]), investdata["PRICE"][int(args[3])]), inline=False)
            await channel.send(embed=embed)
            mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Invest?retryWrites=true&w=majority" % dbpass)
            mclient.Laffey.Data.update_one({"ID": authinfo["ID"]}, {"$set": authinfo})
            userdata["HAVE"][int(args[3])] -= int(args[4])
            if userdata["HAVE"][int(args[3])] <= 0:
                userdata["BUYPRICE"][int(args[3])] = "전량 판매"
            investuserdbsave(userdata, dbpass)
        else:
            await channel.send("지휘관, 매도에 필요한 양이 모자란 것 같아...")
    else:
        await channel.send("지휘관, 그런 이름의 투자처는 없어...")


async def investrenew(channel, dbpass, isbot):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Invest?retryWrites=true&w=majority" % dbpass)
    investdata = mclient.Invest.System.find_one({"SYSTEM": "INVEST"})
    if investdata["OPERATING"] is True:
        investpre = investdata
        del(investpre["_id"])
        del(investpre["SYSTEM"])
        mclient.Invest.System.update_one({"SYSTEM": "INVESTPRE"}, {"$set": investpre})
        for i in range(0, len(investdata["NAME"])):
            investdata["PRICE"][i] = int(investdata["PRICE"][i] * (1.0 - (investdata["VARIANCE"][i] * ((random.random() * 2.0) - 1.0))))
            if investdata["PRICE"][i] <= 50:
                print(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S %Z") + " - " + str(investdata["NAME"][i]) + " Bankrupted!")
                investdata["PRICE"][i] = 0
                users = mclient.Invest.Userdata.find({"HAVE": {"$gt": 0}})
                for user in users:
                    user["HAVE"][i] = 0
                    user["BUYPRICE"][i] = "휴지조각이 되었음"
                    mclient.Invest.Userdata.update_one({"ID": user["ID"]}, {"$set": user})
                investdata["PRICE"][i] = investdata["FIRSTPRICE"][i]
                if isbot is True:
                    await channel.send("```[ %s ] 이(가) 상장폐지 이후 재상장되었습니다.```" % investdata["NAME"][i])
        mclient.Invest.System.update_one({"SYSTEM": "INVEST"}, {"$set": investdata})
        print(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S %Z") + " - Investment Renew Complete.")


def investdbload(uid, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Invest?retryWrites=true&w=majority" % dbpass)
    investdata = mclient.Invest.System.find_one({"SYSTEM": "INVEST"})
    userdata = mclient.Invest.Userdata.find_one({"ID": uid})
    if userdata is None:
        havelist = []
        pricelist = []
        for i in range(0, len(investdata["NAME"])):
            havelist.append(0)
            pricelist.append(0)
        mclient.Invest.Userdata.insert_one({"ID": uid, "HAVE": havelist, "BUYPRICE": pricelist})
        userdata = mclient.Invest.Userdata.find_one({"ID": uid})
    for i in range(0, (len(investdata["NAME"])-len(userdata["HAVE"]))):
        userdata["HAVE"].append(0)
        userdata["BUYPRICE"].append(0)
    return investdata, userdata


def investuserdbsave(userdata, dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Invest?retryWrites=true&w=majority" % dbpass)
    mclient.Invest.Userdata.update_one({"ID": userdata["ID"]}, {"$set": userdata})


# 라피 복권 기능
async def lottery(message, args, authinfo, dbpass):
    channel = message.channel
    if len(args) == 2:
        embed = discord.Embed(title="복권", description="지휘관, 복권 사려고...?",
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```명령어```",
                        value="!라피 복권 [목록|종류] : 복권 종류을 열람합니다.\n" +
                              "!라피 복권 정보 (이름) : 해당 복권에 대한 자세한 정보를 열람합니다. 제작중.\n" +
                              "!라피 복권 구매 (이름) (개수) : 해당 복권을 구매합니다.\n" +
                              "!라피 복권 로또 : 로또에 대해 열람합니다. 제작중.", inline=False)
        embed.add_field(name="```도움말```",
                        value="```cs\n1. 복권과 로또는 하루에 각각 '10장'까지 구매가 가능합니다." +
                              "\n2. 로또는 매일 '오후 6시'에 추첨이 진행됩니다." +
                              "\n3. 복권은 매일 '오전 0시'에 초기화됩니다.```", inline=False)
        await channel.send(embed=embed)
    elif args[2] in ["목록", "종류"]:
        await lotterylist(channel, dbpass)
    elif args[2] in ["정보"]:
        await lotteryinfo(channel, args[3], dbpass)
    elif args[2] in ["구매", "사기"]:
        await lotterybuy(channel, args, authinfo, dbpass)
    elif args[2] in ["로또"]:
        await lotterylottery(channel, args, authinfo, dbpass)
    else:
        await channel.send("지휘관, 알 수 없는 명령어야...")


async def lotterylist(channel, dbpass):
    lotterydata = lotterydbload(0, dbpass, False)
    lotlist = []
    for i in range(0, len(lotterydata["NAME"])):
        if lotterydata["COUNT"][i] <= 0:
            lotlist.append(str(i + 1) + ". " + lotterydata["NAME"][i] +
                           " : 품절됨.")
            continue
        lotlist.append(str(i + 1) + ". " + lotterydata["NAME"][i] +
                       " : 개당 " + str(lotterydata["PRICE"][i]) +
                       " LP\n  남은 수량 : " + str(lotterydata["COUNT"][i]) + " 개")
    lotlist = "\n".join(lotlist)
    embed = discord.Embed(title="복권", description="지휘관, 복권에 대해 궁금해...?",
                          color=0xf8f5ff)
    embed.set_thumbnail(
        url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
    embed.add_field(name="```복권 목록```",
                    value="```cs\n%s```" % lotlist, inline=False)
    await channel.send(embed=embed)


async def lotteryinfo(channel, name, dbpass):
    lotterydata = lotterydbload(0, dbpass, False)
    num = -1
    for i in range(0, len(lotterydata["NAME"])):
        if name == lotterydata["NAME"][i]:
            num = i
            break
    if num != -1:
        initial = []
        current = []
        for i in range(0, len(lotterydata["WINDATA"][num]["NAME"])):
            initial.append(str(i + 1) + ". " + str(lotterydata["WINDATA"][num]["NAME"][i]) + " : " + str(lotterydata["WINDATA"][num]["COUNT"][i]) +
                           " 개\n  당첨금 : " + str(lotterydata["WIN"][num][lotterydata["WINDATA"][num]["NAME"][i]]) + " LP")
        for i in range(0, len(lotterydata["WINDATA"][num]["NAME"])):
            current.append(str(i + 1) + ". " + str(lotterydata["WINDATA"][num]["NAME"][i]) + " : " + str(lotterydata["DATA"].count(lotterydata["WINDATA"][num]["NAME"][i])) +
                           " 개\n  당첨금 : " + str(lotterydata["WIN"][num][lotterydata["WINDATA"][num]["NAME"][i]]) + " LP")
        initial = "\n".join(initial)
        current = "\n".join(current)
        embed = discord.Embed(title="복권", description="지휘관, [ %s ]에 대한 정보를 가져왔어..." % name,
                              color=0xf8f5ff)
        embed.set_thumbnail(
            url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
        embed.add_field(name="```초기 당첨금```",
                        value="%s" % initial, inline=False)
        embed.add_field(name="```남은 당첨금```",
                        value="%s" % current, inline=False)
        await channel.send(embed=embed)
    else:
        await channel.send("지휘관... 그런 이름의 복권은 없어...")
    return


async def lotterybuy(channel, args, authinfo, dbpass):
    lotterydata = lotterydbload(0, dbpass, False)
    userdata = lotterydbload(authinfo["ID"], dbpass, True)
    if len(args) != 5 or (args[4].isdigit() and int(args[4]) <= 0):
        await channel.send("지휘관 사용법이 틀린 것 같아...")
    elif args[3] in lotterydata["NAME"]:
        if (userdata["COUNTS"][0] + int(args[4])) > 10:
            await channel.send("지휘관...이미 복권을 10번 구입했어...")
            return
        for i in range(0, len(lotterydata["NAME"])):
            if args[3] == lotterydata["NAME"][i]:
                args[3] = i
                break
        if lotterydata["COUNT"][int(args[3])] <= int(args[4]):
            await channel.send("지휘관...남은 복권 양이 모자라...")
            return
        if lotterydata["PRICE"][int(args[3])] * int(args[4]) <= authinfo["POINTS"]:
            authinfo["POINTS"] -= lotterydata["PRICE"][int(args[3])] * int(args[4])
            userdata["COUNTS"][0] += int(args[4])
            lotterydata["COUNT"][int(args[3])] -= int(args[4])
            result = []
            total = 0
            for i in range(0, int(args[4])):
                res = lotterydata["DATA"][int(args[3])].pop()
                authinfo["POINTS"] += lotterydata["WIN"][int(args[3])][res]
                total += lotterydata["WIN"][int(args[3])][res]
                result.append(str(i+1)+". "+res+" - 당첨금 : "+str(lotterydata["WIN"][int(args[3])][res])+" LP")
            result.append("총 당첨금 : "+str(total)+" LP")
            result = "\n".join(result)
            embed = discord.Embed(title="복권", description="지휘관, 성공적으로 구매를 완료했어...",
                                  color=0xf8f5ff)
            embed.set_thumbnail(
                url="https://images2.imgbox.com/20/b1/fi8X55Pc_o.png")
            embed.add_field(name="```%s 구매 결과```" % lotterydata["NAME"][int(args[3])],
                            value="```cs\n%s```" % result, inline=False)
            await channel.send(embed=embed)
            mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
            mclient.Laffey.Data.update_one({"ID": authinfo["ID"]}, {"$set": authinfo})
            lotterydbsave(userdata, dbpass, True)
            lotterydbsave(lotterydata, dbpass, False)
        else:
            await channel.send("지휘관, 소지 포인트가 모자란 것 같아...")
    else:
        await channel.send("지휘관, 그런 이름의 복권은 없어...")


async def lotterylottery(channel, args, authinfo, dbpass):
    await channel.send("제작중.")
    return


def lotterydbload(uid, dbpass, isuser):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    if isuser is False:
        lotterydata = mclient.Laffey.Lottery.find_one({"SYSTEM": "LOTTERY"})
        return lotterydata
    else:
        userdata = mclient.Laffey.Lottery.find_one({"ID": uid})
        if userdata is None:
            mclient.Laffey.Lottery.insert_one({"ID": uid, "LOTTERY": [], "COUNTS": [0, 0]})
            userdata = mclient.Laffey.Lottery.find_one({"ID": uid})
        return userdata


def lotterydbsave(data, dbpass, isuser):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    if isuser is True:
        mclient.Laffey.Lottery.update_one({"ID": data["ID"]}, {"$set": data})
        return
    else:
        mclient.Laffey.Lottery.update_one({"SYSTEM": "LOTTERY"}, {"$set": data})
        return


def lotteryrestock(name, dbpass):
    lotterydata = lotterydbload(0, dbpass, False)
    if lotterydata is None:
        print(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S %Z") + " - DB Data Not Found")
        return
    num = -1
    for i in range(0, len(lotterydata["NAME"])):
        if name == lotterydata["NAME"][i]:
            num = i
            break
    if num != -1:
        lotterydata["DATA"][num] = []
        for i in range(0, len(lotterydata["WINDATA"][num]["NAME"])):
            for j in range(0, lotterydata["WINDATA"][num]["COUNT"][i]):
                lotterydata["DATA"][num].append(lotterydata["WINDATA"][num]["NAME"][i])
        random.shuffle(lotterydata["DATA"][num])
        lotterydata["COUNT"][num] = lotterydata["FIRSTCOUNT"][num]
        lotterydbsave(lotterydata, dbpass, False)
        print(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S %Z") + " - " + str(name) + " 재보급 완료!")
    else:
        print(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S %Z") + " - "+str(name)+" is Not Exist")
    return


def lotterylimitreset(dbpass):
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    users = mclient.Laffey.Lottery.find({"ID": {"$gt": 0}})
    for user in users:
        user["COUNTS"][0] = 0
        user["COUNTS"][1] = 0
        mclient.Invest.Userdata.update_one({"ID": user["ID"]}, {"$set": user})
