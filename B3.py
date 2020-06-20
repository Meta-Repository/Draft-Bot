
import discord
import random
BotToken = "NzA2NjUzMzEyMDc3NzkxMzIz.Xq9sSw.ZjK0g-p8xt6GfgJTXEq8cQhF9nc"
GuildName = "fspluver's server"
GuildID = 706652047042412565
client = discord.Client()

from discord.ext import commands
bot = commands.Bot(command_prefix='B!')

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

#Welcomes people who join the server
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )
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
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if (('fuck' or 'Fuck') or ('FUCK')) in message.content.lower():
        await message.channel.send(random.choice(ProfanityRej))
    if ('faggot' or 'Faggot') in message.content.lower():
        await message.channel.send(SlurRej)
    if ('nigger' or 'Nigger') in message.content.lower():
        await message.channel.send(SlurRej)
    if ('fag' or 'nigga') in message.content.lower():
        await message.channel.send(SlurRej)

@bot.command(name='trap')
async def trap_cards(ctx):
    TrapList = [
        'Mirror Force',
        'Ring of Destruction',
        'Sakuretsu Armor',
        'Reinforcements',
    ]

    response = random.choice(TrapList)
    await ctx.send(response)

bot.run(BotToken)
client.run(BotToken)




