from commands_admin import *
from commands import *
from command_System import command_list, command_list_admin

def get_answer(**kwargs):
    message = "Прости, не понимаю тебя. Напиши 'помощь', чтобы узнать мои команды"
    text = kwargs.get('key')
    text = text if text else 'photo'
    data = None
    if text.lower() in ['меню', 'привет', 'назад' ]:
        message = welcome(obj = kwargs.get('obj'))
        kwargs.get('obj').queue = []

    elif kwargs.get('obj').queue :
        q = kwargs.get('obj').queue
        for i in q:
            message = i(key = text, obj = kwargs.get('obj'))
            q.pop(0)
            break
    else:
        if text[0] in ['#', '?', '$']:
            data = text[1:]
            text = text[0]
        elif text[:6] == 'vk.com':
            data = text
            text = 'vk.com'
        for com in command_list:
            if text in com.keys:
                msg = com.process(key = text.lower(), obj = kwargs.get('obj'), data = data)
                message = msg if msg else message
            if const.flag_break:
                const.flag_break = False
                break

    return message

def get_answer_admin(**kwargs):
    msg = 'Сначала вам нужно пожтвердить заявку...'
    for com in command_list_admin:
        print(com)
        if kwargs.get('key').lower() in com.keys:
            msg = com.process(key = kwargs.get('key'))
    return msg


