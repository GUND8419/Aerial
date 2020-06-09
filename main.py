import os, discord, fortnitepy, json, yaml, dotenv, asyncio, random, requests
from functools import partial

# Load YAML Config #
def load_config():
	if os.path.isfile("config.yml"):
		with open("config.yml", "r") as config:
			return yaml.safe_load(config)
	else:
		sys.exit("Cannot Load config.yml!")

# Auth Detail Functions #
def get_device_auth_details() -> dict:
	if os.path.isfile("device_auths.yml"):
		with open("device_auths.yml", "r") as fp:
			return yaml.safe_load(fp)
		return {}

def store_device_auth_details(email: str, details: dict):
	existing = get_device_auth_details()
	existing[email] = details
	with open("device_auths.yml", "w") as fp:
		yaml.dump(existing, fp, sort_keys=False, indent=2)

# API Functions #
def get_cosmetic(name: str, backendType: str):
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
config = load_config()
dotenv.load_dotenv()
password = os.getenv("PASSWORD")
clients = {}
reverse = {}
available = {}
owner = {}
reverseowner = {}
messages = {}

loop = asyncio.get_event_loop()

# Discord Client #
dclient = discord.Client(
	activity=discord.Streaming(
		platform="Twitch",
		name="Fortnite Bots",
		details="Fortnite Bots",
		game="Fortnite Bots",
		url="https://twitch.tv/andre4ik3",
		assets={
			"large_image": "purple"
		},
		twitch_name="purple"
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
			url=get_cosmetic(client.party.me.outfit, "AthenaCharacter")['icons']['icon']
		)
	)

async def stop_bot(client: fortnitepy.Client):
	if client.is_ready():
		for f in client.friends.values():
			await f.remove()
		for f in client.pending_friends.values():
			await f.decline()
		await client.close()
	available[reverse[client]] = client
	reverseowner.pop(owner[client])
	owner.pop(client)
	await messages[client].edit(
		embed=discord.Embed(
			title="<:Offline:719321200098017330> Bot Offline",
			type="rich",
			color=0x747f8d
		)
	)

async def start_bot(member: discord.Member, time: int = 5400):
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
	if member.id in owner.values():
		await message.edit(
			embed=discord.Embed(
				title=":x: Bot Already Running!",
				color=0xe46b6b
			),
			delete_after=3
		)
		return
	else:
		client = random.choice(available)
		available.pop(reverse[client])
		owner[client] = member.id
		reverseowner[member.id] = client
		messages[client] = message
	
	@client.event
	async def event_friend_request(friend: fortnitepy.PendingFriend):
		rmsg = await member.send(
			embed=discord.Embed(
				title="<:FriendRequest:719042256849338429> Friend Request from " + friend.display_name,
				type="rich",
				description="<:Accept:719047548219949136> Accept	<:Reject:719047548819472446> Reject"
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
				description="<:Accept:719047548219949136> Accept	<:Reject:719047548819472446> Reject"
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
	await client.party.me.edit_and_keep(
		partial(client.party.me.set_outfit, "CID_565_Athena_Commando_F_RockClimber"),
		partial(client.party.me.set_backpack, "BID_122_HalloweenTomato"),
		partial(client.party.me.set_banner, icon="otherbanner31", color="defaultcolor3", season_level=1337)
	)
	await message.edit(
		embed=discord.Embed(
			title="<:Online:719038976677380138> " + client.user.display_name,
			type="rich",
			color=0xfc5fe2
		).set_thumbnail(
			url=get_cosmetic_by_id("CID_565_Athena_Commando_F_RockClimber")['icons']['icon']
		)
	)
	
	loop.call_later(time, stop_bot(client))

async def parse_command(message: discord.Message):
	if type(message.channel) != discord.DMChannel or message.author.bot:
		return
	msg = message.content.split(" ")
	if message.author.id not in list(reverseowner.keys()):
		return
	client = reverseowner[message.author.id]
	if msg[0].lower() == "stop" or msg[0].lower() == "logout":
		await stop_bot(client)
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
					await client.party.me.set_outfit(msg[2])
					await message.channel.send("<:Accept:719047548219949136> Set Outfit to " + msg[2], delete_after=10)
					refresh_message(client)
				else:
					cosmetic = get_cosmetic(name=msg[2], backendType="AthenaCharacter")
					if list(cosmetic.keys()) == ['error']:
						await message.channel.send("<:Reject:719047548819472446> Cannot Find Outfit " + msg[2], delete_after=10)
					else:
						await client.party.me.set_outfit(cosmetic['id'])
						await message.channel.send("<:Accept:719047548219949136> Set Outfit to " + cosmetic['name'], delete_after=10)
						await refresh_message(client)
			elif msg[1].lower() == "backbling" or msg[1].lower() == "backpack":
				msg[2] = " ".join(msg[2:])
				if msg[2].startswith("BID_"):
					await client.party.me.set_backpack(msg[2])
					await message.channel.send("<:Accept:719047548219949136> Set Back Bling to " + msg[2], delete_after=10)
				elif msg[2].lower() == "none":
					await client.party.me.clear_backpack()
					await message.channel.send("<:Accept:719047548219949136> Set Back Bling to None", delete_after=10)
				else:
					cosmetic = get_cosmetic(name=msg[2], backendType="AthenaBackpack")
					if list(cosmetic.keys()) == ['error']:
						await message.channel.send("<:Reject:719047548819472446> Cannot Find Back Bling " + msg[2], delete_after=10)
					else:
						await client.party.me.set_backpack(cosmetic['id'])
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
					await client.party.me.set_pickaxe(msg[2])
					await message.channel.send("<:Accept:719047548219949136> Set Harvesting Tool to " + msg[2], delete_after=10)
				else:
					cosmetic = get_cosmetic(name=msg[2], backendType="AthenaPickaxe")
					if list(cosmetic.keys()) == ['error']:
						await message.channel.send("<:Reject:719047548819472446> Cannot Find Harvesting Tool " + msg[2], delete_after=10)
					else:
						await client.party.me.set_pickaxe(cosmetic['id'])
						await message.channel.send("<:Accept:719047548219949136> Set Harvesting Tool to " + cosmetic['name'], delete_after=10)
			elif msg[1].lower() == "banner" and len(msg) == 4:
				if msg[2].lower() == "design" or msg[2].lower() == "icon":
					await client.party.me.set_banner(icon=msg[3], color=client.party.me.banner[1], season_level=client.party.me.banner[2])
					await message.channel.send("<:Accept:719047548219949136> Set Banner Design to " + msg[3], delete_after=10)
				elif msg[2].lower() == "color" or msg[2].lower() == "colour":
					await client.party.me.set_banner(icon=client.party.me.banner[0], color=msg[3], season_level=client.party.me.banner[2])
					await message.channel.send("<:Accept:719047548219949136> Set Banner Color to " + msg[3], delete_after=10)
				elif msg[2].lower() == "season_level" or msg[2].lower() == "level":
					await client.party.me.set_banner(icon=client.party.me.banner[0], color=client.party.me.banner[1], season_level=msg[3])
					await message.channel.send("<:Accept:719047548219949136> Set Season Level to " + msg[3], delete_after=10)
			elif msg[1].lower() == "battlepass" or msg[1].lower() == "bp" and len(msg) == 4:
				if msg[2].lower() == "has_purchased":
					if msg[3] == "true":
						await client.party.me.set_battlepass_info(has_purchased=True)
						await message.channel.send("<:Accept:719047548219949136> Set Battle Pass Purchase Status to True", delete_after=10)
					elif msg[3] == "false":
						await client.party.me.set_battlepass_info(has_purchased=False)
						await message.channel.send("<:Accept:719047548219949136> Set Battle Pass Purchase Status to False", delete_after=10)
				elif msg[2].lower() == "level":
					await client.party.me.set_battlepass_info(level=msg[3])
					await message.channel.send("<:Accept:719047548219949136> Set Battle Pass Level to " + msg[3], delete_after=10)
				elif msg[3] == "self_boost_xp":
					await client.party.me.set_battlepass_info(self_boost_xp=msg[3])
					await message.channel.send("<:Accept:719047548219949136> Set Battle Pass Self Boost to " + msg[3], delete_after=10)
				elif msg[3] == "friend_boost_xp":
					await client.party.me.set_battlepass_info(friend_boost_xp=msg[3])
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
					if list(playlist.keys()) == ['error']:
						await message.channel.send("<:Reject:719047548819472446> Cannot Find Playlist " + msg[2], delete_after=10)
					else:
						await client.party.me.set_pickaxe(playlist['id'])
						await message.channel.send("<:Accept:719047548219949136> Set Playlist to " + playlist['name'], delete_after=10)
			elif msg[1].lower() == "variants" or msg[1].lower() == "variant":
				if msg[2].lower() == "outfit" or msg[2].lower() == "skin":
					await client.party.me.set_outfit(
						asset=client.party.me.outfit,
						variants=client.party.me.create_variants(
							item="AthenaCharacter",
							**{msg[3]: msg[4]}
						)
					)
					await message.channel.send("<:Accept:719047548219949136> Set Variants to " + msg[3] + " = " + msg[4], delete_after=10)
				elif msg[2].lower() == "backbling" or msg[2].lower() == "backpack":
					await client.party.me.set_backpack(
						asset=client.party.me.backpack,
						variants=client.party.me.create_variants(
							item="AthenaBackpack",
							**{msg[3]: msg[4]}
						)
					)
					await message.channel.send("<:Accept:719047548219949136> Set Variants to " + msg[3] + " = " + msg[4], delete_after=10)
				elif msg[2].lower() == "harvesting_tool" or msg[2].lower() == "pickaxe":
					await client.party.me.set_pickaxe(
						asset=client.party.me.pickaxe,
						variants=client.party.me.create_variants(
							item="AthenaPickaxe",
							**{msg[3]: msg[4]}
						)
					)
					await message.channel.send("<:Accept:719047548219949136> Set Variants to " + msg[3] + " = " + msg[4], delete_after=10)
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
#	elif msg[0].lower() == "variants":
#		

###################
#     Discord     #
###################

loop.create_task(dclient.start(os.getenv("TOKEN")))

@dclient.event
async def on_message(message: discord.Message):
	if message.channel.id == 718979003968520283:
		if "start" in message.content:
			await message.delete()
			await start_bot(message.author)
		else:
			await message.delete()
	elif type(message.channel) == discord.DMChannel:
		await parse_command(message)

for c in config:
	device_auth_details = get_device_auth_details().get(config[c], {})
	
	auth = fortnitepy.AdvancedAuth(
		email=config[c],
		password=password,
		delete_existing_device_auths=False,
		**device_auth_details
	)
	
	client = fortnitepy.Client(
		auth=auth,
		platform=fortnitepy.Platform.MAC
	)
	
	clients[c] = client
	reverse[client] = c
	available[c] = client

try:
	loop.run_forever()
except KeyboardInterrupt:
	loop.create_task(dclient.close())
	for client in owner:
		loop.create_task(stop_bot(client))
	for task in asyncio.Task.all_tasks():
		task.cancel()
