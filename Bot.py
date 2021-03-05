import discord
from discord.ext import tasks
import asyncio
import pymongo
import os
import commands
import gamblefunction
import gachafunction
import points


dbpass = os.environ["DB_PASS"]
client = discord.Client()


@client.event
async def on_ready():
    print("========================================")
    print("ID : ", client.user.id)
    print("Project : Bot. Laffey")
    print("Version : v.1.0")
    print("Made by Team Kyle.")
    print("========================================")
    status = "낮잠 자기"
    await client.change_presence(status=discord.Status.idle, activity=discord.Game(status))
    print("Bot is ready.")


@client.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel
    if user.bot:
        return None
    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    db = mclient.Laffey.Data
    authinfo = db.find_one({"ID": user.id})
    if authinfo["ISONREACT"] is False:
        db.update_one({"ID": user.id}, {"$set": {"ISONREACT": True}})
        await gachafunction.letsgachaonreact(reaction, user, dbpass)

        await gamblefunction.dicegameonreact(reaction, user, dbpass)
        await gamblefunction.updownonreact(reaction, user, dbpass)
        await gamblefunction.blackjackonreact(reaction, user, dbpass)
        await gamblefunction.laffeyduelonreact(reaction, user, dbpass)
        await gamblefunction.drawpokeronreact(reaction, user, dbpass)
        db.update_one({"ID": user.id}, {"$set": {"ISONREACT": False}})


@client.event
async def on_message(message):
    def asking(m):
        return m.channel == channel and m.author == m.author

    mclient = pymongo.MongoClient("mongodb+srv://Admin:%s@botdb.0iuoe.mongodb.net/Laffey?retryWrites=true&w=majority" % dbpass)
    db = mclient.Laffey.Data
    uid = message.author.id
    channel = message.channel
    authinfo = db.find_one({"ID": uid})

    if message.author.bot:  # 봇에는 반응하지 않도록.
        await gachafunction.letsgachaaddreact(message, client)

        await gamblefunction.dicegamefirstreact(message, client)
        await gamblefunction.updownfirstreact(message, client)
        await gamblefunction.blackjackfirstreact(message, client)
        await gamblefunction.laffeyduelfirstreact(message, client)
        await gamblefunction.drawpokerfirstreact(message, client)
        return None

    # db에 없는 id일 경우.
    if authinfo is None:
        db.insert_one({"ID": uid, "NAME": message.author.name, "POINTS": 1000, "DCTime": 0, "DCStimul": 0, "DCTotal": 0, "BANKDATE": 0, "SAVING": 0, "DEBT": 0, "ISONACT": False, "ISONREACT": False})
    db.update_one({"ID": uid}, {"$set": {"NAME": message.author.name}})

    # 만약 특정 채널에서만 작동 가능 위해서는 아래 문구를 조건 뒤에 추가.
    # and str(channel) == "봇채널"
    if message.content.startswith("!라피"):
        db.update_one({"ID": uid}, {"$set": {"NAME": message.author.name}})
        if authinfo["ISONACT"] is True:
            await channel.send("지휘관, 이미 무언가를 하고 있어...")
            return None
        cmdline = message.content.split(' ')
        if len(cmdline) == 1:
            await channel.send(commands.noargs())
        elif len(cmdline) >= 2:
            if cmdline[1] == "도움말":
                await commands.bothelp(channel, cmdline)
            elif cmdline[1] == "정보":
                await commands.botinfo(channel)
            elif cmdline[1] == "포인트":
                await points.botpoint(channel, cmdline, authinfo, dbpass)
            elif cmdline[1] == "출석체크":
                await commands.attendcheck(channel, authinfo, dbpass)
            elif cmdline[1] == "도박":
                await commands.gamble(message, cmdline, authinfo, dbpass)
            elif cmdline[1] == "가챠":
                await commands.gacha(message, cmdline, authinfo, dbpass)
            elif cmdline[1] == "포인트벌이":
                await points.pointearning(message, cmdline, authinfo, dbpass)
            elif cmdline[1] == "저금":
                await points.pointsaving(message, cmdline, authinfo, dbpass)
            elif cmdline[1] == "투자":
                await points.pointinvest(message, cmdline, authinfo, dbpass)
            elif cmdline[1] == "디버그":
                await commands.debug(client, message, cmdline, authinfo, dbpass)
            else:
                await channel.send("지휘관, 무슨 말인지 모르겠어...졸려...같이 코~할래?")
    if message.content.startswith("!벤슨"):
        await message.channel.send("벤슨 언니...좋긴 하지만...귀찮은 걸 많이 시켜...")
    if message.content.startswith("!니미"):
        await message.channel.send("자벨린, 아야나미, Z23......모두 친구... 모두랑 쭈욱 함께 있고 싶어.")
    if message.content.startswith("!자벨린"):
        await message.channel.send("자벨린, 아야나미, Z23......모두 친구... 모두랑 쭈욱 함께 있고 싶어.")
    if message.content.startswith("!아야나미"):
        await message.channel.send("자벨린, 아야나미, Z23......모두 친구... 모두랑 쭈욱 함께 있고 싶어.")
    if message.content.startswith("!아카시"):
        await message.channel.send("지휘관도 아카시의 수리가 필요한 거냥?")


@tasks.loop(minutes=10.0)
async def invest_renewing():
    await client.wait_until_ready()
    cha = discord.Client.get_channel(client, 817014562561851442)
    await points.investrenew(cha, dbpass)


# 수동 토큰 설정시

access_token = os.environ["BOT_TOKEN"]
invest_renewing.start()
client.run(access_token)
