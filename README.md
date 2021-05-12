This is a Penguin Soldiers initiative to create a digital Yu-Gi-Oh cube draft experience through a Discord bot.

# How To Use

## Step 1
Run the cubemaker.py script passing allcards.json as the first argument and your desired cube list (one card per line) as the second. Make sure that both files are in the same directory as cubemaker.py.
* Note that if you desire alternative images from the latest version of your card, you'll want to format it like so: Treeborn Frog|https://www.bbtoystore.com/mm5/yugioh/YU_GLD2EN010_496x705.jpg (no spaces, I'm _lazy_.)
* You can also use this same separator to specifiy alternative card IDs because the geniuses at DuelingBook don't recognize multiple for the cards that have them. i.e. Monster Reborn|83764718
    * The importer is smart enough to figure out which is which if you use both (though name must always come first), as long as there's a | between.
* Once the script has executed, you should have a shiny new .cub file in the directory called list.cub. If any cards could not be found, they will be output in a one card per line list as missed_cards.txt. You'll wanna run the whole thing again once you figure out the spelling/formatting issues of these cards.

## Step 2
Add a discord bot api token to the config.json file. This can be obtained through the discord developer portal. 

## Step 3
Run B30.py. All cubes should be in the cubes/ directory. 

## TODO:
* Make a better system for the pick timer.
* Add a message when a player is kicked.
* Make !leavedraft work from any channel.
* Automatically kick players from a draft after a certain amount of time has past after pack 4 pick 15.
