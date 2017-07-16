import command_System
import sqlite3 as sqlite
import const, base, temp
import shutil
from const import users_steps, users_callback
import vk_api
import requests, os
import commands_admin

vk_session = vk_api.VkApi(token=const.token)
vk_session.auth()
up = vk_api.VkUpload(vk_session)
vk = vk_session.get_api()



def make_upper(data):
    data  = data[0].upper() + data[1:]
    return data

# приветсвенное сообщение
def welcome(**kwargs):
    obj = kwargs.get('obj')
    message = const.welcomeClient
    count = 1
    obj.callback.clear()
    for key in base.giveElements():
        message += '\n'+ str(count) +'. ' + key
        obj.callback[str(count)] =  key
        count += 1
    message += '\n%s. Оставить заявку на добавление пользователя'%str(count)
    obj.callback[str(count)] = 'Заявка'
    if obj.editor:
        message+= '\nАдмин-панель'
    obj.step = 'kat_choose'


    return message

welCommand = command_System.Command()

welCommand.keys = ['привет', 'здравствуй', 'здравствуйте', 'start', 'меню']
welCommand.description = 'Главное меню'
welCommand.process = welcome



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
            rating = "\nРейтинг: " + str(user.rate) + '%'


        return text+rating
    else: return 'Вы не находитесь ни в одной категории, вернитесь в главное меню'
show = command_System.Command()
show.keys = ['остальные', 'показать всех', 'все']
show.process = show_all

#получение информации о конкретном пользователе
'''def get_info(text):
    q = []
    user = base.defineUser(text, const.userInfo[0])
    if user != None:
        text = user.name + ' ' + user.surname
        rating = "\nРейтинг: " + str(user.rate) + '%'
        extra = "\nНапиши 'показать всех' чтобы увидеть всех пользователей в этой категории"
        #path = 'userImages/' + text
        # for image in os.listdir(path=path):
        #   bot.send_photo(message.chat.id, photo=open(path + '/' + image, 'rb'))
        q.extend((text, rating, extra))
        return q
    else: return None
user = command_System.Command()'''


#отображение пользователей с выбранным именем
def list_us(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'confirm_name':
        msg = 'Список пользователей:\n'
        data = kwargs.get('data')
        if data:
            q = base.getUsers(data, obj.kat)
        else:
            q = base.getUsers(make_upper(kwargs.get('key')), obj.kat)
        if q:
            count = 1
            obj.callback.clear()
            for me in q:
                msg += str(count) + '. ' + me+'\n'
                obj.callback[str(count)] = me
                count += 1
            msg += '\nВведите цифру'
            obj.step = 'confirm_surname'
            obj.name = data if data else make_upper(kwargs.get('key'))
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
        data = obj.callback.get(kwargs.get('key'))
        obj.surname = data.split()[1]
        print(' '.join([obj.name, obj.surname]))
        user_local = base.defineUser(' '.join([obj.name, obj.surname]), obj.kat)
        if user_local != None:
            text = user_local.name + ' ' + user_local.surname
            rating = "\nРейтинг: " + str(user_local.rate) + '%\n'
            if user_local.link:
                rating += user_local.link
            extra = "\nНапиши 'показать всех' чтобы увидеть всех пользователей в этой категории"
            path = 'userImages/' + text
            photo = up.photo_messages(path+'/av.jpg')
            attach = 'photo'+ str(photo[0].get('owner_id'))+'_'+str(photo[0].get('id'))+'&'
            obj.callback.clear()
            return text + rating + extra + attach

        else:
            return 'Пользователь не найден'
    else: return

list_surnames_com = command_System.Command()
list_surnames_com.keys = map(str, range(1, 20))
list_surnames_com.process = list_surnames


#админ-панель
def admin_panel(**kwargs):
    obj = kwargs.get('obj')
    if obj.editor:
        msg = 'Выберите нужную категорию для редактирования\n' \
              '1.Категории\n' \
              '2.Пользователи'
        obj.step = 'edit'
        return msg

    else: return 'Вы не обладаете правами доступа, чтобы использовать данную команду'
admin_panel_com = command_System.Command()
admin_panel_com.keys = ['админ-панель', 'админ']
admin_panel_com.process = admin_panel

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
        extra = '\nЕсли хотите добавить пользователя, отправьте ?<имя и фамилия пользователя>'
        const.flag_break = True
        obj.step = 'edit_user_info'
        return msg + extra
    else: return 'Вы не обладаете правами доступа, чтобы использовать данную команду'
user_edit_com = command_System.Command()
user_edit_com.keys = ['пользователи','2']
user_edit_com.process = users_edit


#получение данных пользователя для редактирования
def edit_user_info(**kwargs):
    obj = kwargs.get('obj')
    print('done')
    if obj.step == 'edit_user_info':
        if obj.editor:
            name = obj.callback.get(kwargs.get('key'))
            db = sqlite.connect(const.dbPath)
            cur = db.cursor()
            cur.execute('SELECT * FROM Users WHERE ("firstName" || " " || "lastName") = (?)', (name,))
            c = cur.fetchone()
            us = temp.User()
            us.set_full_data(*c)
            text = us.name + ' ' + us.surname
            rating = "\nРейтинг: " + str(us.rate) + '%\n'
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

user = temp.User()

def add_user(**kwargs):
    if kwargs.get('obj').step == 'edit_user_info':
        user.name, user.surname = kwargs.get('data').split()
        kwargs.get('obj').queue.append(adding_rate)
        return 'Введите рейтинг'
    else: return

add_user_com = command_System.Command()
add_user_com.keys = ['?']
add_user_com.process = add_user

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


#выбор категории
def kat_choose(**kwargs):
    obj = kwargs.get('obj')
    if obj.step == 'kat_choose':
        if obj.callback.get(kwargs.get('key')) == 'Заявка':

            obj.step = 'edit_user_info'
            message = 'Если хотите добавить пользователя, отправьте ?<имя и фамилия пользователя>'
        else:
            try:
                obj.kat = obj.callback.get(kwargs.get('key'))

            except:
                obj.kat = make_upper(kwargs.get('key'))
            obj.callback.clear()
            message = 'Категория выбрана! Введите имя или ссылку в формате vk. com/ssylka (строка без пробелов).'
            obj.step = 'confirm_name'
        return message
    else: return

kat = command_System.Command()
count = 0
for i in base.giveElements():
    kat.keys.append(i.lower())
    count+=1
kat.keys.extend(map(str, range(1, count+2)))
kat.process = kat_choose

def adding_rate(**kwargs):
    user.rate = kwargs.get('key')
    kwargs.get('obj').queue.append(adding_kat)
    msg = 'Выберите категорию в которую хотите добавить.'
    count = 1
    obj = kwargs.get('obj')
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
    request = 'Вам отправлена заявка на добавление пользователя:\n'
    request+= ' '.join([user.name, user.surname])
    request += '\nВыставленный пользователем рейтинг:' + user.rate
    request += '\nВыбранная категория:' + user.kat
    request += '\nВарианты вашего одобрения:\n' + const.actions
    commands_admin.user_for_confirm = user
    const.admin_step = 'confirm'
    photo = up.photo_messages('userImages/' + ' '.join([user.name, user.surname]) + '/av.jpg')
    attach = 'photo' + str(photo[0].get('owner_id')) + '_' + str(photo[0].get('id'))
    vk.messages.send(user_id = const.admin_id, message = request, attachment = attach)

    return 'Ваша заявка отправлена на рассмотрение администратору!\n' \
           'Если она будет одобрена, ваш профиль появится в выбранной категории'

def adding_link(**kwargs):
    path = user.name + ' ' + user.surname
    os.mkdir('userImages/' + path)
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
               'Если хотите установить фото по умолчанию - отправьте "по умолчанию"'



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
        if kwargs.get('obj').editor:

            base.addUser(user)
            list_us_com.keys = [user.name.lower()]
            msg = 'Пользователь успешно добавлен\n'
            msg += admin_panel(obj = kwargs.get('obj'))
            return msg
        else:
            confirm_awards(obj = kwargs.get('obj'))
            return 'Фото добавлено в заявку'
    else: return 'Неправильный формат ссылки'

def setting_image(**kwargs):
    text = kwargs.get('key')
    path = user.name + ' ' + user.surname
    if text.lower() == 'по умолчанию':
        file = open('userImages/' + path + '/av.jpg', 'w+')
        shutil.copyfile('default.png', 'userImages/' + path + '/av.jpg')
        if kwargs.get('obj').editor:
            base.addUser(user)
            list_us_com.keys = [user.name.lower()]
            msg = 'Пользователь успешно добавлен\n'
            msg += admin_panel(obj = kwargs.get('obj'))
        else:
            confirm_awards()
            msg = 'Заявка отправлена!'
        return msg
    elif text == 'photo':
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
                    if kwargs.get('obj').editor:
                        base.addUser(user)
                        list_us_com.keys = [user.name.lower()]
                        msg = 'Пользователь успешно добавлен\n'
                        msg += admin_panel(obj = kwargs.get('obj'))
                    else:
                        confirm_awards()
                        msg = 'Заявка отправлена!'

                    return msg
                except:
                    return 'Произошла ошибка. Возможно, проблемы с сервером'
    else:
        kwargs.get('obj').queue.append(setting_image)
        return 'Пришлите фото'
