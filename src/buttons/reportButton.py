from typing import Optional

import disnake

from src.module import ReportUtils, Yml, EmbedFactory


class ReportButton(disnake.ui.View):
    def __init__(self, report_utils: ReportUtils, report_id: int, bot):
        super().__init__(timeout=20.0)
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

        self.report_settings = Yml("./config/config.yml").load().get("Report", {})
        self.embed_color = Yml("./config/config.yml").load().get("EmbedColors", {})
        self.report_utils = report_utils
        self.report_id = report_id
        self.value = Optional[bool]

    @disnake.ui.button(label="Принять", style=disnake.ButtonStyle.green, custom_id="report_accept", emoji="✅")
    async def report_accept(self, button: disnake.ui.Button, interaction: disnake.CommandInteraction):
        if not self.report_utils.claim_report(self.report_id, interaction.user.id):
            await interaction.response.send_message("Ошибка принятия репорта.", ephemeral=True)
            return

        # category_id = int(self.report_settings.get("Channel", {}).get("Category", 0))
        # category = interaction.guild.get_channel(category_id)
        #
        # if category is None:
        #     embed = disnake.Embed(
        #         title="<:crossmark:1272260131677278209> Ошибка!",
        #         color=int(self.embed_color.get("Error", "#ff6161").lstrip("#"), 16),
        #         description="Не удалось найти категорию для каналов!"
        #     )
        #     await interaction.response.send_message(embed=embed, ephemeral=True)
        #     return
        #
        # vc_channel = None
        # if self.report_settings.get("Channel", {}).get("VC", False):
        #     vc_channel = await interaction.guild.create_voice_channel(
        #         name=f"Репорт-{interaction.user.display_name}",
        #         category=category
        #     )
        #
        # await interaction.guild.create_text_channel(
        #     name=f"репорт-{interaction.user.display_name}",
        #     category=category,
        #     topic=self.report_settings.get("Channel", {}).get(
        #         "Topic", ""
        #     )
        # )
        #
        # embed = disnake.Embed(
        #     title="<:tick:1272260155190546584> Успех!",
        #     color=int(self.embed_color.get("Success", "#6cff61").lstrip("#"), 16),
        #     description=f"Репорт принят и назначен вам. Созданы каналы: {vc_channel.mention if vc_channel else ''} {text_channel.mention}."
        # )
        #
        # await interaction.response.send_message(embed=embed, ephemeral=True)
        self.value = True
        self.stop()

    @disnake.ui.button(label="Отклонить", style=disnake.ButtonStyle.red, custom_id="report_reject", emoji="⛔")
    async def report_reject(self, button: disnake.ui.Button, interaction: disnake.CommandInteraction):
        success = self.report_utils.close_report(self.report_id, interaction.user.id)

        if success:
            message_id = self.report_utils.get_message_id(self.report_id)

            if message_id:
                try:
                    channel = interaction.channel
                    message = await channel.fetch_message(message_id)
                    await message.delete()
                except disnake.NotFound:
                    pass
            embed = await self.embed_factory.create_embed(preset="ReportReject", color_type="Success")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = await self.embed_factory.create_embed(preset="ReportRejectError", color_type="Success")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        self.value = False
        self.stop()
