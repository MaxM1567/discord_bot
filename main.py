import discord
from discord.ext import commands
from interaction_db import User
import youtube_dl
import datetime as dt
import json
import os

# VERSION 0.5.2
# Изменения:
# 1. добавлены очки
# 2. очки начисляются за сообщения
# 3. очки начисляются за нахождение в голосовом канале
# 4. появился каталог пользователя
# 5. команды / удаляются из чата после выполнения
# 6. незначительная оптимизация

# ПАРАМЕТРЫ
token = 'NzM4OTE1MTU0OTgwNTAzNTgz.XyS2XQ.gKn-xiAJsg7hj3gPPDEBAkKz-dk'  # токен
PREFIX = '/'  # префикс
intents = discord.Intents.all()  # права

# системные каналы
chat_music = 958851176089141288
chat_catalog = 959472093756555396
chat_warn = 950115623508271166
chat_information = 959455666613923860
chat_audit_log = 958956405816168468
chat_afk = 958855439448162334

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
    warn_channel = bot.get_channel(chat_warn)  # нужный канал

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
    point = user.quantity_point
    member = ctx.author

    # тесты
    '''
    print('----------CTX----------')
    print(dir(ctx))
    print('-----------------')
    print(ctx.author.id)
    print('-----------------')
    print(f'<@{ctx.author.id}>')
    print('-----------------')
    print(member)
    '''
    # ГЕНЕРАЦИЯ СООБЩЕНИЯ
    emb = discord.Embed(title='Информация пользавателя', colour=discord.Color.blue())
    emb.add_field(name='POINT', value=f'{point}')
    emb.add_field(name='WARN', value=f'{warn}')
    emb.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
    await ctx.send(embed=emb)
    await ctx.message.delete()


# CATALOG (показывает пользователю его каталог)
@bot.command()
async def catalog(ctx):
    # ПОДКЛЮЧЕНИЕ К БД
    user = User.get(User.user_id == f'<@{ctx.author.id}>')
    point = user.quantity_point
    member = ctx.author

    # ГЕНЕРАЦИЯ СООБЩЕНИЯ
    emb = discord.Embed(title=f'{member.name} ({point} очков у вас)', colour=discord.Color.green())
    emb.add_field(name='ТОВАРЫ:', value='!товары пока отсутствуют, загляните позже!')
    emb.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
    await ctx.send(embed=emb)
    await ctx.message.delete()


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

    elif message.channel.id == chat_catalog and (('/catalog' not in message.content)  # если сообщение в МАГАЗИН
                                                 and ('/buy' not in message.content)):

        # ДОБАВИЛ WARN ПОЛЬЗОВАТЕЛЮ И ВЫВЕЛ ОБ ЭТОМ СООБЩЕНИЯ
        add_warn_user(message)
        await warn_message(message)

        # информация в консоль
        print(f'DELETED ({message.author.mention}: {message.content})')

        await message.delete()
        await message.channel.send(
            f"{message.author.mention} !!!СООБЩЕНИЕ БЫЛО УДАЛЕНО!!! (ознакомитесь с <#{chat_information}>)")

    elif message.channel.id == chat_music and (('/play' in message.content)  # если сообщение в МУЗЫКА
                                               or ('/resume' in message.content)
                                               or ('/pause' in message.content)
                                               or ('/stop' in message.content)
                                               or ('/leave' in message.content)):

        print(message.content)

        # ПОДКЛЮЧЕНИЕ К БД
        user = User.get(User.user_id == message.author.mention)
        point = user.quantity_point

        # информация в консоль
        print(f'OK ({message.author.mention}: {message.content}; point: {int(point) + 10})')

        # ОБНОВИЛ ДАННЫE БД
        user = User(quantity_point=str(int(point) + 10))
        user.user_id = message.author.mention  # Тот самый первичный ключ
        user.save()

        await bot.process_commands(message)

    elif check__warn_root_word(message) or message.content.lower() in ban_words:  # если бан слово
        # ДОБАВИЛ WARN ПОЛЬЗОВАТЕЛЮ И ВЫВЕЛ ОБ ЭТОМ СООБЩЕНИЯ
        add_warn_user(message)
        await warn_message(message)

        # информация в консоль
        print(f'DELETED ({message.author.mention}: {message.content})')

        await message.delete()
        await message.channel.send(f"{message.author.mention} !!!СООБЩЕНИЕ БЫЛО УДАЛЕНО!!! (ругательства запрещены)")

    elif 'https://' in message.content or 'http://' in message.content:  # если ссылка
        # ДОБАВИЛ WARN ПОЛЬЗОВАТЕЛЮ И ВЫВЕЛ ОБ ЭТОМ СООБЩЕНИЯ
        add_warn_user(message)
        await warn_message(message)

        # информация в консоль
        print(f'DELETED ({message.author.mention}: {message.content})')

        await message.delete()
        await message.channel.send(
            f"{message.author.mention} !!!СООБЩЕНИЕ БЫЛО УДАЛЕНО!!! (в этом чате ссылки запрещены)")

    else:  # всё в порядке

        # ПОДКЛЮЧЕНИЕ К БД
        user = User.get(User.user_id == message.author.mention)
        point = user.quantity_point

        # информация в консоль
        print(f'OK ({message.author.mention}: {message.content}; point: {int(point) + 10})')

        # ОБНОВИЛ ДАННЫE БД
        user = User(quantity_point=str(int(point) + 10))
        user.user_id = message.author.mention  # Тот самый первичный ключ
        user.save()

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
        await ctx.send(
            f'{author_command} !!!ДОЖДИТЕСЬ ПОКА БОТ ЗАКОНЧИТ ПРОИГРЫВАНИЕ ИЛИ ИСПОЛЬЗУЙТЕ КОМАНДУ <<stop>>!!!')
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
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:  # загрузка видео
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
        await ctx.message.delete()


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
        await ctx.message.delete()


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
    await ctx.message.delete()


# ОЧКИ ЗА ВРЕМЯ
def points_for_time(user_id):
    user = User.get(User.user_id == f'<@{user_id}>')

    last_con = user.last_con
    last_dis_con = user.last_dis_con
    point = user.quantity_point

    last_con = list(map(lambda x: int(x), (((((str(last_con)[:3] + str(last_con)[3:].replace('0', '')).split())[0]).split('-')) + ((((str(last_con)).split())[1]).split(':')))))
    for i in range(4):
        if str(last_con[i])[0] == '0':
            last_con[i] = int(str(last_con[i][0:]))

    last_dis_con = list(map(lambda x: int(x), (((((str(last_dis_con)[:3] + str(last_dis_con)[3:].replace('0', '')).split())[0]).split('-')) + ((((str(last_dis_con)).split())[1]).split(':')))))
    for i in range(4):
        if str(last_dis_con[i])[0] == '0':
            last_con[i] = int(str(last_dis_con[i][0:]))

    communication_time = ((str(dt.datetime(last_dis_con[0], last_dis_con[1], last_dis_con[2], last_dis_con[3], last_dis_con[4]) - (dt.datetime(last_con[0], last_con[1], last_con[2], last_con[3], last_con[4]))))[:-3]).split(':')

    for i in range(len(communication_time)):
        if str(communication_time[i])[0] == '0':
            communication_time[i] = str(communication_time[i][0:])

    time = (int(communication_time[0]) * 60) + (int(communication_time[1].replace('0', '')))

    if time != 0:
        # ОБНОВИЛ ДАННЫE БД
        user = User(quantity_point=str(int(point) + (7 * time)))
        user.user_id = f'<@{user_id}>'  # Тот самый первичный ключ
        user.save()


# УСТАНАВЛИВАЕТ ВРЕМЯ ПОСЛЕДНЕГО ВХОДА И ВЫХОДА ПОЛЬЗОВАТЕЛЯ
def date_registration(user_id, action):

    if user_id == 738915154980503583:
        pass

    elif action == 'con':
        # ОБНОВИЛ ДАННЫE БД
        user = User(last_con=str(dt.datetime.now().strftime('%Y-%m-%d %H:%M')))
        user.user_id = f'<@{user_id}>'  # Тот самый первичный ключ
        user.save()

    elif action == 'dis_con' or action == 'moved_afk':
        # ОБНОВИЛ ДАННЫE БД
        user = User(last_dis_con=str(dt.datetime.now().strftime('%Y-%m-%d %H:%M')))
        user.user_id = f'<@{user_id}>'  # Тот самый первичный ключ
        user.save()

        points_for_time(user_id)
    else:
        pass


# АУДИТ ЛОГИ
@bot.event
async def on_voice_state_update(member, before, after):
    # ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ
    audit_log_channel = bot.get_channel(chat_audit_log)  # нужный канал

    # ПРОВЕРКА СОБЫТИЙ
    if before.channel is None and after.channel is not None:  # зашёл в голосовой канал

        # ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ
        action = 'con'

        # ГЕНЕРАЦИЯ СООБЩЕНИЯ
        emb = discord.Embed(colour=discord.Colour.green(),
                            description=f'Пользователь {member} подключился к голосовому каналу **{after.channel}**')

        emb.set_author(name=member, icon_url=member.avatar_url)
        emb.timestamp = dt.datetime.utcnow()
        await audit_log_channel.send(embed=emb)

    # left voice
    elif before.channel is not None and after.channel is None:  # вышел из голосового канала

        # ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ
        action = 'dis_con'

        # ГЕНЕРАЦИЯ СООБЩЕНИЯ
        emb = discord.Embed(colour=discord.Colour.red(),
                            description=f'Пользователь {member} отключился от голосового канала **{before.channel}**')
        emb.timestamp = dt.datetime.utcnow()
        emb.set_author(name=member, icon_url=member.avatar_url)
        await audit_log_channel.send(embed=emb)

    else:  # переместился

        # ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ
        if after.channel.id == chat_afk:
            action = 'moved_afk'
        else:
            action = 'moved'

        # ГЕНЕРАЦИЯ СООБЩЕНИЯ
        emb = discord.Embed(colour=discord.Colour.from_rgb(r=254, g=254, b=34),
                            description=f'Пользователь {member} отключился от голосового канала **{before.channel}** и подключился к **{after.channel}**')
        emb.timestamp = dt.datetime.utcnow()
        emb.set_author(name=member, icon_url=member.avatar_url)
        await audit_log_channel.send(embed=emb)

    date_registration(member.id, action)


# Теперь запускаем нашего бота
print('BOT_CONNECTED')
bot.run(token)
