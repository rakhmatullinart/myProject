
from commands import *
from command_System import command_list, command_list_admin

def get_answer(**kwargs):
    message = "Прости, не понимаю тебя. Напиши 'помощь', чтобы узнать мои команды"
    text = kwargs.get('key')
    text = text if text else 'photo'
    data = None

    if text.lower() in ['меню', 'привет', 'назад', 'отмена' ]:
        message = welcome(obj = kwargs.get('obj'))
        kwargs.get('obj').queue = []


    elif kwargs.get('obj').queue :
        q = kwargs.get('obj').queue
        for i in q:
            if text[:6] in ['https:', 'vk.com']:
                data = text[text.find('vk.com'):]
                text = 'vk.com'
            message = i(key = text, obj = kwargs.get('obj'), data = data, id = kwargs.get('id'), user_id = kwargs.get('user_id'))
            q.pop(0)
            break
    else:
        if text[0] in ['#', '?', '$']:
            data = text[1:]
            text = text[0]
        elif text[:6] in ['https:', 'vk.com']:
            data = text
            text = 'vk.com'

        distance = len(text)
        command = None
        key = ''
        for com in command_list:
            msg = ''
            for k in com.keys:
                flag = False
                try:
                    if int(k) == int(text):
                        d = 0
                        flag = True
                except:

                    d = damerau_levenshtein_distance(text.lower(), k)

                if d < distance or flag:
                    distance = d
                    command = com
                    key = k
                    if distance == 0:

                        msg = com.process(key=text.lower(), obj=kwargs.get('obj'), data=data)
                        if msg:
                            break
            if msg:
                message = msg
                break

        if distance < len(text) * 0.4 and distance != 0:
            message = command.process(key=key, obj=kwargs.get('obj'), data=data)
            message = 'Я понял ваш запрос как "%s"\n\n' % key + message


    return message

def get_answer_admin(**kwargs):
    msg = 'Сначала вам нужно пожтвердить заявку...'
    for com in command_list_admin:
        print(com)
        if kwargs.get('key').lower() in com.keys:
            msg = com.process(key = kwargs.get('key'))
    return msg

def damerau_levenshtein_distance(s1, s2):
   d = {}
   lenstr1 = len(s1)
   lenstr2 = len(s2)
   for i in range(-1, lenstr1 + 1):
       d[(i, -1)] = i + 1
   for j in range(-1, lenstr2 + 1):
       d[(-1, j)] = j + 1
   for i in range(lenstr1):
       for j in range(lenstr2):
           if s1[i] == s2[j]:
               cost = 0
           else:
               cost = 1
           d[(i, j)] = min(
               d[(i - 1, j)] + 1,  # deletion
               d[(i, j - 1)] + 1,  # insertion
               d[(i - 1, j - 1)] + cost,  # substitution
           )
           if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
               d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition
   return d[lenstr1 - 1, lenstr2 - 1]
