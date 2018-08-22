import discord
import asyncio
import random
import pymongo
import pprint
import urllib.request
from PIL import Image
from PIL import ImageOps


#os.chdir('..')

class settings:
    botToken = ""
    mongo = ""
    spawnChannel = ""
    arenaChannel = ""
    DBname = "db"
    client = discord.Client()
    helpText = 'helpCommand.txt not found if you see this you should probably tell the bot owner'
    
    #mongo = pymongo.MongoClient()

    mongoDB = pymongo.MongoClient("mongodb+srv://Cookie:Cookie@cluster0-t8vqn.mongodb.net/test?retryWrites=true")
    db = mongoDB[DBname]
    #coll = db.admin
    flavor = db.flavors
    users = db.users
    monsters = db.monsters
    arenas = db.arenas
    channel = discord.Channel
    arena = discord.Channel
    #channel = client.get_channel('444469825381859330')
    #arena = client.get_channel('447892299825938443')
    printVerbose = True


class botStatus:
    requestStop = False
    
class gameData:
    monsterCount = 0
    maxRarity = 3

class encounter:
    monsterID = 0
    monsterName = '' 
    monsterRemaining = 0
    message = None
    image = None


class arena:
    monster1 = 0
    monsterName1 = ''
    user1 = 0
    HP1 = 0
    monster2 = 0
    monsterName2 = ''
    user2 = 0
    HP2 = 0
    arenaMessage = None
    arenaImage = None
    arenaStatus = None
    
def printDetails(string):
    if settings.printVerbose:
        print(string)
        
def summonRandomMonster():
    printDetails("Finding a random monster")
    #First choose a rarity level
    rarity = 0
    for x in range(0, gameData.maxRarity*2):
        rarity += random.randint(0,1)
    rarity -= gameData.maxRarity
    rarity = abs(rarity)
    printDetails("Rarity chosen is "+str(rarity))
    #Then choose a monster
    monsterList = settings.monsters.find({"rarity":rarity})
    if monsterList.count()<1:
        return None
    monster = monsterList[random.randint(0,monsterList.count()-1)]
    printDetails("Monster ID selected is "+str(monster["monsterID"]))
    printDetails("Monster name selected is "+monster["name"])
    
        
    return monster

def catchMonster(user):
    if(encounter.monsterID==0):
        print("A race condition may have occured please tell cookie if you see this message.")
        print("Or you may have tampered with the database wrong. Don't give a monster an ID of 0!")
    printDetails("Catch monster")
    #first check if the user exists in the database
    userDoc = settings.users.find_one({'userID' : int(user.id)})
    userFound = userDoc != None
    if (userFound):
        printDetails("User already exists")
    else:
        printDetails("User does not exist")
    
    #create new user if they do not exist
    printDetails("Checking if new user")
    if (not userFound):
        printDetails("Creating New User")
        array = [False]*1#(userChannel.monsterCount+1)
        settings.users.insert_one({"userID": int(user.id),"collection": array})
        userDoc = settings.users.find_one({"userID": int(user.id)})
        
        
    #make sure the user's array is the right size
    printDetails("Checking array size")
    userArray =  userDoc["collection"]
    #0 is reserved for when there is no monster so the array can only hold
    #its length-1
    needsUpdate = gameData.monsterCount>(len(userArray)-1)
    print("monsterCount " +str(gameData.monsterCount ))
    print("user coll length "+str((len(userArray)-1)))
    if (needsUpdate):
        printDetails("Updating")
        extension = gameData.monsterCount-(len(userArray)-1)
        
        
        for x in range(len(userArray),gameData.monsterCount+1):
             #userArray[x] = False
             #userArray.append([False]*extension)
             userArray.append(False)
        printDetails("Extending array by "+ str(extension))
        printDetails(userArray)
        printDetails("Array now has a length of "+ str(len(userArray)))
    else:
        printDetails("No extension needed")
   
    #check if the user has the monster already and update it
    printDetails("Updating user catch list")

    userHasMonster = userArray[encounter.monsterID]
    print("User has monster "+ str(userArray[encounter.monsterID]))
    
    if(userHasMonster):
        printDetails("User already has monster")
        return False
    else:
        printDetails("User caught monster " + str(encounter.monsterID))
        userArray[encounter.monsterID] = True
        settings.users.find_one_and_update({'userID' : int(user.id)},{'$set':{"collection":userArray } })
        return True
    #return true if they caught the monster else return false if they already have it
    
def parseFlavorText(flavor, userName):
    # 1 = catch monster
    # 2 = fail monster catch
    # 3 = monster appear
    # 4 = monster leave
    # 5 = monsters all caught
    # 6 = no monster summonable
    printDetails("Parsing flavor text")
    flavorList = settings.flavor.find({"type":flavor})
    textDoc = flavorList[random.randint(0,flavorList.count()-1)]
    text = textDoc["text"]
    text = text.replace("[monster]", encounter.monsterName)
    text = text.replace("[user]", userName)
    printDetails(text)
    return text

def parseArenaText(flavor, ATK, DEF, damage):
    # 7 = attack
    # 8 = defend
    # 9 = miss
    
    
    
    printDetails("Parsing arena text")
    flavorList = settings.flavor.find({"type":flavor})
    textDoc = flavorList[random.randint(0,flavorList.count()-1)]
    text = textDoc["text"]
    text = text.replace("[ATK]", ATK)
    text = text.replace("[DEF]", DEF)
    text = text.replace("[damage]", str(damage))
    printDetails(text)
    return text


def describeMonster(userID, monsterID):
    printDetails("Describing monster")
    #check if user has monster
    userDoc = settings.users.find_one({'userID':int(userID)})
    userArray = userDoc["collection"]
    pprint.pprint(userArray)
    #Check if the number is past the UserArray sub 1 to get true monster count
    if (len(userArray)-1<int(monsterID)):
        printDetails("Monster out of range")
        return 'No data found'
    
    userHasMonster = userArray[int(monsterID)]
    printDetails("Does the user have this monster?"+str(userHasMonster))
    #get the monster's description and then return it
    if(userHasMonster):
        monster = settings.monsters.find_one({'monsterID': int(monsterID)})
        return '```'+monster["description"]+'```'
    else:
        printDetails("monster not owned")
        return 'No data found'

def listOwnedMonsters(userID):
    #Loop through user's
    printDetails("Listing user's owned monsters")
    monsterList = '```'
    userDoc = settings.users.find_one({'userID':int(userID)})
    userArray = userDoc["collection"]
    for x in range(0,len(userArray)):
        print(x)
        #may cause a bug if monster 0 is set to true but that should never be true anyway
        if userArray[x]:
            monster = settings.monsters.find_one({'monsterID': int(x)})
            monsterList = monsterList + str(x)+'. '+monster['name']+'\n'
    monsterList = monsterList + '```'
    return monsterList

def getMonsterList(userID):
    printDetails("Acuiring monster List")
    userDoc = settings.users.find_one({'userID':int(userID)})
    userArray = userDoc["collection"]
    return userArray

def compileArena (arena,monsterA,monsterB,xPos1,yPos1,xPos2,yPos2,halign,valign):
    
    print("compiling arena")
    A = monsterA.convert('RGBA')
    B = monsterB.convert('RGBA')
    B = ImageOps.mirror(B)
    arena = arena.convert('RGBA')
    
    #calculate offset coords
    xFinal1 = xPos1+(A.size[0]*halign)
    yFinal1 = yPos1+(A.size[1]*valign)
    xFinal2 = xPos2+(B.size[0]*halign)
    yFinal2 = yPos2+(B.size[1]*valign)
    #if it is too negative don't draw it
    draw1 = True
    draw2 = True
    #crop if the image is in the negatives
    if (xFinal1<0 or yFinal1<0):
        #check if the image is completely out of view 
        if(xFinal1<=-A.size[0]or yFinal1<=-A.size[1]):
            print('image OOB')
            draw1 = False
        #crop it if it isn't
        else:
            print('cropping image')
            A = A.crop((abs(xFinal1),abs(yFinal1),A.size[0],A.size[1]))
            #set the negatives to 0 so it can draw properly
            if (xFinal1<0):
                print('Set x1 to 0')
                xFinal1 = 0
            if (yFinal1<0):
                print('Set y1 to 0')
                xFinal1 = 0
    #crop if the image is in the negatives
    if (xFinal2<0 or yFinal2<0):
        #check if the image is completely out of view 
        if(xFinal2<=-B.size[0]or yFinal2<=-B.size[1]):
            print('image OOB')
            draw2 = False
        #crop it if it isn't
        else:
            print('cropping image')
            B = B.crop((abs(xFinal2),abs(yFinal2),B.size[0],B.size[1]))
            #set the negatives to 0 so it can draw properly
            if (xFinal2<0):
                print('Set x2 to 0')
                xFinal2 = 0
            if (yFinal2<0):
                print('Set y2 to 0')
                xFinal2 = 0
    #composite = Image.composite(A, B,'RGBA')
    
    arena.alpha_composite(A, (int(xFinal1),int(yFinal1)))
    arena.alpha_composite(B, (int(xFinal2),int(yFinal2)))
    #arena.paste(monsterA,(150,100),composite)
    arena.save("arenaDisplay.png")
    return arena

def enterArena(userID,monsterID):
    printDetails("Arena Entry")
    #first check if it is a valid entry
    userArray = getMonsterList(userID)
    if (not userArray[monsterID]):
        return "Invalid Entry"
    #check if arena slot 1 is open
    if arena.monster1 == 0:
        arena.monster1 = monsterID
        arena.user1 = userID
        arena.HP1 = 100
        return "Entry accepted"
    #if not put in slot two
    elif arena.monster2 == 0:
        arena.monster2 = monsterID
        arena.user2 = userID
        arena.HP2 = 100
        #begin an arena coroutine if both slots are filled
        
        settings.client.loop.create_task(arenaBattle(settings.client))
        return "Entry accepted beginning battle!"
    else:
        return "Arena is full"

def validateMonsterOwned(monsterID,userID):
    printDetails("Validate Monster Owned")
    #first check if it is a valid entry
    userArray = getMonsterList(userID)
    try:
        if (not userArray[monsterID]):
            return False
        else:
            return True
    except IndexError:
        return False

def getMonsterImage(monsterID):
    printDetails("Getting monster image ID: "+str(monsterID))
    monster = settings.monsters.find_one({'monsterID': monsterID})
    i = urllib.request.urlopen(monster["monsterImage"])
    image = Image.open(i)
    return image

def getMonsterImageFile(monsterID,temp):
    printDetails("Getting monster image ID: "+str(monsterID))
    monster = settings.monsters.find_one({'monsterID': monsterID})
    print(str(monster))
    i = urllib.request.urlretrieve(monster["monsterImage"],temp)

    
def getMonsterName(monsterID):
    printDetails("Getting monster name")
    monster = settings.monsters.find_one({'monsterID': monsterID})
    return monster['name']


def updateArenaStatus(monster1,monster2):
    return '```'+str(monster1)+': '+str(arena.HP1)+' '+str(monster2)+': '+str(arena.HP2)+'```'



@asyncio.coroutine
async def arenaBattle(client):
    printDetails("Arena Fight")
    #Intro message
    if arena.arenaMessage == None:
        #display Monster arena
        #randomly select arena
        arenaCount = settings.arenas.count()-1
        arenaSelected = random.randint(0,arenaCount)
        arenaDoc = settings.arenas.find_one({'id' : arenaSelected})
        
        
        arenaImageFile = urllib.request.urlopen(arenaDoc["arenaImage"])
        arenaImage = Image.open(arenaImageFile)
        
        monsterImage1 = getMonsterImage(arena.monster1)
        monsterImage2 = getMonsterImage(arena.monster2)

        x1 = arenaDoc['x1']
        y1 = arenaDoc['y1']
        x2 = arenaDoc['x2']
        y2 = arenaDoc['y2']

        halign = arenaDoc['halign']
        valign = arenaDoc['valign']
        finalArena = compileArena(arenaImage,monsterImage1,monsterImage2,x1,y1,x2,y2,halign,valign)
        finalArena.save('finalArena.png')
        arenaDisplayMessage = await settings.client.send_file(settings.arena,'finalArena.png')

        
        print(settings.arena.name)
        arena.arenaMessage = await settings.client.send_message(settings.arena,'Battle Start!')
        arena.monsterName1 = getMonsterName(arena.monster1)
        arena.monsterName2  = getMonsterName(arena.monster2)
        arena.arenaStatus = await settings.client.send_message(settings.arena,updateArenaStatus(arena.monster1,arena.monster2))
        winner = None
       
    while (arena.HP1>0 and arena.HP2>0):
        
        
        #player 1 attack message
        damage = random.randint(0,10)
        attackMessage = parseArenaText(7, arena.monsterName1, arena.monsterName2, damage)
        await settings.client.edit_message(arena.arenaMessage,new_content= '```'+attackMessage+'```')
        await asyncio.sleep(5)
        
        
        #player 2 defense message
        if damage != 0:
            attackMessage = parseArenaText(8, arena.monsterName1, arena.monsterName2, damage)
        else:
            attackMessage = parseArenaText(9, arena.monsterName1, arena.monsterName2, damage)
        await settings.client.edit_message(arena.arenaMessage,new_content= '```'+attackMessage+'```')
        arena.HP2-=damage
        
        if arena.HP2<1:
            winner = arena.monsterName2
            break
        await settings.client.edit_message(arena.arenaStatus,new_content= updateArenaStatus(arena.monsterName1,arena.monsterName2))
        
        await asyncio.sleep(5)
        #check to kill process

        #player 2 attack message
        damage = random.randint(0,10)
        attackMessage = parseArenaText(7, arena.monsterName2, arena.monsterName1, damage)
        await settings.client.edit_message(arena.arenaMessage,new_content= '```'+attackMessage+'```')
        await asyncio.sleep(5)
        
        
        #player 1 defense message
        if damage != 0:
            attackMessage = parseArenaText(8, arena.monsterName2, arena.monsterName1, damage)
        else:
            attackMessage = parseArenaText(9, arena.monsterName2, arena.monsterName1, damage)
        await settings.client.edit_message(arena.arenaMessage,new_content= '```'+attackMessage+'```')
        arena.HP1-=damage
        if arena.HP1<1:
            winner = arena.monsterName1
            break
        await settings.client.edit_message(arena.arenaStatus,new_content= updateArenaStatus(arena.monsterName1,arena.monsterName2))
        await asyncio.sleep(5)
        

        #declare victory and reset arena
    await settings.client.edit_message(arena.arenaMessage,new_content= '```'+winner+" has emerged victorious!"+'```')
    await settings.client.delete_message(arena.arenaStatus)
    arena.monster1 = 0
    arena.monsterName1 = ''
    arena.user1 = 0
    arena.HP1 = 0
    arena.monster2 = 0
    arena.monsterName2 = ''
    arena.user2 = 0
    arena.HP2 = 0
    arena.arenaMessage = None
    arena.arenaImage = None
    arena.arenaStatus = None
    await settings.client.delete_message(arenaDisplayMessage)


@settings.client.event
async def on_ready():
    await settings.client.login(settings.botToken)
    print('Logged in as')
    print(settings.client.user.name)
    gameData.monsterCount = int(settings.monsters.count({ 'monsterID' : { '$exists' : 'true' } }))
    print("Number of monsters is " + str(gameData.monsterCount ))
    #validate channels
    channelCount = 0
    encounterFound = False
    arenaFound = False
    for server in settings.client.servers:
        for channel in server.channels:
            if(channel.name == settings.spawnChannel):
                settings.channel = channel
                encounterFound = True
                print("Encounter channel found!")
            if(channel.name == settings.arenaChannel):
                settings.arena = channel
                arenaFound = True
                print("Arena channel found!")
        if(arenaFound and encounterFound):
            print("Channels validated!")
            break

    if (not encounterFound or not arenaFound):
       input("The channels were not found. Please use the bot edit program to ensure the channels were chosen correctly")
       exit(0)
    #set help file
    helpFile = open('helpCommand.txt','r')
    settings.helpText = helpFile.read()
    settings.client.loop.create_task(periodicEvent(settings.client))
    print('Periodic event')
    
    
    
    





    
@asyncio.coroutine
async def periodicEvent(client):
    
    c = settings.client.get_channel('444469825381859330')
    sleep = 300
    while True:
        if encounter.monsterID == 0: #summon monster
            monster = summonRandomMonster()
            sleep = 300
            if monster != None:
                encounter.monsterID = monster["monsterID"]
                encounter.monsterRemaining = 3
                encounter.monsterName = monster["name"]
            
                #urllib.request.urlretrieve(monster["monsterImage"],'image.png')
                getMonsterImageFile(encounter.monsterID,"encounter.png")
                encounter.message = await settings.client.send_message(c,parseFlavorText(3,''))
                encounter.image = await settings.client.send_file(c,"encounter.png")
            else:
                await settings.client.send_message(c,parseFlavorText(6,''))

        elif encounter.monsterID != 0: #remove monster
            sleep = random.randint(400,2000)
            if encounter.monsterRemaining > 0:
                await settings.client.edit_message(encounter.message,new_content= parseFlavorText(4,''))
                encounter.monsterRemaining = 0
                
            encounter.monsterID = 0

            #remove image
            await settings.client.delete_message(encounter.image)
            
        await asyncio.sleep(sleep)




    
@settings.client.event
async def on_message(message):
    c = settings.client.get_channel('444469825381859330')
    if message.content.startswith('!desc') and message.channel.is_private:
           
        arg = ''.join(char for char in message.content if char.isdigit())
        
        if (validateMonsterOwned(int(arg),message.author.id)):
            getMonsterImageFile(int(arg),"desc.png")
            encounter.image = await settings.client.send_file(message.channel,"desc.png")
            await settings.client.send_message(message.channel,describeMonster(message.author.id,int(arg)))
        else:
            await settings.client.send_message(message.channel,"Monster not found")

    elif message.content.startswith('!index') and message.channel.is_private:
                
        await settings.client.send_message(message.channel,listOwnedMonsters(message.author.id))

    elif message.content.startswith('!arena') and not message.channel.is_private:

        arg = ''.join(char for char in message.content if char.isdigit())
        await settings.client.send_message(message.channel,enterArena(message.author.id,int(arg)))
        
    elif message.content.startswith('!help'):
        if message.channel.is_private:
            await settings.client.send_message(message.channel,settings.helpText)
        else:
            await settings.client.send_message(message.channel,"DM the bot with !help to access the command list")

    elif message.content.startswith('!catchmonster') and not message.channel.is_private: #catch monster
        if encounter.monsterID != 0:
            if catchMonster(message.author):#monster was caught by user
                encounter.monsterRemaining -= 1
                await settings.client.send_message(c, parseFlavorText(1,message.author.name))

                if encounter.monsterRemaining<1: #no monsters left
                    encounter.monsterID = 0
                    #remove image
                    await settings.client.delete_message(encounter.image)
                    #update text
                    await settings.client.edit_message(encounter.message,new_content= parseFlavorText(5,message.author.name))
            else: #monster was not caught by user
                await settings.client.send_message(c, parseFlavorText(2,message.author.name))



def UI():
    
    try:
        file = open('settings.txt','r+')
    except FileNotFoundError:
        input("No settings found. Use the bot editor to set up the bot")
        exit(0)
    print("Current settings are")

    settings.botToken = file.readline()[:-1]
    settings.mongo = file.readline()[:-1]
    settings.DBname = file.readline()[:-1]
    settings.spawnChannel = file.readline()[:-1]
    settings.arenaChannel = file.readline()[:-1]
    #Update database references
    mongoDB = pymongo.MongoClient(settings.mongo)
    settings.db = mongoDB[settings.DBname]
    settings.flavor = settings.db.flavors
    settings.users = settings.db.users
    settings.monsters = settings.db.monsters
    settings.arenas = settings.db.arenas
    
    #End update database references
    file.close()
    print('\nBot Token: \n'+ settings.botToken)
    print('\nMongoDB login: \n'+ settings.mongo)
    print('\nDatabase Name : \n'+ settings.DBname)
    print('\nMonster Encounter Channel: \n'+ settings.spawnChannel)
    print('\nMonster Battle Channel: \n'+ settings.arenaChannel)

    userInput = input ('\nRun with these settings? Type yes to continue or anything else to exit.')
    userInput = userInput.lower()

    if (userInput == 'y' or userInput == 'yes'):
        print('Beginning bot')
        settings.client.run(settings.botToken)
    
    print('Goodbye')
    #settings.client.run(settings.botToken)

    
UI()




