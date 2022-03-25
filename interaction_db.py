# Импортируем библиотеку, соответствующую типу нашей базы данных
# В данном случае импортируем все ее содержимое, чтобы при обращении не писать каждый раз имя библиотеки, как мы делали в первой статье
from peewee import *

# Создаем соединение с нашей базой данных
# В нашем примере у нас это просто файл базы
conn = SqliteDatabase('ds_bot_db.db')

# Создаем курсор - специальный объект для запросов и получения данных с базы
cursor = conn.cursor()


# Определяем базовую модель о которой будут наследоваться остальные
class BaseModel(Model):
    class Meta:
        database = conn  # соединение с базой, из шаблона выше


# Определяем модель исполнителя
class User(BaseModel):
    user_id = AutoField(column_name='user')
    quantity_warn = TextField(column_name='warn_user', null=True)

    class Meta:
        table_name = 'Users'


'''
user = User.get(User.user_id == '<@490211131109933056>')
print(user.user_id, user.quantity_warn)  # artist:  1 AC/DC
'''
conn.close()
