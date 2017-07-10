import vk_api
import base
from commands import *
from command_System import command_list

def get_answer(**kwargs):
    message = "Прости, не понимаю тебя. Напиши 'помощь', чтобы узнать мои команды"
    for com in command_list:
        if kwargs.get('key') in com.keys:
            message = com.process(key = kwargs.get('key'), step = kwargs.get('step'), kat = kwargs.get('kat'))
    return message




