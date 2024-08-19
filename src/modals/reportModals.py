import disnake
from disnake import TextInputStyle
from disnake.ext import commands

from src.buttons.reportButton import ReportButton
from src.module import Yml, ReportUtils, EmbedFactory


class ReportModal(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml')

        self.report_settings = Yml("./config/config.yml").load().get("Report", {})
        self.channel_settings = Yml("./config/config.yml").load().get("Channels", {})
        self.staff_roles = self.report_settings.get("StaffRoles", [])
        self.ping_support = self.report_settings.get("PingSupport", False)
        self.report_utils = ReportUtils()

        components = [
            disnake.ui.TextInput(
                label="Нарушитель",
                placeholder="ID нарушителя",
                custom_id="username",
                style=TextInputStyle.short,
                max_length=24,
            ),
            disnake.ui.TextInput(
                label="Тема",
                placeholder="Краткая суть проблемы",
                custom_id="subject",
                style=TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Описание",
                placeholder="Подробное описание проблемы",
                custom_id="description",
                style=TextInputStyle.paragraph,
                max_length=500
            ),
        ]

        super().__init__(title="Репорт", components=components)

    async def callback(self, interaction: disnake.MessageInteraction):
        channel_id = int(self.channel_settings.get("Reports", 0))
        channel = interaction.guild.get_channel(channel_id)

        if channel is None:
            embed = self.embed_factory.create_embed(preset="ReportMissingChannel", color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        user_id = interaction.text_values["username"]
        description = interaction.text_values["description"]

        try:
            user_id = int(user_id)
            user = interaction.guild.get_member(user_id)

            if user is None:
                embed = self.embed_factory.create_embed(preset="ReportUserNotFound", color_type="Error",
                                                        user_id=user_id)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        except ValueError:
            embed = self.embed_factory.create_embed(preset="ReportInvalidUserID", color_type="Error",
                                                    user_id=user_id)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user.id == interaction.author.id:
            embed = self.embed_factory.create_embed(preset="ReportSelfReport", color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        report = self.report_utils.create_report(
            victim_id=interaction.author.id,
            perpetrator_id=user.id,
            guild_id=interaction.guild.id
        )

        if report is None:
            embed = self.embed_factory.create_embed(preset="ReportExists", color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.ping_support:
            mention_roles = ' '.join([f"<@&{role_id}>" for role_id in self.staff_roles])
            content = f"@here {mention_roles}"
        else:
            content = ""

        default_color = "#242424"
        color_int = int(default_color.lstrip("#"), 16)
        embed = disnake.Embed(
            title=interaction.text_values["subject"],
            color=color_int,
            description=f"<:profile:1272248323280994345> **Автор жалобы**: <@{interaction.author.id}>\n<:space:1272248683903189084><:arrowright:1272249470297440417> ID: {interaction.author.id}\n<:report:1274406261814722761> **Нарушитель**: <@{user.id}>\n<:space:1272248683903189084><:arrowright:1272249470297440417> ID: {user.id}\n<:text:1274281670459133962> **Описание**: \n{description}"
        )

        buttons = ReportButton(self.report_utils, report.id)

        await channel.send(content=content, embed=embed, view=buttons)

        embed = self.embed_factory.create_embed(preset="ReportSuccess", color_type="Success")
        await interaction.response.send_message(embed=embed, ephemeral=True)
