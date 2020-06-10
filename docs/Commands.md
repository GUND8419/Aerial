# Commands
Aerial Bot has a wide range of commands, including changing cosmetics, kicking, promoting, joining, and more.

## Main Commands
### Cosmetics
- `set outfit <Name or ID>` Set the outfit of the client.
- `set backbling <Name or ID or None>` Set the back bling of the client.
- `set harvesting_tool <Name or ID>` Set the harvesting tool of the client.
- `set emote <Name or ID or None>` Set the emote of the client.
- `set banner`
	- `set banner design <design>` Set the client's banner design.
	- `set banner color <color>` Set the client's banner color.
	- `set banner season_level <level>` Set the client's banner season level.
- `set battlepass`
	- `set battlepass has_purchased <True or False>` Set the client's battle pass purchase status.
	- `set battlepass level <level>` Set the client's battle pass level.
	- `set battlepass self_boost_xp <boost>` Set the client's battle pass personal XP boost.
	- `set battlepass friend_boost_xp` Set the client's battle pass friend XP boost.
- `set variant <item> <key> <value>` Set the client's variants for either the outfit, back bling, or harvesting tool. This command is considered advanced, since variants don't seem to follow much logic.
- `set enlightenment <season> <level>` Set the client's enlightenment level for the outfit or the back bling. You will probably have to select a variant before setting.  
	```
	Example for Golden Peely
	
	set outfit Agent Peely
	set variant outfit progressive 4
	set enlightenment 2 340
	```
- `clone <user>` Copies the cosmetic loadout of a user in the party.
- `variants <item>` Show the possible variants for the current outfit, back bling, or harvesting tool.

### Party
- `set status <status>` Set the client's status.
- `set code <matchmakingcode>` Set the custom matchmaking code, if the client is the party leader.
- `set playlist <Name or ID>` Set the playlist, if the client is the party leader.
- `join <user>` Join a friend's party.
- `kick <user>` Kick a party member, if the client is party leader.
- `promote <user>` Promote another party member, if the client is party leader.
- `send <message>` Send a message in party chat.

### Friend
- `friend add <user>` Send a friend request to a user.
- `friend remove <user>` Remove a friend from the bot's friends.

### Other
- `stop` Stop the bot. Please run this command once you are finished with it, to free up space for others.

## Cloud Hosting Commands

## Self Hosting Commands