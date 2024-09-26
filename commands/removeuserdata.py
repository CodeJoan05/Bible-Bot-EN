import discord, sqlite3
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# Create a SQLite database

conn = sqlite3.connect('data/user_settings.db')
c = conn.cursor()

# Create a table to store user settings

c.execute('''CREATE TABLE IF NOT EXISTS user_settings
             (user_id INTEGER PRIMARY KEY, default_translation TEXT, timezone TEXT)''')

@client.tree.command(name="removeuserdata", description="Deleting user data from the database")
async def removeuserdata(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_name = interaction.user.mention
    
    c.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()
    
    if user_data:
        c.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
        conn.commit()

        embed = discord.Embed(
            title="Deleting user data",
            description=f"Deleted user {user_name} data from database. To be able to fully use the bot you must re-set the default Bible translation using the `/setversion` command",
            color=12370112
        )
    else:
        embed = discord.Embed(
            title="Error",
            description="User data not found in database",
            color=0xff1d15
        )
    await interaction.response.send_message(embed=embed)