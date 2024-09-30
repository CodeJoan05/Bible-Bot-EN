import discord, datetime, asyncio, pytz, json, sqlite3, os, re
from discord.ext import commands
from discord import app_commands
from typing import List
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

conn = sqlite3.connect('data/user_settings.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS user_settings
             (user_id INTEGER PRIMARY KEY, default_translation TEXT, timezone TEXT)''')

# Italics font

def format_verse_text(text):
    return re.sub(r'\[([^\]]+)\]', r'*\1*', text)

# Function to create chapter and verse index based on the file of a given Bible translation

def create_bible_index(translation: str):
    bible_index = {}

    bible_path = f'resources/bibles/{translation}.json'
    if not os.path.exists(bible_path):
        return None

    with open(bible_path, 'r', encoding='utf-8') as file:
        bible_data = json.load(file)

    for verse in bible_data:
        book_name = verse['book_name']
        chapter = verse['chapter']
        verse_number = verse['verse']

        if book_name not in bible_index:
            bible_index[book_name] = {}

        if chapter not in bible_index[book_name]:
            bible_index[book_name][chapter] = []

        bible_index[book_name][chapter].append(verse_number)

    return bible_index

# Autocomplete function for book names

async def autocomplete_books(interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice]:
    user_id = interaction.user.id

    c.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()

    if not user_data or not user_data[1]:
        return []

    translation = user_data[1]
    user_timezone = user_data[2]

    bible_path = f'resources/bibles/{translation}.json'
    if not os.path.exists(bible_path):
        return []

    with open(bible_path, 'r', encoding='utf-8') as file:
        bible_data = json.load(file)

    book_names = {verse['book_name'] for verse in bible_data}

    return [
        discord.app_commands.Choice(name=book, value=book)
        for book in book_names if current.lower() in book.lower()
    ][:15]

# Autocomplete function for chapters

async def autocomplete_chapter(interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice]:
    book = interaction.namespace.book
    user_id = interaction.user.id

    c.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()

    if not user_data or not user_data[1]:
        return []

    translation = user_data[1]
    user_timezone = user_data[2]

    bible_index = create_bible_index(translation)
    if not bible_index or book not in bible_index:
        return []

    chapters = list(bible_index[book].keys())

    return [
        discord.app_commands.Choice(name=str(chapter), value=str(chapter))
        for chapter in chapters if current.isdigit() and current in str(chapter)
    ][:15]

# Autocomplete function for verses

async def autocomplete_verse(interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice]:
    book = interaction.namespace.book
    chapter = interaction.namespace.chapter
    user_id = interaction.user.id

    c.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()

    if not user_data or not user_data[1]:
        return []

    translation = user_data[1]
    user_timezone = user_data[2]

    bible_index = create_bible_index(translation)
    if not bible_index or book not in bible_index or int(chapter) not in bible_index[book]:
        return []

    verses = bible_index[book][int(chapter)]

    return [
        discord.app_commands.Choice(name=str(verse), value=str(verse))
        for verse in verses if current.isdigit() and current in str(verse)
    ][:15]

@client.tree.command(name="dailyverse", description="Displays the verse(s) of the day from the Bible")
@app_commands.autocomplete(book=autocomplete_books, chapter=autocomplete_chapter, start_verse=autocomplete_verse, end_verse=autocomplete_verse)
@app_commands.describe(book="Book name", chapter="Chapter number", start_verse="Start verse number", end_verse="End verse number", hour="Time of the message sent (in HH:MM format)")
async def dailyverse(interaction: discord.Interaction, book: str, chapter: int, start_verse: int, end_verse: int, hour: str = None):
    await interaction.response.defer()
   
    user_id = interaction.user.id

    c.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()
   
    if not user_data or not user_data[1]:
        embed = discord.Embed(
            title="Set the default Bible translation",
            description='To use the Bible passage search function, you must first set the default Bible translation using the `/setversion` command. To set the default Bible translation, you need to specify a translation abbreviation. All translation abbreviations are available in `/versions`',
            color=12370112)
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    translation = user_data[1]
    user_timezone = user_data[2]
    
    if not user_timezone:
        embed = discord.Embed(
            title="Set your time zone",
            description="Please set your time zone using the `/settimezone` command",
            color=12370112
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    with open(f'resources/bibles/{translation}.json', 'r') as file:
        bible = json.load(file)

    with open('resources/translations/translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)

    selected_verses = [
        verse for verse in bible
        if verse['book_name'] == book and verse['chapter'] == chapter
        and start_verse <= verse['verse'] <= end_verse
    ]

    if not selected_verses:
        error_embed = discord.Embed(
            title="Error",
            description="The passage was not found",
            color=0xff1d15
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    title = f"{book} {chapter}:{start_verse}-{end_verse}"
    description = " ".join(
        f"**({verse['verse']})** {format_verse_text(verse['text'])}" for verse in selected_verses
    )

    embed = discord.Embed(title=title, description=description, color=12370112)
    embed.set_footer(text=f'{translations[translation]}')

    if hour:
        try:
            user_tz = pytz.timezone(user_timezone)
            now = datetime.now(user_tz)
            send_time = datetime.strptime(hour, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
            send_time = user_tz.localize(send_time)

            if send_time < now:
                send_time += timedelta(days=1)

            delay = (send_time - now).total_seconds()

            confirmation_embed = discord.Embed(
                description=f"The message will be sent at **{send_time.strftime('%H:%M %Z')}**",
                color=12370112
            )
            confirmation_message = await interaction.followup.send(embed=confirmation_embed, ephemeral=True)

            await asyncio.sleep(delay)
            await interaction.channel.send(embed=embed)
            await confirmation_message.delete()

        except ValueError:
            error_embed=discord.Embed(
                title="Error",
                description="Invalid time format was specified. The correct format is **HH:MM**",
                color=0xff1d15
            )
            await interaction.followup.send(embed=error_embed)
    else:
        await interaction.followup.send(embed=embed, ephemeral=True)