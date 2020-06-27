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
version = 1  # INCREMENT THIS BEFORE RELEASE
latest = requests.get(
    "https://api.github.com/repos/andre4ik3/Aerial/releases/latest"
).json().get("id", version)
if latest > version:
    cprint("New Version Available! Version " + latest, "green")
    cprint(
        "Download Here: https://github.com/andre4ik3/Aerial/releases/latest"
    )
    time.sleep(10)

# Config #
if os.path.isfile("config.yml"):
    config = yaml.safe_load(open("config.yml", "r"))
    cprint("Loaded Config.", "green")
else:
    cprint("Cannot Load Configuration File!", "red")
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
cprint("Loaded Database.", "green")


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
async def event_device_auth_generate(details: dict, email: str):
    store_details(details)
    cprint("Stored Device Auth Details.", "green")


@client.event
async def event_ready():
    cprint("Client Ready as " + client.user.display_name, "green")
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


@client.event
async def event_friend_message(message: fortnitepy.FriendMessage):
    cprint(f"[{message.author.display_name}] {message.content}", "magenta")


@client.event
async def event_party_message(message: fortnitepy.PartyMessage):
    cprint(f"[{message.author.display_name}] {message.content}", "yellow")

loop.create_task(client.start())

try:
    loop.run_until_complete(future=asyncio.Future(loop=loop))
except KeyboardInterrupt:
    cprint("\nShutting Down!", "red", attrs=["bold"])
    loop.create_task(client.close())
