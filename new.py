import urllib.parse as parse
import urllib.request as urllib
import  json, time
import vk_api as vk


messages_get_method = 'messages.get'
mark_as_read_method = 'messages.markAsRead'
send_message_method = 'messages.send'
get_friends_method = 'friends.get'
get_user_method = 'users.get'

out = '0'
offset = '0'
count = '200'
time_offset = '0'
filters = '0'
preview_length = '0'
last_message_id = '0'

access_token = '7625f6b4cb0646db2cb3d670fcdb792dfd0ab9337775a9b1d7aa749bb0f388c37681f68b1595306fe8bde'
ac_tkn = '&access_token='
request_url = 'https://api.vk.com/method/'


get_messages_request = request_url + messages_get_method \
                       + '?out=' + out \
                       + '&offset=' + offset \
                       + '&count=' + count \
                       + '&time_offset=' + time_offset \
                       + '&filters=' + filters \
                       + '&preview_length=' + preview_length \
                       + '&last_message_id=' + last_message_id \
                       + ac_tkn + access_token

def mark_as_read(message_id, from_user_id):
    mark_as_read_request = request_url + mark_as_read_method \
                           + '?message_ids=' + str(message_id) \
                           + '&peer_id=' + str(from_user_id) \
                           + ac_tkn + access_token
    data = urllib.urlopen(mark_as_read_request)
    encrypted_data = data.read().decode()
    final_data = json.loads(encrypted_data)
    print(final_data)
    print(' '.join(['for', str(from_user_id), 'message', str(message_id), 'was marked as read with data:\n', str(final_data)]))


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


def check_messages():
    data = urllib.urlopen(get_messages_request)
    decoded_data = data.read().decode()
    final = json.loads(decoded_data).get('response')[1:]
    for msg in final:
        if not msg.get('chat_id'):
            if msg.get('read_state') == 0:
                text = msg.get('body')
                user = msg.get('uid')
                mark_as_read(msg.get('mid'), user)
                send_message_back(user, 'нет')




st = request_url + 'messages.getLongPollServer?need_pts=1&Ip_version=2'+ ac_tkn + access_token

request = 'https://imv4.vk.com\/im3982?act=a_check&key=5cd78ad67684d3292be50d5632b5f1cae29044ce&ts=1845235047&wait=25&mode=2&version=2'
print(request)