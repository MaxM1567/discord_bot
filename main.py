import discord
from discord.ext import commands
from interaction_db import User
import youtube_dl
import datetime as dt
import json
import os

# VERSION 0.4.0
# Изменения:
# 1. добавлен чат audit_log
# 3. незначительная оптимизация

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


# INFO (показывает пользователю информацию о нём)
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
    print(f'<@{ctx.author.id}>')
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

    # ТЕСТЫ
    # print(message)
    # print(dir(message))
    # print(message.channel.id)
    # message.channel.id (id текстового канала в виде int)
    # message.content (содержимое сообщения в виде str)

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

    elif message.channel.id == 958851176089141288:
        # информация в консоль
        print(f'OK ({message.author.mention}: {message.content})')
        await bot.process_commands(message)

    elif 'https://' in message.content or 'http://' in message.content:  # если начинается как ссылка => удаляет и выводит причину
        # ДОБАВИЛ WARN ПОЛЬЗОВАТЕЛЮ И ВЫВЕЛ ОБ ЭТОМ СООБЩЕНИЯ
        add_warn_user(message)
        await warn_message(message)

        # информация в консоль
        print(f'DELETED ({message.author.mention}: {message.content})')

        await message.delete()
        await message.channel.send(f"{message.author.mention} !!!СООБЩЕНИЕ БЫЛО УДАЛЕНО!!! (в этом чате ссылки запрещены)")

    else:  # если всё в порядке
        # информация в консоль
        print(f'OK ({message.author.mention}: {message.content})')
        await bot.process_commands(message)


# PLAY (начинает играть музыка по переданной ссылке)
@bot.command()
async def play(ctx, url: str):
    # ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ
    song_there = os.path.isfile("song.mp3")  # название файла музыки
    author_command = f'<@{ctx.author.id}>'

    # если музыка играет, бот высылает сообщение
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send(f'{author_command} !!!ДОЖДИТЕСЬ ПОКА БОТ ЗАКОНЧИТ ПРОИГРЫВАНИЕ ИЛИ ИСПОЛЬЗУЙТЕ КОМАНДУ <<stop>>!!!')
        return
    try:
        voice_user = discord.utils.get(ctx.guild.voice_channels, name=ctx.message.author.voice.channel.name)  # тоже канал пользователя
        voice_bot = discord.utils.get(bot.voice_clients, guild=ctx.guild)  # канал бота
    except AttributeError:
        await ctx.send(f'{author_command} !!!ДЛЯ НАЧАЛА ЗАЙДИТЕ В ГОЛОСОВОЙ КАНАЛ!!!')
        return

    # ПОДКЛЮЧЕНИЕ БОТА К ГОЛОСОВОМУ КАНАЛУ
    if voice_bot is None:  # если у бота нет голосового канала
        vc = await voice_user.connect()  # подключение к каналу пользователю

    else:  # иначе он перемещается к пользователю
        await voice_bot.disconnect()
        vc = await voice_user.connect()  # подключение к каналу пользователю

    # информация в консоль
    await ctx.send(f'{author_command} !!!БОТ НАЧАЛ ЗАГРУЗКУ МУЗЫКИ, ОЖИДАЙТЕ!!!')

    # РАБОТА С YOUTUBE_DL (загрузка и форматирование видео)
    # параметры загрузки видео
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    }

    # ЗАГРУЗКА ВИДЕО
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:   # загрузка видео
        ydl.download([url])

    for file in os.listdir("./"):  # преобразование файла в mp3
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")

    # НАЧИНАЕТ ИГРАТЬ МУЗЫКУ
    try:
        vc.play(discord.FFmpegPCMAudio('song.mp3'))
    except AttributeError:
        voice_bot.play(discord.FFmpegPCMAudio('song.mp3'))


# PAUSE (ставит музыку на паузу)
@bot.command()
async def pause(ctx):
    # ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ
    author_command = f'<@{ctx.author.id}>'
    voice_bot = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # информация в консоль
    if voice_bot.is_playing():
        voice_bot.pause()
    else:
        await ctx.send(f'<@{author_command}> !!!В ДАННЫЙ МОМЕНТ БОТ НЕ ПРОИГРЫВАЕТ МУЗЫКУ!!!')


# RESUME (ставит музыку на паузу)
@bot.command()
async def resume(ctx):
    # ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ
    author_command = f'<@{ctx.author.id}>'
    voice_bot = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # информация в консоль
    if voice_bot.is_paused():
        voice_bot.resume()
    else:
        await ctx.send(f'{author_command} !!!МУЗЫКА НЕ СТОИТ НА ПАУЗЕ!!!')


# PAUSE (ставит музыку на паузу)
@bot.command()
async def stop(ctx):
    # ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ
    voice_bot = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    # ОСТАНОВКА МУЗЫКИ
    voice_bot.stop()


# LEAVE (отключает бота от голосового канала)
@bot.command()
async def leave(ctx):
    # ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ
    author_command = f'<@{ctx.author.id}>'
    voice_bot = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # информация в консоль
    if voice_bot is None:
        await ctx.send(f'{author_command} !!!БОТ НЕ ПОДКЛЮЧЕН К ГОЛОСОВУ КАНАЛУ!!!')
    else:
        await voice_bot.disconnect()


# АУДИТ ЛОГИ
@bot.event
async def on_voice_state_update(member, before, after):
    # ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ
    audit_log_channel = bot.get_channel(958956405816168468)  # нужный канал

    # ПРОВЕРКА СОБЫТИЙ
    if before.channel is None and after.channel is not None:  # зашёл в голосовой канал

        # ГЕНЕРАЦИЯ СООБЩЕНИЯ
        emb = discord.Embed(colour=discord.Colour.green(),
                            description=f'Пользователь {member} подключился к голосовому каналу **{after.channel}**')

        emb.set_author(name=member, icon_url=member.avatar_url)
        emb.timestamp = dt.datetime.utcnow()
        await audit_log_channel.send(embed=emb)

    # left voice
    elif before.channel is not None and after.channel is None:  # вышел из голосового канала

        # ГЕНЕРАЦИЯ СООБЩЕНИЯ
        emb = discord.Embed(colour=discord.Colour.red(),
                            description=f'Пользователь {member} отключился от голосового канала **{before.channel}**')
        emb.timestamp = dt.datetime.utcnow()
        emb.set_author(name=member, icon_url=member.avatar_url)
        await audit_log_channel.send(embed=emb)

    elif before.channel is not None and after.channel is not None:  # переместился

        # ГЕНЕРАЦИЯ СООБЩЕНИЯ
        emb = discord.Embed(colour=discord.Colour.from_rgb(r=254, g=254, b=34),
                            description=f'Пользователь {member} отключился от голосового канала **{before.channel}** и подключился к **{after.channel}**')
        emb.timestamp = dt.datetime.utcnow()
        emb.set_author(name=member, icon_url=member.avatar_url)
        await audit_log_channel.send(embed=emb)

# Теперь запускаем нашего бота
print('BOT_CONNECTED')
bot.run(token)
