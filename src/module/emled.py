import asyncio
from datetime import datetime
from typing import Optional

import disnake
from disnake import Embed
from disnake.ext import commands

from src.module import Yml
from .utils import TextFormatter


class EmbedFactory:
    def __init__(self, embeds_path: str, config_path: str, bot: commands.Bot):
        self.embeds = Yml(embeds_path).load()
        self.config = Yml(config_path).load()
        self.formatter = TextFormatter(bot)

    async def create_embed(self, preset: Optional[str] = None, user: disnake.Member = None, channel: Optional[disnake.TextChannel] = None, color_type: Optional[str] = None, **kwargs) -> Embed:
        embed_data = self.embeds.get('Embeds', {}).get(preset, {}) if preset else {}
        embed_data.update(kwargs)

        title = await self.formatter.format_text(embed_data.get("Title", ""), user, channel)
        description = await self.formatter.format_text(embed_data.get("Description", ""), user, channel)
        color_key = color_type if color_type else embed_data.get("Color", "Default")
        color = int(self.config['EmbedColors'].get(color_key, "#242424").lstrip("#"), 16)

        embed = Embed(
            title=title,
            description=description,
            url=embed_data.get("Url", ""),
            color=color
        )

        if "Author" in embed_data:
            embed.set_author(
                name=await self.formatter.format_text(embed_data['Author'], user=user, channel=channel),
                url=embed_data.get('AuthorUrl', None),
                icon_url=await self.formatter.format_text(embed_data.get('AuthorIcon', ""), user=user, channel=channel)
            )
        if "Thumbnail" in embed_data:
            embed.set_thumbnail(url=embed_data["Thumbnail"])
        if "Image" in embed_data:
            embed.set_image(url=embed_data["Image"])
        if "Footer" in embed_data:
            footer_text = await self.formatter.format_text(embed_data["Footer"], user, channel=channel)
            footer_icon_url = await self.formatter.format_text(embed_data.get("FooterIcon", ""), user, channel=channel)
            embed.set_footer(
                text=footer_text,
                icon_url=footer_icon_url
            )

        if embed_data.get("Timestamp", False):
            embed.timestamp = datetime.utcnow()
        if "Fields" in embed_data:
            fields = await asyncio.gather(*[
                self.formatter.format_text(field["name"], user, channel=channel)
                for field in embed_data["Fields"]
            ], *[
                self.formatter.format_text(field["value"], user, channel=channel)
                for field in embed_data["Fields"]
            ])
            for i, field in enumerate(embed_data["Fields"]):
                embed.add_field(
                    name=fields[i],
                    value=fields[i + len(embed_data["Fields"])],
                    inline=field.get("inline", False)
                )

        return embed
