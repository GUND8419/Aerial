import os
import discord
import fortnitepy
import json
import yaml
import dotenv
import asyncio
import random
import requests
import sys
from functools import partial

# Load Accounts #
if os.path.isfile("accounts.yml"):
    accounts = yaml.safe_load(open("accounts.yml"))
else:
    sys.exit("Cannot Load accounts.yml!")


# API Functions #
def get_cosmetic(name: str, backendType: str = ""):
    return json.loads(requests.get(
        "https://benbotfn.tk/api/v1/cosmetics/br/search",
        params={
            "lang": "en",
            "searchLang": "en",
            "matchMethod": "contains",
            "backendType": backendType,
            "name": name
        }
    ).text)


def get_cosmetic_by_id(id: str):
    r = requests.get(
        "https://benbotfn.tk/api/v1/cosmetics/br/" + id
    )
    return json.loads(r.text) if r.status_code != 404 else None


def get_playlist(name: str):
    return json.loads(requests.get(
        "http://scuffedapi.xyz/api/playlists/search",
        params={
            "displayName": name
        }
    ).text)


# Variables #
dotenv.load_dotenv()
clients = {}
available = {}
owner = {}
messages = {}
loop = asyncio.get_event_loop()

# Discord Client #
dclient = discord.Client(
    activity=discord.Streaming(
        platform="Twitch",
        name="256 Fortnite Bots",
        details="256 Fortnite Bots",
        game="256 Fortnite Bots",
        url="https://twitch.tv/andre4ik3"
    )
)


# Bot Functions #
async def refresh_message(client: fortnitepy.Client):
    message = messages[client]
    await message.edit(
        embed=discord.Embed(
            title="<:Online:719038976677380138> " + client.user.display_name,
            type="rich",
            color=0xfc5fe2
        ).set_thumbnail(
            url=get_cosmetic_by_id(client.party.me.outfit)['icons']['icon']
        )
    )


async def stop_bot(client: fortnitepy.Client, ownerid: int, text: str = None):
    await client.wait_until_ready()
    for f in list(client.friends.values()):
        await f.remove()
    for f in list(client.pending_friends.values()):
        await f.decline()
    name = client.user.display_name
    await client.close()
    available[name] = client
    owner.pop(ownerid)
    await messages[client].edit(
        embed=discord.Embed(
            title="<:Offline:719321200098017330> Bot Offline",
            description=text,
            type="rich",
            color=0x747f8d
        )
    )
    await dclient.get_channel(720787276329910363).edit(
        name=str(len(owner)) + "/256 Clients Running"
    )


async def start_bot(member: discord.Member, time: int):
    try:
        message = await member.send(
            embed=discord.Embed(
                title="<a:Loading:719025775042494505> Starting Bot...",
                type="rich",
                color=0x7289da
            )
        )
    except discord.Forbidden:
        return
    if member.id in list(owner.keys()):
        await message.edit(
            embed=discord.Embed(
                title=":x: Bot Already Running!",
                color=0xe46b6b
            ),
            delete_after=3
        )
        return
    else:
        name = random.choice(list(available.keys()))
        client = available[name]
        available.pop(name)
        owner[member.id] = client
        messages[client] = message

    @client.event
    async def event_friend_request(friend: fortnitepy.PendingFriend):
        if friend.direction != "INBOUND":
            return
        rmsg = await member.send(
            embed=discord.Embed(
                title="<:FriendRequest:719042256849338429> Friend Request from " + friend.display_name,
                type="rich",
                description="<:Accept:719047548219949136> Accept    <:Reject:719047548819472446> Reject"
            )
        )
        await rmsg.add_reaction(":Accept:719047548219949136")
        await rmsg.add_reaction(":Reject:719047548819472446")

        def check(reaction, user):
            if str(reaction.emoji) in ["<:Accept:719047548219949136>", "<:Reject:719047548819472446>"] and not user.bot:
                return True
            else:
                return False

        try:
            reaction, user = await dclient.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await friend.decline()
            await rmsg.edit(
                delete_after=1,
                embed=discord.Embed(
                    title="<:FriendRequest:719042256849338429> Friend Request from " + friend.display_name,
                    type="rich",
                    color=0xf24949
                )
            )
        else:
            if str(reaction.emoji) == "<:Accept:719047548219949136>":
                await friend.accept()
                await rmsg.edit(
                    delete_after=1,
                    embed=discord.Embed(
                        title="<:FriendRequest:719042256849338429> Friend Request from " + friend.display_name,
                        type="rich",
                        color=0x43b581
                    )
                )
            elif str(reaction.emoji) == "<:Reject:719047548819472446>":
                await friend.decline()
                await rmsg.edit(
                    delete_after=1,
                    embed=discord.Embed(
                        title="<:FriendRequest:719042256849338429> Friend Request from " + friend.display_name,
                        type="rich",
                        color=0xf24949
                    )
                )

    @client.event
    async def event_party_invite(invitation: fortnitepy.ReceivedPartyInvitation):
        rmsg = await member.send(
            embed=discord.Embed(
                title="<:PartyInvite:719198827281645630> Party Invite from " + invitation.sender.display_name,
                type="rich",
                description="<:Accept:719047548219949136> Accept    <:Reject:719047548819472446> Reject"
            )
        )
        await rmsg.add_reaction(":Accept:719047548219949136")
        await rmsg.add_reaction(":Reject:719047548819472446")

        def check(reaction, user):
            if str(reaction.emoji) in ["<:Accept:719047548219949136>", "<:Reject:719047548819472446>"] and not user.bot:
                return True
            else:
                return False
        try:
            reaction, user = await dclient.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await invitation.decline()
            await rmsg.edit(
                delete_after=1,
                embed=discord.Embed(
                    title="<:PartyInvite:719198827281645630> Party Invite from " + invitation.sender.display_name,
                    type="rich",
                    color=0xf24949
                )
            )
        else:
            if str(reaction.emoji) == "<:Accept:719047548219949136>":
                await invitation.accept()
                await rmsg.edit(
                    delete_after=1,
                    embed=discord.Embed(
                        title="<:PartyInvite:719198827281645630> Party Invite from " + invitation.sender.display_name,
                        type="rich",
                        color=0x43b581
                    )
                )
            elif str(reaction.emoji) == "<:Reject:719047548819472446>":
                await invitation.decline()
                await rmsg.edit(
                    delete_after=1,
                    embed=discord.Embed(
                        title="<:PartyInvite:719198827281645630> Party Invite from " + invitation.sender.display_name,
                        type="rich",
                        color=0xf24949
                    )
                )
    loop.create_task(client.start())
    await client.wait_until_ready()
    for f in client.friends.values():
        await f.remove()
    for f in client.pending_friends.values():
        await f.decline()
    await client.party.me.edit_and_keep(
        partial(client.party.me.set_outfit, "CID_565_Athena_Commando_F_RockClimber"),
        partial(client.party.me.set_backpack, "BID_122_HalloweenTomato"),
        partial(client.party.me.set_banner, icon="otherbanner31", color="defaultcolor3", season_level=1337)
    )
    client.set_avatar(
        fortnitepy.Avatar(
            asset="CID_565_Athena_Commando_F_RockClimber",
            background_colors=[
                "7c0dc8",
                "b521cc",
                "ed34d0"
            ]
        )
    )
    await message.edit(
        embed=discord.Embed(
            title="<:Online:719038976677380138> " + client.user.display_name,
            type="rich",
            color=0xfc5fe2
        ).set_thumbnail(
            url=get_cosmetic_by_id(client.party.me.outfit)['icons']['icon']
        )
    )
    await dclient.get_channel(720787276329910363).edit(
        name=str(len(owner)) + "/256 Clients Running"
    )
    loop.call_later(time, loop.create_task, stop_bot(client, member.id, "This bot automatically shuts down after 90 minutes."))


async def parse_command(message: discord.Message):
    if type(message.channel) != discord.DMChannel or message.author.bot:
        return
    msg = message.content.split(" ")
    if message.author.id not in list(owner.keys()):
        return
    client = owner[message.author.id]
    if msg[0].lower() == "stop" or msg[0].lower() == "logout":
        await stop_bot(client, message.author.id)
    elif msg[0].lower() == "restart" or msg[0].lower() == "reboot":
        restartmsg = await message.channel.send(content="<a:Queue:720808283740569620> Restarting...")
        await client.restart()
        await client.wait_until_ready()
        await restartmsg.edit(content="<:Accept:719047548219949136> Restarted!", delete_after=10)
    elif msg[0].lower() == "ready":
        await client.party.me.set_ready(fortnitepy.ReadyState.READY)
    elif msg[0].lower() == "unready" or msg[0].lower() == "sitin":
        await client.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
    elif msg[0].lower() == "sitout":
        await client.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
    elif msg[0].lower() == "leave":
        await client.party.me.leave()
    elif msg[0].lower() == "promote":
        msg[1] = " ".join(msg[1:])
        p = await client.fetch_profile(msg[1])
        if p is None:
            return
        p = client.party.get_member(p.id)
        if p is None:
            return
        try:
            await p.promote()
            await message.channel.send("<:Accept:719047548219949136> Promoted " + p.display_name, delete_after=10)
        except fortnitepy.Forbidden:
            await message.channel.send("<:Reject:719047548819472446> I am Not Party Leader!", delete_after=10)
    elif msg[0].lower() == "kick":
        msg[1] = " ".join(msg[1:])
        p = await client.fetch_profile(msg[1])
        if p is None:
            return
        p = client.party.get_member(p.id)
        if p is None:
            return
        try:
            await p.kick()
            await message.channel.send("<:Accept:719047548219949136> Kicked " + p.display_name, delete_after=10)
        except fortnitepy.Forbidden:
            await message.channel.send("<:Reject:719047548819472446> I am Not Party Leader!", delete_after=10)
    elif msg[0].lower() == "join":
        msg[1] = " ".join(msg[1:])
        p = await client.fetch_profile(msg[1])
        if p is None:
            return
        p = client.get_friend(p.id)
        if p is None:
            return
        try:
            await p.join_party()
            await message.channel.send("<:Accept:719047548219949136> Joined " + p.display_name, delete_after=10)
        except fortnitepy.Forbidden:
            await message.channel.send("<:Reject:719047548819472446> Cannot Join " + p.display_name + " as their Party is Private", delete_after=10)
    elif msg[0].lower() == "set":
        if len(msg) >= 3:
            if msg[1].lower() == "outfit" or msg[1].lower() == "skin":
                msg[2] = " ".join(msg[2:])
                if msg[2].startswith("CID_"):
                    await client.party.me.edit_and_keep(partial(client.party.me.set_outfit, msg[2]))
                    await message.channel.send("<:Accept:719047548219949136> Set Outfit to " + msg[2], delete_after=10)
                    await refresh_message(client)
                else:
                    cosmetic = get_cosmetic(name=msg[2], backendType="AthenaCharacter")
                    if list(cosmetic.keys()) == ['error']:
                        await message.channel.send("<:Reject:719047548819472446> Cannot Find Outfit " + msg[2], delete_after=10)
                    else:
                        await client.party.me.edit_and_keep(partial(client.party.me.set_outfit, cosmetic['id']))
                        await message.channel.send("<:Accept:719047548219949136> Set Outfit to " + cosmetic['name'], delete_after=10)
                        await refresh_message(client)
            elif msg[1].lower() == "backbling" or msg[1].lower() == "backpack":
                msg[2] = " ".join(msg[2:])
                if msg[2].startswith("BID_"):
                    await client.party.me.edit_and_keep(partial(client.party.me.set_backpack, msg[2]))
                    await message.channel.send("<:Accept:719047548219949136> Set Back Bling to " + msg[2], delete_after=10)
                elif msg[2].lower() == "none":
                    await client.party.me.edit_and_keep(partial(client.party.me.clear_backpack))
                    await message.channel.send("<:Accept:719047548219949136> Set Back Bling to None", delete_after=10)
                else:
                    cosmetic = get_cosmetic(name=msg[2], backendType="AthenaBackpack")
                    if list(cosmetic.keys()) == ['error']:
                        await message.channel.send("<:Reject:719047548819472446> Cannot Find Back Bling " + msg[2], delete_after=10)
                    else:
                        await client.party.me.edit_and_keep(partial(client.party.me.set_backpack, cosmetic['id']))
                        await message.channel.send("<:Accept:719047548219949136> Set Back Bling to " + cosmetic['name'], delete_after=10)
            elif msg[1].lower() == "emote" or msg[1].lower() == "dance":
                msg[2] = " ".join(msg[2:])
                if msg[2].startswith("EID_"):
                    await client.party.me.set_emote(msg[2])
                    await message.channel.send("<:Accept:719047548219949136> Set Emote to " + msg[2], delete_after=10)
                elif msg[2].lower() == "none":
                    await client.party.me.clear_emote()
                    await message.channel.send("<:Accept:719047548219949136> Set Emote to None", delete_after=10)
                else:
                    cosmetic = get_cosmetic(name=msg[2], backendType="AthenaDance")
                    if list(cosmetic.keys()) == ['error']:
                        await message.channel.send("<:Reject:719047548819472446> Cannot Find Emote " + msg[2], delete_after=10)
                    else:
                        await client.party.me.clear_emote()
                        await client.party.me.set_emote(cosmetic['id'])
                        await message.channel.send("<:Accept:719047548219949136> Set Emote to " + cosmetic['name'], delete_after=10)
            elif msg[1].lower() == "harvesting_tool" or msg[1].lower() == "harvestingtool" or msg[1].lower() == "pickaxe":
                msg[2] = " ".join(msg[2:])
                if msg[2].startswith("Pickaxe_ID"):
                    await client.party.me.edit_and_keep(partial(client.party.me.set_pickaxe, msg[2]))
                    await message.channel.send("<:Accept:719047548219949136> Set Harvesting Tool to " + msg[2], delete_after=10)
                else:
                    cosmetic = get_cosmetic(name=msg[2], backendType="AthenaPickaxe")
                    if list(cosmetic.keys()) == ['error']:
                        await message.channel.send("<:Reject:719047548819472446> Cannot Find Harvesting Tool " + msg[2], delete_after=10)
                    else:
                        await client.party.me.edit_and_keep(partial(client.party.me.set_pickaxe, cosmetic['id']))
                        await message.channel.send("<:Accept:719047548219949136> Set Harvesting Tool to " + cosmetic['name'], delete_after=10)
            elif msg[1].lower() == "banner" and len(msg) == 4:
                if msg[2].lower() == "design" or msg[2].lower() == "icon":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_banner, icon=msg[3], color=client.party.me.banner[1], season_level=client.party.me.banner[2]))
                    await message.channel.send("<:Accept:719047548219949136> Set Banner Design to " + msg[3], delete_after=10)
                elif msg[2].lower() == "color" or msg[2].lower() == "colour":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_banner, icon=client.party.me.banner[0], color=msg[3], season_level=client.party.me.banner[2]))
                    await message.channel.send("<:Accept:719047548219949136> Set Banner Color to " + msg[3], delete_after=10)
                elif msg[2].lower() == "season_level" or msg[2].lower() == "level":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_banner, icon=client.party.me.banner[0], color=client.party.me.banner[1], season_level=msg[3]))
                    await message.channel.send("<:Accept:719047548219949136> Set Season Level to " + msg[3], delete_after=10)
            elif msg[1].lower() == "battlepass" or msg[1].lower() == "bp" and len(msg) == 4:
                if msg[2].lower() == "has_purchased":
                    if msg[3] == "true":
                        await client.party.me.edit_and_keep(partial(client.party.me.set_battlepass_info, has_purchased=True))
                        await message.channel.send("<:Accept:719047548219949136> Set Battle Pass Purchase Status to True", delete_after=10)
                    elif msg[3] == "false":
                        await client.party.me.edit_and_keep(partial(client.party.me.set_battlepass_info, has_purchased=False))
                        await message.channel.send("<:Accept:719047548219949136> Set Battle Pass Purchase Status to False", delete_after=10)
                elif msg[2].lower() == "level":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_battlepass_info, level=msg[3]))
                    await message.channel.send("<:Accept:719047548219949136> Set Battle Pass Level to " + msg[3], delete_after=10)
                elif msg[2].lower() == "self_boost_xp":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_battlepass_info, self_boost_xp=msg[3]))
                    await message.channel.send("<:Accept:719047548219949136> Set Battle Pass Self Boost to " + msg[3], delete_after=10)
                elif msg[2].lower() == "friend_boost_xp":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_battlepass_info, friend_boost_xp=msg[3]))
                    await message.channel.send("<:Accept:719047548219949136> Set Battle Pass Friend Boost to " + msg[3], delete_after=10)
            elif msg[1].lower() == "status" or msg[1].lower() == "presence":
                msg[2] = " ".join(msg[2:])
                await client.set_status(msg[2])
                await message.channel.send("<:Accept:719047548219949136> Set Status to " + msg[2], delete_after=10)
            elif msg[1].lower() == "code":
                msg[2] = " ".join(msg[2:])
                try:
                    await client.party.set_custom_key(msg[2])
                    await message.channel.send("<:Accept:719047548219949136> Set Matchmaking Code to " + msg[2], delete_after=10)
                except fortnitepy.Forbidden:
                    await message.channel.send("<:Reject:719047548819472446> I am Not Party Leader!", delete_after=10)
            elif msg[1].lower() == "playlist" or msg[1].lower() == "gamemode" or msg[1].lower() == "mode":
                msg[2] = " ".join(msg[2:])
                if msg[2].startswith("Playlist_"):
                    await client.party.set_playlist(msg[2])
                    await message.channel.send("<:Accept:719047548219949136> Set Playlist to " + msg[2], delete_after=10)
                else:
                    playlist = get_playlist(name=msg[2])
                    if list(playlist.keys()) == ['error']:
                        await message.channel.send("<:Reject:719047548819472446> Cannot Find Playlist " + msg[2], delete_after=10)
                    else:
                        try:
                            await client.party.me.set_playlist(playlist['id'])
                            await message.channel.send("<:Accept:719047548219949136> Set Playlist to " + playlist['name'], delete_after=10)
                        except fortnitepy.Forbidden:
                            await message.channel.send("<:Reject:719047548819472446> I am Not Party Leader!", delete_after=10)
            elif msg[1].lower() == "variants" or msg[1].lower() == "variant":
                if msg[2].lower() == "outfit" or msg[2].lower() == "skin":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_outfit,
                        asset=client.party.me.outfit,
                        variants=client.party.me.create_variants(
                            item="AthenaCharacter",
                            **{msg[3]: msg[4]}
                        )
                    ))
                    await message.channel.send("<:Accept:719047548219949136> Set Variants to " + msg[3] + " = " + msg[4], delete_after=10)
                elif msg[2].lower() == "backbling" or msg[2].lower() == "backpack":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_backpack,
                        asset=client.party.me.backpack,
                        variants=client.party.me.create_variants(
                            item="AthenaBackpack",
                            **{msg[3]: msg[4]}
                        )
                    ))
                    await message.channel.send("<:Accept:719047548219949136> Set Variants to " + msg[3] + " = " + msg[4], delete_after=10)
                elif msg[2].lower() == "harvesting_tool" or msg[2].lower() == "harvestingtool" or msg[2].lower() == "pickaxe":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_pickaxe,
                        asset=client.party.me.pickaxe,
                        variants=client.party.me.create_variants(
                            item="AthenaPickaxe",
                            **{msg[3]: msg[4]}
                        )
                    ))
                    await message.channel.send("<:Accept:719047548219949136> Set Variants to " + msg[3] + " = " + msg[4], delete_after=10)
            elif msg[1].lower() == "enlightenment" or msg[1].lower() == "enlighten":
                if msg[2].lower() == "outfit" or msg[2].lower() == "skin":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_outfit,
                        asset=client.party.me.outfit,
                        variants=client.party.me.outfit_variants,
                        enlightenment=(msg[3], msg[4])
                    ))
                    await message.channel.send("<:Accept:719047548219949136> Set Enlightenment to Season " + msg[3] + " Level " + msg[4], delete_after=10)
                elif msg[2].lower() == "backbling" or msg[2].lower() == "backpack":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_backpack,
                        asset=client.party.me.backpack,
                        variants=client.party.me.backpack_variants,
                        enlightenment=(msg[3], msg[4])
                    ))
                    await message.channel.send("<:Accept:719047548219949136> Set Enlightenment to Season " + msg[3] + " Level " + msg[4], delete_after=10)
                elif msg[2].lower() == "harvesting_tool" or msg[2].lower() == "harvestingtool" or msg[2].lower() == "pickaxe":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_pickaxe,
                        asset=client.party.me.pickaxe,
                        variants=client.party.me.pickaxe_variants,
                        enlightenment=(msg[3], msg[4])
                    ))
                    await message.channel.send("<:Accept:719047548219949136> Set Enlightenment to Season" + msg[3] + " Level " + msg[4], delete_after=10)
    elif msg[0].lower() == "friend":
        msg[2] = " ".join(msg[2:])
        p = await client.fetch_profile(msg[2])
        if p is None:
            return
        if msg[1].lower() == "add":
            await client.add_friend(p.id)
            await message.channel.send("<:Accept:719047548219949136> Sent Friend Request to " + p.display_name, delete_after=10)
        elif msg[1].lower() == "remove":
            p = client.get_friend(p.id)
            if p is None:
                await message.channel.send("<:Reject:719047548819472446> Not Friends with " + p.display_name, delete_after=10)
                return
            await p.remove()
            await message.channel.send("<:Accept:719047548219949136> Removed " + p.display_name, delete_after=10)
    elif msg[0].lower() == "send":
        msg[1] = " ".join(msg[1:])
        await client.party.send(msg[1])
        await message.channel.send("<:Accept:719047548219949136> Sent Party Message", delete_after=10)
    elif msg[0].lower() == "clone" or msg[0].lower() == "copy":
        msg[1] = " ".join(msg[1:])
        p = await client.fetch_profile(msg[1])
        if p is None:
            return
        p = client.party.get_member(p.id)
        if p is None:
            return
        await client.party.me.edit_and_keep(
            partial(
                client.party.me.set_outfit,
                asset=p.outfit,
                variants=p.outfit_variants
            ),
            partial(
                client.party.me.set_backpack,
                asset=p.backpack,
                variants=p.backpack_variants
            ),
            partial(
                client.party.me.set_pickaxe,
                asset=p.pickaxe,
                variants=p.pickaxe_variants
            ),
            partial(
                client.party.me.set_banner,
                icon=p.banner[0],
                color=p.banner[1],
                season_level=p.banner[2]
            ),
            partial(
                client.party.me.set_battlepass_info,
                has_purchased=p.battlepass_info[0],
                level=p.battlepass_info[1],
                self_boost_xp=p.battlepass_info[2],
                friend_boost_xp=p.battlepass_info[3]
            )
        )
        await message.channel.send("<:Accept:719047548219949136> Cloned " + p.display_name, delete_after=10)
    elif msg[0].lower() == "variants":
        if msg[1].lower() == "outfit" or msg[1].lower() == "skin":
            cosm = get_cosmetic_by_id(client.party.me.outfit)
        elif msg[1].lower() == "backbling" or msg[1].lower() == "backpack":
            cosm = get_cosmetic_by_id(client.party.me.backpack)
        elif msg[1].lower() == "harvesting_tool" or msg[1].lower() == "harvestingtool" or msg[1].lower() == "pickaxe":
            cosm = get_cosmetic_by_id(client.party.me.pickaxe)
        elif msg[1].startswith(("CID", "BID", "Pickaxe_ID")):
            cosm = get_cosmetic_by_id(msg[1])
        if cosm is None:
            await message.channel.send("<:Reject:719047548819472446> Cannot Find Cosmetic " + msg[1])
            return
        elif "variants" not in list(cosm.keys()):
            await message.channel.send("<:Reject:719047548819472446> " + cosm['name'] + " has no variants")
            return
        await message.channel.send(embed=discord.Embed(
            title="Variants for " + cosm['name'],
            type="rich"
        ).set_thumbnail(
            url=cosm['icons']['icon']
        ).add_field(
            name="Description",
            value=cosm['description'] + "\n" + cosm['setText'],
            inline=True
        ).add_field(
            name="ID",
            value=cosm['id'],
            inline=True
        ), delete_after=300)
        for ch in cosm['variants']:
            embed = discord.Embed(
                title=ch['channel'],
                type="rich"
            )
            for st in ch['options']:
                embed.add_field(
                    name=st['tag'],
                    value=st['name'],
                    inline=True
                )
            await message.channel.send(embed=embed, delete_after=300)


###################
#     Discord     #
###################

loop.create_task(dclient.start(os.getenv("TOKEN")))


@dclient.event
async def on_message(message: discord.Message):
    if message.channel.id == 718979003968520283:
        if "start" in message.content.lower():
            await message.delete()
            await start_bot(message.author, 5400)
        else:
            await message.delete()
    elif type(message.channel) == discord.DMChannel:
        await parse_command(message)
for a in accounts:
    auth = fortnitepy.AdvancedAuth(
        email=accounts[a]['Email'],
        password=accounts[a]['Password'],
        account_id=accounts[a]['Account ID'],
        device_id=accounts[a]['Device ID'],
        secret=accounts[a]['Secret']
    )
    client = fortnitepy.Client(
        auth=auth,
        platform=fortnitepy.Platform.MAC
    )
    clients[a] = client
    available[a] = client
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.create_task(dclient.close())
    for ownerid in owner:
        loop.create_task(stop_bot(owner[ownerid]), ownerid, "All bots have been stopped by the server.")
    for task in asyncio.Task.all_tasks():
        task.cancel()
