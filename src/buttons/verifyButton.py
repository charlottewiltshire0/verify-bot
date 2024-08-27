from typing import Optional

import disnake

from src.module import Yml, VerifyUtils, EmbedFactory, get_button_style


class VerifyButton(disnake.ui.View):
    def __init__(self, verify_utils: VerifyUtils, embed_factory: EmbedFactory, member: disnake.Member):
        super().__init__(timeout=20.0)
        self.verify_settings = Yml("./config/config.yml").load().get("Verify", {})
        self.verify_utils = verify_utils
        self.embed_factory = embed_factory
        self.member = member
        self.value = Optional[bool]
        self.unverified_role_id = int(self.verify_settings.get("UnverifiedRole", 0))

    @disnake.ui.button(label="Верифицировать", style=disnake.ButtonStyle.green, custom_id="verify_accept", emoji="✅")
    async def verify_accept(self, button: disnake.ui.Button, interaction: disnake.CommandInteraction):
        view = RoleButton(self.member, self.verify_utils)

        embed = await self.embed_factory.create_embed(preset='SelectRole', user=self.member)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()

        if self.unverified_role_id:
            role = interaction.guild.get_role(self.unverified_role_id)
            if role:
                await self.member.remove_roles(role)

        self.value = True
        embed = await self.embed_factory.create_embed(preset='VerifySuccess', user=self.member, color_type="Success")
        await interaction.followup.send(embed=embed, ephemeral=True)
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


class RoleButton(disnake.ui.View):
    def __init__(self, member: disnake.Member, verify_utils: VerifyUtils):
        super().__init__(timeout=20.0)
        self.value = Optional[int]
        self.member = member
        self.verify_utils = verify_utils
        self.verify_settings = Yml("./config/config.yml").load().get("Verify", {})

        for role in self.verify_settings["Roles"]:
            role_id = int(role['id'])
            guild_role = member.guild.get_role(role_id)
            if guild_role:
                self.add_item(disnake.ui.Button(
                    label=guild_role.name,
                    style=get_button_style(role['color']),
                    custom_id=f"role_{role['id']}",
                    emoji=role['emoji']
                ))

    async def interaction_check(self, interaction: disnake.AppCmdInter) -> bool:
        custom_id = interaction.data.custom_id
        if custom_id.startswith("role_"):
            role_id = int(custom_id.split("_")[1])
            role = interaction.guild.get_role(role_id)
            if role:
                await self.member.add_roles(role)
                self.verify_utils.set_role(user_id=self.member.id, role_id=role_id, guild_id=self.member.guild.id)
                self.value = role_id
                self.stop()
                return True
        return False
