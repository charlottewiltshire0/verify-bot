import disnake
from disnake.ext import commands
from loguru import logger

from src.modals.reportModals import ReportModal
from src.module import EmbedFactory, Yml, ReportUtils, log_action


class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)
        self.report_settings = Yml("./config/config.yml").load().get("Report", {})
        self.report_utils = ReportUtils()
        self.staff_roles = [int(role_id) for role_id in self.report_settings.get("StaffRoles", [])]
        self.limit_per_user = self.report_settings.get("LimitPerUser", 5)

        self.logging_enabled = Yml("./config/config.yml").load().get('Logging', {}).get('Report', {}).get('Enabled',
                                                                                                          False)
        self.logging_channel_id = int(Yml("./config/config.yml").load().get('Logging', {}).get('Report', {})
                                      .get('ChannelID', 0))

    async def check_staff_roles(self, interaction: disnake.AppCmdInter) -> bool:
        user_roles = [role.id for role in interaction.author.roles]
        is_admin = any(role.permissions.administrator for role in interaction.author.roles)
        if is_admin or any(role_id in self.staff_roles for role_id in user_roles):
            return True

        embed = await self.embed_factory.create_embed(preset='NoPermissions', color_type="Error")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False

    async def check_self_report(self, interaction: disnake.AppCmdInter, member: disnake.Member) -> bool:
        if member.id == interaction.author.id:
            embed = await self.embed_factory.create_embed(preset='SelfReportError', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return True
        return False

    @commands.slash_command(
        name="report",
        description="Сообщить о проблеме или нарушении"
    )
    async def report_slash(self, interaction: disnake.AppCmdInter):
        pass

    @report_slash.sub_command(
        name="new",
        description="Сообщить о проблеме или нарушении"
    )
    async def report_new_slash(self, interaction: disnake.AppCmdInter):
        modal = ReportModal(self.bot)
        await interaction.response.send_modal(modal=modal)

    # @report_slash.sub_command(
    #     name="add-user",
    #     description="Добавить пользователя в репорт"
    # )
    # async def report_add_slash(self, interaction: disnake.AppCmdInter, report_id: int, member: disnake.Member):
    #     if not await self.check_staff_roles(interaction):
    #         return
    #
    #     if await self.check_self_report(interaction, member):
    #         return
    #
    #     report = self.report_utils.get_report_by_id_or_victim(report_id=report_id)
    #     if not report:
    #         embed = await self.embed_factory.create_embed(preset="ReportNotFound", color_type="Error")
    #         await interaction.response.send_message(embed=embed, ephemeral=True)
    #         return
    #
    #     member_ids = self.report_utils.get_member_ids(report_id=report_id)
    #     if member_ids and len(member_ids) >= self.limit_per_user:
    #         embed = await self.embed_factory.create_embed(preset="ReportAddLimitExceeded", color_type="Error")
    #         await interaction.response.send_message(embed=embed, ephemeral=True)
    #         return
    #
    #     success = self.report_utils.add_member_to_report(member_id=member.id, report_id=report_id)
    #     if success:
    #         # Проверка, был ли участник успешно добавлен
    #         member_ids = self.report_utils.get_member_ids(report_id=report_id)
    #         if member.id in member_ids:
    #             if self.logging_enabled:
    #                 await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
    #                                  embed_factory=self.embed_factory,
    #                                  action='LogReportAddedSuccess', member=interaction.author, color="Success")
    #
    #             embed = await self.embed_factory.create_embed(preset="ReportAdded", color_type="Success")
    #             await interaction.response.send_message(embed=embed, ephemeral=True)
    #         else:
    #             embed = await self.embed_factory.create_embed(preset="ReportAddAlreadyExists", color_type="Error")
    #             await interaction.response.send_message(embed=embed, ephemeral=True)
    #             logger.info(f"Failed to add user {member} to report #{report_id}.")
    #     else:
    #         embed = await self.embed_factory.create_embed(preset="ReportAddAlreadyExists", color_type="Error")
    #         await interaction.response.send_message(embed=embed, ephemeral=True)
    #         logger.info(f"Failed to add user {member} to report #{report_id}.")


def setup(bot: commands.Bot):
    bot.add_cog(Report(bot))
