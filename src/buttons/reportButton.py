from typing import Optional

import disnake

from src.module import ReportUtils, Yml, EmbedFactory, log_action, send_embed_to_member, TextFormatter


class ReportButton(disnake.ui.View):
    def __init__(self, report_utils: ReportUtils, report_id: int, bot):
        super().__init__(timeout=20.0)
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)
        self.formatter = TextFormatter(bot)

        self.report_settings = Yml("./config/config.yml").load().get("Report", {})
        self.embed_color = Yml("./config/config.yml").load().get("EmbedColors", {})
        self.staff_roles = [int(role_id) for role_id in self.report_settings.get("StaffRoles", [])]
        self.report_utils = report_utils
        self.report_id = report_id
        self.value = Optional[bool]

        self.logging_enabled = Yml("./config/config.yml").load().get('Logging', {}).get('Report', {}).get('Enabled',
                                                                                                          False)
        self.logging_channel_id = int(Yml("./config/config.yml").load().get('Logging', {}).get('Report', {})
                                      .get('ChannelID', 0))

        self.dm_user_enabled = self.report_settings.get('DMUser', False)

    @disnake.ui.button(label="Принять", style=disnake.ButtonStyle.green, custom_id="report_accept", emoji="✅")
    async def report_accept(self, button: disnake.ui.Button, interaction: disnake.AppCmdInter):
        await interaction.response.defer()

        if not self.report_utils.claim_report(report_id=self.report_id, moderator_id=interaction.user.id):
            await interaction.followup.send("Ошибка принятия репорта.", ephemeral=True)
            return

        category_id = int(self.report_settings.get("Channel", {}).get("Category", 0))
        category = interaction.guild.get_channel(category_id)

        if category is None:
            embed = await self.embed_factory.create_embed(preset="ReportMissingCategory", color_type="Error")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        member = interaction.guild.get_member(self.report_utils.get_victim_id(self.report_id))
        reporter = interaction.guild.get_member(self.report_utils.get_perpetrator_id(self.report_id))

        staff_roles = [interaction.guild.get_role(role_id) for role_id in self.staff_roles]
        staff_permissions = {role: disnake.PermissionOverwrite(read_messages=True) for role in staff_roles}

        permissions = {
            interaction.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            interaction.user: disnake.PermissionOverwrite(read_messages=True),
            member: disnake.PermissionOverwrite(read_messages=True),
            reporter: disnake.PermissionOverwrite(read_messages=True),
            **staff_permissions
        }

        voice_channel = None
        if self.report_settings.get("Channel", {}).get("VC", False):
            voice_channel = await interaction.guild.create_voice_channel(
                name=f"🔊・{self.report_id}-{member.display_name}",
                category=category,
                overwrites=permissions
            )

        text_channel = await interaction.guild.create_text_channel(
            name=f"🎫・беседа-{self.report_id}-{member.display_name}",
            category=category,
            topic=await self.formatter.format_text(self.report_settings.get("Channel", {}).get("Topic", ""),
                                                   user=member),
            overwrites=permissions
        )

        self.report_utils.set_channels_id(
            text_channel_id=text_channel.id,
            voice_channel_id=voice_channel.id if voice_channel else None,
            report_id=self.report_id
        )

        if self.logging_enabled:
            await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                             embed_factory=self.embed_factory,
                             action='LogReportClaimed', member=interaction.author, color="Success")

        if self.dm_user_enabled:
            member = await self.bot.fetch_user(self.report_utils.get_victim_id(self.report_id))
            await send_embed_to_member(embed_factory=self.embed_factory, member=member,
                                       preset="DMReportClaimed", color_type="Success")

        embed = await self.embed_factory.create_embed(preset="ReportClaimed", color_type="Success")
        await interaction.followup.send(embed=embed, ephemeral=True)

        staff_mentions = ' '.join(role.mention for role in staff_roles)
        content = f"{member.mention} {reporter.mention} {staff_mentions}"
        embed = await self.embed_factory.create_embed(preset="ReportClaimedDetails", color_type="Success")

        message = await text_channel.send(content=content, embed=embed)
        await message.pin()

        message_id = self.report_utils.get_message_id(self.report_id)

        if message_id:
            try:
                channel = interaction.channel
                message = await channel.fetch_message(message_id)
                await message.delete()
            except disnake.NotFound:
                pass

        self.value = True
        self.stop()

    @disnake.ui.button(label="Отклонить", style=disnake.ButtonStyle.red, custom_id="report_reject", emoji="⛔")
    async def report_reject(self, button: disnake.ui.Button, interaction: disnake.AppCmdInter):
        await interaction.response.defer()
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

            if self.logging_enabled:
                await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                 embed_factory=self.embed_factory,
                                 action='LogReportRejection', member=interaction.author, color="Error")

            if self.dm_user_enabled:
                member = await self.bot.fetch_user(self.report_utils.get_victim_id(self.report_id))
                await send_embed_to_member(embed_factory=self.embed_factory, member=member,
                                           preset="DMReportReject", color_type="Error")

            embed = await self.embed_factory.create_embed(preset="ReportReject", color_type="Success")
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = await self.embed_factory.create_embed(preset="ReportRejectError", color_type="Success")
            await interaction.followup.send(embed=embed, ephemeral=True)

        self.value = False
        self.stop()
