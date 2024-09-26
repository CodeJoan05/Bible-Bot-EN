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

@client.tree.command(name="versions", description="Available Bible translations")
async def versions(interaction: discord.Interaction):
    description = [
        f'These are the available Bible translations:\n\n**Afrikaans:**\n\n`AFRI` - Afrikaans (1953)\n\n**Albanian:**\n\n`ALB` - Albanian\n\n**Arabic:**\n\n`SVD` - Smith and van Dycks al-Kitab al-Muqaddas (1865)\n`NAV` - New Arabic Version (1988/1997)',
        f'These are the available Bible translations:\n\n**Armenian:**\n\n`ARME` - Eastern Armenian Bible\n`ARMW` - Western Armenian NT (1853)\n\n**Azerbaijani:**\n\n`NAT` - Northern Azeri Translation\n\n**Belarusian:**\n\n`BELA` - Belarusian Bible (2003)',
        f'These are the available Bible translations:\n\n**Bulgarian:**\n\n`VCB` - Veren’s Contemporary Bible (1871)\n\n**Czech:**\n\n`BKR` - Bible Kralicka (1579)\n`CCEP` - Czech Ekumenicky Cesky preklad (2001)\n`CB21` - Czech Bible Překlad 21 (2009)\n`CCSP` - Czech Český studijní překlad (2009)\n\n**Chinese:**\n\n`CHIUNS` - 和合本 简体字 Chinese Union Simplified (1919)',
        f'These are the available Bible translations:\n\n`CHIUN` - 和合本 繁體字 Chinese Union Traditional (1919)\n`CHISB` - 思高本 Sīgāo Běn (1954/1960)\n`NCVS` - 新译本 Chinese New Version Simplified (1976/2010)\n\n**Croatian:**\n\n`CROS` - Hrvatska Biblija Ivana Šarića (1941/1942)\n\n**Danish:**\n\n`DA` - Danish with original orthography (1907/1931)\n\n**Dutch:**\n\n`DUTSVV` - Dutch Statenvertaling Bijbel (1618/1619)',
        f'These are the available Bible translations:\n\n`NLC` - Petrus Canisius Translation (1939)\n\n**English:**\n\n`TCB` - Coverdale Bible (1535)\n`TYN` - Tyndale Bible (1535)\n`BSB` - Bishops Bible (1568)\n`GNV` - Geneva Bible (1587)\n`KJV` - King James Version (1611/1769)\n`WEBS` - Webster Bible (1833)\n`YLT` - Youngs Literal Translation (1898)\n`ASV` - American Standard Version (1901)\n`NET` - NET Bible (1996/2016)',
        f'These are the available Bible translations:\n\n`AKJV` - American King James Version (1999)\n`UKJV` - Updated King James Version (2000)\n`WEB` - World English Bible (2006)\n\n**Estonian:**\n\n`EST` - Estonian Bible\n\n**Finnish:**\n\n`FINN` - Finnish Biblia (1776)\n`FPR` - Finnish Pyhä Raamattu (1992)\n`FRK` - Raamattu Kansalle (2012)\n`STLK` - Pyhä Raamattu (2017)',
        f'These are the available Bible translations:\n\n**French:**\n\n`FPGR` - Bible Perret-Gentil et Rilliet (1858/1861)\n`FREK` - La Bible de Zadoc Khan (1899)\n`FBBB` - French Bible Bovet Bonnet (1900)\n`FRES` - Bible Louis Segond (1910)\n`FREC` - La Bible Augustin Crampon (1923)\n\n**German:**\n\n`LUTH` - Luther Bibel (1545)\n`ELB` - Elberfelder Bibel (1871)\n`GRUN` - Grünewaldbibel (1924)\n`SCH` - Schlachter Bibel (1951)',
        f'These are the available Bible translations:\n\n**Greek:**\n\n`LXX` - Septuagint: Morphologically Tagged Rahlfs\n`TR` - Textus Receptus (1550/1884)\n`BYZ` - Byzantine Text (2013)\n\n**Haitian:**\n\n`HAI` - Haitian Creole Bible\n\n**Hebrew:**\n\n`ALEP` - Aleppo Codex\n`WLC` - Westminster Leningrad Codex\n`HEBM` - Modern Hebrew Bible',
        f'These are the available Bible translations:\n\n**Hungarian:**\n\n`HUNKAR` - Revideált Károli Biblia (1908)\n`HUNUJ` - A Magyar Bibliatársulat Újfordítású Bibliája (1990)\n`HUNRUF` - A Magyar Bibliatársulat Revideált Újfordítású Bibliája\n`HUNKNB` - Káldi-Neovulgáta: katolikus (2013)\n\n**Italian:**\n\n`DIO` - Italian Giovanni Diodati Bibbia (1649)\n`RIVE` - Italian Riveduta Bibbia (1927)\n\n**Indonesian:**\n\n`TL` - Terjemahan Lama',
        f'These are the available Bible translations:\n\n`TB` - Terjemahan Baru (1994)\n\n**Japanese:**\n\n`RAG` - Japanese Raguet-yaku (1910)\n`BUN` - Japanese Bungo-yaku (1953)\n`KOU` - Japanese Kougo-yaku (1954/1955)\n\n**Kazakh:**\n\n`KAZ` - Киелі кітап (1993/2010)\n\n**Korean:**\n\n`KOR` - Korean',
        f'These are the available Bible translations:\n\n`KHKJV` - Hangul King James Version\n\n**Latin:**\n\n`VG` - Vulgate\n\n**Latvian:**\n\n`LVG` - Latvian Glück 8th edition (1898)\n`LVNT` - Latvian New Testament\n\n**Lingala:**\n\n`LINVB` - Liloba lya Nzambe: édition Verbum (2009)',
        f'These are the available Bible translations:\n\n**Lithuanian:**\n\n`LTKBB` - Lithuanian Bible\n\n**Malagasy:**\n\n`MG` - Baiboly Malagasy (1865)\n\n**Maori:**\n\n`MAORI` - Maori Bible\n\n**Mongolian:**\n\n`MONKJV` - Mongolian King James Version (2011/2015)',
        f'These are the available Bible translations:\n\n**Norwegian:**\n\n`NORSMB` - Studentmållagsbibelen (1921)\n`NOR` - Bibelen på Norsk (1930)\n`NORB` - Brød Nye Testamente (2010/2011)\n\n**Persian:**\n\n`OPT` - Old Persian Translation (1895)\n`OPV` - Persian Holy Bible: Tarjumeh-ye Ghadeem (1896/1996)\n`THN` - Tarjumeh-ye Hezare Noh\n`TPV` - Todays Persian Version',
        f'These are the available Bible translations:\n\n**Polish:**\n\n`BB` - Biblia Brzeska (1563)\n`BJW` - Biblia Jakuba Wujka (1599/1874)\n`BG` - Biblia Gdańska (1881)\n`BP` - Biblia Poznańska (1975)\n`BW` - Biblia Warszawska (1975)\n`BT` - Biblia Tysiąclecia: wydanie V (1999)\n`GOR` - Biblia Góralska (2005)\n`NBG` - Nowa Biblia Gdańska (2012)\n`UBG` - Uwspółcześniona Biblia Gdańska (2017)\n`BE` - Biblia Ekumeniczna (2018)\n`SNP` - Słowo Nowego Przymierza: przekład literacki (2018)\n`TNP` - Przekład Toruński Nowego Przymierza (2020)',
        f'These are the available Bible translations:\n\n`TRO` - Textus Receptus Oblubienicy (2023)\n\n**Portuguese:**\n\n`LIV` - Biblia Livre\n`PORA` - Biblia Sagrada Traduzida em Portuguez Por João Ferreeira DAlmeida (1911)\n`PORNVA` - Bíblia Nova Versão de Acesso Livre\n`PORCAP` - Bíblia Sagrada Capuchinhos (2017)\n\n**Romanian:**\n\n`ROMCOR` - Cornilescu Bible in Romanian language (1921)',
        f'These are the available Bible translations:\n\n**Russian:**\n\n`SYN` - Синодального Перевода Библии (1867/1876)\n`SYNLIO` - Russian Synodal Bible: Licht im Osten Edition\n\n**Serbian:**\n\n`SBDKE` - Serbian Bible Daničić-Karadžić Ekavski (1865)\n`SBDKI` - Serbian Bible Daničić-Karadžić Ijekavski (1865)\n\n**Slovenian:**\n\n`SLOKJV` - Slovenian translation of Holy Bible King James Version (1769)\n`SLOCH` - Sveto pismo Starega in Novega zakona (1925)',
        f'These are the available Bible translations:\n\n**Spanish:**\n\n`RV` - La Santa Biblia Reina-Valera (1909)\n`TDP` - Spanish Traducción de dominio público: Mateo a Romanos\n\n**Swedish:**\n\n`SWE` - Swedish Bible (1917)\n`FOLK` - Svenska Folkbibeln (2015)\n\n**Syriac:**\n\n`PESH` - Syriac Peshitta (1905)',
        f'These are the available Bible translations:\n\n**Tagalog:**\n\n`TAG` - Philippine Bible Society (1905)\n\n**Thai:**\n\n`THKJV` - Thai KJV\n\n**Turkish:**\n\n`TUR` - Turkish\n`NTB` - New Turkish Bible: Kutsal Kitap (2009)',
        f'These are the available Bible translations:\n\n**Ukrainian:**\n\n`UKRK` - Новий Завіт Переклад П Куліша (1871)\n`UKRO` - Українська Біблія Переклад Івана Огієнка\n\n**Vietnamese:**\n\n`VC` - Vietnamese Cadman (1934)\n`NVB` - New Vietnamese Bible (2002)\n`LCCMN` - Lời Chúa Cho Mọi Người (2007)\n\n**Welsh:**\n\n`BEIBL` - beibl.net'
    ]
    embeds = [discord.Embed(title="Available Bible translations", description=desc, color=12370112) for desc in description]
    view = PaginatorView(embeds)
    await interaction.response.send_message(embed=view.initial, view=view)