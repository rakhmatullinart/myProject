import json
import logging
import like -a - s
import time
import urllib.parse as parse
import urllib.request as urllib
import postgresql as pg
import vk






logfile = ''  # 'logs.log', for example
logging.basicConfig(format=u'%(asctime)s | %(message)s',
                    level=logging.WARNING, filename=logfile)  # edit log's filename if needed

#               Put your
app_id = ''  # app id here
login = ''  # VK's login
password = ''  # Password for this login
my_id = ''  # VK id here

# some useful string constants here
access_token = '7625f6b4cb0646db2cb3d670fcdb792dfd0ab9337775a9b1d7aa749bb0f388c37681f68b1595306fe8bde'
ac_tkn = '&access_token='
request_url = 'https://api.vk.com/method/'
# method names
messages_get_method = 'messages.get'
mark_as_read_method = 'messages.markAsRead'
send_message_method = 'messages.send'
get_friends_method = 'friends.get'
get_user_method = 'users.get'

DAY = 86400

good_list = [
    87070490, 946041, 2873028,
    9344219, 14760190, 19375989,
    26570113, 41053069, 106909773,
    111166636, 121702873, 138731510,
    144258940, 165580957, 225193884,
    225328940, 379805606, 426541359
]

# messages
default_msg = "Здравствуйте, к сожалению, а не могу ответить на ваше сообщение," \
              " т.к. я прекратил свою деятельность в соц.сети Вконтакте," \
              " но вы можете связаться со мной лично с помощью:" \
              "\n\tTelegram - @NickF40" \
              "\n\tE-mail - e_n_k@list.ru" \
              "\nИли выберите из предложенных ниже вариантов и напишите его в чате:" \
              "\n\t- Оставить заявку на встречу" \
              "\n\t- Оставить просьбу" \
              "\n\t- Поделиться музыкой(спасибо!)" \
              "\nНапишите один из выбранных вариантов ниже(без тире и комментариев в скобках).."

day_selection_msg = "Напишите выбранное вами число (В формате #{месяц}.{день}" \
                    "(Знак решётки необходимо оставить, прошу прощения за неудобство, интерфейс в разработке).."

# settings
out = '0'
offset = '0'
count = '200'
time_offset = str(DAY)
filters = '0'
preview_length = '0'
last_message_id = '0'

get_messages_request = request_url + messages_get_method \
                       + '?out=' + out \
                       + '&offset=' + offset \
                       + '&count=' + count \
                       + '&time_offset=' + time_offset \
                       + '&filters=' + filters \
                       + '&preview_length=' + preview_length \
                       + '&last_message_id=' + last_message_id \
                       + ac_tkn + access_token

get_friends_request = request_url + get_friends_method \
                      + '?user_id=' + my_id \
                      + '&order=hints' \
                      + '&fields=online,last_seen' \
                      + ac_tkn + access_token


def get_today():
    t = time.time()
    return days_.get(time.strftime('%A', time.localtime(t)))


def mark_as_read(message_id, from_user_id):
    mark_as_read_request = request_url + mark_as_read_method \
                           + '?message_ids=' + str(message_id) \
                           + '&peer_id=' + str(from_user_id) \
                           + ac_tkn + access_token
    data = urllib.urlopen(mark_as_read_request)
    encrypted_data = data.read().decode()
    final_data = json.loads(encrypted_data)
    print(
        ' '.join(['for', str(from_user_id), 'message', str(message_id), 'was marked as read with data:\n', final_data]))


def send_message_back(from_user_id, message):
    send_message_request = request_url + send_message_method \
                           + '?user_id=' + str(from_user_id) \
                           + '&message={0}'.format(parse.quote_plus(message)) \
                           + ac_tkn + access_token
    print(send_message_request)
    data = urllib.urlopen(send_message_request)
    encrypted_data = data.read().decode()
    final_data = json.loads(encrypted_data)
    print(' '.join(
        ['for ', str(from_user_id), 'was sent message with text', message, 'with return data', str(final_data)]))


def get_name(user_id):
    get_user_request = request_url + get_user_method \
                       + '?user_ids=' + str(user_id) \
                       + '&fields=photo_id,verified,sex,bdate,' \
                         'city,country,home_town,has_photo,' \
                         'photo_max,photo_max_orig,online,domain,has_mobile,' \
                         'contacts,site,education,universities,schools,status,' \
                         'last_seen,followers_count,common_count,occupation,' \
                         'nickname,relatives,relation,personal,connections,' \
                         'exports,wall_comments,activities,interests,music,' \
                         'movies,tv,books,games,about,quotes,can_post,' \
                         'can_see_all_posts,can_see_audio,can_write_private_message,' \
                         'can_send_friend_request,is_favorite,is_hidden_from_feed,' \
                         'timezone,screen_name,maiden_name,is_friend,' \
                         'friend_status,career,military' \
                       + ac_tkn + access_token
    data = urllib.urlopen(get_user_request)
    decoded_data = data.read().decode()
    final = json.loads(decoded_data).get('response')[0]
    if final:
        print(final)
        return [final.get('last_name'), final.get('first_name'), final.get('domain')]


def handle_other(message):
    pass


def get_friends():
    encrypted_data = urllib.urlopen(get_friends_request).read().decode()
    data = json.loads(encrypted_data).get('response')
    return [user.get('uid') for user in data if 'deactivated' not in user.keys()]


def check_messages():
    data = urllib.urlopen(get_messages_request)
    decoded_data = data.read().decode()
    final = json.loads(decoded_data).get('response')[1:]
    sent = []
    for msg in final:
        if not msg.get('chat_id'):
            if msg.get('read_state') == 0:
                text = msg.get('body')
                user = msg.get('uid')
                if text == 'Оставить заявку на встречу':
                    mark_as_read(msg.get('mid'), user)
                    send_message_back(user, day_selection_msg)

                elif text[0] == '#':
                    data = text[1:].split(sep='.')
                    try:
                        mon = int(data[0])
                        day = int(data[1])
                    act = get_activities(mon, day)()


                    except Exception as e:
                    print(e)
                    handle_other(text)
                pass
            elif text == 'Оставить просьбу':
                pass
            elif text == 'Поделиться музыкой':
                pass

            logging.log(logging.INFO, ' : '.join([*get_name(msg.get('uid')), '\'' + msg.get('body') + '\'']))
            if user not in sent:
                send_message_back(user, default_msg)
                mark_as_read(msg.get('mid'), user)
                sent.append(user)
                final = [msg for msg in final if msg.get('uid') != user]
                print(final)


while True:
    check_messages()
    print(str(time.ctime()))
    time.sleep(60 * 15)