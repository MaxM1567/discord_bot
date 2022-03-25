import discord
from discord.ext import commands
from interaction_db import User
import json

# VERSION 0.2.0
# Изменения:
# 1. бот может модерировать чат
# 2. бот может выдавать WARN-ы за плохие слова и ссылки
# 3. база данных и взаимодействие с ней
# 4. команда info - показывает кол-во WARN-ов пользователя

# ПАРАМЕТРЫ
token = 'NzM4OTE1MTU0OTgwNTAzNTgz.XyS2XQ.gKn-xiAJsg7hj3gPPDEBAkKz-dk'
PREFIX = '/'  # префикс
intents = discord.Intents.all()

with open("ban_words.json", "r", encoding='utf-8') as read_file:  # открыл json файл для чтения
    ban_words = json.load(read_file)  # список запрещённых слов
    # print(ban_words)

with open("ban_root_words.json", "r", encoding='utf-8') as read_file_2:  # открыл json файл для чтения
    ban_root_words = json.load(read_file_2)  # список запрещённых корней слов
    # print(ban_root_words)

with open("list_users.json", "r", encoding='utf-8') as read_file_3:  # открыл json файл для чтения
    list_users = json.load(read_file_3)  # список запрещённых корней слов
    # print(ban_root_words)

bot = commands.Bot(command_prefix=PREFIX, intents=intents)  # Там где 'PREFIX' ставьте свой префикс по желанию. У меня это будет "-"


# ДОБАВЛЯЕТ WARN ПОЛЬЗОВАТЕЛЮ
def add_warn_user(message):
    user = User.get(User.user_id == message.author.mention)
    warn = user.quantity_warn

    print(f'WARN ({message.author.mention}: {warn} => {int(warn) + 1})')

    user = User(quantity_warn=str(int(warn) + 1))
    user.user_id = message.author.mention  # Тот самый первичный ключ
    # который связывает наш объект с конкретной строке таблицы базы данных
    user.save()


# ПРОВЕРКА СООБЩЕНИЯ НА ЗАПРЕЩЁННЫЕ КОРНИ
def check__warn_root_word(message):
    for word_root in ban_root_words:
        # print(f'проверка {word_root} В СООБЩЕНИИ: {(message.content.lower())}')
        # print(word_root)
        if word_root in str(message.content.lower()):
            return True
    return False


# ВЫВОД СООБЩЕНИЯ О НАРУШЕНИИ
async def warn_message(message):
    # количество warn
    user = User.get(User.user_id == message.author.mention)
    warn = user.quantity_warn
    # нужный канал
    warn_channel = bot.get_channel(950115623508271166)  # подключение к тестовому каналу

    # print(message.author.mention)
    # print(type(message.author.mention))

    # генерация сообщения
    embA = discord.Embed(colour=discord.Color.red())
    embA.add_field(name='Пользователь', value=f'{message.author.mention}')
    # embA.add_field(name='Модератор', value='{}'.format(self.bot.user.mention)) D?
    embA.add_field(name='Модератор', value='<@738915154980503583>')  # D?
    embA.add_field(name='Причина', value='Использование плохих слов', inline=False)
    embA.add_field(name='Канал', value=f'{message.channel.mention}')
    embA.add_field(name='WARN (бета)', value=f'{warn}')
    embA.add_field(name='Сообщение', value=f'||{message.content}||', inline=False)
    # embA.set_author(name='[WARN]{}#{}'.format(message.author.name, message.author.discriminator), icon_url=message.author.avatar_url) D?

    await warn_channel.send(embed=embA)


# ТЕСТОВАЯ КОМАНДА (заменяет сообщения)
@bot.command()  # создаём команду
async def info(ctx):
    user = User.get(User.user_id == f'<@{ctx.author.id}>')
    warn = user.quantity_warn
    member = ctx.author

    print('----------CTX----------')
    print(dir(ctx))
    print('-----------------')
    print(ctx.author.id)
    print('-----------------')
    print(f'@<{ctx.author.id}>')
    print('-----------------')
    print(member)

    emb = discord.Embed(title='Информация пользавателя', colour=discord.Color.blue())
    emb.add_field(name='WARN', value=f'{warn}')
    emb.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
    await ctx.send(embed=emb)


# ПРОВЕРКА СООБЩЕНИЯ НА ЗАПРЕЩЁННЫЕ СЛОВА
@bot.event
async def on_message(message):

    if message.author.mention not in list_users:

        list_users.append(message.author.mention)
        with open('list_users.json', 'w') as outfile:
            json.dump(list_users, outfile)

        User.create(user_id=message.author.mention, quantity_warn=0)

    # print('запущена функция: on_message(message)')
    # print(message.content.lower())
    # print(type(message.content.lower()))

    if message.author.mention == '<@738915154980503583>':  # если сообщение от бота
        # print('BOT_MESSAGE')
        pass

    elif check__warn_root_word(message) or message.content.lower() in ban_words:  # если бан слово

        # TEST---TEST---TEST
        add_warn_user(message)
        # TEST---TEST---TEST

        await warn_message(message)

        print(f'DELETED ({message.author.mention}: {message.content})')
        await message.delete()
        await message.channel.send(f"{message.author.mention} !!!СООБЩЕНИЕ БЫЛО УДАЛЕНО!!! (ругательства запрещены)")

    elif 'https://' in message.content:  # если начинается как ссылка => удаляет и выводит причину

        # TEST---TEST---TEST
        add_warn_user(message)
        # TEST---TEST---TEST

        await warn_message(message)

        print(f'DELETED ({message.author.mention}: {message.content})')
        await message.delete()
        await message.channel.send(f"{message.author.mention} В этом чате нельзя использовать ссылки!")

    else:  # если всё в порядке
        print(f'OK ({message.author.mention}: {message.content})')
        await bot.process_commands(message)


# Теперь запускаем нашего бота
print('BOT_CONNECTED')
bot.run(token)
