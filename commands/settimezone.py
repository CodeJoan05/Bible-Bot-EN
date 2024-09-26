import discord, pytz, sqlite3
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# Create a SQLite database

conn = sqlite3.connect('data/user_settings.db')
c = conn.cursor()

# Create a table to store user settings

c.execute('''CREATE TABLE IF NOT EXISTS user_settings
             (user_id INTEGER PRIMARY KEY, default_translation TEXT, timezone TEXT)''')

# Function to dynamically autocomplete timezone options
async def timezone_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    # Filter timezones based on the current input
    return [
        app_commands.Choice(name=tz, value=tz)
        for tz in pytz.all_timezones
        if current.lower() in tz.lower()
    ][:25]  # Limit to the first 25 matches

@client.tree.command(name="settimezone", description="Set your time zone")
@app_commands.describe(timezone="Set your time zone (e.g. Europe/London)")
@app_commands.autocomplete(timezone=timezone_autocomplete)
async def settimezone(interaction: discord.Interaction, timezone: str):
    user_id = interaction.user.id
    try:
        # Verify the timezone is valid
        pytz.timezone(timezone)

        # Downloading default translation
        c.execute("SELECT default_translation FROM user_settings WHERE user_id = ?", (user_id,))
        user_data = c.fetchone()

        # Save default translation
        translation = user_data[0] if user_data else None
        
        # Save new settings
        c.execute("REPLACE INTO user_settings (user_id, default_translation, timezone) VALUES (?, ?, ?)", (user_id, translation, timezone))
        conn.commit()

        embed = discord.Embed(
            title="Setting the time zone",
            description=f"Time zone set to `{timezone}`",
            color=12370112
        )
        await interaction.response.send_message(embed=embed)
    except pytz.UnknownTimeZoneError:
        error_embed = discord.Embed(
            title="Error",
            description="Invalid time zone. Please provide a valid time zone (e.g. Europe/London)",
            color=0xff1d15
        )
        await interaction.response.send_message(embed=error_embed)
