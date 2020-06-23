import sys
import json
import os
import os.path
from os import path
import imagemanager

#takes a filepath expected to be newline delimited list of desired cards
def read_cube_list(filepath):
    return open(filepath).read().splitlines()

#takes a filepath expected to be JSON file of yugioh cards and reads them to a dictionary
def read_card_list(filepath):
    with open(filepath, "r") as f:
        cardDict = json.load(f)
        return cardDict["data"]

#I don't care to be safer than this. If it blows up, that's on you.
allCards = read_card_list(sys.argv[1])
cubeList = read_cube_list(sys.argv[2])

#These are what we're gonna be exporting
cubeCards = []
unidentifiedCards = []

#heart of it
for name in cubeList:
    #grabs any alt image URLs
    nameComponents = name.split('|')
    #I miss .Where()
    match = [card for card in allCards if card['name'].lower() == nameComponents[0].lower().strip()]
    #ya messed up. We print it and slap it to the list of names to export.
    if not match:
        print('Could not find card ' + name.strip() + '. Please check spelling.')
        unidentifiedCards.append(name)
    #hey good job it's a card
    else:    
        #technically speaking, match could have multiple elements. We only ever expect it to have one.
        matchedCard = match[0]
        #if we were given an alternate URL, we use that
        imageUrl = matchedCard['card_images'][0]['image_url'] if len(nameComponents) == 1 else nameComponents[1]
        #Python string formatting is niceish
        print('Name: %s | Id: %s | Type: %s | Image Link: %s \n' % (matchedCard['name'], matchedCard['id'], matchedCard['type'], imageUrl))
        #set the URL of the object we want to export to JSON
        matchedCard['card_images'][0]['image_url'] = imageUrl
        #add the card to the list of things we're gonna export
        cubeCards.append(matchedCard)

#if there are four lines in script that scream "I'm not sure how Python works, and do not care to find out.", these are it.
if(path.exists("list.cub")):
    os.remove('list.cub')
if(path.exists("missed_cards.txt")):
    os.remove('missed_cards.txt')

#dump the now defined cube list to a new JSON file
with open("list.cub", "w") as export_list:
    json.dump(cubeCards, export_list)

#dump any and all unfound card names to a new text file
if(unidentifiedCards):
    with open("missed_cards.txt", 'w') as whoops:
        for missedCard in unidentifiedCards:
            whoops.write(missedCard + '\n')

#Download all card images
imagemanager.cache_all_images()