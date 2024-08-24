import disnake
from disnake.ext import commands

from src.module import EmbedFactory, Yml, MentionUtils, log_action


class ChannelMention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_factory = EmbedFactory('./config/embeds.yml', './config/config.yml', bot=bot)
        self.mention_utils = MentionUtils()

        self.logging_enabled = Yml("./config/config.yml").load().get('Logging', {}).get('Mention', {}).get('Enabled',
                                                                                                           False)
        self.logging_channel_id = int(Yml("./config/config.yml").load().get('Logging', {}).get('Mention', {})
                                      .get('ChannelID', 0))

    @commands.slash_command(name="mention",
                            description="Отправляет упоминание новым пользователям, уведомляя их о необходимости пройти верификацию на сервер")
    async def mention_slash(self, interaction: disnake.AppCmdInter):
        pass

    @mention_slash.sub_command(name="add", description="Установить канал для упоминания новых пользователей")
    async def mention_slash_add(self, interaction: disnake.AppCmdInter, channel: disnake.TextChannel):
        channel_added = self.mention_utils.add_channel_mention(interaction.guild.id, channel.id)
        if channel_added:
            embed = await self.embed_factory.create_embed(preset='MentionAdd', channel=channel, color_type="Success")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            if self.logging_enabled:
                await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                 embed_factory=self.embed_factory,
                                 action='LogMentionAdd', member=interaction.author, color="Success")
        else:
            embed = await self.embed_factory.create_embed(preset='MentionAlreadyAdded', channel=channel,
                                                          color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @mention_slash.sub_command(name="remove", description="Удалить канал для упоминания новых пользователей")
    async def mention_slash_remove(self, interaction: disnake.AppCmdInter):
        if self.logging_enabled:
            await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                             embed_factory=self.embed_factory,
                             action='LogMentionRemove', member=interaction.author, color="Error")

        channel_removed = self.mention_utils.remove_channel_mention(interaction.guild.id)
        if channel_removed:
            embed = await self.embed_factory.create_embed(preset='MentionDelete', color_type="Success")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = await self.embed_factory.create_embed(preset='NoMentionChannel', color_type="Error")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @mention_slash.sub_command(name="set", description="Изменить канал для упоминания новых пользователей")
    async def mention_slash_set(self, interaction: disnake.AppCmdInter, channel: disnake.TextChannel):
        success = self.mention_utils.set_channel_mention(interaction.guild.id, channel.id)
        if success:
            embed = await self.embed_factory.create_embed(preset='MentionSet', channel=channel, color_type="Success")
            if self.logging_enabled:
                await log_action(bot=self.bot, logging_channel_id=self.logging_channel_id,
                                 embed_factory=self.embed_factory,
                                 action='LogMentionSet', member=interaction.author, color="Success")

        else:
            embed = await self.embed_factory.create_embed(preset='MentionSetFailed', color_type="Error")
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(ChannelMention(bot))
