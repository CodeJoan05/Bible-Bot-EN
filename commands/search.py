import discord, json, sqlite3, re
from typing import List
from collections import deque
from discord.ext import commands

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

# Create a SQLite database

conn = sqlite3.connect('data/user_settings.db')
c = conn.cursor()

# Create a table to store user settings

c.execute('''CREATE TABLE IF NOT EXISTS user_settings
             (user_id INTEGER PRIMARY KEY, default_translation TEXT, timezone TEXT)''')

# Italics font

def format_verse_text(text):
    return re.sub(r'\[([^\]]+)\]', r'*\1*', text)

@client.tree.command(name="search", description="Searching passages in the Bible")
async def search(interaction: discord.Interaction, text: str):

    user_id = interaction.user.id
    c.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()

    if not user_data:
        embed = discord.Embed(
            title="Set the default Bible translation",
            description='To use the Bible passage search function, you must first set the default Bible translation using the `/setversion` command. To set the default Bible translation, you need to specify a translation abbreviation. All translation abbreviations are available in `/versions`',
            color=12370112)
        await interaction.response.send_message(embed=embed)
        return

    translation = user_data[1]

    with open('resources/translations/translations.json', 'r', encoding='utf-8') as file:
        translations = json.load(file)

    embeds = []

    with open(f'resources/bibles/{translation}.json', 'r', encoding='utf-8') as file:
        bible = json.load(file)

    try:
        words = text.split()
        verses = []
        for verse in bible:
            if all(word in verse['text'] for word in words):
                for word in words:
                    verse['text'] = verse['text'].replace(word, f'**{word}**')
                italics_font = format_verse_text(verse['text'])
                verses.append(f"**{verse['book_name']} {verse['chapter']}:{verse['verse']}** \n{italics_font} \n")
        if not verses:
            raise ValueError(f'No verse found containing the word(s) "**{text}**" in translation `{translations[translation]}`')
        
    except ValueError as err:
        embed = discord.Embed(
            title="Search error",
            description=str(err),
            color=0xff1d15)
        await interaction.response.send_message(embed=embed)
        return

    message = ''
    for verse in verses:
        if len(message) + len(verse) < 650:
            message += f"{verse}\n"
        else:
            embed = discord.Embed(
                title=f'Bible passages containing the word(s) - *{text}*',
                description=message,
                color=12370112
            )
            embed.add_field(name="", value=f'**{translations[translation]}**')
            embeds.append(embed)
            message = f"{verse}\n"

    if message:
        embed = discord.Embed(
            title=f'Bible passages containing the word(s) - *{text}*',
            description=message,
            color=12370112
        )
        embed.add_field(name="", value=f'**{translations[translation]}**')
        embeds.append(embed)

    view = PaginatorView(embeds)
    await interaction.response.send_message(embed=view.initial, view=view)