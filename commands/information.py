import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

@client.tree.command(name="information", description="Information about the bot")
async def information(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Information",
        description="**Bible** is a bot that allows you to read the Bible in multiple languages for in-depth study of the differences between the original texts and their translations\n\nThe bot has **122** Bible translations in **50** languages\n\n**Website:** https://bible-bot.netlify.app/\n\n[Terms of Service](https://bible-bot.netlify.app/terms-of-service) | [Privacy Policy](https://bible-bot.netlify.app/privacy-policy)",
        color=12370112)
    await interaction.response.send_message(embed=embed)