import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

class InviteView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Add bot", url="https://discord.com/oauth2/authorize?client_id=1208111472987738172&permissions=277025401856&integration_type=0&scope=bot+applications.commands"))

@client.tree.command(name="invite", description="Add the bot to your server")
async def invite(interaction: discord.Interaction):
    view = InviteView()
    await interaction.response.send_message(view=view)