import command_System
import const, base
from const import users_steps, users_callback
import vk_api

vk_session = vk_api.VkApi(token=const.token)
vk_session.auth()
up = vk_api.VkUpload(vk_session)




def make_upper(data):
    data  = data[0].upper() + data[1:]
    return data

# приветсвенное сообщение
def welcome(**kwargs):
    message = const.welcomeClient
    count = 1
    for key in base.giveElements():
        message += '\n'+ str(count) +'. ' + make_upper(key)
        count += 1
    user_id = kwargs.get('user_id')
    if base.is_editor(user_id):
        message+= '\nАдмин-панель'
    users_steps[user_id][0] = 'kat_choose'

    return message

welCommand = command_System.Command()

welCommand.keys = ['привет', 'здравствуй', 'здравствуйте', 'start']
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
    u_id = kwargs.get('user_id')
    if users_steps[u_id][1]:
        text, rating = '', ''
        for user in base.typeFinder(users_steps[u_id][1]):
            text = '\n'+ user.name + ' ' + user.surname
            rating = "\nРейтинг: " + str(user.rate) + '%'
            #files = os.listdir(path='userImages/'+text)
            #bot.send_photo(call.message.chat.id, photo=open('userImages/'+text+'/'+files[0], 'rb'))
            #bot.send_message(call.message.chat.id, text + rating)

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
    user_id = kwargs.get('user_id')
    if users_steps[user_id][0] == 'confirm_name':
        msg = 'Список пользователей:\n'
        data = make_upper(kwargs.get('key'))
        q = base.getUsers(data, users_steps[user_id][1])
        if q:
            count = 1
            for me in q.items():
                name = ' '.join(map(make_upper, me))
                msg += str(count) + '. ' + name
                users_callback[user_id][str(count)] = name
                count += 1
            msg += '\nВведите цифру'
            users_steps[user_id][0], users_steps[user_id][2] = 'confirm_surname', data
        else:
            msg = 'Пользователей с такими данными не найдено в этой категории. Попробуйте еще раз'
        return msg
    else:
        return
list_us_com = command_System.Command()
list_us_com.keys = base.get_users().keys()
list_us_com.keys = base.get_users().values()
list_us_com.process = list_us


#выбор пользователей по фамилии
def list_surnames(**kwargs):
    user_id = kwargs.get('user_id')
    if users_steps.get(user_id)[0] == 'confirm_surname':
        data = users_callback.get(user_id).get(kwargs.get('key'))
        users_steps[user_id][3] = data.split()[1]
        user = base.defineUser(' '.join(users_steps.get(user_id)[2:]), users_steps.get(user_id)[1])
        if user != None:
            text = user.name + ' ' + user.surname
            rating = "\nРейтинг: " + str(user.rate) + '%'
            extra = "\nНапиши 'показать всех' чтобы увидеть всех пользователей в этой категории"
            path = 'userImages/' + text
            photo = up.photo_messages(path+'/av.jpg')
            attach = 'photo'+ str(photo[0].get('owner_id'))+'_'+str(photo[0].get('id'))+'&'
            return text + rating + extra + attach
        else:
            return 'Пользователь не найден'
    else: return

list_surnames_com = command_System.Command()
list_surnames_com.keys = map(str, range(1, 20))
list_surnames_com.process = list_surnames


#админ-панель
def admin_panel(**kwargs):
    users_id = kwargs.get('user_id')
    if base.is_editor(kwargs.get('user_id')):
        msg = 'Выберите нужную категорию для редактирования\n' \
              'Категории\n' \
              'Пользователи'
        users_steps[users_id][0] = 'edit'
        return msg

    else: return 'Вы не обладаете правами доступа, чтобы использовать данную команду'
admin_panel_com = command_System.Command()
admin_panel_com.keys = ['админ-панель', 'админ']
admin_panel_com.process = admin_panel

#редактирование категорий

def kats_edit(**kwargs):
    if base.is_editor(kwargs.get('user_id')):
        msg = 'Чтобы добавить категорию, напишите ?название категории\n' \
              'Чтобы удалить категорию, напишите #название категории\n' \
              '(Префикс обязателен)\n' \
              'Список доступных категорий:'
        for key in base.giveElements():
            msg += '\n' + '. ' + make_upper(key)
        return msg
    else: return 'Вы не обладаете правами доступа, чтобы использовать данную команду'
kat_edit_com = command_System.Command()
kat_edit_com.keys = ['категории']
kat_edit_com.process = kats_edit

#добавление и удаление категории

def delete_kat(**kwargs):
    data = make_upper(kwargs.get('data'))
    if base.isEmptyKat(data):
        base.delete_kat(data)
        msg = 'Категория удалена'
    else:
        msg ='Категория не может быть удалена, так как в ней есть данные.\n'\
                                   'Сначала удалите пользователей из этой категории'
    return msg
delete_kat_com = command_System.Command()
delete_kat_com.keys = ['#']
delete_kat_com.process = delete_kat

def add_kat(**kwargs):
    data = kwargs.get('data')
    if base.add_kat(data):
        msg = 'Категория успешно добавлена'
    else:
        msg = 'Ошибка добавления категории. Возможно, данная категория уже существует'
    return msg

add_kat_com = command_System.Command()
add_kat_com.keys = ['?']
add_kat_com.process = add_kat

#редактирование пользователей
def users_edit(**kwargs):
    user_id = kwargs.get('user_id')
    if base.is_editor(user_id):
        msg = 'Выберите человека (Введите имя и фамилию)\n'
        for kat in base.giveElements():
            kat = make_upper(kat)
            msg += '\U0001F449' + kat + '\n'
            temp = base.giveUsers()
            for key in temp[kat]:
                if key != None:
                    msg += '....' + key.name + ' ' + key.surname + '\n'

        users_steps[user_id][0] = 'edit_user_info'
        return msg
    else: return 'Вы не обладаете правами доступа, чтобы использовать данную команду'
user_edit_com = command_System.Command()
user_edit_com.keys = ['пользователи']
user_edit_com.process = users_edit


#получение данных пользователя для редактирования
def edit_user_info(**kwargs):
    user_id = kwargs.get('user_id')
    if base.is_editor(user_id) and users_steps[user_id][0] == 'edit_user_info':
        pass
    else: return 'Вы не обладаете правами доступа, чтобы использовать данную команду'
edit_user_com = command_System.Command()
edit_user_com.keys = []
edit_user_com.process = edit_user_info


#выбор категории
def kat_choose(**kwargs):
    user_id = kwargs.get('user_id')
    if users_steps[user_id][0] == 'kat_choose':
        try:
            users_steps[user_id][1] = make_upper(kat.keys[int(kwargs.get('key'))-1])
        except:
            users_steps[user_id][1] = make_upper(kwargs.get('key'))
        message = 'Категория выбрана! Введите имя.'
        users_steps[user_id][0] = 'confirm_name'
        return message
    else: return

kat = command_System.Command()
count = 0
for i in base.giveElements():
    kat.keys.append(i.lower())
    count+=1
kat.keys.extend(map(str, range(1, count+1)))
kat.process = kat_choose