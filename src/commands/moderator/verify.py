import disnake
from disnake.ext import commands
from disnake.ext.commands import MissingPermissions

from src.buttons.verifyButton import VerifyButton
from src.module import EmbedFactory, VerifyUtils, Yml, log_action, send_embed_to_member, check_staff_roles


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)
        self.verify_utils = VerifyUtils()
        self.verify_settings = Yml("./config/config.yml").load().get("Verify", {})
        self.staff_roles = [int(role_id) for role_id in self.verify_settings.get("StaffRoles", [])]
        self.unverified_role = self.verify_settings.get("UnverifiedRole", None)

        self.logging_enabled = Yml("./config/config.yml").load().get('Logging', {}).get('Verify', {}).get('Enabled',
                                                                                                          False)
        self.logging_channel_id = int(Yml("./config/config.yml").load().get('Logging', {}).get('Verify', {})
                                      .get('ChannelID', 0))

        self.dm_user_enabled = self.verify_settings.get('DMUser', False)

    async def check_self_verification(self, interaction: disnake.AppCmdInter, member: disnake.Member) -> bool:
        if member.id == interaction.author.id:
            embed = await self.embed_factory.create_embed(preset='SelfVerifyError', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return True
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

        if not await check_staff_roles(interaction=interaction, staff_roles=self.staff_roles,
                                       embed_factory=self.embed_factory):
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
            if self.logging_enabled:
                await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id, embed_factory=self.embed_factory,
                                 action='LogVerifySuccess', member=member, color="Success")
            if self.dm_user_enabled:
                await send_embed_to_member(embed_factory=self.embed_factory, member=member, preset="UserVerifySuccess",
                                           color_type="Success")

        elif view.value is False:
            self.verify_utils.give_rejection(member.id, interaction.guild.id)
            if self.logging_enabled:
                await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id, embed_factory=self.embed_factory,
                                 action='LogVerifyRejection', member=member, color="Error")
            if self.dm_user_enabled:
                await send_embed_to_member(embed_factory=self.embed_factory, member=member,
                                           preset="UserVerifyRejection", color_type="Error")

    @verify_slash.sub_command(
        name="remove",
        description="Удалить пользователя из верифицированных"
    )
    async def verify_remove_slash(self, interaction: disnake.AppCmdInter, member: disnake.Member):
        if await self.check_self_verification(interaction, member):
            return

        if not await check_staff_roles(interaction=interaction, staff_roles=self.staff_roles,
                                       embed_factory=self.embed_factory):
            return

        if not self.verify_utils.is_user_verified(member.id, interaction.guild.id):
            embed = await self.embed_factory.create_embed(preset='NotVerified', user=member, color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.verify_utils.last_moder(member.id, interaction.guild.id, interaction.user.id)

        verify_role_id = self.verify_utils.get_verify_role(user_id=member.id, guild_id=interaction.guild.id)
        if verify_role_id is None:
            embed = await self.embed_factory.create_embed(preset='RoleNotFound', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        role = disnake.utils.get(interaction.guild.roles, id=int(verify_role_id))
        if role is None:
            embed = await self.embed_factory.create_embed(preset='RoleNotFound', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await member.remove_roles(role)

        if self.unverified_role:
            unverified_role = disnake.utils.get(interaction.guild.roles, id=int(self.unverified_role))
            if unverified_role:
                await member.add_roles(unverified_role)

        self.verify_utils.unverify_user(member.id, interaction.guild.id)
        embed = await self.embed_factory.create_embed(preset='VerifyRemoved', user=member, color_type="Success")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        if self.logging_enabled:
            await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id, embed_factory=self.embed_factory,
                             action='LogVerifyRemoved', member=member, color="Error")
        if self.dm_user_enabled:
            await send_embed_to_member(embed_factory=self.embed_factory, member=member,
                                       preset="UserVerifyRemoved", color_type="Success")

    @verify_add_slash.error
    @verify_remove_slash.error
    async def verify_command_error(self, interaction: disnake.AppCmdInter, error):
        if isinstance(error, MissingPermissions):
            embed = await self.embed_factory.create_embed(preset='NoPermissions', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Verify(bot))
