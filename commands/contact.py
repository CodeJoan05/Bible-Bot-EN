import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

@client.tree.command(name="contact", description="Contact to the bot author")
async def contact(interaction: discord.Integration):
    embed = discord.Embed(
        title="Contact",
        description="If you would like to report a bug or give a suggestion for changes to the bot please contact me:\n\nDiscord: **code_joan**\nInstagram: **god.is.graceful**",
        color=12370112)
    await interaction.response.send_message(embed=embed)