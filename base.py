import sqlite3 as sqlite
import temp

import const


def is_editor(user_id):
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    cur.execute('SELECT user_id FROM editors WHERE user_id = (?)', (str(user_id),))
    if cur.fetchone():
        return True
    else:
        return False


def getUsers(name):
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    data = name + ' ' + const.userInfo[0]
    print(data)
    cur.execute('SELECT ("firstName" || " " || "lastName") FROM Users WHERE ("firstName" || " " || "category") = (?)', (data,))
    tempNames = cur.fetchall()
    names = []
    for i in tempNames:
        names.append(i[0])
    return names


def get_user_names():
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    cur.execute('SELECT firstName FROM Users')
    tempNames = cur.fetchall()
    names = []
    for i in tempNames:
        names.append(i[0])
    return names

def giveElements():
    db = sqlite.connect('clientbase.db')
    cur = db.cursor()
    cur.execute("SELECT name FROM categories")
    temp_items = cur.fetchall()
    categories = []
    for item in temp_items:
        categories.append(item[0])
    return categories

def defineUser(username, kat):
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    data = username + ' ' + kat
    cur.execute('SELECT * FROM Users WHERE ("firstName" || " " || "lastName" || " " || "category") = (?)', (data,))
    c = cur.fetchone()
    db.close()
    if c:
        user = temp.User()
        user.set_full_data(*c)
        return user
    else:
        return None

def typeFinder(kat):
    db = sqlite.connect("clientbase.db")
    cur = db.cursor()
    cur.execute('SELECT ("firstName" || " " || "lastName") FROM Users WHERE category = (?)', (kat,))
    tempUsers = cur.fetchall()
    if tempUsers:
        users = []
        for user in tempUsers:
            users.append(defineUser(user[0], kat))

        return users
    else:
        return []