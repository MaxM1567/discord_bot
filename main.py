# VERSION 0.0.1
# Изменения:
# 1. добавлен каркас бота
# 2. возможность запуска бота

# Импортируем нужные библиотеки
import discord
from discord.ext import commands

# ПАРАМЕТРЫ
token = 'NzM4OTE1MTU0OTgwNTAzNTgz.XyS2XQ.gKn-xiAJsg7hj3gPPDEBAkKz-dk'
PREFIX = '/'  # префикс
intents = discord.Intents.all()  # права
bot = commands.Bot(command_prefix=PREFIX, intents=intents)  # указал ПРЕФИК(PREFIX) и ПРАВА(intents) бота

# ЗАПУСКА БОТА
print('BOT_CONNECTED')  # информация в консоль
bot.run(token)  # запуска бота
