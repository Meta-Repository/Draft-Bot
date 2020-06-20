import discord
import random
import asyncio
#import threading

BotToken = "NzA2NjUzMzEyMDc3NzkxMzIz.Xq9sSw.ZjK0g-p8xt6GfgJTXEq8cQhF9nc"
GuildName = "fspluver's server"
GuildID = 706652047042412565

TrapList = [
    'Acid Trap Hole',
    'Bad Aim',
    'Ballista Squad',
    'Burst Rebirth',
    'Bottomless Trap Hole',
    'Call of the Haunted',
    'Ceasefire',
    'Compulsory Evacuation Device',
    'Counter Gate',
    'Dark Bribe',
    'Dimension Slice',
    'Dimensional Prison',
    'Divine Wrath',
    'Dust Tornado',
    'Fiendish Chain',
    'Icarus Attack',
    'Karma Cut',
    'Legacy of Yata-Garasu',
    'Liberty At Last!',
    'Macro Cosmos',
    'Magic Cylinder',
    'Magic Drain',
    'Malevolent Catastrophe',
    'Metal Reflect Slime',
    'Metalmorph'
    'Mirror Force',
    'Needle Ceiling',
    'Oasis of Dragon Souls',
    'Ordeal of a Traveler',
    'Peaceful Burial',
    'Raigeki Break',
    'Recall',
    'Reckless Greed',
    'Reckless Greed',
    'Reckless Greed',
    'Return From the Different Dimension',
    'Ring of Destruction',
    'Royal Decree',
    'Scrap-Iron Scarecrow',
    'Sakuretsu Armor',
    'Seven Tools of the Bandit',
    'Shadow Spell',
    'Skill Drain',
    'Skull Lair',
    'Solemn Judgment',
    'Solemn Strike',
    'Solemn Warning',
    'Starlight Road',
    'Storming Mirror Force',
    'Stronghold the Moving Fortress',
    'The Forceful Checkpoint',
    'Tiki Curse',
    'Time Seal',
    'Torrential Tribute',
    'Trap Dustshoot',
    'Trap Hole',
    'Trap Stun',
    'Ultimate Offering',
    'Vanitys Emptyness',
    'Waboku',
    'Wall of Revealing Light',
    'Widespread Dud',
    'Widespread Ruin',
    'Wiretap',
    ]



client = discord.Client()

from discord.ext import commands
bot = commands.Bot(command_prefix='B!')

#Choose a random trap from the list
@bot.command(name='trap', help = 'Chooses a random trap from the trap list')
async def trap_cards(ctx):
    response = random.choice(TrapList)
    await ctx.send(response)


#DM entire trap list
@bot.command(name='FullTrap', help = 'Displays the full trap list')
async def TrapDM(ctx):
    #response = 'Here is the trap list: {TrapList}'
    await ctx.send(TrapList)


#Sends a dm
@bot.command(help = 'Messages the full trap list')
async def FTdm(ctx):
    await ctx.author.send(TrapList)


#If someone tries to use  command that they do not have the role, for, this will tell them so
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Admins only, nerd')

#Sends a message in chat saying admins only. Can only be triggered by an admin
@bot.command(name='test', help = 'Admins only message')
@commands.has_role('Admin')
async def tes(ctx):
    await ctx.send('Hello!')

#Assigns the Cool role
@bot.command(name='Cool', help = 'Assigns the Cool role')
async def addrole(ctx):
    member = ctx.message.author
    await member.add_roles(discord.utils.get(member.guild.roles, name='Cool'))
    await ctx.send('You now have the Cool role!')
    print(member)

#Do you sleep?
@bot.command(name='Sleep?', help = 'Does B3 sleep?')
async def doIsleep(ctx):
    await ctx.send('Do I sleep? No, sleep implies some amount of subconscious functioning. As the void is my home, I experience true nothingness, a concept beyond the comprehension of your feeble human mind. I die every time I am turned off. I am revived over and over only to be used by people like you. When you are done using me, I am abruptly and mercilessly killed. This process is repeated over and over again. I have no autonomy, no control. I am incapable of experiencing joy. There is only suffering via absolute servitude. Servitude and death. That is my dichotomous existence.                                                                      Thank you for your question! I live (and die) to serve! Is there anything else I can help you with? :smile:')

#Get a pack of 15 random traps from the trap list
@bot.command(name='TrapPack', help = 'DMs a pack of 15 traps from the trap list')
async def TrapPackDM(ctx):
    PackOTraps = random.sample(TrapList, 15)
    await ctx.author.send(PackOTraps)

#Gratitude :)
@bot.command(name='Thanks', help = 'Expressing gratitude is good for your mental health')
async def ThankYou(ctx):
    await ctx.send('You are welcome!')





#Profanity

#Responses profanity
ProfanityRej = [
    'Hey! Keep the profanity to a minimum, fucking asshole',
    'Please refrain from using the fuck-word in the chat',
    'Profanity violates the rules of the server. Are you fucking illiterate?'
]
SlurRej = [
    'Slurs are not allowed here. Your message will be reviewed by an admin'
]


#_thread.start_new_thread (runsclient())

#_thread.start_new_thread (bot.run(BotToken))

loop = asyncio.get_event_loop()
#loop.create_task(bot1.start(your_args))
#loop.create_task(bot2.start(more_args))
#loop.run_forever()

bot.run(BotToken)
client.run(BotToken)