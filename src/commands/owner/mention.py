import disnake
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

    @commands.group(name="mention", invoke_without_command=True, description="Отправляет упоминание новым пользователям, уведомляя их о необходимости пройти верификацию на сервер")
    async def mention(self, ctx: commands.Context):
        """Parent command for user mentions."""
        embed = await self.embed_factory.create_embed(preset='MentionHelp')
        await ctx.send(embed=embed)

    @mention.command(name="add", description="Установить канал для упоминания новых пользователей")
    async def mention_add(self, ctx: commands.Context, channel: disnake.TextChannel):
        db: Session = next(self.get_db())
        channel_added = add_channel_mention(db, ctx.guild.id, channel.id)
        if channel_added:
            embed = await self.embed_factory.create_embed(preset='MentionAdd', channel=channel, color_type="Success")
            await ctx.reply(embed=embed, delete_after=60)
        else:
            embed = await self.embed_factory.create_embed(preset='MentionAlreadyAdded', channel=channel, color_type="Error")
            await ctx.reply(embed=embed, delete_after=60)

    @mention.command(name="remove", description="Изменить канал для упоминания новых пользователей")
    async def mention_remove(self, ctx: commands.Context):
        db: Session = next(self.get_db())
        remove_channel_mention(db, ctx.guild.id)
        await ctx.send(f"Канал для упоминания новых пользователей был удален.")

    @mention.command(name="set", description="Изменить канал для упоминания новых пользователей")
    async def mention_set(self, ctx: commands.Context, channel: disnake.TextChannel):
        db: Session = next(self.get_db())
        set_channel_mention(db, ctx.guild.id, channel.id)
        embed = await self.embed_factory.create_embed(preset='MentionAdd', channel=channel)
        await ctx.send(f"Канал для упоминания новых пользователей изменен на {channel.mention}.")

    @commands.slash_command(name="mention", description="Отправляет упоминание новым пользователям, уведомляя их о необходимости пройти верификацию на сервер")
    async def mention_slash(self, interaction: disnake.CommandInteraction):
        """Slash command for user mentions."""
        embed = await self.embed_factory.create_embed(preset='MentionHelp')
        await interaction.response.defer()
        await interaction.followup.send(embed=embed)

    @mention_slash.sub_command(name="add", description="Установить канал для упоминания новых пользователей")
    async def mention_slash_add(self, interaction: disnake.CommandInteraction, channel: disnake.TextChannel):
        db: Session = next(self.get_db())
        channel_added = add_channel_mention(db, interaction.guild.id, channel.id)
        if channel_added:
            await interaction.response.defer()
            await interaction.followup.send(
                f"Упоминания новых пользователей будут отправляться в канал {channel.mention}.")
        else:
            await interaction.response.defer()
            await interaction.followup.send(f"Этот канал уже привязан для упоминаний новых пользователей.")

    @mention_slash.sub_command(name="remove", description="Удалить канал для упоминания новых пользователей")
    async def mention_slash_remove(self, interaction: disnake.CommandInteraction):
        db: Session = next(self.get_db())
        remove_channel_mention(db, interaction.guild.id)
        await interaction.response.defer()
        await interaction.followup.send("Канал для упоминания новых пользователей был удален.")

    @mention_slash.sub_command(name="set", description="Изменить канал для упоминания новых пользователей")
    async def mention_slash_set(self, interaction: disnake.CommandInteraction, channel: disnake.TextChannel):
        db: Session = next(self.get_db())
        set_channel_mention(db, interaction.guild.id, channel.id)
        await interaction.response.defer()
        await interaction.followup.send(f"Канал для упоминания новых пользователей изменен на {channel.mention}.")


def setup(bot: commands.Bot):
    bot.add_cog(ChannelMention(bot))
