import vk

token = '7625f6b4cb0646db2cb3d670fcdb792dfd0ab9337775a9b1d7aa749bb0f388c37681f68b1595306fe8bde'
session = vk.Session(access_token=token)
api = vk.API(session, v=5.0)

data = api.messages.getLongPollServer(Ip_version =2)

def send_message(user_id, token, message, attachment=""):
    api.messages.send(access_token=token, user_id=str(user_id), message=message, attachment=attachment)