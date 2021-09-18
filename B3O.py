import discord
import asyncio
import json
import os
import csv
from io import StringIO
from draft import Draft
from draft import Player
from draft import pickdata
import cardInfo
from draft import reactions

#Config Loading 
key = None
with open('config.json', 'r') as config_file:
    config_json = json.load(config_file)
    key = config_json['key']

#Constants:
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

drafts = {}
cubes = {}
messagestring = "x"

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
                CardList.append(cardInfo.cardJsonToCardInfo(card))
        cubes[cub] = CardList

import_cubes()
print('Cubes imported')

def createAttributeDictionary(cardList):
    global attributes
    attributeDict = {} 
    for attr in attributes:
        #add an entry to our dictonary with the attribute name and count of cards with that attribute
        attributeDict[attr] = len([card for card in cardList if card.attribute == attr])
    return {"**" + str(k) + "**": v for k, v in sorted(attributeDict.items(), key=lambda item: item[1], reverse=True) if v != 0}
    
def createTypeDictionary(cardList):
    global monsterTypes
    monsterTypeDict = {} 
    for monsterType in monsterTypes:
        #add an entry to our dictonary with the type name and count of cards with that type
        monsterTypeDict[monsterType] = len([card for card in cardList if card.race == monsterType])
    return {"**" + str(k) + "**": v for k, v in sorted(monsterTypeDict.items(), key=lambda item: item[1], reverse=True) if v != 0}

def createLevelDictionary(cardList):
    global levels
    levelDict = {} 
    for level in levels:
        #add an entry to our dictonary with the level and count of cards of that level (not in extra)
        levelDict[level] = len([card for card in cardList if card.level == level and 'synchro' not in card.cardType.lower() and 'xyz' not in card.cardType.lower()])
    return {"**Level " + str(k) + "**": v for k, v in levelDict.items() if v != 0}

def createTunerDictionary(cardList):
    global levels
    tunerDict = {} 
    for level in levels:
        #add an entry to our dictonary with the level and count of tuners with that level
        tunerDict[level] = len([card for card in cardList if card.level == level and 'tuner' in card.cardType.lower() and 'synchro' not in card.cardType.lower()])
    return {"**Level " + str(k) + "**": v for k, v in tunerDict.items() if v != 0}

def createExtraMessage(cardList):
    global levels
    syncDict = {} 
    xyzDict = {} 
    for level in levels:
        #add an entry to our dictonary with the level and count of synchros with that level
        syncDict[level] = len([card for card in cardList if card.level == level and 'synchro' in card.cardType.lower()])
        #add an entry to our dictonary with the level and count of xyz with that level
        xyzDict[level] = len([card for card in cardList if card.level == level and 'xyz' in card.cardType.lower()])
    syncLine = '__Synchros__ ' + str({"**Level " + str(k) + "**": v for k, v in syncDict.items() if v != 0})
    xyzLine = '__XYZ__ ' + str({"**Rank " + str(k) + "**": v for k, v in xyzDict.items() if v != 0})
    return syncLine + '\n' + xyzLine 

#this one's just gonna have to get close enough
def createSpreadDictionary(cardList):
    global cardTypes
    cardTypeDict = {} 
    for cardType in cardTypes:
        #add an entry to our dictonary with the level and count of cards with that card type
        cardTypeDict[cardType] = len([card for card in cardList if cardType.lower() in card.cardType.lower()])
    return {"**" + str(k) + "**": v for k, v in cardTypeDict.items() if v != 0}

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
                    #100 used as a value thats larger than anything we use, so pick will ignore it.
                    cardIndex = reactions.index(str(reaction)) if str(reaction) in reactions else 100
                    player.pick(cardIndex)
                    return

#Responds in chat to messages. 
@client.event
async def on_message(message):
    global drafts
    global cubes

    global messagestring

    #Ignores the bots own messages.
    if message.author == client.user:
        return

    if '!commands' in message.content.lower():
        await message.channel.send("Commands for all users: \n !joindraft: Signs up for an open draft \n !leavedraft: De-registers the player \n !currentplayers: Lists the players currently registered for a draft \n !mypool: Lists the contents of the players draft pool \n !ydk: Exports the users card pool as a YDK file \n \n Commands that require the Host, Moderator, or Admin role: \n !!createdraft: Creates a draft that players can register for. Requires the name of the cube (eg list.cub) \n !!startdraft: Begins the draft - B3O will send packs to registered players \n ")

    if '!joindraft' in message.content.lower():
        #Makes sure there is both a draft in this channel, that draft hasnt started yet, and that the player isnt already in a draft.
        #Might want to split that up for serpeate error messages for the user. 
        currentlyPlaying = []
        for draft in drafts:
            for player in drafts[draft].players:
                if not player.user in currentlyPlaying:
                    currentlyPlaying.append(player.user)
        if message.channel in drafts and drafts[message.channel].currentPack == 0 and message.author not in currentlyPlaying:
            drafts[message.channel].players.append(Player(message.author, drafts[message.channel]))
            await message.channel.send(message.author.name + ' has joined the draft!')
        else:
           await message.channel.send("The draft is already running or you are already in another draft. Try !leavedraft in the channel where you previously drafted.")

    #de-registers a player
    if ('!leavedraft') in message.content.lower():
        if message.channel in drafts:
            for player in drafts[message.channel].players:
                if message.author == player.user:
                    drafts[message.channel].kick(player)
                    await message.channel.send('So sorry to see you leave, ' + message.author.name + '. Catch you for the next one!')

    #Sends the name of all registered players.
    if ('!currentplayers') in message.content.lower():
        if message.channel in drafts:
            await message.channel.send([player.user.name for player in drafts[message.channel].players])
        else:
            await message.channel.send('There is no draft in this channel currently.')

    if ('!!createdraft') in message.content.lower():
        if 'Admin' in str(message.author.roles) or 'Moderator' in str(message.author.roles) or 'Host' in str(message.author.roles): #Only admins, mods or draft hosts can do this command
            for key in cubes.keys():
                if len(message.content.lower().split()) > 1 and key == message.content.lower().split()[1]:
                    drafts[message.channel] = Draft(cubes[key], message.channel)
                    await message.channel.send('Draft created. Players can now join.')
                    messagestring = message.content.lower()
                    return
            await message.channel.send('Cube not found, please enter one from this list next time:\n' + str(list(cubes.keys())))
            
    if ('!!startdraft') in message.content.lower():
        if 'Admin' in str(message.author.roles) or 'Moderator' in str(message.author.roles)or 'Host' in str(message.author.roles): #Only admins, mods or draft hosts can do this command
            #Confirms there is a unstarted draft in the channel.
            if message.channel in drafts and drafts[message.channel].currentPack == 0:
                await message.channel.send('The draft is starting! All players have received their first pack. Good luck!')
                drafts[message.channel].startDraft()
        else:
            await message.channel.send('Only admins or moderators can start the draft')

    if ('!cubemetric' in message.content.lower()):
        if 'Admin' in str(message.author.roles): #Only admins can do this command
            for key in cubes.keys():
                if len(message.content.lower().split()) > 1 and key == message.content.lower().split()[1]:
                    CardList = cubes[key]
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
                    return
            await message.channel.send('Cube not found, please enter one from this list next time:\n' + str(list(cubes.keys())))


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

    #Lists all cards in all pools and says who has each card. Could be useful for detecting cheating if necessary
    if ('!totalpool') in message.content.lower():
        if 'Admin' in str(message.author.roles): #Only admins can do this command
            pooltosend = ''
            for draft in drafts:
                for player in drafts[draft].players:
                    pooltosend += '\n\n' + player.user.name
                    for thing in player.pool:
                        pooltosend +='%s\n' % thing
            asyncio.create_task(message.author.send(file=discord.File(fp=StringIO(pooltosend),filename="OverallPool.ydk")))
        else:
            asyncio.create_task(message.channel.send('Admins only'))
    
    #Removes people from the draft. Does not use @. For example, !remove fspluver, not !remove @fspluver
    if message.content.lower().strip().startswith('!remove'):
        if ('Admin' in str(message.author.roles) or 'Moderator' in str(message.author.roles) or 'Host' in str(message.author.roles)) and message.channel in drafts: #Only admins, mods or draft hosts can do this command and makes sure there is a draft in this channel
            for player in drafts[message.channel].players:
                if player.user.name in message.content:
                    drafts[message.channel].kick(player)
                    await message.channel.send('That player has been removed from the draft.')
        else:           
            await message.channel.send('Only admins or moderators can remove players from the draft. If you yourself would like to leave, use !leavedraft.')

    if ('!grabdata' in message.content.lower()):
        pickdata.append(messagestring)
        file = open('pick_data_file.csv', 'w+', newline = '')
        with file:
            write = csv.writer(file)
            write.writerows(pickdata)
            
        asyncio.create_task(message.author.send(file=discord.File(r'pick_data_file.csv')))


    if ('!ydk' in message.content.lower()):
        for draft in drafts:
            for player in drafts[draft].players:
                if player.user == message.author:
                    tempidpoolnoextra = []
                    tempidpoolextra = []
                    tempidpoolside = []
                    overflow_counter = 0

                    for card in player.pool:
                        if (card.cardType != ("Synchro Monster") or ("Synchro Tuner Monster")) and (card.cardType != "XYZ Monster"):                
                            tempidpoolnoextra.append(card.id) #puts the ids of the main deck cards in a list
                        if ('xyz' in card.cardType.lower() or 'synchro' in card.cardType.lower() and (overflow_counter < 14)):
                            tempidpoolextra.append(card.id) #puts the ids of the extra deck cards in a list
                            overflow_counter = overflow_counter + 1
                        if ('xyz' in card.cardType.lower() or 'synchro' in card.cardType.lower()) and (overflow_counter > 13):
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
        if 'Admin' in str(message.author.roles) or 'Moderator' in str(message.author.roles) or 'Host' in str(message.author.roles): #Only admins, mods or draft hosts can do this command
            await message.channel.send('The draft has concluded! Type "!mypool" to see your cardpool, and !ydk to get an export of your list. Good luck in your duels!')

    #TODO: Low priority. Fix this later.
    # if ('!picklog') in message.content.lower():
    #     if 'Admin' in str(message.author.roles):
    #         #await message.author.send(PickLog) 
    #         for thing in PickLog:
    #             logtosend+='%s\n' % thing
    #         asyncio.create_task(message.author.send(file=discord.File(fp=StringIO(logtosend),filename="PickLog.csv")))    

#Connecting
@client.event
async def on_ready():
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

if not key is None and key != '':
    client.run(key)
else:
    print('Key not configured.')