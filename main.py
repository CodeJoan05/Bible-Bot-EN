import discord, json, re, sqlite3, os
import webserver
from discord.ext import commands

# Import commands

from commands.help import help
from commands.information import information
from commands.versions import versions
from commands.invite import invite
from commands.contact import contact
from commands.setversion import setversion
from commands.search import search
from commands.removeuserdata import removeuserdata
from commands.random import random
from commands.settimezone import settimezone

DISCORD_TOKEN = os.environ['discordkey']

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# Command registration

client.tree.add_command(help)
client.tree.add_command(information)
client.tree.add_command(versions)
client.tree.add_command(invite)
client.tree.add_command(contact)
client.tree.add_command(setversion)
client.tree.add_command(search)
client.tree.add_command(removeuserdata)
client.tree.add_command(random)
client.tree.add_command(settimezone)

# Create a SQLite database

conn = sqlite3.connect('data/user_settings.db')
c = conn.cursor()

# Create a table to store user settings

c.execute('''CREATE TABLE IF NOT EXISTS user_settings
             (user_id INTEGER PRIMARY KEY, default_translation TEXT, timezone TEXT)''')

# Accepted book names

def Find_Bible_References(text):
    with open('resources/booknames/books.json', 'r', encoding='utf-8') as file:
        books = json.load(file)

    pattern = r"\b("
    pattern += "|".join(books.keys())
    pattern += r"|"
    pattern += "|".join([abbr for abbrs in books.values() for abbr in abbrs])
    pattern += r")\s+(\d+)(?::(\d+))?(?:-(\d+))?\b"

    regex = re.compile(pattern, re.IGNORECASE)
    matches = regex.findall(text)

    references = []
    for match in matches:
        full_book_name = next((book for book, abbreviations in books.items() if match[0].lower() in abbreviations), match[0])
        references.append((full_book_name, int(match[1]), int(match[2]) if match[2] else None, int(match[3]) if match[3] else None))

    return references

def Get_Passage(translation, book, chapter, start_verse, end_verse):

    if (start_verse == 0 or end_verse == 0) and start_verse > end_verse:
        return None

    with open(f'resources/bibles/{translation}.json', 'r') as file:
        bible = json.load(file)

    verses = list(filter(lambda x: x['book_name'] == book and x['chapter'] ==
                  chapter and x['verse'] >= start_verse and x['verse'] <= end_verse, bible))

    if len(verses) != 0:
        versesRef = str(verses[0]["verse"])
        if verses[0]["verse"] != verses[len(verses)-1]["verse"]:
            versesRef += "-"+str(verses[len(verses)-1]["verse"])
    else:
        return None

    return {"name": book, "chapter": chapter, "verses_ref": versesRef, "verses": verses}

def Filter_Verses(verse, start_verse, end_verse):
    return verse["verse"] >= start_verse and verse["verse"] <= end_verse

# Information about logging in and activity on Discord

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')
    await client.change_presence(activity=discord.Activity(name='Bible', type=discord.ActivityType.watching))
    try:
        synced = await client.tree.sync()
        print(f"Synchronized {len(synced)} commands")
    except Exception as e:
        print(e)

     # Restore user settings from the database

    c.execute("SELECT * FROM user_settings")
    rows = c.fetchall()
    for row in rows:
        default_translations[row[0]] = row[1]

# Italics font

def format_verse_text(text):
    return re.sub(r'\[([^\]]+)\]', r'*\1*', text)

# Default translation

default_translations = {}

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('/setversion'):
        return

    user_id = message.author.id 

    c.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()

    translation = user_data[1] if user_data else None

    # Command !stats

    if message.content.startswith('!stats'):
        channel_count = sum(len(guild.text_channels) for guild in client.guilds)

        c.execute("SELECT COUNT(*) FROM user_settings")
        users_count = c.fetchone()[0]

        embed = discord.Embed(
            title="Statistics",
            description=f"Server count: **{len(client.guilds)}**\nUser count: **{users_count}**\nChannel count: **{channel_count}**",
            color=12370112
        )
        await message.channel.send(embed=embed)
    
    BibleVerses = Find_Bible_References(message.content)
    if BibleVerses and not user_data:
        embed = discord.Embed(
            title="Set the default Bible translation",
            description='To use the Bible passage search function, you must first set the default Bible translation using the `/setversion` command. To set the default Bible translation, you need to specify a translation abbreviation. All translation abbreviations are available in `/versions`',
            color=12370112)
        await message.channel.send(embed=embed)
    elif translation:
        words = message.content.split()
        last_word = words[-1]

        with open('resources/translations/bible_translations.txt', 'r') as file:
            bible_translations = [line.strip() for line in file]

        if last_word in bible_translations:
            translation = last_word
            message.content = ' '.join(words[:-1])

        await process_message_with_translation(message, translation)

async def process_message_with_translation(message, translation):
    # Processing messages with a specific Bible translation
    pass

    # Sending a message on the given Bible passage(s)

    with open('resources/translations/translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)

    BibleJson = []
    BibleVerses = Find_Bible_References(message.content)

    for verse in BibleVerses:
        if verse[1] is not None and verse[2] is not None and verse[3] is not None:
            BibleJson.append(Get_Passage(
                translation, verse[0], verse[1], verse[2], verse[3]))
        elif verse[1] is not None and verse[2] is not None and verse[3] is None:
            BibleJson.append(Get_Passage(
                translation, verse[0], verse[1], verse[2], verse[2]))

    for Verses in BibleJson:
        if Verses != None and "verses" in Verses:

            header = Verses["name"]+" "+str(Verses["chapter"]) + ":" + Verses["verses_ref"]
            desc = ""

            for v in Verses["verses"]:

                desc += "**(" + \
                    str(v["verse"])+")** "+format_verse_text(v["text"]).replace("\n", " ").replace("  ", " ").strip()+" "
            desc = (desc[:4093] + '...') if len(desc) > 4093 else desc

            embed = discord.Embed(
                title=header, description=desc, color=12370112)
            embed.set_footer(text=translations[translation])
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Search error", description="The verse(s) given does not exist or the Bible translation does not contain the Old or New Testament", color=0xff1d15)
            await message.channel.send(embed=embed)

webserver.keep_alive()
client.run(DISCORD_TOKEN)
