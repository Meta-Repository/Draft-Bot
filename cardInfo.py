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

def cardJsonToCardInfo(card):
    return CardInfo(card['name'], card['id'], card['type'], card['desc'], card['card_images'][0]['image_url'], card.get('attribute'), card.get('level'), card.get('race'))
