There are 3 programs within this build
They are all located in the dist folder

If you downloaded the pre compiled version you will need 
Inside the dist folder you will find 3 more folders. Each contains an executable which can be run. 

If you downloaded the uncompiled code you will need the following libraries. 
Ensure they are all in the same directory with the settings.txt and helpCommand.txt

discord
pymongo
PIL

The BOT folder is the actual bot itself that will send messages to Discord. 
You will need to use the other programs to set it up

The COMMAND and GUI folders contain the set up programs. 
Both can be used to set up the bot


SETTING MENU

If you leave the settings menu all of the changes you made will be lost unless you click the save button


1 Discord bot token
Visit discord's official website and access developers > developer's portal. 
If you are logged in you can create an APP. You will need the APP's bot token
Enter it under BOT TOKEN
You will also need to invite the bot to your Discord server

2. MongoDB credentials
In order to run this program you need a mongoDB server.
If you are using the COMMAND program it will prompt you to enter this before it will do anything
MongoDB offers a free service known as ATLAS that you can use here
https://www.mongodb.com/download-center?jmp=nav#atlas

You will need the connection string. Enter it under MONGODB LOGIN.
If you have set up permissions for the user to use a specific database enter the name under DATABASE NAME

3. Enter the name of channel you want the monsters to appear in the MONSTER ENCOUNTER CHANNEL
Enter the name of channel you want the arena to be in the MONSTER BATTLE CHANNEL

Remember to click save!


DATABASE MENUS

There are 3 main database menus. MONSTERS, FLAVORS, and ARENAS
You can use the UPDATE button to change their parameters which will be explained below.
You can use the DETAIL VIEW button to view the images of the monsters and arenas
You can use the ADD button to add new entries
NOTE- Please use PNG files only for your images
NOTE- It is highly recommended you DO NOT edit the IDs of monsters.
If you must do so edit update one at a time.

MONSTERS
Monsters will appear the MONSTER ENCOUNTER CHANNEL. Users can use !catchmonster to catch them.
Monsters have 4 attribues. NAME RARITY DESCRIPTION MONSTERIMAGE
NAME is the name of the monster

RARITY is how rare the monster is. Think of each rarity as a pool. 
RARITY 0 has a 50% chance of being selected. 
Each higher rarity will have half as much chance to be selected.
If it is chosen then all of the monsters in that pool have an even chance of being selected
RARITY -1 will never be chosen. Use it if you want to temporarily remove a monster

MONSTER DESCRIPTIONs can be read when the user DMs the bot !desc

MONSTERIMAGE is the URL where the PNG for the monster is stored

FLAVORS
Flavors are text used to describe event such as monster appearences or arena battles
Flavors have 2 Attributes TYPE TEXT
NOTE ensure that you have 1 type of each flavor
TYPE dictates what events cause a flavor to appear
Encounter Channel
# 1 = When a monster is caught
# 2 = When a user tries to catch a monster they've already caught
# 3 = When a monster appears
# 4 = When a monster leaves
# 5 = When 3 monsters are caught
# 6 = When the bot picks a rarity that have no monsters

Arena Channel
# 7 = When a monster Attacks
# 8 = When a monster defends
# 9 = When a monster misses

TEXT is the text that will be displayed when the flavor is called
Certain character combinations can be used to display certain info
These can only be used in their respective channels
Encounter channel
[user]- Displays the username of someone who attempts to capture a monster
[monster]- Displays the name of the monster that is appearing or being caught

ArenaChannel
[ATK]- The name of the attacking monster
[DEF]- The name of the defending monster


ARENAS
Monsters can be sent with the !arena [int] command.
Where [int] is the ID of a monster
A user must have caught the monster before sending to the arena

Arenas have many attributes

x1- x coordinate of the first contestant
y1- y coordinate of the first contestant
x2- x coordinate of the second contestant
y2- y coordinate of the second contestant
Alignments dictate where the coordinate is relative to the whole image
e.g. Setting halign to LEFT means x coordinate is the leftmost part of the image Center 
halign- Left Middle Right
valign- Top Middle Bottom
arenaImage- The image of the arena


EXPORT
exports allow you to download all of the data.
It is recommended you use this for back ups.

IMPORTS 
Imports allow you to download files created by the export function
Keep in mind that it does not perform overrides and simply adds 
the data in the import on top of the old data. 
IDs are calculated to increment according to the data already in the database

It is recommended that when restoring a back up to instead create a new database 

helpCommand.txt
Inside the DIST folder there exists a file called helpCommand.txt
It can be accessed by users with !help
you may edit this file if you wish for it to say something else.