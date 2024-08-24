import disnake
from disnake.ext import commands

from src.module import EmbedFactory, VerifyUtils, Yml, BanUtils, check_staff_roles


class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)
        self.ban_utils = BanUtils()
        self.ban_settings = Yml("./config/config.yml").load().get("Ban", {})
        self.staff_roles = [int(role_id) for role_id in self.ban_settings.get("StaffRoles", [])]
        self.require_reason = self.ban_settings.get('RequireReason', False)
        self.require_proof = self.ban_settings.get('RequireProof', False)

        self.logging_enabled = Yml("./config/config.yml").load().get('Logging', {}).get('Verify', {}).get('Enabled',
                                                                                                          False)
        self.logging_channel_id = int(Yml("./config/config.yml").load().get('Logging', {}).get('Verify', {})
                                      .get('ChannelID', 0))
        self.dm_user_enabled = self.ban_settings.get('DMUser', False)

    async def check_self_ban(self, interaction: disnake.AppCmdInter, member: disnake.Member) -> bool:
        if member.id == interaction.author.id:
            self.bot.error(preset='SelfBanError', ephemeral=True, interaction=interaction,
                           embed_factory=self.embed_factory)
            return True
        return False

    @commands.slash_command(
        name="ban",
        description="Забанить пользователя с сервера"
    )
    async def ban_slash(self, interaction: disnake.AppCmdInter):
        pass

    @ban_slash.sub_command(
        name="add",
        description="Добавить пользователя в верифицированные"
    )
    async def ban_add_slash(self, interaction: disnake.AppCmdInter, member: disnake.Member, reason: str = None,
                            duration: str = None, proof: str = None):
        await interaction.response.defer()
        if await self.check_self_ban(interaction, member):
            return

        if not await check_staff_roles(interaction=interaction, staff_roles=self.staff_roles,
                                       embed_factory=self.embed_factory):
            return

        if self.require_reason and not reason:
            self.bot.error(preset='RequireReasonError', ephemeral=True, interaction=interaction,
                           embed_factory=self.embed_factory)
            return

        if self.require_proof and not proof:
            self.bot.error(preset='RequireProofError', ephemeral=True, interaction=interaction,
                           embed_factory=self.embed_factory)
            return

        self.bot.success(preset='BanSuccess', ephemeral=True, interaction=interaction,
                         embed_factory=self.embed_factory)

def setup(bot: commands.Bot):
    bot.add_cog(Ban(bot))
