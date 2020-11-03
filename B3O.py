import discord
import random
import asyncio
import json
import os
import imagemanipulator
from io import StringIO

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

#Constants:
BotToken = "NzA3MzI0NjAxNDQ4NzkyMDY0.XrHJbw.mwn0yBiFMXRTBs2W93ePyWwcW64"
client = discord.Client()

#technically there's a LAUGH attribute too, but we don't fux with that
attributes = ['DARK', 'DIVINE', 'EARTH', 'FIRE', 'LIGHT', 'WATER', 'WIND'] 
#yes I know they're strings. It's all strings all the way down. Deal with it.
levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#thought there were way more than 25 of these
monsterTypes = ['Aqua', 'Beast', 'Beast-Warrior', 'Creator God', 'Cyberse', 'Dinosaur', 'Divine-Beast', 'Dragon', 'Fairy', 'Fiend', 'Fish', 'Insect',
'Machine', 'Plant', 'Psychic', 'Pyro', 'Reptile', 'Rock', 'Sea Serpent', 'Spellcaster', 'Thunder', 'Warrior', 'Winged Beast', 'Wyrm', 'Zombie']
#may be comprehensive?
cardTypes = ['Normal Monster', 'Gemini Monster', 'Effect Monster', 'Tuner Monster', 'Spell', 'Trap', 'Synchro', 'XYZ']
reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '0️⃣',
 '🇦', '🇧','🇨','🇩','🇪']

drafts = {}
cubes = {}

#import code. Short and sweet.
def import_cubes():
    global cubes
    cubes = {}
    for cub in os.listdir('cubes'):
        CardList = []
        print('Cube list discovered. Importing.')
        with open('cubes/' + cub) as cubeFile:
            #Python makes some things so so easy
            cardDict = json.load(cubeFile)
            #Instantiate a new CardInfo object for each card in the list. Definitely could pull in more info from the JSON - there's a lot there.
            for card in cardDict:
                CardList.append(CardInfo(card['name'], card['id'], card['type'], card['desc'], card['card_images'][0]['image_url'], card.get('attribute'), card.get('level'), card.get('race')))
        cubes[cub] = CardList

import_cubes()
print('Cubes imported')

def sortPack(pack):
    #this is going to be sloppy shit
    monsters = [card for card in pack if 'monster' in card.cardType.lower() and ('synchro' not in card.cardType.lower() and 'xyz' not in card.cardType.lower())]
    spells = [card for card in pack if 'spell' in card.cardType.lower()]
    traps = [card for card in pack if 'trap' in card.cardType.lower()]
    extras = [card for card in pack if 'xyz' in card.cardType.lower() or 'synchro' in card.cardType.lower()]
    return monsters + spells + traps + extras

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


async def add_reactions(message, emojis):
    for emoji in emojis:
        asyncio.create_task(message.add_reaction(emoji))

#This exists to allow making the pack messages async.
async def send_pack_message(text, player, pack):
    asyncio.create_task(add_reactions(await player.user.send(content=text, file=discord.File(fp=imagemanipulator.create_pack_image(pack),filename="image.jpg")), reactions[:len(pack)]))

#Stores their pool of picked cards and discord user. Store within drafts.
class Player:

    def pick(self, cardIndex):
        #Checking if the card is in the pack.
        if cardIndex <= (len(self.pack) - 1):
            #Making sure they havent already picked
            if len(self.pack) + self.draft.currentPick == 16:
                self.pool.append(self.pack[cardIndex])
                self.pack.pop(cardIndex)
                self.draft.checkPacks()

    def __init__(self, user, draft, pack = None, pool=[],):
        self.draft = draft
        self.pack = pack
        self.pool = pool
        self.user = user
    
    def __repr__(self):
        return self.user

class Timer:

    def start(self):
        #Assures that we havent gone onto the next pick in the draft.
        if self == self.draft.timer:
            print("DO TIMER")

    def __init__(self, draft, legnth=180):
        self.legnth = legnth
        self.draft = draft
        self.start()

class Draft:
    #cube: The cube the pool was created from
    #pool: The cards remaining to be picked from
    #players: The players in the draft. Player class.
    #channel: The channel the draft was started from
    #timer: The timer tracking the picks. Reassign every pick.
    def __init__(self, cube, channel, players = []):
        self.cube = cube
        self.pool = cube
        self.players = players
        self.channel = channel
        self.timer = None
        self.currentPick = -1
        self.currentPack = 0

    def newPacks(self):
        self.currentPick = 1
        self.currentPack += 1
        self.timer = Timer(self) #resets the timer
        self.players.reverse()

        FullList = random.sample(self.pool, len(self.players)*15)
        self.pool = [q for q in self.pool if q not in FullList] #Removes the cards from the full card list

        i = 0 #For pulling cards from the full list into packs
        for player in self.players:
            pack = sortPack(FullList[i:i+15])
            player.pack = pack #Holds the packs
            i = i+15
            #splices reactions into pack
            packWithReactions = [a + ': ' + b.name for a, b in zip(reactions, pack)] 
            asyncio.create_task(send_pack_message("Here's your first pack! React to select a card. Happy drafting!\n"+str(packWithReactions), player, pack))
        
    def rotatePacks(self):
        self.currentPick += 1
        self.timer = Timer(self) #resets the timer

        #Creates a list of all the packs
        packs = [player.pack for player in self.players]
        for player in self.players:
            #Gives the player the next pack in the list. If that would be out of bounds give them the first pack.
            player.pack = packs[0] if (packs.index(player.pack) + 1) >= len(packs) else packs[packs.index(player.pack) + 1]
            #splices reactions into pack
            packWithReactions = [a + ': ' + b.name for a, b in zip(reactions, player.pack)] 
            asyncio.create_task(send_pack_message('Your next pack: \n\n'+str(packWithReactions), player, player.pack))
    
    #Decides if its time to rotate or send a new pack yet.
    def checkPacks(self):
        #Checks if every player has picked.
        if len([player for player in self.players if len(player.pack) + player.draft.currentPick == 16]) == 0:
            if self.currentPick < 15:
                self.rotatePacks()
            elif self.currentPack >= 4:
                print('TODO FINISH THIS')
                #Finish draft
            else:
                self.newPacks()
    
    def startDraft(self):
        self.newPacks()

#Welcomes people who join the server
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@client.event
async def on_reaction_add(reaction, user):
    global drafts

    #checks to make sure there are packs, this is a DM, and the player is in the draft
    if not "DMChannel" in str(type(reaction.message.channel)):
        return    

    for draft in drafts:
        for player in drafts[draft].players:
            if user == player.user:
                    cardIndex = reactions.index(str(reaction)) if str(reaction) in reactions else 100
                    player.pick(cardIndex)

#Responds in chat to messages. 
@client.event
async def on_message(message):
    global drafts
    global cubes

    #Ignores the bots own messages.
    if message.author == client.user:
        return
 
    # Useful for finding channel ids to 
    # print(message.channel.name)
    # print(message.channel.guild)
    # print(message.channel.id)
    # print('--------------------------')

 #Players - Sign up and check current players

    if '!joindraft' in message.content.lower():
        #Makes sure there is both a draft in this channel, that draft hasnt started yet, and that the player isnt already in it.
        #Might want to split that up for serpeate error messages for the user.
        if message.channel in drafts and drafts[message.channel].currentPack == 0 and message.author not in [player.user for player in drafts[message.channel].players]:
            drafts[message.channel].players.append(Player(message.author, drafts[message.channel]))
            await message.channel.send(message.author.name + ' has joined the draft!')
        else:
           await message.channel.send("The draft has not been reset since it was last fired. Please join after it gets reset.")

    #de-registers a player
    if ('!leavedraft') in message.content.lower():
        if message.channel in drafts:
            for player in drafts[message.channel].players:
                if message.author == player.user:
                    drafts[message.channel].players.remove(player)
                    await message.channel.send('So sorry to see you leave, ' + message.author.name + '. Catch you for the next one!')

    #Sends the name of all registered players.
    if ('!currentplayers') in message.content.lower():
        if message.channel in drafts:
            await message.channel.send([player.user.name for player in drafts[message.channel].players])
        else:
            await message.channel.send('There is no draft in this channel currently.')

    if ('!!createdraft') in message.content.lower():
        if 'Admin' in str(message.author.roles) or 'Moderator' in str(message.author.roles): #Only admins/mods can do this command
            drafts[message.channel] = Draft(list(cubes.values())[0], message.channel)

    if ('!!startdraft') in message.content.lower():
        if 'Admin' in str(message.author.roles) or 'Moderator' in str(message.author.roles): #Only admins/mods can do this command
            #Confirms there is a unstarted draft in the channel.
            if message.channel in drafts and drafts[message.channel].currentPack == 0:
                await message.channel.send('The draft is starting! All players have received their first pack. Good luck!')
                drafts[message.channel].startDraft()
        else:
            await message.channel.send('Only admins or moderators can start the draft')

    #TODO: Low priority to get this up to date.
    # if ('!cubemetric' in message.content.lower()):
    #     if 'Admin' in str(message.author.roles): #Only admins can do this command
    #         if ('attr' in message.content.lower()): 
    #             asyncio.create_task(message.channel.send(createAttributeDictionary(CardList)))
    #         elif ('type' in message.content.lower()):
    #             asyncio.create_task(message.channel.send(createTypeDictionary(CardList)))
    #         elif ('level' in message.content.lower()):
    #             asyncio.create_task(message.channel.send(createLevelDictionary(CardList)))     
    #         elif ('tuner' in message.content.lower()):
    #             asyncio.create_task(message.channel.send(createTunerDictionary(CardList)))
    #         elif ('extra' in message.content.lower()):
    #             asyncio.create_task(message.channel.send(createExtraMessage(CardList)))
    #         else:
    #             asyncio.create_task(message.channel.send(createSpreadDictionary(CardList)))


    if ('!mypool' in message.content.lower()):
        for draft in drafts:
            for player in drafts[draft].players:
                if player.user == message.author:
                    temppool = player.pool[:]
                    if ('attr' in message.content.lower()): 
                        await message.channel.send(createAttributeDictionary(temppool))
                    elif ('type' in message.content.lower()):
                        await message.channel.send(createTypeDictionary(temppool))
                    elif ('level' in message.content.lower()):
                        await message.channel.send(createLevelDictionary(temppool))
                    elif ('tuner' in message.content.lower()):
                        await message.channel.send(createTunerDictionary(temppool))
                    elif ('extra' in message.content.lower()):
                        await message.channel.send(createExtraMessage(temppool))
                    elif ('list' in message.content.lower()):
                        await message.author.send(temppool)
                    else:
                        monsters = [card for card in temppool if 'monster' in card.cardType.lower() and 'synchro' not in card.cardType.lower() and 'xyz' not in card.cardType.lower()]
                        if(len(monsters) > 0):
                            #Async so they dont stall the other messages waiting for the response from the server
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

    #TODO: Need to rework
    #Lists all cards in all pools and says who has each card. Could be useful for detecting cheating if necessary
    # if ('!totalpool') in message.content.lower():
    #     if 'Admin' in str(message.author.roles): #Only admins can do this command
    #         for thing in pool:
    #             pooltosend+='%s\n' % thing
    #         asyncio.create_task(message.author.send(file=discord.File(fp=StringIO(pooltosend),filename="OverallPool.ydk")))
    #     else:
    #         asyncio.create_task(message.channel.send('Admins only'))
    
    #Removes people from the draft. Does not use @. For example, !remove fspluver, not !remove @fspluver
    if message.content.lower().strip().startswith('!remove'):
        if ('Admin' in str(message.author.roles) or 'Moderator' in str(message.author.roles)) and message.channel in drafts: #Only admins/mods can do this command and makes sure there is a draft in this channel
            for player in drafts[message.channel].players:
                if player.user.name in message.content:
                    drafts[message.channel].players.remove(player)
        else:           
            await message.channel.send('Only admins or moderators can remove players from the draft. If you yourself would like to leave, use !leavedraft.')

    if message.content.lower().strip().startswith('!reset'):
        if 'Admin' in str(message.author.roles) or 'Moderator' in str(message.author.roles):
            drafts = {}
            import_cubes()
            await message.channel.send('Bot reset.')


    if ('!ydk' in message.content.lower()):
        for draft in drafts:
            for player in drafts[draft].players:
                if player.user == message.author:
                    tempidpoolnoextra = []
                    tempidpoolextra = []
                    tempidpoolside = []
                    r = 0 #Not 100% sure what "r" is supposed to mean here. But this variable is used for the extra deck overflow counter.

                    for card in player.pool:
                        if (card.cardType != ("Synchro Monster") or ("Synchro Tuner Monster")) and (card.cardType != "XYZ Monster"):                
                            tempidpoolnoextra.append(card.id) #puts the ids of the main deck cards in a list
                        if ('xyz' in card.cardType.lower() or 'synchro' in card.cardType.lower() and (r < 14)):
                            tempidpoolextra.append(card.id) #puts the ids of the extra deck cards in a list
                            r = r + 1
                        if ('xyz' in card.cardType.lower() or 'synchro' in card.cardType.lower()) and (r > 13):
                            tempidpoolside.append(card.id) #puts the ids of the extra deck cards in an overflow side list

                    #This whole block formats their cards for the .ydk format
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
        if 'Admin' in str(message.author.roles) or 'Moderator' in str(message.author.roles): #Only admins/mods can do this command
            await message.channel.send('The draft has concluded! Type "!mypool" to see your cardpool, and !ydk to get an export of your list. Good luck in your duels!')

    #TODO: Low priority. Fix this later.
    # if ('!picklog') in message.content.lower():
    #     if 'Admin' in str(message.author.roles):
    #         #await message.author.send(PickLog) 
    #         for thing in PickLog:
    #             logtosend+='%s\n' % thing
    #         asyncio.create_task(message.author.send(file=discord.File(fp=StringIO(logtosend),filename="PickLog.csv")))    

#Need to transfer this logic into the draft class. Its pretty buggy atm, should probably just be redone completely.
# async def pick_timer():
#     global players
#     global packs
#     global pickNumber
    
#     timer = 140 - (8 * pickNumber)
#     intialPickNumber = pickNumber
#     await asyncio.sleep(timer - 10)
#     unpickedPlayers = (x for x in players if len(packs[players.index(x)]) == 15 - intialPickNumber)
#     for unpickedPlayer in unpickedPlayers:
#         asyncio.create_task(unpickedPlayer.send('Only 10 seconds left to pick!'))
#     await asyncio.sleep(10)
#     unpickedPlayers = (x for x in players if len(packs[players.index(x)]) == 15 - intialPickNumber)
#     for unpickedPlayer in unpickedPlayers:
#         asyncio.create_task(unpickedPlayer.send('You automatically picked the first card.'))
#         pick(unpickedPlayer, 0, packs[players.index(unpickedPlayer)], True)

#Connecting
@client.event
async def on_ready():
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

client.run(BotToken)





