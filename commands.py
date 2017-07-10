import command_System
import const, base

# приветсвенное сообщение
def welcome(**kwargs):
    message = const.welcomeClient
    count = 1
    for key in base.giveElements():
        message += '\n'+ str(count) +'. ' + key
        count += 1
    return message

welCommand = command_System.Command()

welCommand.keys = ['привет', 'здравствуй', 'здравствуйте', 'start']
welCommand.description = 'Главное меню'
welCommand.process = welcome

#херь
def catch_kat():
    pass

catchKat = command_System.Command()
catchKat.keys = base.giveElements()
catchKat.process = catch_kat

#информация
def info(*args):
    msg = ''
    for c in command_System.command_list:
        msg += c.keys[0] + ' - ' + c.description + '\n'
    return msg

infoCommand = command_System.Command()

infoCommand.keys = ['помощь', 'помоги', 'help']
infoCommand.description = const.commands
infoCommand.process = info


#показ всех пользователей категории
def show_all(*args):
    q = []
    for user in base.typeFinder(const.userInfo[0]):
        text = '\n'+ user.name + ' ' + user.surname
        rating = "\nРейтинг: " + str(user.rate) + '%'
        #files = os.listdir(path='userImages/'+text)
        #bot.send_photo(call.message.chat.id, photo=open('userImages/'+text+'/'+files[0], 'rb'))
        #bot.send_message(call.message.chat.id, text + rating)
        q.extend((text, rating))
    return q

show = command_System.Command()
show.keys = ['остальные', 'показать всех', 'все']
show.process = show_all

#получение информации о конкретном пользователе
def get_info(text):
    q = []
    user = base.defineUser(text, const.userInfo[0])
    if user != None:
        text = user.name + ' ' + user.surname
        rating = "\nРейтинг: " + str(user.rate) + '%'
        extra = "\nНапиши 'показать всех' чтобы увидеть всех пользователей в этой категории"
        path = 'userImages/' + text
        # for image in os.listdir(path=path):
        #   bot.send_photo(message.chat.id, photo=open(path + '/' + image, 'rb'))
        q.extend((text, rating, extra))
        return q
    else: return None
user = command_System.Command()


#отображение пользователей с выбранным именем
def list_us(**kwargs):
    msg = 'Список пользователей:\n'
    q = base.getUsers(kwargs.get('key'))
    for me in q:
        msg += me + '\n'
    return msg
list_us_com = command_System.Command()
list_us_com.keys = base.get_user_names()
list_us_com.process = list_us


def kat_choose(**kwargs):
    try:
        const.userInfo[0] = kat.keys[int(kwargs.get('key'))-1]
    except:
        const.userInfo[0] = kwargs.get('key')
    message = 'Категория выбрана! Введите имя.'
    const.process_user_step = 'confirm_name'
    return message

kat = command_System.Command()
count = 0
for i in base.giveElements():
    kat.keys.append(i)
    count+=1
kat.keys.extend(map(str, range(1, count+1)))
kat.process = kat_choose