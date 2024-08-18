import disnake
from disnake.ext import commands
from disnake.ext.commands import MissingPermissions
from loguru import logger

from src.buttons.verifyButton import VerifyButton
from src.module import EmbedFactory, VerifyUtils, Yml


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)
        self.verify_utils = VerifyUtils()
        self.verify_settings = Yml("./config/config.yml").load().get("Verify", {})
        self.staff_roles = [int(role_id) for role_id in self.verify_settings.get("StaffRoles", [])]

        self.logging_enabled = Yml("./config/config.yml").load().get('Logging', {}).get('Verify', {}).get('Enabled', False)
        self.logging_channel_id = int(Yml("./config/config.yml").load().get('Logging', {}).get('Verify', {})
                                      .get('ChannelID', 0))

        self.dm_user_enabled = self.verify_settings.get('DMUser', False)

    async def log_action(self, action: str, member: disnake.Member, color: str = None):
        if not self.logging_enabled or not self.logging_channel_id:
            return

        channel = self.bot.get_channel(self.logging_channel_id)
        if channel:
            embed = await self.embed_factory.create_embed(preset=action, user=member, color_type=color)
            await channel.send(embed=embed)
        else:
            logger.warning(f"Logging channel with ID {self.logging_channel_id} not found.")

    async def check_self_verification(self, interaction: disnake.AppCmdInter, member: disnake.Member) -> bool:
        if member.id == interaction.author.id:
            embed = await self.embed_factory.create_embed(preset='SelfVerifyError', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return True
        return False

    async def check_staff_roles(self, interaction: disnake.AppCmdInter) -> bool:
        user_roles = [role.id for role in interaction.author.roles]
        is_admin = any(role.permissions.administrator for role in interaction.author.roles)
        if is_admin or any(role_id in self.staff_roles for role_id in user_roles):
            return True

        embed = await self.embed_factory.create_embed(preset='NoPermissions', color_type="Error")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False

    @commands.slash_command(
        name="verify",
        description="Верифицировать пользователя на сервере"
    )
    async def verify_slash(self, interaction: disnake.AppCmdInter):
        pass

    @verify_slash.sub_command(
        name="add",
        description="Добавить пользователя в верифицированные"
    )
    async def verify_add_slash(self, interaction: disnake.AppCmdInter, member: disnake.Member):

        if await self.check_self_verification(interaction, member):
            return

        if not await self.check_staff_roles(interaction):
            return

        if self.verify_utils.is_user_verified(member.id, interaction.guild.id):
            embed = await self.embed_factory.create_embed(preset='AlreadyVerified', user=member, color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.verify_utils.last_moder(member.id, interaction.guild.id, interaction.user.id)

        view = VerifyButton(self.verify_utils, self.embed_factory, member)
        embed = await self.embed_factory.create_embed(preset='Verify', user=member)
        await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
        await view.wait()

        if view.value is True:
            self.verify_utils.verify_user(member.id, interaction.guild.id, interaction.user.id)
            await self.log_action('LogVerifySuccess', member, "Success")

            embed = await self.embed_factory.create_embed(preset='UserVerifySuccess', color_type="Success")
            if self.dm_user_enabled:
                await member.send(embed=embed)
        elif view.value is False:
            self.verify_utils.give_rejection(member.id, interaction.guild.id)
            await self.log_action('LogVerifyRejection', member, "Error")
            embed = await self.embed_factory.create_embed(preset='UserVerifyRejection', color_type="Error")
            if self.dm_user_enabled:
                await member.send(embed=embed)

    @verify_slash.sub_command(
        name="remove",
        description="Удалить пользователя из верифицированных"
    )
    async def verify_remove_slash(self, interaction: disnake.AppCmdInter, member: disnake.Member):
        if await self.check_self_verification(interaction, member):
            return

        if not await self.check_staff_roles(interaction):
            return

        if not self.verify_utils.is_user_verified(member.id, interaction.guild.id):
            embed = await self.embed_factory.create_embed(preset='NotVerified', user=member, color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.verify_utils.last_moder(member.id, interaction.guild.id, interaction.user.id)

        self.verify_utils.unverify_user(member.id, interaction.guild.id)
        embed = await self.embed_factory.create_embed(preset='VerifyRemoved', user=member, color_type="Success")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        await self.log_action('LogVerifyRemoved', member)

    @verify_add_slash.error
    @verify_remove_slash.error
    async def verify_command_error(self, interaction: disnake.AppCmdInter, error):
        if isinstance(error, MissingPermissions):
            embed = await self.embed_factory.create_embed(preset='NoPermissions', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Verify(bot))
