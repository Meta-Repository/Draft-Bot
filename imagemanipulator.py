from PIL import Image
from io import BytesIO
import imagemanager

#Constants
imageWidth = 421
imageHeight = 614

def create_pack_image(pack):
    images = []
    for card in pack:
        images.append(Image.open(BytesIO(imagemanager.get_image(card.id))))
    #Displays up to 15 cards
    image = Image.new("RGB", (imageWidth*5,imageHeight*3))
    for y in range(0,imageHeight*3,imageHeight):
        for x in range(0,imageWidth*5,imageWidth):
            if len(images) == 0:
                break
            image.paste(images[0], (x,y))
            del images[0]
    output = BytesIO()
    image.save(output, format="JPEG")
    output.seek(0)
    return output