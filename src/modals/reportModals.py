import disnake
from disnake import TextInputStyle

from src.module import Yml


class ReportModal(disnake.ui.Modal):
    def __init__(self):
        self.report_settings = Yml("./config/config.yml").load().get("Report", {})
        self.embed_color = Yml("./config/config.yml").load().get("EmbedColors", {})
        self.channel_settings = Yml("./config/config.yml").load().get("Channels", {})
        self.staff_roles = self.report_settings.get("StaffRoles", [])
        self.ping_support = self.report_settings.get("PingSupport", False)

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
            embed = disnake.Embed(
                title="<:crossmark:1272260131677278209> Ошибка!",
                color=int(self.embed_color.get("Error", "#ff6161").lstrip("#"), 16),
                description="Не удалось найти канал для репортов!"
            )
            await interaction.send(embed=embed, ephemeral=True)
            return

        user_id = interaction.text_values["username"]
        description = interaction.text_values["description"]

        try:
            user_id = int(user_id)
            user = interaction.guild.get_member(user_id)

            if user is None:
                embed = disnake.Embed(
                    title="<:crossmark:1272260131677278209> Ошибка!",
                    color=int(self.embed_color.get("Error", "#ff6161").lstrip("#"), 16),
                    description=f"Пользователь с ID `{user_id}` не найден."
                )
                await interaction.send(embed=embed, ephemeral=True)
                return

        except ValueError:
            embed = disnake.Embed(
                title="<:crossmark:1272260131677278209> Ошибка!",
                color=int(self.embed_color.get("Error", "#ff6161").lstrip("#"), 16),
                description="Неверный формат ID пользователя."
            )
            await interaction.send(embed=embed, ephemeral=True)
            return

        if user.id == interaction.author.id:
            embed = disnake.Embed(
                title="<:crossmark:1272260131677278209> Ошибка!",
                color=int(self.embed_color.get("Error", "#ff6161").lstrip("#"), 16),
                description="Вы не можете подать репорт на самого себя."
            )
            await interaction.send(embed=embed, ephemeral=True)
            return

        if self.ping_support:
            mention_roles = ' '.join([f"<@&{role_id}>" for role_id in self.staff_roles])
            content = f"@here {mention_roles}"
        else:
            content = ""

        embed = disnake.Embed(
            title=interaction.text_values["subject"],
            color=int(self.embed_color.get("Default", "#242424").lstrip("#"), 16),
            description=f"<:profile:1272248323280994345> **Автор жалобы**: <@{interaction.author.id}>\n<:space:1272248683903189084><:arrowright:1272249470297440417> ID: {interaction.author.id}\n<:report:1274406261814722761> **Нарушитель**: <@{user.id}>\n<:space:1272248683903189084><:arrowright:1272249470297440417> ID: {user.id}\n<:text:1274281670459133962> **Описание**: \n{description}"
        )
        await channel.send(content=content, embed=embed)

        embed = disnake.Embed(
            title="<:tick:1272260155190546584> Успех!",
            color=int(self.embed_color.get("Success", "#6cff61").lstrip("#"), 16),
            description="Ваш репорт был отправлен!"
        )
        await interaction.send(embed=embed, ephemeral=True)
