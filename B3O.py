
import discord
import random
import asyncio
import sys
import json
import os
import os.path
from os import path
import imagemanipulator

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

    #Listing people in the server
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

# not a fan of Python classes, but this is the implemetation I'm doing to allow for a list of just strings as well (for now)
class CardInfo:
    #Left all but name as optional so that we can fall back if that's all we have. Definitely could have more properties in this class, just wanted a good starting point.
    def __init__(self, name, id = -1, cardType="", description = "", imageUrl = ""):
        self.name = name
        self.id = id
        self.cardType = cardType
        self.description = description
        self.imageUrl = imageUrl
    #We're just displaying names for now, but that can change. What these mean is that if you print a list of these, only their names will show.
    def __repr__(self):
        return self.name
    def __str__(self):
        self.name


CardList = []

#import code. Short and sweet.
if (path.exists('list.cub')):
    print('Cube list discovered. Importing.')
    with(open("list.cub", 'r')) as cubeFile:
        #Python makes some things so so easy
        cardDict = json.load(cubeFile)
        #Instantiate a new CardInfo object for each card in the list. Definitely could pull in more info from the JSON - there's a lot there.
        for card in cardDict:
            CardList.append(CardInfo(card['name'], card['id'], card['type'], card['desc'], card['card_images'][0]['image_url']))

else:
    print('Did not find cube list. Falling back to default list.')
    CardNames = [
        'acid trap hole',
        'bad aim',
        'ballista squad',
        'burst rebirth',
        'bottomless trap hole',
        'call of the haunted',
        'ceasefire',
        'compulsory evacuation device',
        'counter gate',
        'dark bribe',
        'dimension slice',
        'dimensional prison',
        'divine wrath',
        'dust tornado',
        'fiendish chain',
        'icarus attack',
        'karma cut',
        'legacy of yata-garasu',
        'liberty at last!',
        'macro cosmos',
        'magic cylinder',
        'magic drain',
        'malevolent catastrophe',
        'metal reflect slime',
        'metalmorph',
        'mirror force',
        'needle ceiling',
        'oasis of dragon souls',
        'ordeal of a traveler',
        'peaceful burial',
        'raigeki break',
        'recall',
        'reckless greed1',
        'reckless greed2',
        'reckless greed3',
        'return from the different dimension',
        'ring of destruction',
        'royal decree',
        'scrap-iron scarecrow',
        'sakuretsu armor',
        'seven tools of the bandit',
        'shadow spell',
        'skill drain',
        'skull lair',
        'solemn judgment',
        'solemn strike',
        'solemn warning',
        'starlight road',
        'storming mirror force',
        'stronghold the moving fortress',
        'the forceful checkpoint',
        'tiki curse',
        'time seal',
        'torrential tribute',
        'trap dustshoot',
        'trap hole',
        'trap stun',
        'ultimate offering',
        'vanitys emptyness',
        'waboku',
        'wall of revealing light',
        'widespread dud',
        'widespread ruin',
        'wiretap',
        'a feather of the phoenix', #Spells starting here
        'allure of darkness',
        'autonomous action unit',
        'axe of despair',
        'axe of fools',
        'back to square one',
        'bait doll',
        'book of eclipse',
        'book of moon',
        'book of taiyou',
        'brain control',
        'burden of the mighty',
        'butterfly dagger elma',
        'card destruction',
        'card trader',
        'change of heart',
        'charge of the light brigade',
        'chicken game',
        'cold wave',
        'creature swap',
        'dark core',
        'dark hole',
        'dark snake syndrome',
        'dark world dealings',
        'dark world lightning',
        'darkworld shackles',
        'dicephoon',
        'double summon',
        'dragged down into the grave',
        'ectoplasmer',
        'enemy controller',
        'exchange',
        'fissure',
        'foolish burial',
        'forbidden chalice',
        'forbidden lance',
        'giant trunade',
        'gold sarcophagus',
        'graceful charity',
        'heavy storm',
        'into the void',
        'kaiser colosseum',
        'last will',
        'level limit area b',
        'lightning vortex',
        'mage power',
        'magical mallet',
        'magical stone excavation',
        'march of the monarchs',
        'megamorph',
        'messenger of peace',
        'mind control',
        'monster gate',
        'monster reborn',
        'my body as a shield',
        'mystical space typhoon',
        'nightmares steelcage',
        'nobleman of crossout',
        'offerings to the doomed',
        'one for one',
        'painful choice',
        'pianissimo',
        'pot of avarice',
        'pot of dichotomy',
        'pot of duality',
        'pot of greed',
        'premature burial',
        'prevention star',
        'reasoning',
        'reinforcement of the army',
        'riryoku',
        'scapegoat',
        'shard of greed',
        'shield crush',
        'shooting star bow ceal',
        'shrink',
        'smashing ground',
        'snatch steal',
        'soul exchange',
        'soul taker',
        'star blast',
        'stray lambs',
        'swords of concealing light',
        'swords of revealing light',
        'the dark door',
        'the shallow grave',
        'tribute to the doomed',
        'twister',
        'upstart goblin',
        'dimension fusion', #Monsters after here
        ]

    for cardName in CardNames:
        CardList.append(CardInfo(cardName))

pools = []
pool = []
players = []
playernames = []
packs = []
pack = []
i = 0
x = 0

#Welcomes people who join the server
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )
#Profanity
#Responses profanity
ProfanityRejFuck = [
    'Hey! Keep the profanity to a minimum, fucking asshole',
    'Please refrain from using the fuck-word in the chat',
    'Profanity violates the rules of the server. Are you fucking illiterate?',
    'https://media.giphy.com/media/GBIzZdF3AxZ6/giphy.gif'
]
ProfanityRejShit = [
    'Listen here you little shit, profanity violates the rules of the server',
    'Think you are hot shit? I will ban your ass if you continue with the language',
    'Shit. /SHit/. Noun: A person or object of little value. For example, people who do not read and follow the rules of the server are shits.'
]

SlurRej = [
    'Slurs are not allowed here. Your message will be reviewed by an admin. https://media.giphy.com/media/Vh2c84FAPVyvvjZJNM/giphy.gif'
]

#is this ever used again?
PackOTraps = random.sample(CardList, 15)

#Responds in chat to messages. 
@client.event
async def on_message(message):
    global packs
    global CardList
    global FullList
    global w
    w = 0
    #printprint(message.content.lower())
    if message.author == client.user:
        return
#Profanity and slurs
    if ('fuck') in message.content.lower():
        await message.channel.send(random.choice(ProfanityRejFuck))
    if ('shit') in message.content.lower():
        await message.channel.send(random.choice(ProfanityRejShit))
    if ('faggot') in message.content.lower():
        await message.channel.send(SlurRej)
    if ('nigger') in message.content.lower():
        await message.channel.send(SlurRej)
    if ('fag') in message.content.lower():
        await message.channel.send(SlurRej)
    if ('nigga') in message.content.lower():
        await message.channel.send(SlurRej)
 
#Draft bot mostly starts here. Previous is just declaring variables and the card list

 #Players - Sign up and check current players

    #Message is someone tries to sign up twice
    if ('!joindraft') in message.content.lower() and message.author in players:
        await message.channel.send('It\'s not possible! No one has the power to be in two draft seats at once!')
    #Registers the player
    if (('!joindraft') in message.content.lower() and packs == []) and (message.author not in players):
        #made it announce name - we might want to look into always sending this to the main server even if draft is joined in PM
        await message.channel.send(message.author.name + ' has joined the draft!')
        players.append(message.author)
        playernames.append(message.author.name)
    #Sends the name of all registered players. Commented out has all the person's info (e.g. Discord ID)    
    if ('!currentplayers') in message.content.lower():
        await message.channel.send(playernames)
        #await message.channel.send(players)
 
        
 #Sends first pack to all players
    if ('!!startdraft') in message.content.lower():
        await message.channel.send('The draft is starting! All players have received their first pack. Good luck!')
        FullList = random.sample(CardList, len(players)*15)
        CardList = [q for q in CardList if q not in FullList] #Removes the cards from the full card list

        i = 0 #For pulling cards from the full list into packs
        for word in players:
            pack = FullList[i:i+14]
            packs.append(pack) #Holds the packs
            i = i+15
            await word.send(file=discord.File(fp=imagemanipulator.create_pack_image(pack),filename="image.jpg"))
            await word.send("Here's your first pack! Use !pick _cardname_ to select a card. Happy drafting!")
            await word.send(pack)


 #Puts picks into pool and removes the pick from the pack
    if message.content.lower().strip().startswith('!pick'):

        #card name, all lower, without trailing or leading spaces
        pickText = message.content.lower().replace('!pick', '').strip()

        #this is my pack, there are many like it, but this one is mine
        workingPack = packs[players.index(message.author)]

        #index of the card in the pack, if it's -1 after we verify it ain't in there
        cardIndex = -1
        try: #this language's iteration syntax confuses me greatly
            cardIndex = next(i for i, c in enumerate(workingPack) if pickText in c.name.lower())
        except:
            cardIndex = -1

        if cardIndex != -1: #Changed from earlier versions so people can only pick from their pack            
            pool.append([message.author.name, workingPack[cardIndex]]) #add card to pool
            workingPack.remove(workingPack[cardIndex]) #remove card from pack
            await message.author.send('---------------Nice pick! It has been added to your pool.---------------')
            await message.author.send('Type !mypool to view your entire cardpool')            

            #Automatically passing the pack
            length = len(packs[0])
            if all (len(y)==length for y in packs): #Works (tested with 2 and 3 players)
                packs = packs[1:] + packs[:1]
                for word in players:
                    await word.send(file=discord.File(fp=imagemanipulator.create_pack_image(packs[players.index(word)]),filename="image.jpg"))
                    await word.send('Your next pack contains:')
                    await word.send(packs[players.index(word)])
                if len(packs[0]) == 0:
                    packs = []

        else:
            await message.author.send("Sorry! That card doesn't look like it's in this pack. Try again.") #Git gud, learn how 2 read   

    if ('!mypool' in message.content.lower()):
        temppool = []
        for word in pool:
            if message.author.name in word:
                temppool.append(word[1].name + " : " + word[1].imageUrl) #could send any combination of card properties in any sort of format
        await message.author.send(temppool)
        

    if ('!ydkmypool' in message.content.lower()):
        tempidpoolnoextra = []
        tempidpoolextra = []
        tempidpoolside = []
        r = 0
        for word in pool:
            if (word[1].cardType != "Synchro Monster") and word[1].cardType != "XYZ Monster":                
                if message.author.name in word:
                    tempidpoolnoextra.append(word[1].id) #puts the ids of the main deck cards in a list
            if ((word[1].cardType == "Synchro Monster") or (word[1].cardType == "XYZ Monster")) and (r < 14):
                if message.author.name in word:
                    tempidpoolextra.append(word[1].id) #puts the ids of the extra deck cards in a list
                    r = r + 1
            if ((word[1].cardType == "Synchro Monster") or (word[1].cardType == "XYZ Monster")) and (r > 13):
                if message.author.name in word:
                    tempidpoolside.append(word[1].id) #puts the ids of the extra deck cards in an overflow side list

        await message.author.send(tempidpoolnoextra + tempidpoolextra) 
        with open('listfile.ydk', 'w') as filehandle:
            ydkstuff = ["#created by ...", "#main"]
            for listitem in ydkstuff: #puts in the necessary ydk stuff
                filehandle.write('%s\n' % listitem)
            for listitem in tempidpoolnoextra:
                filehandle.write('%s\n' % listitem) #should put main deck cards in the ydk file
            ydkextraline = ["#extra"]
            for listitem in ydkextraline: #Stuff after this gets put in the extra deck (until side)
                filehandle.write('%s\n' % listitem)
            for listitem in tempidpoolextra:
                filehandle.write('%s\n' % listitem)
            ydksidestuff = ["!side"] #Stuff after this gets put in the side
            for listitem in ydksidestuff:
                filehandle.write('%s\n' % listitem)           
            for listitem in tempidpoolside:
                filehandle.write('%s\n' % listitem)

    if ('!draftdone') in message.content.lower():
        await message.players.send('The draft has concluded! Type "!mypool" to see your cardpool! Good luck in your duels!')





client.run(BotToken)





