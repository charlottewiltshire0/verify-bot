import disnake
from disnake import Interaction
from disnake.ext import commands
from sqlalchemy.orm import Session

from src.module import EmbedFactory, add_channel_mention, remove_channel_mention, set_channel_mention, SessionLocal


class ChannelMention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)

    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @commands.slash_command(name="mention", description="Отправляет упоминание новым пользователям, уведомляя их о необходимости пройти верификацию на сервер")
    async def mention_slash(self, interaction: disnake.AppCmdInter):
        """Slash command for user mentions."""
        embed = await self.embed_factory.create_embed(preset='MentionHelp')
        await interaction.response.send_message(embed=embed)

    @mention_slash.sub_command(name="add", description="Установить канал для упоминания новых пользователей")
    async def mention_slash_add(self, interaction: disnake.AppCmdInter, channel: disnake.TextChannel):
        db: Session = next(self.get_db())
        channel_added = add_channel_mention(db, interaction.guild.id, channel.id)
        if channel_added:
            embed = await self.embed_factory.create_embed(preset='MentionAdd', channel=channel, color_type="Success")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = await self.embed_factory.create_embed(preset='MentionAlreadyAdded', channel=channel, color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @mention_slash.sub_command(name="remove", description="Удалить канал для упоминания новых пользователей")
    async def mention_slash_remove(self, interaction: disnake.AppCmdInter):
        db: Session = next(self.get_db())
        channel_removed = remove_channel_mention(db, interaction.guild.id)
        if channel_removed:
            embed = await self.embed_factory.create_embed(preset='MentionDelete', color_type="Success")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = await self.embed_factory.create_embed(preset='NoMentionChannel', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @mention_slash.sub_command(name="set", description="Изменить канал для упоминания новых пользователей")
    async def mention_slash_set(self, interaction: disnake.AppCmdInter, channel: disnake.TextChannel):
        db: Session = next(self.get_db())
        set_channel_mention(db, interaction.guild.id, channel.id)
        embed = await self.embed_factory.create_embed(preset='MentionSet', channel=channel)
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(ChannelMention(bot))
