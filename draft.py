import asyncio
import random
import discord
import imagemanipulator
import math

#Constants
reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '0️⃣', '🇦', '🇧','🇨','🇩','🇪']

#Starting with a list that will hold pick data
pickdata = [['Name', 'Pick', 'User', 'Cube']]

#Stores their pool of picked cards and discord user. Store within drafts.
class Player:

    def hasPicked(self):
        return not (len(self.pack) + self.draft.currentPick == 16)

    def pick(self, cardIndex):
        #Checking if the card is in the pack.
        if cardIndex <= (len(self.pack) - 1):
            #Making sure they havent already picked
            if not self.hasPicked():
                asyncio.create_task(self.user.send('You have picked ' + self.pack[cardIndex].name + '.'))
                self.pool.append(self.pack[cardIndex])
                
                temppickdata = []
                tempcardname = str(self.pack[cardIndex].name) #Adding the card name to the temppickdata vector to append to file

                self.pack.pop(cardIndex)
                self.draft.checkPacks()

                tempcardname = tempcardname.replace(',', " ") #Removing commas for CSV purposes
                temppickdata.append(tempcardname)
                temppickdata.append(len(self.pack)) #Adding pick #
                temppickdata.append(self.user) #Adding the person who picked
                temppickdata.append('x') #Noting which cube was used. Will add once I get this working
                pickdata.append(temppickdata)
                

    def __init__(self, user, draft):
        self.draft = draft
        self.pack = None
        self.pool = []
        self.user = user
    
    def __repr__(self):
        return self.user

class Timer:

    async def start(self):
        #Scales the legnth of the timer to the size of the pack.
        #Mathematica:
        #In: NSolve[{a*Log[10, b*5] == 150, a*Log[10, b*19] == 30}, {a, b}]
        #Out: {{a -> -206.974, b -> 0.0376965}}
        #Pick + 4
        newLegnth = -206.974*math.log10(0.0376965*(self.draft.currentPick + 4))
        self.legnth = round(newLegnth)
        #A little bit of psych here. Tell them there is shorter left to pick than there really is.
        await asyncio.sleep(self.legnth - 12)
        #Return if this thread is now a outdated and no longer needed timer.
        if self != self.draft.timer:
            return
        for player in self.draft.players:
            if not player.hasPicked():
                asyncio.create_task(player.user.send('Hurry! Only ten seconds left to pick!'))
        await asyncio.sleep(12)
        if self != self.draft.timer:
            return
        players = [player for player in self.draft.players if not player.hasPicked()]
        for player in players:
            if not player.hasPicked() and self == self.draft.timer:
                if self.draft.currentPick == 15 and self.draft.currentPack != 4:
                    asyncio.create_task(player.user.send('Ran out of time. You have been kicked for missing the final pick in a pack.'))
                    self.draft.kick(player)
                else:
                    asyncio.create_task(player.user.send('Ran out of time. You have automatically picked the first card in the pack.'))
                    player.pick(0)

    def __init__(self, draft, legnth=150):
        self.legnth = legnth
        self.draft = draft
        asyncio.create_task(self.start())

class Draft:
    #cube: The cube the pool was created from
    #pool: The cards remaining to be picked from
    #players: The players in the draft. Player class.
    #channel: The channel the draft was started from
    #timer: The timer tracking the picks. Reassign every pick.
    def __init__(self, cube, channel):
        self.cube = cube[:]
        self.pool = cube[:]
        self.players = [] #Was orginally a default value. Created very complicated errors with underlying objects and references in the Python interpter. Wasn't being used at the time anyway.
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
            asyncio.create_task(send_pack_message("Here's your #" + str(self.currentPack) + " pack! React to select a card. Happy drafting!\n"+str(packWithReactions), player, pack))
        
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
        if len([player for player in self.players if not player.hasPicked()]) == 0:
            if self.currentPick < 15:
                self.rotatePacks()
            elif self.currentPack >= 4:
                for player in self.players:
                    asyncio.create_task(player.user.send('The draft is now finished. Use !ydk or !mypool to get started on deckbuilding. Your draft organizer should be posting a bracket soon.'))
            else:
                self.newPacks()
    
    def startDraft(self):
        self.newPacks()

    def kick(self, player):
        #A little worried about how we currently call this from the seperate timer thread from all the other main logic.
        #Drops the players pack into the void currently. 
        self.players.remove(player)
        self.checkPacks()

def sortPack(pack):
    monsters = [card for card in pack if 'monster' in card.cardType.lower() and ('synchro' not in card.cardType.lower() and 'xyz' not in card.cardType.lower())]
    spells = [card for card in pack if 'spell' in card.cardType.lower()]
    traps = [card for card in pack if 'trap' in card.cardType.lower()]
    extras = [card for card in pack if 'xyz' in card.cardType.lower() or 'synchro' in card.cardType.lower()]
    return monsters + spells + traps + extras

async def add_reactions(message, emojis):
    for emoji in emojis:
        asyncio.create_task(message.add_reaction(emoji))

#This exists to allow making the pack messages async.
async def send_pack_message(text, player, pack):
    asyncio.create_task(add_reactions(await player.user.send(content=text, file=discord.File(fp=imagemanipulator.create_pack_image(pack),filename="image.jpg")), reactions[:len(pack)]))