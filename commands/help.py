import discord
from discord.ext import commands
from typing import List
from collections import deque

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# Buttons

class PaginatorView(discord.ui.View):
    def __init__(
        self, 
        embeds:List[discord.Embed]
    ) -> None:
        super().__init__(timeout=None)
        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._current_page = 1
        self._len = len(embeds)

        if self._len == 1:
            self.previous_page.disabled = True
            self.next_page.disabled = True

    def get_page_number(self) -> str:
        return f"Page {self._current_page} of {self._len}"

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="⬅️")
    async def previous_page(self, interaction: discord.Interaction, _):
        self._queue.rotate(1)
        embed = self._queue[0]
        if self._current_page > 1:
            self._current_page -= 1
        else:
            self._current_page = self._len
        embed.set_footer(text=self.get_page_number())
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji="➡️")
    async def next_page(self, interaction: discord.Interaction, _):
        self._queue.rotate(-1)
        if self._current_page < self._len:
            self._current_page += 1
        else:
            self._current_page = 1
        embed = self._queue[0]
        embed.set_footer(text=self.get_page_number())
        await interaction.response.edit_message(embed=embed)

    @property
    def initial(self) -> discord.Embed:
        embed = self._initial
        embed.set_footer(text=self.get_page_number())
        return embed

@client.tree.command(name="help", description="How to use the Bible bot")
async def help(interaction: discord.Interaction):
    description = [
        f'Commands you can use:\n\n`/setversion [translation]` - sets the default Bible translation. To set the default Bible translation, you need to enter a translation abbreviation. All translation abbreviations are available in `/versions`\n\n`/search [text]` - is used to find bible passages from the Bible translation\n\n`[book] [chapter]:[verse-(s)] [translation]` - command scheme for obtaining passages from the Bible. If the user wants to obtain a passage from some Bible translation, the translation abbreviation should be given. For example: `John 3:16-17 KJV`. If the user has set the default Bible translation, the translation abbreviation need not be given. For example: `John 1:1`\n\n`/versions` - shows available Bible translations',
        f'Commands you can use:\n\n`/information` - shows information about the bot\n\n`/invite` - allows to add a bot to the server\n\n`/contact` - includes contact to the bot author\n\n`/random [hour]` - displays random verse(s) from the Bible (1 to 10 verses)\n\n`/removeuserdata` - deletes user data in the database\n\n`/settimezone [timezone]` - sets the time zone'
    ]
    embeds = [discord.Embed(title="Help", description=desc, color=12370112) for desc in description]
    view = PaginatorView(embeds)
    await interaction.response.send_message(embed=view.initial, view=view)