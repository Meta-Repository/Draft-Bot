import discord
import random
import asyncio
import sys
import json
import os
import os.path
from os import path
import imagemanipulator
from io import StringIO

BotToken = "NzA3MzI0NjAxNDQ4NzkyMDY0.XrHJbw.mwn0yBiFMXRTBs2W93ePyWwcW64"
GuildName = "fspluver's server"
GuildID = 706652047042412565
client = discord.Client()

from discord.ext import commands
client = commands.Bot(command_prefix = 'B!')

#Connecting
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GuildName:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


# not a fan of Python classes, but this is the implemetation I'm doing to allow for a list of just strings as well (for now)
class CardInfo:
    #Left all but name as optional so that we can fall back if that's all we have. Definitely could have more properties in this class, just wanted a good starting point.
    def __init__(self, name, id = -1, cardType="", description = "", imageUrl = "", attribute = "", level = "", race = ""):
        self.name = name
        self.id = id
        self.cardType = cardType
        self.description = description
        self.imageUrl = imageUrl
        self.attribute = attribute
        self.level = level
        self.race = race
    #We're just displaying names for now, but that can change. What these mean is that if you print a list of these, only their names will show.
    def __repr__(self):
        return self.name
    def __str__(self):
        self.name

def sortPack(pack):
    #this is going to be sloppy shit
    monsters = [card for card in pack if 'monster' in card.cardType.lower() and ('synchro' not in card.cardType.lower() and 'xyz' not in card.cardType.lower())]
    spells = [card for card in pack if 'spell' in card.cardType.lower()]
    traps = [card for card in pack if 'trap' in card.cardType.lower()]
    extras = [card for card in pack if 'xyz' in card.cardType.lower() or 'synchro' in card.cardType.lower()]
    return monsters + spells + traps + extras


#technically there's a LAUGH attribute too, but we don't fux with that
attributes = ['DARK', 'DIVINE', 'EARTH', 'FIRE', 'LIGHT', 'WATER', 'WIND'] 

#yes I know they're strings. It's all strings all the way down. Deal with it.
levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

#thought there were way more than 25 of these
monsterTypes = ['Aqua', 'Beast', 'Beast-Warrior', 'Creator God', 'Cyberse', 'Dinosaur', 'Divine-Beast', 'Dragon', 'Fairy', 'Fiend', 'Fish', 'Insect',
'Machine', 'Plant', 'Psychic', 'Pyro', 'Reptile', 'Rock', 'Sea Serpent', 'Spellcaster', 'Thunder', 'Warrior', 'Winged Beast', 'Wyrm', 'Zombie']

#may be comprehensive?
cardTypes = ['Normal Monster', 'Gemini Monster', 'Effect Monster', 'Tuner Monster', 'Spell', 'Trap', 'Synchro', 'XYZ']


def createAttributeDictionary(cardList):
    #still do not understand globals
    global attributes
    #this feels jank
    attributeDict = {} 
    for attr in attributes:
        #add an entry to our dictonary with the attribute name and count of cards with that attribute
        attributeDict[attr] = len([card for card in cardList if card.attribute == attr])
    #I did not understand this, now I do, and it is pretty clean
    return {"**" + str(k) + "**": v for k, v in sorted(attributeDict.items(), key=lambda item: item[1], reverse=True) if v != 0}
    
def createTypeDictionary(cardList):
    #still do not understand globals
    global monsterTypes
    #this feels jank
    monsterTypeDict = {} 
    for monsterType in monsterTypes:
        #add an entry to our dictonary with the type name and count of cards with that type
        monsterTypeDict[monsterType] = len([card for card in cardList if card.race == monsterType])
    #I did not understand this, now I do, and it is pretty clean
    return {"**" + str(k) + "**": v for k, v in sorted(monsterTypeDict.items(), key=lambda item: item[1], reverse=True) if v != 0}

def createLevelDictionary(cardList):
    #still do not understand globals
    global levels
    #this feels jank
    levelDict = {} 
    for level in levels:
        #add an entry to our dictonary with the level and count of cards of that level (not in extra)
        levelDict[level] = len([card for card in cardList if card.level == level and 'synchro' not in card.cardType.lower() and 'xyz' not in card.cardType.lower()])
    #I did not understand this, now I do, and it is pretty clean
    return {"**Level " + str(k) + "**": v for k, v in levelDict.items() if v != 0}

def createTunerDictionary(cardList):
    #still do not understand globals
    global levels
    #this feels jank
    tunerDict = {} 
    for level in levels:
        #add an entry to our dictonary with the level and count of tuners with that level
        tunerDict[level] = len([card for card in cardList if card.level == level and 'tuner' in card.cardType.lower() and 'synchro' not in card.cardType.lower()])
    #I did not understand this, now I do, and it is pretty clean
    return {"**Level " + str(k) + "**": v for k, v in tunerDict.items() if v != 0}

def createExtraMessage(cardList):
    #still do not understand globals
    global levels
    #this feels jank
    syncDict = {} 
    xyzDict = {} 
    for level in levels:
        #add an entry to our dictonary with the level and count of synchros with that level
        syncDict[level] = len([card for card in cardList if card.level == level and 'synchro' in card.cardType.lower()])
        #add an entry to our dictonary with the level and count of xyz with that level
        xyzDict[level] = len([card for card in cardList if card.level == level and 'xyz' in card.cardType.lower()])
    #I did not understand this, now I do, and it is pretty clean
    syncLine = '__Synchros__ ' + str({"**Level " + str(k) + "**": v for k, v in syncDict.items() if v != 0})
    xyzLine = '__XYZ__ ' + str({"**Rank " + str(k) + "**": v for k, v in xyzDict.items() if v != 0})
    return syncLine + '\n' + xyzLine 

#this one's just gonna have to get close enough
def createSpreadDictionary(cardList):
    #still do not understand globals
    global cardTypes
    #this feels jank
    cardTypeDict = {} 
    for cardType in cardTypes:
        #add an entry to our dictonary with the level and count of cards with that card type
        cardTypeDict[cardType] = len([card for card in cardList if cardType.lower() in card.cardType.lower()])
    #I did not understand this, now I do, and it is pretty clean
    return {"**" + str(k) + "**": v for k, v in cardTypeDict.items() if v != 0}

CardList = []

#import code. Short and sweet.
def import_cube():
    global CardList
    CardList = []
    if (path.exists('list.cub')):
        print('Cube list discovered. Importing.')
        with(open("list.cub", 'r')) as cubeFile:
            #Python makes some things so so easy
            cardDict = json.load(cubeFile)
            #Instantiate a new CardInfo object for each card in the list. Definitely could pull in more info from the JSON - there's a lot there.
            for card in cardDict:
                CardList.append(CardInfo(card['name'], card['id'], card['type'], card['desc'], card['card_images'][0]['image_url'], card.get('attribute'), card.get('level'), card.get('race')))

    else:
        print('Did not find cube list.')

import_cube()

pools = []
pool = []
players = []
playernames = []
packs = []
pack = []
i = 0
x = 0
t = 0
pickNumber = 0
pooltosend = ""
PickLog = []
logtosend = ""

reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '0️⃣',
 '🇦', '🇧','🇨','🇩','🇪']


#Welcomes people who join the server
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@client.event
async def on_reaction_add(reaction, user):
    global packs
    global pickNumber
    global t
    global CardList

    #checks to make sure there are packs, this is a DM, and the player is in the draft
    if(len(packs) == 0 or  not (user in players) or not "DMChannel" in str(type(reaction.message.channel))):
        return    

    #given how reacts are spliced into packs, this gets the index of the reacted card
    cardIndex = reactions.index(str(reaction)) if str(reaction) in reactions else 100
    #get this player's pack
    workingPack = packs[players.index(user)]

    pick(user, cardIndex, workingPack)
                
def pick(user, cardIndex, workingPack, afk = False):
    global packs
    global pickNumber
    global t
    global CardList
    global PickLog

    #is the react in the pack?
    if(cardIndex <= len(workingPack) - 1):

        #checks to guarantee that there aren't multiple picks from one pack
        poolCount = len([card for card in pool if user.name in card])     
        if(poolCount % 15 > pickNumber):
            asyncio.create_task(user.send("I know they're all good cards, but one per pack, please. Maybe get a snack or something while you wait.")) #we don't like cheaters
            return  

        pool.append([user.name, workingPack[cardIndex]]) #add card to pool
        PickLog.append([workingPack[cardIndex], len(workingPack), len(workingPack)])
        workingPack.remove(workingPack[cardIndex]) #remove card from pack
        asyncio.create_task(user.send('Nice pick! It has been added to your pool. Type !mypool to view your entire cardpool.'))


        if(afk and pickNumber == 14):
            asyncio.create_task(user.send('You have been removed from the draft due to inactivity.'))
            del packs[players.index(user)]
            players.remove(user)

        #Automatically passing the pack
        length = len(packs[0])
        if all (len(y)==length for y in packs):
            if t == (1 or 3):
                packs = packs[1:] + packs[:1] #Play with this to make packs pass reverse. I think can just add - before the 1s
            else:
                packs = packs[-1:] + packs[:-1] #Play with this to make packs pass reverse. I think can just add - before the 1s
            if len(packs[0]) == 0:
                packs = []
                pickNumber = 0
                t = t+1
                if t < 4:
                    asyncio.create_task(user.send('Here is your next pack! It may take a few seconds to load. Good luck!'))
                    FullList = random.sample(CardList, len(players)*15)
                    CardList = [q for q in CardList if q not in FullList] #Removes the cards from the full card list

                    i = 0 #For pulling cards from the full list into packs
                    for word in players:
                        pack = sortPack(FullList[i:i+15])
                        packs.append(pack) #Holds the packs
                        i = i+15
                        #splices reactions into pack
                        packWithReactions = [a + ': ' + b.name for a, b in zip(reactions, pack)]
                        asyncio.create_task(send_pack_message("React to select a card. Happy drafting!\n"+str(packWithReactions), word, pack))
                asyncio.create_task(pick_timer())
            else:                   
                for word in players:
                    #splices reactions into pack
                    packWithReactions = [a + ': ' + b.name for a, b in zip(reactions, packs[players.index(word)])] 
                    asyncio.create_task(send_pack_message('Your next pack: \n\n'+str(packWithReactions), word, packs[players.index(word)]))
                pickNumber = pickNumber + 1
                asyncio.create_task(pick_timer())

#Responds in chat to messages. 
@client.event
async def on_message(message):
    global packs
    global CardList
    global FullList
    global w
    global pickNumber
    global t
    global pooltosend
    global players
    global pool
    global playernames
    global u
    global PickLog
    global logtosend
    w = 0
    u = 0
    #printprint(message.content.lower())
    if message.author == client.user:
        return
 

 #Players - Sign up and check current players

    #Message is someone tries to sign up twice
    if ('!joindraft') in message.content.lower() and message.author in players:
        asyncio.create_task(message.channel.send('It\'s not possible! No one has the power to be in two draft seats at once!'))
    #Registers the player
    if (('!joindraft') in message.content.lower() and packs == []) and (message.author not in players):
        #made it announce name - we might want to look into always sending this to the main server even if draft is joined in PM
        if u == 0: #u becomes 1 once the draft has started. Prevents people from joining mid draft
            asyncio.create_task(message.channel.send(message.author.name + ' has joined the draft!'))
            players.append(message.author)
            playernames.append(message.author.name)
    #de-registers a player
    if ('!leavedraft') in message.content.lower() and message.author in players:
        if u == 0: #u becomes 1 once the draft has started. Prevents people from leaving mid draft
            asyncio.create_task(message.channel.send('So sorry to see you leave, ' + message.author.name + '. Catch you for the next one!'))
            players.remove(message.author)
            playernames.remove(message.author.name)
    #Sends the name of all registered players. Commented out has all the person's info (e.g. Discord ID)    
    if ('!currentplayers') in message.content.lower():
        asyncio.create_task(message.channel.send(playernames))

   



 #Sends first pack to all players
    if ('!!stardraft') in message.content.lower():
        if 'Admin' in str(message.author.roles): #Only admins can do this command
            u = 1 #See !joindraft. Prevents people from signing up once draft has started
            asyncio.create_task(message.channel.send('The draft is starting! All players have received their first pack. Good luck!'))
            FullList = random.sample(CardList, len(players)*15)
            CardList = [q for q in CardList if q not in FullList] #Removes the cards from the full card list

            i = 0 #For pulling cards from the full list into packs
            for word in players:
                pack = sortPack(FullList[i:i+15])
                packs.append(pack) #Holds the packs
                i = i+15
                #splices reactions into pack
                packWithReactions = [a + ': ' + b.name for a, b in zip(reactions, pack)] 
                asyncio.create_task(send_pack_message("Here's your first pack! React to select a card. Happy drafting!\n"+str(packWithReactions), word, pack))
            
            asyncio.create_task(pick_timer())
        else:
            asyncio.create_task(message.channel.send('Only admins can start the draft'))

    if ('!cubemetric' in message.content.lower()):
        if 'Admin' in str(message.author.roles): #Only admins can do this command
            if ('attr' in message.content.lower()): 
                asyncio.create_task(message.channel.send(createAttributeDictionary(CardList)))
            elif ('type' in message.content.lower()):
                asyncio.create_task(message.channel.send(createTypeDictionary(CardList)))
            elif ('level' in message.content.lower()):
                asyncio.create_task(message.channel.send(createLevelDictionary(CardList)))     
            elif ('tuner' in message.content.lower()):
                asyncio.create_task(message.channel.send(createTunerDictionary(CardList)))
            elif ('extra' in message.content.lower()):
                asyncio.create_task(message.channel.send(createExtraMessage(CardList)))
            else:
                asyncio.create_task(message.channel.send(createSpreadDictionary(CardList)))


    if ('!mypool' in message.content.lower()):   
        temppool = []
        for word in pool:
            if message.author.name in word:
                temppool.append(word[1])

        if ('attr' in message.content.lower()): 
            asyncio.create_task(message.channel.send(createAttributeDictionary(temppool)))
        elif ('type' in message.content.lower()):
            asyncio.create_task(message.channel.send(createTypeDictionary(temppool)))
        elif ('level' in message.content.lower()):
            asyncio.create_task(message.channel.send(createLevelDictionary(temppool)))     
        elif ('tuner' in message.content.lower()):
            asyncio.create_task(message.channel.send(createTunerDictionary(temppool)))
        elif ('extra' in message.content.lower()):
            asyncio.create_task(message.channel.send(createExtraMessage(temppool)))
        elif ('list' in message.content.lower()):
            asyncio.create_task(message.author.send(temppool))
        else:
            monsters = [card for card in temppool if 'monster' in card.cardType.lower() and 'synchro' not in card.cardType.lower() and 'xyz' not in card.cardType.lower()]
            if(len(monsters) > 0):
                asyncio.create_task(message.channel.send("**Monsters (" + str(len(monsters)) + "):** " + str(monsters)))
            spells = [card for card in temppool if 'spell' in card.cardType.lower()]
            if(len(spells) > 0):
                asyncio.create_task(message.channel.send("**Spells (" + str(len(spells)) + "):** " + str(spells)))        
            traps = [card for card in temppool if 'trap' in card.cardType.lower()]
            if(len(traps) > 0):
                asyncio.create_task(message.channel.send("**Traps (" + str(len(traps)) + "):** " + str(traps)))
            extra = [card for card in temppool if 'xyz' in card.cardType.lower() or 'synchro' in card.cardType.lower()]
            if(len(extra) > 0):
                asyncio.create_task(message.channel.send("**Extra Deck (" + str(len(extra)) + "):** " + str(extra)))


       
        

    #Lists all cards in all pools and says who has each card. Could be useful for detecting cheating if necessary
    if ('!totalpool') in message.content.lower():
        if 'Admin' in str(message.author.roles): #Only admins can do this command
            for thing in pool:
                pooltosend+='%s\n' % thing
            asyncio.create_task(message.author.send(file=discord.File(fp=StringIO(pooltosend),filename="OverallPool.ydk")))
        else:
            asyncio.create_task(message.channel.send('Admins only'))
    
    #Removes people from the draft. Does not use @. For example, !remove fspluver, not !remove @fspluver
    if message.content.lower().strip().startswith('!remove'):
        if 'Admin' in str(message.author.roles): #Only admins can do this command
            y = 0
            for person in players: #This loop removes them from the players list            
                if person.name in message.content:
                    players.remove(players[y])                      
                y = y+1
            for person in playernames: #This loop removes them from the playernames list
                if person in message.content:
                    playernames.remove(person)
                    await message.channel.send(person + " has been removed from the draft.")
        else:           
            await message.channel.send('Only admins can remove players from the draft. If you can no longer play, please let an admin know')

    if message.content.lower().strip().startswith('!reset'):
        if 'Admin' in str(message.author.roles):
            pools = []
            pool = []
            players = []
            playernames = []
            packs = []
            pack = []
            i = 0
            x = 0
            t = 0
            u = 0
            pickNumber = 0
            pooltosend = ""
            import_cube()
            asyncio.create_task(message.channel.send('Draft reset.'))


    if ('!ydk' in message.content.lower()):
        tempidpoolnoextra = []
        tempidpoolextra = []
        tempidpoolside = []
        r = 0

        #extras = [card for card in pack if 'xyz' in card.cardType.lower() or 'synchro' in card.cardType.lower()]

        for word in pool:
            if (word[1].cardType != ("Synchro Monster") or ("Synchro Tuner Monster")) and (word[1].cardType != "XYZ Monster"):                
                if message.author.name in word:
                    tempidpoolnoextra.append(word[1].id) #puts the ids of the main deck cards in a list
            if ('xyz' in word[1].cardType.lower() or 'synchro' in word[1].cardType.lower() and (r < 14)):
                if message.author.name in word:
                    tempidpoolextra.append(word[1].id) #puts the ids of the extra deck cards in a list
                    r = r + 1

            if ('xyz' in word[1].cardType.lower() or 'synchro' in word[1].cardType.lower()) and (r > 13):
                if message.author.name in word:
                    tempidpoolside.append(word[1].id) #puts the ids of the extra deck cards in an overflow side list

        ydkString = ""
        ydkstuff = ["#created by ...", "#main"]
        for listitem in ydkstuff: #puts in the necessary ydk stuff
            ydkString+='%s\n' % listitem
        for listitem in tempidpoolnoextra:
            ydkString+=('%s\n' % listitem) #should put main deck cards in the ydk file
        ydkextraline = ["#extra"]
        for listitem in ydkextraline: #Stuff after this gets put in the extra deck (until side)
            ydkString+='%s\n' % listitem
        for listitem in tempidpoolextra:
            ydkString+='%s\n' % listitem
        ydksidestuff = ["!side"] #Stuff after this gets put in the side
        for listitem in ydksidestuff:
            ydkString+='%s\n' % listitem           
        for listitem in tempidpoolside:
            ydkString+='%s\n' % listitem
        asyncio.create_task(message.author.send(file=discord.File(fp=StringIO(ydkString),filename="YourDraftPool.ydk")))

    if ('!draftdone') in message.content.lower():
        if 'Admin' in str(message.author.roles): #Only admins can do this command
            asyncio.create_task(message.players.send('The draft has concluded! Type "!mypool" to see your cardpool! Good luck in your duels!'))

    if ('!picklog') in message.content.lower():
        #await message.author.send(PickLog) 
        for thing in PickLog:
            logtosend+='%s\n' % thing
        asyncio.create_task(message.author.send(file=discord.File(fp=StringIO(logtosend),filename="PickLog.csv")))    


async def pick_timer():
    global players
    global packs
    global pickNumber
    
    timer = 140 - (8 * pickNumber)
    intialPickNumber = pickNumber
    await asyncio.sleep(timer - 10)
    unpickedPlayers = (x for x in players if len(packs[players.index(x)]) == 15 - intialPickNumber)
    for unpickedPlayer in unpickedPlayers:
        asyncio.create_task(unpickedPlayer.send('Only 10 seconds left to pick!'))
    await asyncio.sleep(10)
    unpickedPlayers = (x for x in players if len(packs[players.index(x)]) == 15 - intialPickNumber)
    for unpickedPlayer in unpickedPlayers:
        asyncio.create_task(unpickedPlayer.send('You automatically picked the first card.'))
        pick(unpickedPlayer, 0, packs[players.index(unpickedPlayer)], True)

async def add_reactions(message, emojis):
    for emoji in emojis:
        asyncio.create_task(message.add_reaction(emoji))

#This exists to allow making the pack messages async.
async def send_pack_message(text, player, pack):
    asyncio.create_task(add_reactions(await player.send(content=text, file=discord.File(fp=imagemanipulator.create_pack_image(pack),filename="image.jpg")), reactions[:len(pack)]))

client.run(BotToken)





