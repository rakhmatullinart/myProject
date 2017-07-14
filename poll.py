# -*- coding: utf-8 -*-
import vk_api, logging, os
from vk_api.longpoll import VkLongPoll, VkEventType
import const
from message_handler import get_answer
from command_System import command_list
from commands import *
from info import Choice
from info import objects

logfile = 'logs.log'  # 'logs.log', for example
logging.basicConfig(format=u'%(asctime)s | %(message)s',
                    level=logging.WARNING, filename=logfile)  # edit log's filename if needed


while True:
    try:
        vk_session = vk_api.VkApi(token=const.token)

        try:
            vk_session.auth()
        except vk_api.AuthError as error_msg:
            print(error_msg)
            logging.log(logging.ERROR, error_msg)
            break

        longpoll = VkLongPoll(vk_session)
        vk = vk_session.get_api()


        for event in longpoll.listen():

            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                        #try:
                            if event.user_id not in const.user_ids:
                                const.user_ids.append(event.user_id)
                                inf = Choice(event.user_id)
                            else:
                                for i in objects:
                                    if i.user_id == event.user_id:
                                        inf = i
                                        break
                            text= get_answer(key=event.text, obj = inf)

                            attach = None
                            if text[-1] == '&':
                                attach = text[-26:-1]
                                text = text[:-26]

                            vk.messages.send(user_id=event.user_id, message=text, attachment = attach)


                         #except Exception as e:
                          #  logging.log(logging.ERROR, 'CANT CONNECT VK ' + str(e))

    except KeyboardInterrupt:
        exit()
