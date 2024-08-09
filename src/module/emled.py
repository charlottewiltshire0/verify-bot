import disnake
from disnake.ext import commands
from typing import Optional

from src.module import Yml
from .utils import TextFormatter


class EmbedFactory:
    def __init__(self, embed_config_path: str, color_config_path: str, bot: commands.Bot):
        self.embed_data = Yml(embed_config_path).load()
        self.color_data = Yml(color_config_path).load()
        self.formatter = TextFormatter(bot)

    def create_embed(self, preset: Optional[str] = None, user: disnake.Member = None, **kwargs) -> disnake.Embed:
        embed_dict = self.embed_data.get('Embeds', {}).get(preset, {}) if preset else kwargs

        embed = disnake.Embed(
            title=self.formatter.format_text(embed_dict.get('Title', ''), user=user),
            description=self.formatter.format_text(embed_dict.get('Description', ''), user=user),
            url=embed_dict.get('Url', ''),
            color=disnake.Color.from_rgb(*self.hex_to_rgb(embed_dict.get('Color', self.color_data['EmbedColors'].get('Default', '#242424'))))
        )

        if 'Author' in embed_dict:
            embed.set_author(
                name=self.formatter.format_text(embed_dict['Author'], user=user),
                url=embed_dict.get('AuthorUrl', None),
                icon_url=self.formatter.format_text(embed_dict.get('AuthorIcon', None), user=user)
            )

        if 'Footer' in embed_dict:
            embed.set_footer(
                text=self.formatter.format_text(embed_dict['Footer'], user=user),
                icon_url=self.formatter.format_text(embed_dict.get('FooterIcon', None), user=user)
            )

        if 'Thumbnail' in embed_dict:
            embed.set_thumbnail(url=self.formatter.format_text(embed_dict['Thumbnail'], user=user))

        if 'Image' in embed_dict:
            embed.set_image(url=self.formatter.format_text(embed_dict['Image'], user=user))

        if embed_dict.get('Timestamp', False):
            embed.timestamp = disnake.utils.utcnow()

        for field in embed_dict.get('Fields', []):
            embed.add_field(
                name=self.formatter.format_text(field.get('name', 'No Name'), user=user),
                value=self.formatter.format_text(field.get('value', 'No Value'), user=user),
                inline=field.get('inline', False)
            )

        return embed

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# Usage example:
# embed_factory = EmbedFactory('embeds.yml', 'config.yml')
# embed = embed_factory.create_embed(preset='Example')  # Using preset
# embed = embed_factory.create_embed(Title="Custom Title", Description="Custom Description")  # Direct input
