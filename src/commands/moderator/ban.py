import disnake
from disnake.ext import commands

from src.module import EmbedFactory, VerifyUtils, Yml, BanUtils, check_staff_roles, send_embed_to_member, log_action


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
            embed = await self.embed_factory.create_embed(preset='SelfBanError', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            self.bot.error(preset='SelfBanError', ephemeral=True, interaction=interaction, embed_factory=self.embed_factory)
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
            embed = await self.embed_factory.create_embed(preset='RequireReasonError', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.require_proof and not proof:

            embed = await self.embed_factory.create_embed(preset='RequireProofError', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        ban = self.ban_utils.issue_ban(
            user_id=member.id,
            guild_id=interaction.guild.id,
            moderator_id=interaction.author.id,
            reason=reason,
            proof=proof,
            duration=duration
        )

        if ban:
            embed = await self.embed_factory.create_embed(preset='BanSuccess', color_type="Error",
                                                          user=member)
            await interaction.followup.send(embed=embed, ephemeral=True)

            if self.dm_user_enabled:
                await send_embed_to_member(embed_factory=self.embed_factory, member=member, preset="DMBan",
                                           color_type="Error")

            if self.logging_enabled:
                await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                 embed_factory=self.embed_factory, action='LogBan', member=member, color="Error")

        else:
            embed = await self.embed_factory.create_embed(preset='BanFailed', color_type="Error")
            await interaction.followup.send(embed=embed, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Ban(bot))
