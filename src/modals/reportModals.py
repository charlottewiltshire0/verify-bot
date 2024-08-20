import disnake
from disnake import TextInputStyle

from src.buttons.reportButton import ReportButton
from src.module import Yml, ReportUtils, EmbedFactory, log_action, send_embed_to_member


class ReportModal(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

        self.report_settings = Yml("./config/config.yml").load().get("Report", {})
        self.channel_settings = Yml("./config/config.yml").load().get("Channels", {})
        self.staff_roles = self.report_settings.get("StaffRoles", [])
        self.ping_support = self.report_settings.get("PingSupport", False)
        self.report_utils = ReportUtils()

        self.logging_enabled = Yml("./config/config.yml").load().get('Logging', {}).get('Report', {}).get('Enabled',
                                                                                                           False)
        self.logging_channel_id = int(Yml("./config/config.yml").load().get('Logging', {}).get('Report', {})
                                      .get('ChannelID', 0))

        self.dm_user_enabled = self.report_settings.get('DMUser', False)

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
            embed = await self.embed_factory.create_embed(preset="ReportMissingChannel", color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        user_id = interaction.text_values["username"]
        description = interaction.text_values["description"]

        try:
            user_id = int(user_id)
            user = interaction.guild.get_member(user_id)

            if user is None:
                embed = await self.embed_factory.create_embed(preset="ReportUserNotFound", color_type="Error",
                                                              user_id=user_id)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        except ValueError:
            embed = await self.embed_factory.create_embed(preset="ReportInvalidUserID", color_type="Error",
                                                          user_id=user_id)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user.id == interaction.author.id:
            embed = await self.embed_factory.create_embed(preset="ReportSelfReport", color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        report = self.report_utils.create_report(
            victim_id=interaction.author.id,
            perpetrator_id=user.id,
            guild_id=interaction.guild.id,
            reason=description
        )

        if report is None:
            embed = await self.embed_factory.create_embed(preset="ReportExists", color_type="Error")
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
            description=f"<:profile:1272248323280994345> **Автор Репорта**: <@{interaction.author.id}>\n<:space:1272248683903189084><:arrowright:1272249470297440417> ID: {interaction.author.id}\n<:report:1274406261814722761> **Виновник**: <@{user.id}>\n<:space:1272248683903189084><:arrowright:1272249470297440417> ID: {user.id}\n<:text:1274281670459133962> **Описание**: \n{description}"
        )

        buttons = ReportButton(self.report_utils, report.id, bot=self.bot)

        message = await channel.send(content=content, embed=embed, view=buttons)
        self.report_utils.set_message_id(report.id, message.id)

        embed = await self.embed_factory.create_embed(preset="ReportSuccess", color_type="Success")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        if self.logging_enabled:
            await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                             embed_factory=self.embed_factory,
                             action='LogReportSuccess', member=interaction.author, color="Success")

        if self.dm_user_enabled:
            member = interaction.author
            await send_embed_to_member(embed_factory=self.embed_factory, member=member,
                                       preset="DMReportSuccess", color_type="Success")
