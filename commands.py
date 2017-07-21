import command_System
import sqlite3 as sqlite
import const, base, temp
import shutil
from const import users_steps, users_callback
import vk_api
import requests, os
import copy


vk_session = vk_api.VkApi(token=const.token)
vk_session.auth()
up = vk_api.VkUpload(vk_session)
vk = vk_session.get_api()

user = temp.User()


def mup(data):
    data  = data[0].upper() + data[1:]
    return data

# приветсвенное сообщение
def welcome(**kwargs):
    obj = kwargs.get('obj')
    message = const.welcomeClient

    obj.callback.clear()
    message += '1. Список категорий'
    message += '\n2. Заявка на добавление пользователя'
    message += '\n3. Меня внесли сюда незаконно'
    message += '\n4. Отключить бота для диалога с администратором сообщества'
    obj.callback['1'] = 'list_kats'
    obj.callback['2'] = 'request'
    obj.callback['3'] = 'illegal'
    if obj.editor:
        message+= '\n5. Админ-панель'
        obj.callback['5'] = 'admin'
    obj.step = 'menu'


    return message

welCommand = command_System.Command()

welCommand.keys = ['привет', 'здравствуй', 'здравствуйте', 'start', 'меню']
welCommand.description = 'Главное меню'
welCommand.process = welcome


def standby(**kwargs):
    if kwargs.get('obj').step == 'menu':
        msg = 'Бот отключен! Вы можете в любой момент включить его обратно, отправив "1".'
        kwargs.get('obj').offline = True
        return msg
    else: return
standby_com = command_System.Command()
standby_com.keys = ['4']
standby_com.process = standby


def list_kats(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'menu':
        message = ''
        if obj.callback.get(kwargs.get('key')) == 'request':
            obj.step = 'add_user'
            message = 'Сейчас вы оформите заявку на добавление нового пользователя, ' \
                      'после чего она будет отправлена администратору на рассмотрение\n\nОтправьте имя и фамилию пользователя'
            obj.queue.append(add_user)
        elif obj.callback.get(kwargs.get('key')) == 'illegal':
            message = 'Напишите полную информацию в сообщении, чтобы администратор смог отреаировать на это сообщение'
            obj.queue.append(forward_mes)
        elif obj.callback.get(kwargs.get('key')) == 'list_kats':
            obj.step = 'kat_choose'
            message = 'Список категорий:'
            count = 1
            for key in base.giveElements():
                message += '\n'+ str(count) +'. ' + key
                obj.callback[str(count)] =  key
                count += 1
        return message
    else:
        return
list_kats_com = command_System.Command()
list_kats_com.keys = ['1', '2', '3']
list_kats_com.process = list_kats


#выбор категории
def kat_choose(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'kat_choose':
        obj.kat = obj.callback.get(kwargs.get('key'))
        obj.callback.clear()
        message = 'Категория выбрана! Введите имя или ссылку в формате vk. com/ssylka (строка без пробелов).'
        obj.step = 'confirm_name'
        obj.queue.append(list_us)
        return message
    else: return

kat = command_System.Command()
count = len(base.giveElements())
kat.keys = map(str, range(1, count+2))
kat.process = kat_choose

#информация
def info(**kwargs):
    msg = ''
    for c in command_System.command_list:
        msg += c.keys[0] + ' - ' + c.description + '\n'
    return msg

infoCommand = command_System.Command()

infoCommand.keys = ['помощь', 'помоги', 'help']
infoCommand.description = const.commands
infoCommand.process = info


#показ всех пользователей категории
def show_all(**kwargs):
    obj = kwargs.get('obj')
    if obj.kat:
        text, rating = '', ''
        for user in base.typeFinder(obj.kat):
            text = '\n\U0001F464'+ user.name + ' ' + user.surname
            rating = "\nСтатус: " + str(user.rate)
            if user.reason:
                rating += '\nПричина: ' + str(user.reason)


        return text+rating
    else: return 'Вы не находитесь ни в одной категории, вернитесь в главное меню'
show = command_System.Command()
show.keys = ['остальные', 'показать всех', 'все']
show.process = show_all


#отображение пользователей с выбранным именем
def list_us(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'confirm_name':
        msg = 'Список пользователей:\n'
        data = kwargs.get('data')
        name = ''
        if len(kwargs.get('key').split()) > 1:
            obj.step = 'confirm_surname'
            name = kwargs.get('key').lower()
            msg += list_surnames(name = name, obj = obj)
        else:
            if data:
                q = base.getUsers(data.lower(), obj.kat)
                obj.prev_r = data
            else:
                q = base.getUsers(kwargs.get('key').lower(), obj.kat)
                obj.prev_r = kwargs.get('key')
            if q:
                count = 1
                obj.callback.clear()
                for me in q:
                    msg += str(count) + '. ' + ' '.join(map(mup, me.split())) + '  '
                    if base.get_user_link(me) != 'vk.com/link':
                        msg += base.get_user_link(me) + '\n'
                    obj.callback[str(count)] = me
                    count += 1
                msg += '\nВведите цифру'
                obj.step = 'confirm_surname'

                obj.queue.append(list_surnames)
            else:
                msg = 'Пользователей с такими данными не найдено в этой категории. Попробуйте еще раз'
        return msg
    else:
        return
list_us_com = command_System.Command()
list_us_com.keys = base.get_users().keys()
list_us_com.keys = ['vk.com']
list_us_com.process = list_us


#выбор пользователей по фамилии
def list_surnames(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'confirm_surname':
        if kwargs.get('name'):
            obj.name, obj.surname = kwargs.get('name').split()
        else:
            data = obj.callback.get(kwargs.get('key'))
            obj.name, obj.surname = data.split()

        user_local = base.defineUser(' '.join([obj.name, obj.surname]), obj.kat)
        if user_local != None:

            text = mup(user_local.name) + ' ' + mup(user_local.surname)
            rating = "\nСтатус: " + str(user_local.rate) + '\n'
            if user_local.reason:
                rating += 'Причина: ' + str(user_local.reason) + '\n'
            if user_local.link:
                rating += user_local.link
            if not kwargs.get('name'):
                extra = "\nНапиши 0 чтобы вернуться к списку\n" \
                        "Напиши 9 чтобы показать доказательства"
            else:
                extra = "\nНапиши 9 чтобы показать доказательства"
            path = 'userImages/' + text
            photo = up.photo_messages(path+'/av.jpg')
            attach = 'photo'+ str(photo[0].get('owner_id'))+'_'+str(photo[0].get('id'))+'&'
            obj.callback.clear()
            obj.step = 'extra'
            return text + rating + extra + attach

        else:
            return 'Пользователь не найден'
    else: return

list_surnames_com = command_System.Command()
list_surnames_com.keys = map(str, range(1, 20))
list_surnames_com.process = list_surnames


def return_to_list(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'extra' and obj.prev_r:

        obj.step = 'confirm_name'
        data = None
        if obj.prev_r[:3] == 'vk.':
            data = obj.prev_r
        msg = list_us(obj = obj, key = obj.prev_r, data = data)
        obj.prev_r = ''
        return msg
    else: return
return_to_list_com = command_System.Command()
return_to_list_com.keys = ['0']
return_to_list_com.process = return_to_list


def show_proof(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'extra':
        path = 'userImages/' + obj.name + ' ' + obj.surname
        try:
            photo = up.photo_messages(path + '/proof.jpg')
            attach = 'photo' + str(photo[0].get('owner_id')) + '_' + str(photo[0].get('id')) + '&'
            msg =  'Лови' + attach
        except:
            msg =  'У этого пользователя нет доказательств'
        return msg
    else:
        return
show_proof_com = command_System.Command()
show_proof_com.keys = ['9']
show_proof_com.process = show_proof

#админ-панель
def admin_panel(**kwargs):
    obj = kwargs.get('obj')
    if obj.editor:
        msg = 'Выберите, что вы хотите отредактировать\n' \
              '1. Категории\n' \
              '2. Пользователи\n' \
              '3. Заявки на добавление пользователей'
        obj.step = 'edit'
        return msg

    else: return 'Вы не обладаете правами доступа, чтобы использовать данную команду'
admin_panel_com = command_System.Command()
admin_panel_com.keys = ['админ-панель', 'админ', '5']
admin_panel_com.process = admin_panel


#показ заявок

def us_requests(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'edit':
        msg = 'Список заявок:\n'
        if const.requests_users:
            for us in const.requests_users.items():
                me = us[1]
                print(me.name, me.surname)
                msg += us[0]+'. ' + me.name + ' ' + me.surname+ '\n'
            obj.queue.append(show_detailed_request)
            msg += 'Выберите заявку, которую хотите рассмотреть'
            return msg
        else: return 'Нет новых заявок\n' + admin_panel(obj = obj)
    return
us_com  = command_System.Command()
us_com.keys = ['3']
us_com.process = us_requests


def show_detailed_request(**kwargs):
    obj = kwargs.get('obj')

    if kwargs.get('edit'):
        temp = const.user_edit
    else:
        key = kwargs.get('key')
        const.key = key
        temp = const.requests_users.get(key)
        const.user_edit = temp
    text = temp.name + ' ' + temp.surname
    stat = "\nСтатус: " + str(temp.stat) + '\n'
    if temp.reason != None:
        stat += '\n' + temp.reason
    if temp.link != 'vk.com/link':
        stat += temp.link
    else: stat += '\nСсылка отсутсвует'
    stat += '\nКатегория:' + temp.kat
    extra = '\nВы можете:\n' \
            '1. Одобрить заявку\n' \
            '2. Изменить статус\n' \
            '3. Изменить категорию\n' \
            '4. Отклонить заявку\n'
    forward_mes = str(temp.forward)
    path = 'userImages/' + text
    photo = up.photo_messages(path + '/av.jpg')
    attach = 'photo' + str(photo[0].get('owner_id')) + '_' + str(photo[0].get('id')) + '&'
    obj.callback.clear()
    obj.step = 'extra'
    return text + stat + extra + attach + forward_mes

# разбор заявок в админе
def choose(**kwargs):
    text = kwargs.get('key')
    obj = kwargs.get('obj')
    msg = None
    obj.callback.clear()
    if obj.step == 'extra':
        if text == '1':
            msg = 'Отправьте фото с доказательствами'
            obj.queue.append(attach_proof)
        elif text =='2':
            msg = 'Выберите статус:\n' \
                  '1. Хороший\n' \
                  '2. Плохой\n' \
                  '3. С осторожностью'
            obj.queue.append(change_rate)
        elif text == '3':
            msg = 'Выберите нужную категорию'
            count = 1
            for key in base.giveElements():
                msg += '\n' + str(count) + '. ' + key
                obj.callback[str(count)] = key
                count += 1
            obj.queue.append(change_kat)
        elif text == '4':
            msg = decline(obj = obj)
        return msg
    else: return
choose_com = command_System.Command()
choose_com.keys = ['1', '2', '3']
choose_com.process = choose

def attach_proof(**kwargs):
    text = kwargs.get('key')
    path = mup(const.user_edit.name) + ' ' + mup(const.user_edit.surname)

    if text == 'photo':
        msg = 'Произошла ошибка. Возможно, проблемы с сервером'
        params = {'out': '0', 'offset':'0', 'count':'30',
                  'time_offset': '0', 'filters':'0', 'preview_length': '0',
                  'last_message_id':'0', 'access_token': const.token}
        url = 'https://api.vk.com/method/messages.get'
        r = requests.get(url, params)
        r = r.json()
        for key in r['response'][1]:
            if key == 'attachment':
                try:
                    photo_url = r['response'][1][key]['photo']['src_big']
                    r = requests.get(photo_url)
                    with open('userImages/' + path + '/proof.jpg', 'wb+') as f:
                        for buf in r.iter_content(1024):
                            if buf:
                                f.write(buf)

                    msg = confirm(obj = kwargs.get('obj'))

                except:
                    pass
        return msg
    else:
        return show_detailed_request(obj = kwargs.get('obj'), edit = const.user_edit)

def confirm(**kwargs):
    obj = kwargs.get('obj')
    base.addUser(const.user_edit)
    list_us_com.keys = [const.user_edit.name]
    name = const.user_edit.name + ' ' + const.user_edit.surname
    text, attach = show_profile()
    text = 'Ваша заявка на добавление пользователя '+ name + ' одобрена\n' + text
    vk.messages.send(user_id=const.user_edit.user_id, message = text, attachment = attach)
    const.requests_users.pop(const.key) #not working
    edit_user_com.keys = [str(int(edit_user_com.keys[-1])+1)]
    const.key = ''
    obj.step = ''

    return 'Вы одобрили заявку!\n\n' + welcome(obj = obj)

def  show_profile():
    temp = const.user_edit
    text = mup(temp.name) + ' ' + mup(temp.surname)
    stat = "\nСтатус: " + str(temp.stat) + '\n'
    if temp.reason != None:
        stat += temp.reason + '\n'
    if temp.link != 'vk.com/link':
        stat += temp.link
    else:
        stat += '\nСсылка отсутсвует'
    stat += '\nКатегория:' + temp.kat
    path = 'userImages/' + text
    photo = up.photo_messages(path + '/av.jpg')
    attach = 'photo' + str(photo[0].get('owner_id')) + '_' + str(photo[0].get('id'))
    return text + stat, attach


def change_rate(**kwargs):
    num = kwargs.get('key')
    obj = kwargs.get('obj')
    msg = 'Выберите причину:\n'
    if num == '1':
        msg += '1. Хорошо заплатил\n' \
               '2. Вежливый\n' \
               '3. Предоставил чёткое ТЗ'
        obj.callback['1'] = 'Хорошо заплатил'
        obj.callback['2'] = 'Вежливый'
        obj.callback['3'] = 'Предоставил чёткое ТЗ'
        const.user_edit.stat = 'Хороший'
        obj.queue.append(confirm_rate)
    elif num == '2':
        msg += '1. Не платит\n' \
               '2. Отказался от оплаты\n' \
               '3. Грубит\n' \
               '4. Неадекватное поведение'
        obj.callback['1'] = 'Не платит'
        obj.callback['2'] = 'Отказался от оплаты'
        obj.callback['3'] = 'Грубит'
        obj.callback['4'] = 'Неадекватное поведение'
        const.user_edit.stat = 'Плохой'
        obj.queue.append(confirm_rate)
    elif num == '3':
        const.user_edit.stat = 'С осторожностью'
        msg = confirm_rate(obj = obj, key = None)
    else:
        msg = 'Нет такого в списке'
    return msg

def confirm_rate(**kwargs):
    obj = kwargs.get('obj')
    const.user_edit.reason = obj.callback.get(kwargs.get('key'))
    msg = 'Статус успешно изменен\n' + show_detailed_request(obj = obj, edit = const.user_edit)
    return msg


def change_kat(**kwargs):
    const.user_edit.kat = kwargs.get('key')
    return 'Категория успешно изменена' + show_detailed_request(obj = kwargs.get('obj'), edit = const.user_edit)


def decline(**kwargs):
    obj = kwargs.get('obj')
    try:
        name = const.user_edit.name + ' ' + const.user_edit.surname
        vk.messages.send(user_id=const.user_edit.user_id,
                         message='Ваша заявка на добавление пользователя %s отклонена'%name)
        shutil.rmtree('userImages/' + name)
        const.requests_users.pop(const.key)
        const.key = ''
        obj.step = ''
    except:
        pass
    return 'Вы отклонили заявку' + welcome(obj = obj)

#редактирование категорий

def kats_edit(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'edit':
        if obj.editor:
            msg = 'Чтобы добавить категорию, напишите ?название категории\n' \
                  'Чтобы удалить категорию, напишите #номер категории\n' \
                  '(Префикс обязателен)\n' \
                  'Список доступных категорий:'
            count = 1
            for key in base.giveElements():
                msg += '\n'+str(count) + '. ' + key
                obj.callback[str(count)] = key
                count +=1
            obj.step = 'edit_kat'
            return msg
        else: return 'Вы не обладаете правами доступа, чтобы использовать данную команду'
    else: return
kat_edit_com = command_System.Command()
kat_edit_com.keys = ['категории', '1']
kat_edit_com.process = kats_edit

#добавление и удаление категории

def delete_kat(**kwargs):
    obj = kwargs.get('obj')
    data = obj.callback.get(kwargs.get('data'))
    if obj.editor and obj.step == 'edit_kat':
        if base.isEmptyKat(data):
            base.delete_kat(data)
            msg = 'Категория удалена\n'
            obj.step = 'edit'
            msg+=kats_edit(obj = obj)
        else:
            msg ='Категория не может быть удалена, так как в ней есть данные.\n'\
                                       'Сначала удалите пользователей из этой категории'
        return msg
    else: return
delete_kat_com = command_System.Command()
delete_kat_com.keys = ['#']
delete_kat_com.process = delete_kat

def add_kat(**kwargs):
    obj = kwargs.get('obj')
    data = kwargs.get('data')
    if obj.step == 'edit_kat':
        if base.add_kat(data):
            msg = 'Категория успешно добавлена\n'
            obj.step = 'edit'
            msg += kats_edit(obj=obj)
        else:
            msg = 'Ошибка добавления категории. Возможно, данная категория уже существует'
        return msg
    else:
        return

add_kat_com = command_System.Command()
add_kat_com.keys = ['?']
add_kat_com.process = add_kat

#редактирование пользователей
def users_edit(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'edit' and obj.editor:
        msg = 'Выберите человека (Введите номер)\n'
        temp = base.giveUsers()
        count = 1
        obj.callback.clear()
        for kat in base.giveElements():
            msg += kat + '\n'
            for u in temp[kat]:

                if u:
                    msg += '\U0001F464'+str(count) +'. ' + u.name + ' ' + u.surname + '\n'
                    obj.callback[str(count)] = u.name + ' ' + u.surname
                    count += 1

        return msg
    else: return 'Вы не обладаете правами доступа, чтобы использовать данную команду'
user_edit_com = command_System.Command()
user_edit_com.keys = ['пользователи','2']
user_edit_com.process = users_edit


#получение данных пользователя для редактирования
def edit_user_info(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'edit_user_info':
        if obj.editor:
            name = obj.callback.get(kwargs.get('key'))
            db = sqlite.connect(const.dbPath)
            cur = db.cursor()
            cur.execute('SELECT * FROM Users WHERE ("firstName" || " " || "lastName") = (?)', (name,))
            c = cur.fetchone()
            us = temp.User()
            us.set_full_data(*c)
            text = mup(us.name) + ' ' + mup(us.surname)
            rating = "\nСтатус: " + str(us.rate)
            if us.reason:
                rating += '\nПричина: ' +str(us.reason) +'\n'
            rating += us.link
            path = 'userImages/' + text
            photo = up.photo_messages(path + '/av.jpg')
            attach = 'photo' + str(photo[0].get('owner_id')) + '_' + str(photo[0].get('id')) + '&'
            extra_info = '\nВыберите действие:\n' \
                         '1. Изменить информацию\n' \
                         '2. Удалить пользователя'
            obj.edit = name
            obj.step = 'process_user_info'
            const.flag_break = True
            return text + rating + extra_info + attach
        else: return 'Вы не обладаете правами доступа, чтобы использовать данную команду'
    else: return
edit_user_com = command_System.Command()
edit_user_com.keys = map(str, list(range(len(base.get_user_names())+2)))
edit_user_com.process = edit_user_info






def change_info(**kwargs):
    pass
change_info_com = command_System.Command()
change_info_com.keys = ['1']
change_info_com.process = change_info

def delete_user(**kwargs):
    if kwargs.get('obj').step == 'process_user_info':
        name = kwargs.get('obj').edit
        db = sqlite.connect("clientbase.db")
        cur = db.cursor()
        cur.execute('DELETE FROM Users WHERE ("firstName" || " " || "lastName") = (?)', (name,))
        db.commit()
        shutil.rmtree('userImages/' + name)
        list_us_com.keys_remove([name])
        msg = 'Пользователь удален\n'
        kwargs.get('obj').step = 'edit'
        msg += users_edit(obj = kwargs.get('obj'))

        return msg
    else: return

delete_user_com = command_System.Command()
delete_user_com.keys = ['2']
delete_user_com.process = delete_user


def add_user(**kwargs):
    if kwargs.get('obj').step == 'add_user':
        msg = 'Должны присутствовать ИМЯ и ФАМИЛИЯ'
        try:
            user.name, user.surname = kwargs.get('key').lower().split()
            kwargs.get('obj').queue.append(stat_choose)
            msg = 'Выберите статус:\n' \
                  '1. Хороший\n' \
                  '2. Плохой\n' \
                  '3. С осторожностью'
            obj = kwargs.get('obj')
            obj.callback['1'] = 'Хороший'
            obj.callback['2'] = 'Плохой'
            obj.callback['3'] = 'С осторожностью'
            user.user_id = kwargs.get('user_id')
        except:
            kwargs.get('obj').queue.append(add_user)

        return msg
    else: return

def stat_choose(**kwargs):
    obj = kwargs.get('obj')
    num = kwargs.get('key')
    user.stat = obj.callback.get(num)
    obj.callback.clear()
    msg = 'Выберите причину:\n'
    if num == '1':
        msg += '1. Хорошо заплатил\n' \
               '2. Вежливый\n' \
               '3. Предоставил чёткое ТЗ'
        obj.callback['1'] = 'Хорошо заплатил'
        obj.callback['2'] = 'Вежливый'
        obj.callback['3'] = 'Предоставил чёткое ТЗ'
        obj.queue.append(define_reason)
    elif num == '2':
        msg += '1. Не платит\n' \
               '2. Отказался от оплаты\n' \
               '3. Грубит\n' \
               '4. Неадекватное поведение'
        obj.callback['1'] = 'Не платит'
        obj.callback['2'] = 'Отказался от оплаты'
        obj.callback['3'] = 'Грубит'
        obj.callback['4'] = 'Неадекватное поведение'
        obj.queue.append(define_reason)
    elif num == '3':
        msg = adding_rate(obj = obj)
    else:
        msg = 'Нет такого в списке'
    return msg

def define_reason(**kwargs):
    obj = kwargs.get('obj')
    user.reason = obj.callback.get(kwargs.get('key'))
    msg = adding_rate(obj = obj)
    return msg

def adding_rate(**kwargs):
    kwargs.get('obj').queue.append(adding_kat)
    msg = 'Выберите категорию в которую хотите добавить.'
    count = 1
    obj = kwargs.get('obj')
    obj.callback.clear()
    for kat in base.giveElements():
        msg += '\n'+str(count)+'. '+kat
        obj.callback[str(count)] = kat
        count+=1
    return msg

def adding_kat(**kwargs):
    obj = kwargs.get('obj')
    kat = obj.callback.get(kwargs.get('key'))
    user.kat = kat

    obj.queue.append(adding_link)
    return 'Введите ссылку пользователя вконтакте - фото будет взято с аватара пользователя\n' \
           'Если ссылка отсутсвует пришлите в ответ "нет"'


def confirm_awards(**kwargs):
    #adding awards here!
    obj = kwargs.get('obj')
    msg = 'Перешлите сообщения из диалога с администратором, чтобы подтвердить свою кандидатуру.' \
          ' Если хотите открыть диалог с администратором, вернитесь в главное меню и выключите бота.' \
          'Затем оформите заявку снова и прикрепите пересланные сообщения'
    obj.queue.append(final_add)
    return msg


def final_add(**kwargs):
    user.forward = kwargs.get('id')
    replica = copy.copy(user)
    const.requests_users[str(const.last_k)] = replica
    const.last_k += 1
    user.reset()

    return 'Ваша заявка отправлена на рассмотрение администратору!\n' \
           'Если она будет одобрена, ваш профиль появится в выбранной категории' + welcome(obj = kwargs.get('obj'))

def adding_link(**kwargs):
    path = user.name + ' ' + user.surname
    user.name = mup(user.name)
    user.surname = mup(user.surname)
    try:
        os.mkdir('userImages/' + path)
    except:
        user.reset()
        return 'Пользователь с такими данными уже существует'
    link = kwargs.get('key')
    if link != 'нет':
        link = link[link.find('vk.com'):]
        user.link = link
        msg = adding_image_via_link(key = link, obj=kwargs.get('obj'), path = path)
        return msg
    else:
        user.link = 'vk.com/link'
        kwargs.get('obj').queue.append(setting_image)
        return 'Чтобы установить фотографию - пришлите её\n' \
               'Если хотите установить фото по умолчанию - отправьте "1"'



def adding_image_via_link(**kwargs):
    text = kwargs.get('key')
    path = kwargs.get('path')
    if text[0:6] in ['vk.com', 'https:']:
        id = text.find('vk.com')
        id = text[id + 7:]
        url = 'https://api.vk.com/method/users.get?user_ids=' + str(id) + '&fields=photo_400_orig'
        response = requests.get(url)
        response = response.json()
        url = response.get('response')[0].get('photo_400_orig')
        url = url.replace('\\', '')
        response = requests.get(url)
        with open('userImages/' + path + '/av.jpg', 'wb+') as f:
            for buf in response.iter_content(1024):
                if buf:
                    f.write(buf)

        msg = confirm_awards(obj = kwargs.get('obj'))
        return msg
    else: return 'Неправильный формат ссылки'


def setting_image(**kwargs):
    text = kwargs.get('key')
    path = user.name + ' ' + user.surname
    if text.lower() == 'по умолчанию' or text == '1':
        file = open('userImages/' + path + '/av.jpg', 'w+')
        shutil.copyfile('default.png', 'userImages/' + path + '/av.jpg')
        msg = confirm_awards(obj=kwargs.get('obj'))
        return msg
    elif text == 'photo':
        msg = 'Произошла ошибка. Возможно, проблемы с сервером'
        params = {'out': '0', 'offset':'0', 'count':'30',
                  'time_offset': '0', 'filters':'0', 'preview_length': '0',
                  'last_message_id':'0', 'access_token': const.token}
        url = 'https://api.vk.com/method/messages.get'
        r = requests.get(url, params)
        r = r.json()
        for key in r['response'][1]:
            if key == 'attachment':
                try:
                    photo_url = r['response'][1][key]['photo']['src_big']
                    r = requests.get(photo_url)
                    with open('userImages/' + path + '/av.jpg', 'wb+') as f:
                        for buf in r.iter_content(1024):
                            if buf:
                                f.write(buf)

                    msg = confirm_awards(obj=kwargs.get('obj'))

                except:
                    pass
        return msg
    else:
        kwargs.get('obj').queue.append(setting_image)
        return 'Пришлите фото'

def forward_mes(**kwargs):
    id = kwargs.get('id')
    vk.messages.send(message = 'Новое сообщение', forward_messages = id, user_id = const.admin_id)
    return 'Ваше сообщение отправлено' + welcome(obj = kwargs.get('obj'))