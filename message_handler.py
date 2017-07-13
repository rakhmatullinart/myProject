import vk_api
import base
from commands import *
from command_System import command_list

def get_answer(**kwargs):
    message = "Прости, не понимаю тебя. Напиши 'помощь', чтобы узнать мои команды"
    text = kwargs.get('key')
    data = None
    if text[0] in ['#', '?']:
        data = text[1:]
        text = text[0]
    for com in command_list:

        if text in com.keys:
            msg = com.process(key = text, step = kwargs.get('step'), kat = kwargs.get('kat'),
                                  user_id = kwargs.get('user_id'), data = data)

            message = msg if msg else message
    return message




