import sqlite3
from urllib.request import urlopen
import json

#Constants
databasePath = "images.db"
cubePath = "list.cub"
cubeJson = json.load(open(cubePath, "r"))

#Use images table (id, image, image_small)
connection = sqlite3.connect(databasePath)
cursor = connection.cursor()

#Takes a few minutes to run depending on cube size.
def cache_all_images():
    print('Cacheing all images...')
    for card in cubeJson:
        print(card["name"])
        cache_card_images(card["id"])

#Downloads both the large and small card images and writes them as BLOBs to the database file.
def cache_card_images(cardId):
    print('Cacheing ' + str(cardId) + '...')
    image = urlopen(get_image_url(cardId)).read()
    smallImage = urlopen(get_small_image_url(cardId)).read()
    cursor.execute('INSERT INTO images VALUES (?, ?, ?)', [cardId, image, smallImage])
    connection.commit()

def get_image_url(cardId):
    #This feels like magic. First brackets creates a list of all images where the id matches. Second chooses only the first entry.
    return [card for card in cubeJson if card["id"] == cardId][0]["card_images"][0]["image_url"]

def get_small_image_url(cardId):
    return [card for card in cubeJson if card["id"] == cardId][0]["card_images"][0]["image_url_small"]

def get_image(cardId):
    result = cursor.execute('SELECT image FROM images WHERE id = ?', [cardId]).fetchone()
    if result is None:
        cache_card_images(cardId)
        return get_image(cardId)
    else:
        return result[0]

def get_small_image(cardId):
    result = cursor.execute('SELECT image_small FROM images WHERE id = ?', [cardId]).fetchone()
    if result is None:
        cache_card_images(cardId)
        return get_small_image(cardId)
    else:
        return result
