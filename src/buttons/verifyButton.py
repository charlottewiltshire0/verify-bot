from typing import Optional

import disnake

from src.module import Yml, VerifyUtils, EmbedFactory


class VerifyButton(disnake.ui.View):
    def __init__(self, verify_utils: VerifyUtils, embed_factory: EmbedFactory, member: disnake.Member):
        super().__init__(timeout=20.0)
        self.verify_settings = Yml("./config/config.yml").load().get("Verify", {})
        self.verify_utils = verify_utils
        self.embed_factory = embed_factory
        self.member = member
        self.value = Optional[bool]

    @disnake.ui.button(label="Верифицировать", style=disnake.ButtonStyle.green, custom_id="verify_accept", emoji="✅")
    async def verify_accept(self, button: disnake.ui.Button, interaction: disnake.CommandInteraction):
        self.value = True
        embed = await self.embed_factory.create_embed(preset='VerifySuccess', user=self.member, color_type="Success")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()

    @disnake.ui.button(label="Недопуск", style=disnake.ButtonStyle.red, custom_id="verify_reject", emoji="⛔")
    async def verify_reject(self, button: disnake.ui.Button, interaction: disnake.CommandInteraction):
        self.value = False
        embed = await self.embed_factory.create_embed(preset='VerifyRejection', user=self.member, color_type="Error")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()

    @disnake.ui.button(label="Отменить", style=disnake.ButtonStyle.gray, custom_id="verify_cancel", emoji="🔙")
    async def verify_cancel(self, button: disnake.ui.Button, interaction: disnake.CommandInteraction):
        self.value = None
        embed = await self.embed_factory.create_embed(preset='VerifyCancelled', user=self.member)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()