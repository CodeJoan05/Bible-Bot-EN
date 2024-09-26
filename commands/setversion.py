import discord, json, sqlite3
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# Default translation

default_translations = {}

# Create a SQLite database

conn = sqlite3.connect('data/user_settings.db')
c = conn.cursor()

# Create a table to store user settings

c.execute('''CREATE TABLE IF NOT EXISTS user_settings
             (user_id INTEGER PRIMARY KEY, default_translation TEXT, timezone TEXT)''')

# Function to dynamically autocomplete Bible translation options
async def translation_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    with open('resources/translations/bible_translations.txt', 'r') as file:
        bible_translations = [line.strip() for line in file]
    
    # Filter the translations based on the current input
    return [
        app_commands.Choice(name=translation, value=translation)
        for translation in bible_translations
        if current.lower() in translation.lower()
    ][:25]  # Limit to the first 25 matches

@client.tree.command(name="setversion", description="Set the default Bible translation")
@app_commands.autocomplete(translation=translation_autocomplete)
async def setversion(interaction: discord.Interaction, translation: str):

    with open('resources/translations/bible_translations.txt', 'r') as file:
        bible_translations = [line.strip() for line in file]

    if translation in bible_translations:
        user_id = interaction.user.id

        # Downloading time zone
        c.execute("SELECT timezone FROM user_settings WHERE user_id = ?", (user_id,))
        user_data = c.fetchone()
        
        # Save time zone
        timezone = user_data[0] if user_data else None
        
        # Save new settings
        c.execute("REPLACE INTO user_settings (user_id, default_translation, timezone) VALUES (?, ?, ?)", (user_id, translation, timezone))
        conn.commit()
        
        with open('resources/translations/translations.json', 'r', encoding='utf-8') as f:
            translations = json.load(f)

        full_name = translations[translation]

        embed = discord.Embed(
            title="Set the default Bible translation",
            description=f'The default Bible translation set to: `{full_name}`',
            color=12370112)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="Error",
            description='Invalid Bible translation was given',
            color=0xff1d15)
        await interaction.response.send_message(embed=embed)