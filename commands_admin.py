import command_System
from commands import *
import temp, base, const
user_for_confirm = temp.User()
queue = []

def choose(**kwargs):
    text = kwargs.get('key')
    msg = None
    if text == '1':
        msg = 'Пользователь добавлен'
        queue.append(confirm)
    elif text =='2':
        msg = 'Введите рейтинг для изменения'
        queue.append(change_rate)
    elif text == '3':
        msg = 'Выберите нужную категорию'
        queue.append(change_kat)
    elif text == '4':
        msg = 'Заявка отклонена'
    return msg
choose_com = command_System.Command(add=True)
choose_com.keys = ['1', '2', '3']
choose_com.process = choose


def confirm(**kwargs):
    base.addUser(user_for_confirm)
    list_us_com.keys = [user_for_confirm.name.lower()]
    const.admin_step = ''
    return 'Вы одобрили заявку!'


def change_rate(**kwargs):
    user_for_confirm.rate = kwargs.get('key')
    return 'Рейтинг успешно изменен' + const.actions

def change_kat(**kwargs):
    user_for_confirm.kat = kwargs.get('key')
    return 'категория успешно изменена' + const.actions

