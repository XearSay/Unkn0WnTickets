import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

TOKEN = "MTM4NTMzNzQzODAyODk1OTk1NA.GUFyuO.EMOWyQhewzBUppnHzl7LDYaB8Ib3Kud_ty7RpU"  # Замените на ваш токен
MODERATOR_ROLE_NAME = "Moderator"  # Название роли модератора

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
ticket_counter = 0


@bot.event
async def on_ready():
    print(f"✅ Бот запущен как {bot.user}")


@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    """Команда для отправки embed-сообщения с кнопкой открытия тикета"""
    button = Button(label="🎟️ Открыть тикет", style=discord.ButtonStyle.green)

    async def button_callback(interaction: discord.Interaction):
        global ticket_counter
        ticket_counter += 1
        guild = interaction.guild
        author = interaction.user

        # Категория тикетов
        category = discord.utils.get(guild.categories, name="🎫 Tickets")
        if category is None:
            category = await guild.create_category("🎫 Tickets")

        # Проверка на уже существующий тикет
        for ch in category.channels:
            if ch.name == f"ticket-{author.id}":
                await interaction.response.send_message(
                    f"❗ У тебя уже есть открытый тикет: {ch.mention}", ephemeral=True
                )
                return

        # Роли и права
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        mod_role = discord.utils.get(guild.roles, name=MODERATOR_ROLE_NAME)
        if mod_role:
            overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await category.create_text_channel(
            name=f"ticket-{author.id}",
            overwrites=overwrites,
            topic=f"Тикет от {author.display_name}"
        )

        await interaction.response.send_message(
            f"✅ Тикет создан: {channel.mention}", ephemeral=True
        )

        # Кнопка "Взять тикет"
        take_button = Button(label="📥 Взять тикет", style=discord.ButtonStyle.blurple)

        async def take_callback(take_interaction: discord.Interaction):
            if not mod_role or mod_role not in take_interaction.user.roles:
                await take_interaction.response.send_message(
                    "⛔ Только модераторы могут брать тикеты.", ephemeral=True
                )
                return

            take_button.disabled = True
            await take_interaction.message.edit(view=view)

            # Кнопка "Закрыть тикет"
            close_button = Button(label="🔒 Закрыть тикет", style=discord.ButtonStyle.red)

            async def close_callback(close_interaction: discord.Interaction):
                if close_interaction.user != author and mod_role not in close_interaction.user.roles:
                    await close_interaction.response.send_message(
                        "🚫 Только автор или модератор может закрыть тикет.", ephemeral=True
                    )
                    return

                await close_interaction.response.send_message("🔐 Тикет закрыт. Канал будет удалён...", ephemeral=True)
                await asyncio.sleep(3)
                await channel.delete()

            close_button.callback = close_callback

            close_view = View()
            close_view.add_item(close_button)

            await take_interaction.response.send_message(
                f"👤 {take_interaction.user.mention} взял тикет.",
                view=close_view
            )

        take_button.callback = take_callback

        view = View()
        view.add_item(take_button)

        await channel.send(
            f"👋 Здравствуйте, {author.mention}!\nОпишите вашу проблемму, поддержка скоро свяжется с вами.",
            view=view
        )

    button.callback = button_callback
    view = View()
    view.add_item(button)

    # Embed-сообщение
    embed = discord.Embed(
        title="📩 Обращение в поддержку",
        description=(
            "🔧 **Пожалуйста, опишите вашу проблему максимально подробно**.\n"
            "📎 Прикрепите скриншоты (если нужно) и укажите все важные детали. Это ускорит решение вашего запроса.\n\n"
            "**📊 Среднее время ответа:** 1–3 часа\n"
            "**🕒 Рабочее время поддержки:** 10:00 – 23:00\n"
            "**🚫 При нарушении правил:** ограничение доступа к тикетам/мут/бан\n\n"
            "🔐 **Правила подачи обращения**\n"
            "> • Будьте вежливы — неадекватное поведение приведёт к блокировке\n"
            "> • Пишите по делу — не отклоняйтесь от темы\n"
            "> • Приложите доказательства (скриншоты, логи и т.д.)\n"
            "> • В тикетах действует регламентированная система правил\n\n"
            "❗ При ошибке системы тикетов напишите в Discord: <@tranquillionz>"
        ),
        color=discord.Color.blurple()
    )
    embed.set_author(name="Unkn0WnTickets", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)

    await ctx.send(embed=embed, view=view)


@ticket.error
async def ticket_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У тебя нет прав для использования этой команды.")


# Запуск бота
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"❌ Ошибка запуска бота: {e}")
