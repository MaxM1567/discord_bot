import discord
from discord.ext import commands
from interaction_db import User
import json

# VERSION 0.2.1
# Изменения:
# 1. бот может модерировать чат
# 2. бот может выдавать WARN-ы за плохие слова и ссылки
# 3. база данных и взаимодействие с ней
# 4. команда info - показывает кол-во WARN-ов пользователя
# 5. незначительная оптимизация

# ПАРАМЕТРЫ
token = 'NzM4OTE1MTU0OTgwNTAzNTgz.XyS2XQ.gKn-xiAJsg7hj3gPPDEBAkKz-dk'  # токен
PREFIX = '/'  # префикс
intents = discord.Intents.all()  # права

# РАБОТА С ФАЙЛАМИ
with open("ban_words.json", "r", encoding='utf-8') as read_file:  # открыл json файл для чтения
    ban_words = json.load(read_file)  # список запрещённых слов
    # print(ban_words)  # тест

with open("ban_root_words.json", "r", encoding='utf-8') as read_file_2:  # открыл json файл для чтения
    ban_root_words = json.load(read_file_2)  # список запрещённых корней слов
    # print(ban_root_words)  # тест

with open("list_users.json", "r", encoding='utf-8') as read_file_3:  # открыл json файл для чтения
    list_users = json.load(read_file_3)  # список запрещённых корней слов
    # print(ban_root_words)  # тест

bot = commands.Bot(command_prefix=PREFIX, intents=intents)  # переменная для взаимодействия с ботом


# ДОБАВЛЯЕТ WARN ПОЛЬЗОВАТЕЛЮ
def add_warn_user(message):
    # ПОДКЛЮЧЕНИЕ К БД
    user = User.get(User.user_id == message.author.mention)
    warn = user.quantity_warn

    # информация в консоль
    print(f'WARN ({message.author.mention}: {warn} => {int(warn) + 1})')

    # ОБНОВИЛ ДАННЫE БД
    user = User(quantity_warn=str(int(warn) + 1))
    user.user_id = message.author.mention  # Тот самый первичный ключ
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
    # ПОДКЛЮЧЕНИЕ К БД
    user = User.get(User.user_id == message.author.mention)  # количество warn
    warn = user.quantity_warn
    warn_channel = bot.get_channel(950115623508271166)  # нужный канал

    # ТЕСТЫ
    # print(message.author.mention)
    # print(type(message.author.mention))

    # ГЕНЕРАЦИЯ СООБЩЕНИЯ
    embA = discord.Embed(colour=discord.Color.red())
    embA.add_field(name='Пользователь', value=f'{message.author.mention}')
    embA.add_field(name='Модератор', value='<@738915154980503583>')
    embA.add_field(name='Причина', value='Запрещённый контент в сообщении', inline=False)
    embA.add_field(name='Канал', value=f'{message.channel.mention}')
    embA.add_field(name='WARN', value=f'{warn}')
    embA.add_field(name='Сообщение', value=f'||{message.content}||', inline=False)

    await warn_channel.send(embed=embA)


# ПОКАЗЫВАЕТ ПОЛЬЗОВАТЕЛЮ ИНФОРМАЦИЮ О НЁМ
@bot.command()
async def info(ctx):
    # ПОДКЛЮЧЕНИЕ К БД
    user = User.get(User.user_id == f'<@{ctx.author.id}>')
    warn = user.quantity_warn
    member = ctx.author

    # информация в консоль
    print('----------CTX----------')
    print(dir(ctx))
    print('-----------------')
    print(ctx.author.id)
    print('-----------------')
    print(f'@<{ctx.author.id}>')
    print('-----------------')
    print(member)

    # ГЕНЕРАЦИЯ СООБЩЕНИЯ
    emb = discord.Embed(title='Информация пользавателя', colour=discord.Color.blue())
    emb.add_field(name='WARN', value=f'{warn}')
    emb.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
    await ctx.send(embed=emb)


# ПРОВЕРКА СООБЩЕНИЯ НА ЗАПРЕЩЁННЫЕ СЛОВА
@bot.event
async def on_message(message):
    # ОБНОВИЛ ДАННЫЙ БД
    if message.author.mention not in list_users:
        # ДОБАВЛЕНИЕ НОВОГО ПОЛЬЗОВАТЕЛЯ В БД
        list_users.append(message.author.mention)
        with open('list_users.json', 'w') as outfile:
            json.dump(list_users, outfile)

        User.create(user_id=message.author.mention, quantity_warn=0)

    # тесты
    # print('запущена функция: on_message(message)')
    # print(message.content.lower())
    # print(type(message.content.lower()))

    # ПРОВЕРКИ СООБЩЕНИЙ НА ЗАПРЕЩЁННЫЙ КОНТЕНТ
    if message.author.mention == '<@738915154980503583>':  # если сообщение от бота
        pass

    elif check__warn_root_word(message) or message.content.lower() in ban_words:  # если бан слово
        # ДОБАВИЛ WARN ПОЛЬЗОВАТЕЛЮ И ВЫВЕЛ ОБ ЭТОМ СООБЩЕНИЯ
        add_warn_user(message)
        await warn_message(message)

        # информация в консоль
        print(f'DELETED ({message.author.mention}: {message.content})')

        await message.delete()
        await message.channel.send(f"{message.author.mention} !!!СООБЩЕНИЕ БЫЛО УДАЛЕНО!!! (ругательства запрещены)")

    elif 'https://' in message.content:  # если начинается как ссылка => удаляет и выводит причину
        # ДОБАВИЛ WARN ПОЛЬЗОВАТЕЛЮ И ВЫВЕЛ ОБ ЭТОМ СООБЩЕНИЯ
        add_warn_user(message)
        await warn_message(message)

        # информация в консоль
        print(f'DELETED ({message.author.mention}: {message.content})')

        await message.delete()
        await message.channel.send(f"{message.author.mention} В этом чате нельзя использовать ссылки!")

    else:  # если всё в порядке
        # информация в консоль
        print(f'OK ({message.author.mention}: {message.content})')
        await bot.process_commands(message)


# Теперь запускаем нашего бота
print('BOT_CONNECTED')
bot.run(token)
