import sqlite3
from urllib.request import urlopen
import os
import json
from cardInfo import cardJsonToCardInfo

#Constants
databasePath = "images.db"

#Use images table (id, image, image_small)
connection = sqlite3.connect(databasePath)
cursor = connection.cursor()

#Takes a few minutes to run depending on cube size.
def cache_all_images():
    print('Cacheing all images...')
    for cub in os.listdir('cubes'):
        cubeJson = json.load(open('cubes/' + cub, "r"))
        for card in cubeJson:
            print(card["name"])
            cache_card_images(cardJsonToCardInfo(card))

#Downloads both the large and small card images and writes them as BLOBs to the database file.
def cache_card_images(card):
    print('Cacheing ' + str(card.id) + '...')
    image = urlopen(get_image_url(card)).read()
    #Small images currently unused.
    smallImage = image
    cursor.execute('INSERT INTO images VALUES (?, ?, ?)', [card.id, image, smallImage])
    connection.commit()

def get_image_url(card):
    return card.imageUrl

def get_small_image_url(card):
    return card.imageUrl
    #Small images are currently unused.
    #return [card for card in cubeJson if card["id"] == card.id][0]["card_images"][0]["image_url_small"]

def get_image(card):
    result = cursor.execute('SELECT image FROM images WHERE id = ?', [card.id]).fetchone()
    if result is None:
        cache_card_images(card)
        return get_image(card)
    else:
        return result[0]

def get_small_image(card):
    result = cursor.execute('SELECT image_small FROM images WHERE id = ?', [card.id]).fetchone()
    if result is None:
        cache_card_images(card)
        return get_small_image(card)
    else:
        return result
