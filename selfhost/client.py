# Self-Host Client for Aerial #
import fortnitepy
import sys
import os
import yaml
import asyncio
import sqlite3
import requests
import time
from termcolor import cprint
from functools import partial

loop = asyncio.get_event_loop()

# Updater #
version = 2  # INCREMENT THIS BEFORE RELEASE
latest = requests.get(
    "https://api.github.com/repos/andre4ik3/Aerial/releases/latest"
).json().get("id", version)
if latest > version:
    cprint("[Client] New Version Available! Version " + latest, "green")
    cprint(
        "Download Here: https://github.com/andre4ik3/Aerial/releases/latest"
    )
    time.sleep(10)


# API Functions #
def get_cosmetic(name: str, backendType: str = ""):
    return requests.get(
        "https://benbotfn.tk/api/v1/cosmetics/br/search",
        params={
            "lang": "en",
            "searchLang": "en",
            "matchMethod": "contains",
            "backendType": backendType,
            "name": name
        }
    ).json()


def get_cosmetic_by_id(id: str):
    r = requests.get(
        "https://benbotfn.tk/api/v1/cosmetics/br/" + id
    )
    return r.json() if r.status_code != 404 else None


def get_playlist(name: str):
    return requests.get(
        "http://scuffedapi.xyz/api/playlists/search",
        params={
            "displayName": name
        }
    ).json()


def convert(ls: list):
    return {ls[i]: ls[i + 1] for i in range(0, len(ls), 2)}


# Config #
if os.path.isfile("config.yml"):
    config = yaml.safe_load(open("config.yml", "r"))
    cprint("[Client] Loaded Config", "green")
else:
    cprint("[Client] Cannot Load Configuration File!", "red")
    sys.exit()

# Database #
if os.path.isfile("db.sqlite"):
    exists = True
else:
    exists = False
db = sqlite3.connect("db.sqlite")
cursor = db.cursor()
if not exists:
    cursor.execute(
        """CREATE TABLE "permissions" (
            "account" bigint, "level" int, PRIMARY KEY (account)
        );"""
    )
    db.commit()
cprint("[Client] Loaded Database", "green")


# Device Auth Details #
def store_details(details: dict):
    global config
    for d in details:
        config['Authorization'][d] = details[d]
    yaml.safe_dump(config, open("config.yml", "w"))


# Client #
client = fortnitepy.Client(
    auth=fortnitepy.AdvancedAuth(
        email=config['Email'],
        password=config['Password'],
        **config['Authorization']
    ),
    status=config['Status'],
    platform=fortnitepy.Platform(config['Platform']),
    default_party_member_config=fortnitepy.DefaultPartyMemberConfig(
        yield_leadership=config['Yield Leadership'],
        meta=[
            partial(
                fortnitepy.ClientPartyMember.set_outfit,
                config['Cosmetics']['Outfit']
            ),
            partial(
                fortnitepy.ClientPartyMember.set_backpack,
                config['Cosmetics']['Back Bling']
            ),
            partial(
                fortnitepy.ClientPartyMember.set_pickaxe,
                config['Cosmetics']['Harvesting Tool']
            ),
            partial(
                fortnitepy.ClientPartyMember.set_banner,
                config['Cosmetics']['Banner']['Design'],
                config['Cosmetics']['Banner']['Color'],
                config['Cosmetics']['Banner']['Season Level']
            ),
            partial(
                fortnitepy.ClientPartyMember.set_battlepass_info,
                config['Cosmetics']['Battle Pass']['Has Purchased'],
                config['Cosmetics']['Battle Pass']['Level'],
                config['Cosmetics']['Battle Pass']['XP Boost Self'],
                config['Cosmetics']['Battle Pass']['XP Boost Others']
            )
        ]
    )
)


@client.event
async def event_friend_request(request: fortnitepy.PendingFriend):
    if config['Accept Friend Requests'] and request.direction == "INBOUND":
        await request.accept()
    else:
        await request.decline()


@client.event
async def event_party_invite(invitation: fortnitepy.ReceivedPartyInvitation):
    if config['Accept Party Invites'] or client.party.member_count == 1:
        await invitation.accept()


@client.event
async def event_device_auth_generate(details: dict, email: str):
    store_details(details)
    cprint("[Client] Stored Device Auth Details", "green")


@client.event
async def event_ready():
    cprint("[Client] Ready as " + client.user.display_name, "green")
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
    cosmetics = config['Cosmetics']
    if cosmetics['Outfit'] != "":
        await client.party.me.edit_and_keep(
            partial(
                client.party.me.set_outfit,
                cosmetics['Outfit']
            )
        )
    if cosmetics['Back Bling'] != "":
        await client.party.me.edit_and_keep(
            partial(
                client.party.me.set_backpack,
                cosmetics['Back Bling']
            )
        )
    if cosmetics['Harvesting Tool'] != "":
        await client.party.me.edit_and_keep(
            partial(
                client.party.me.set_pickaxe,
                cosmetics['Harvesting Tool']
            )
        )
    if cosmetics['Banner'] is not None:
        await client.party.me.edit_and_keep(
            partial(
                client.party.me.set_banner,
                icon=cosmetics['Banner']['Design'],
                color=cosmetics['Banner']['Color'],
                season_level=cosmetics['Banner']['Season Level']
            )
        )
    if cosmetics['Battle Pass'] is not None:
        await client.party.me.edit_and_keep(
            partial(
                client.party.me.set_battlepass_info,
                has_purchased=cosmetics['Battle Pass']['Has Purchased'],
                level=cosmetics['Battle Pass']['Level'],
                self_boost_xp=cosmetics['Battle Pass']['XP Boost Self'],
                friend_boost_xp=cosmetics['Battle Pass']['XP Boost Others']
            )
        )
    if config['Accept Friend Requests']:
        for f in list(client.pending_friends.values()):
            if f.direction == "INBOUND":
                await f.accept()


@client.event
async def event_friend_message(message: fortnitepy.FriendMessage):
    cprint(f"[{message.author.display_name}] {message.content}", "magenta")
    msg = message.content.split(" ")
    if msg[0].lower() == "ready":
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
            await message.reply("Promoted " + p.display_name)
            cprint("[Client] Promoted " + p.display_name, "green")
        except fortnitepy.Forbidden:
            await message.reply("I am Not Party Leader!")
            cprint("[Client] I am Not Party Leader!", "red")
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
            await message.reply("Kicked " + p.display_name)
            cprint("[Client] Kicked " + p.display_name, "green")
        except fortnitepy.Forbidden:
            await message.reply("I am Not Party Leader!")
            cprint("[Client] I am Not Party Leader!", "red")
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
            await message.reply("Joined " + p.display_name)
            cprint("[Client] Joined " + p.display_name, "green")
        except fortnitepy.Forbidden:
            await message.reply("Cannot Join " + p.display_name + " as their Party is Private")
            cprint("[Client] Cannot Join " + p.display_name + " as their Party is Private", "red")
    elif msg[0].lower() == "set":
        if len(msg) >= 3:
            if msg[1].lower() == "outfit" or msg[1].lower() == "skin":
                msg[2] = " ".join(msg[2:])
                if msg[2].startswith("CID_"):
                    await client.party.me.edit_and_keep(partial(client.party.me.set_outfit, msg[2]))
                    await message.reply("Set Outfit to " + msg[2])
                    cprint("[Client] Set Outfit to  " + msg[2], "green")
                else:
                    cosmetic = get_cosmetic(name=msg[2], backendType="AthenaCharacter")
                    if list(cosmetic.keys()) == ['error']:
                        await message.reply("Cannot Find Outfit " + msg[2])
                        cprint("[Client] Cannot Find Outfit " + msg[2], "red")
                    else:
                        await client.party.me.edit_and_keep(partial(client.party.me.set_outfit, cosmetic['id']))
                        await message.reply("Set Outfit to " + cosmetic['name'])
                        cprint("[Client] Set Outfit to " + cosmetic['name'], "green")
            elif msg[1].lower() == "backbling" or msg[1].lower() == "backpack":
                msg[2] = " ".join(msg[2:])
                if msg[2].startswith("BID_"):
                    await client.party.me.edit_and_keep(partial(client.party.me.set_backpack, msg[2]))
                    await message.reply("Set Back Bling to " + msg[2])
                    cprint("[Client] Set Back Bling to " + msg[2], "green")
                elif msg[2].lower() == "none":
                    await client.party.me.edit_and_keep(partial(client.party.me.clear_backpack))
                    await message.reply("Set Back Bling to None")
                    cprint("[Client] Set Back Bling to None", "green")
                else:
                    cosmetic = get_cosmetic(name=msg[2], backendType="AthenaBackpack")
                    if list(cosmetic.keys()) == ['error']:
                        await message.reply("Cannot Find Back Bling " + msg[2])
                        cprint("[Client] Cannot Find Back Bling " + msg[2], "red")
                    else:
                        await client.party.me.edit_and_keep(partial(client.party.me.set_backpack, cosmetic['id']))
                        await message.reply("Set Back Bling to " + cosmetic['name'])
                        cprint("[Client] Set Back Bling to " + cosmetic['name'], "green")
            elif msg[1].lower() == "emote" or msg[1].lower() == "dance":
                msg[2] = " ".join(msg[2:])
                if msg[2].startswith("EID_"):
                    await client.party.me.set_emote(msg[2])
                    await message.reply("Set Emote to " + msg[2])
                    cprint("[Client] Set Emote to " + msg[2], "green")
                elif msg[2].lower() == "none":
                    await client.party.me.clear_emote()
                    await message.reply("Set Emote to None")
                    cprint("[Client] Set Emote to None", "green")
                else:
                    cosmetic = get_cosmetic(name=msg[2], backendType="AthenaDance")
                    if list(cosmetic.keys()) == ['error']:
                        await message.reply("Cannot Find Emote " + msg[2])
                        cprint("[Client] Cannot Find Emote " + msg[2], "red")
                    else:
                        await client.party.me.clear_emote()
                        await client.party.me.set_emote(cosmetic['id'])
                        await message.reply("Set Emote to " + cosmetic['name'])
                        cprint("[Client] Set Emote to " + cosmetic['name'], "green")
            elif msg[1].lower() == "harvesting_tool" or msg[1].lower() == "harvestingtool" or msg[1].lower() == "pickaxe":
                msg[2] = " ".join(msg[2:])
                if msg[2].startswith("Pickaxe_ID"):
                    await client.party.me.edit_and_keep(partial(client.party.me.set_pickaxe, msg[2]))
                    await message.reply("Set Harvesting Tool to " + msg[2])
                    cprint("[Client] Set Harvesting Tool to " + msg[2], "green")
                else:
                    cosmetic = get_cosmetic(name=msg[2], backendType="AthenaPickaxe")
                    if list(cosmetic.keys()) == ['error']:
                        await message.reply("Cannot Find Harvesting Tool " + msg[2])
                        cprint("[Client] Cannot Find Harvesting Tool " + msg[2], "red")
                    else:
                        await client.party.me.edit_and_keep(partial(client.party.me.set_pickaxe, cosmetic['id']))
                        await message.reply("Set Harvesting Tool to " + cosmetic['name'])
                        cprint("[Client] Set Harvesting Tool to " + cosmetic['name'], "green")
            elif msg[1].lower() == "banner" and len(msg) == 4:
                if msg[2].lower() == "design" or msg[2].lower() == "icon":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_banner, icon=msg[3], color=client.party.me.banner[1], season_level=client.party.me.banner[2]))
                    await message.reply("Set Banner Design to " + msg[3])
                    cprint("[Client] Set Banner Design to " + msg[3], "green")
                elif msg[2].lower() == "color" or msg[2].lower() == "colour":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_banner, icon=client.party.me.banner[0], color=msg[3], season_level=client.party.me.banner[2]))
                    await message.reply("Set Banner Color to " + msg[3])
                    cprint("[Client] Set Banner Color to " + msg[3], "green")
                elif msg[2].lower() == "season_level" or msg[2].lower() == "level":
                    await client.party.me.edit_and_keep(partial(client.party.me.set_banner, icon=client.party.me.banner[0], color=client.party.me.banner[1], season_level=msg[3]))
                    await message.reply("Set Season Level to " + msg[3])
                    cprint("[Client] Set Season Level to " + msg[3], "green")
                elif msg[1].lower() == "battlepass" or msg[1].lower() == "bp" and len(msg) == 4:
                    if msg[2].lower() == "has_purchased":
                        if msg[3] == "true":
                            await client.party.me.edit_and_keep(partial(client.party.me.set_battlepass_info, has_purchased=True))
                            await message.reply("Set Battle Pass Purchase Status to True")
                            cprint("[Client] Set Battle Pass Purchase Status to True", "green")
                        elif msg[3] == "false":
                            await client.party.me.edit_and_keep(partial(client.party.me.set_battlepass_info, has_purchased=False))
                            await message.reply("Set Battle Pass Purchase Status to False")
                            cprint("[Client] Set Battle Pass Purchase Status to False", "green")
                    elif msg[2].lower() == "level":
                        await client.party.me.edit_and_keep(partial(client.party.me.set_battlepass_info, level=msg[3]))
                        await message.reply("Set Battle Pass Level to " + msg[3])
                        cprint("[Client] Set Battle Pass Level to " + msg[3], "green")
                    elif msg[2].lower() == "self_boost_xp":
                        await client.party.me.edit_and_keep(partial(client.party.me.set_battlepass_info, self_boost_xp=msg[3]))
                        await message.reply("Set Battle Pass Self Boost to " + msg[3])
                        cprint("[Client] Set Battle Pass Self Boost to " + msg[3], "green")
                    elif msg[2].lower() == "friend_boost_xp":
                        await client.party.me.edit_and_keep(partial(client.party.me.set_battlepass_info, friend_boost_xp=msg[3]))
                        await message.reply("Set Battle Pass Friend Boost to " + msg[3])
                        cprint("[Client] Set Battle Pass Friend Boost to " + msg[3], "green")
            elif msg[1].lower() == "status" or msg[1].lower() == "presence":
                msg[2] = " ".join(msg[2:])
                await client.set_status(msg[2])
                await message.reply("Set Status to " + msg[2])
                cprint("[Client] Set Status to " + msg[2], "green")
            elif msg[1].lower() == "code":
                msg[2] = " ".join(msg[2:])
                try:
                    await client.party.set_custom_key(msg[2])
                    await message.reply("Set Matchmaking Code to " + msg[2])
                    cprint("[Client] Set Matchmaking Code to " + msg[2], "green")
                except fortnitepy.Forbidden:
                    await message.reply("I am Not Party Leader!")
                    cprint("[Client] I am Not Party Leader!", "red")
            elif msg[1].lower() == "playlist" or msg[1].lower() == "gamemode" or msg[1].lower() == "mode":
                msg[2] = " ".join(msg[2:])
                if msg[2].startswith("Playlist_"):
                    await client.party.set_playlist(msg[2])
                    await message.reply("Set Playlist to " + msg[2])
                    cprint("[Client] Set Playlist to " + msg[2], "green")
                else:
                    playlist = get_playlist(name=msg[2])
                    if list(playlist.keys()) == ['error']:
                        await message.reply("Cannot Find Playlist " + msg[2])
                        cprint("[Client] Cannot Find Playlist " + msg[2], "red")
                    else:
                        try:
                            await client.party.me.set_playlist(playlist['id'])
                            await message.reply("Set Playlist to " + playlist['name'])
                            cprint("[Client] Set Playlist to " + playlist['name'], "green")
                        except fortnitepy.Forbidden:
                            await message.reply("I am Not Party Leader!")
                            cprint("[Client] I am Not Party Leader!", "red")
            elif msg[1].lower() == "variants" or msg[1].lower() == "variant":
                variants = convert(msg[3:])
                if msg[2].lower() == "outfit" or msg[2].lower() == "skin":
                    await client.party.me.edit_and_keep(
                        partial(
                            client.party.me.set_outfit,
                            asset=client.party.me.outfit,
                            variants=client.party.me.create_variants(
                                item="AthenaCharacter",
                                **variants
                            )
                        )
                    )
                    await message.reply("Set Variants to " + msg[3] + " = " + msg[4])
                    cprint("[Client] Set Variants to " + msg[3] + " = " + msg[4], "green")
                elif msg[2].lower() == "backbling" or msg[2].lower() == "backpack":
                    await client.party.me.edit_and_keep(
                        partial(
                            client.party.me.set_backpack,
                            asset=client.party.me.backpack,
                            variants=client.party.me.create_variants(
                                item="AthenaBackpack",
                                **variants
                            )
                        )
                    )
                    await message.reply("Set Variants to " + msg[3] + " = " + msg[4])
                    cprint("[Client] Set Variants to " + msg[3] + " = " + msg[4], "green")
                elif msg[2].lower() == "harvesting_tool" or msg[2].lower() == "harvestingtool" or msg[2].lower() == "pickaxe":
                    await client.party.me.edit_and_keep(
                        partial(
                            client.party.me.set_pickaxe,
                            asset=client.party.me.pickaxe,
                            variants=client.party.me.create_variants(
                                item="AthenaPickaxe",
                                **variants
                            )
                        )
                    )
                    await message.reply("Set Variants to " + msg[3] + " = " + msg[4])
                    cprint("[Client] Set Variants to " + msg[3] + " = " + msg[4], "green")
            elif msg[1].lower() == "enlightenment" or msg[1].lower() == "enlighten":
                if msg[2].lower() == "outfit" or msg[2].lower() == "skin":
                    await client.party.me.edit_and_keep(
                        partial(
                            client.party.me.set_outfit,
                            asset=client.party.me.outfit,
                            variants=client.party.me.outfit_variants,
                            enlightenment=(msg[3], msg[4])
                        )
                    )
                    await message.reply("Set Enlightenment to Season " + msg[3] + " Level " + msg[4])
                    cprint("[Client] Set Enlightenment to Season " + msg[3] + " Level " + msg[4], "green")
                elif msg[2].lower() == "backbling" or msg[2].lower() == "backpack":
                    await client.party.me.edit_and_keep(
                        partial(
                            client.party.me.set_backpack,
                            asset=client.party.me.backpack,
                            variants=client.party.me.backpack_variants,
                            enlightenment=(msg[3], msg[4])
                        )
                    )
                    await message.reply("Set Enlightenment to Season " + msg[3] + " Level " + msg[4])
                    cprint("[Client] Set Enlightenment to Season " + msg[3] + " Level " + msg[4], "green")
                elif msg[2].lower() == "harvesting_tool" or msg[2].lower() == "harvestingtool" or msg[2].lower() == "pickaxe":
                    await client.party.me.edit_and_keep(
                        partial(
                            client.party.me.set_pickaxe,
                            asset=client.party.me.pickaxe,
                            variants=client.party.me.pickaxe_variants,
                            enlightenment=(msg[3], msg[4])
                        )
                    )
                    await message.reply("Set Enlightenment to Season" + msg[3] + " Level " + msg[4])
                    cprint("[Client] Set Enlightenment to Season " + msg[3] + " Level " + msg[4], "green")
    elif msg[0].lower() == "friend":
        msg[2] = " ".join(msg[2:])
        p = await client.fetch_profile(msg[2])
        if p is None:
            return
        if msg[1].lower() == "add":
            await client.add_friend(p.id)
            await message.reply("Sent Friend Request to " + p.display_name)
            cprint("[Client] Sent Friend Request to " + p.display_name, "green")
        elif msg[1].lower() == "remove":
            p = client.get_friend(p.id)
            if p is None:
                await message.reply("Not Friends with " + p.display_name)
                cprint("[Client] Not Friends with " + p.display_name, "red")
                return
            await p.remove()
            await message.reply("Removed " + p.display_name)
            cprint("[Client] Removed " + p.display_name, "red")
    elif msg[0].lower() == "send":
        msg[1] = " ".join(msg[1:])
        await client.party.send(msg[1])
        await message.reply("Sent Party Message")
        cprint("[Client] Sent Party Message", "green")
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
        await message.reply("Cloned " + p.display_name)
        cprint("[Client] Cloned " + p.display_name, "green")


@client.event
async def event_party_message(message: fortnitepy.PartyMessage):
    cprint(f"[{message.author.display_name}] {message.content}", "yellow")

loop.create_task(client.start())

try:
    loop.run_until_complete(future=asyncio.Future(loop=loop))
except KeyboardInterrupt:
    cprint("\n[Client] Shutting Down...", "red", attrs=["bold"])
    loop.create_task(client.close())
