import sqlite3 as sqlite
import temp, const
import logging


# create logger
logger = logging.getLogger('base.py')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.FileHandler('logs.log')

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

def is_editor(user_id):
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    cur.execute('SELECT user_id FROM editors WHERE user_id = (?)', (str(user_id),))
    if cur.fetchone():
        return True
    else:
        return False


def getUsers(name, kat):
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    data = name + ' ' + kat
    cur.execute('SELECT ("firstName" || " " || "lastName") FROM Users WHERE ("firstName" || " " || "category") = (?)', (data,))
    tempNames = cur.fetchall()
    if not tempNames:
        cur.execute(
            'SELECT ("firstName" || " " || "lastName") FROM Users WHERE ("link" || " " || "category") = (?)',
            (data,))
        tempNames = cur.fetchall()
    names = []
    for i in tempNames:
        names.append(i[0])
    return names


def get_user_names():
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    cur.execute('SELECT firstName FROM Users')
    tempNames = cur.fetchall()
    names = []
    for i in tempNames:
        names.append(i[0].lower())
    return names

def giveElements():
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    cur.execute("SELECT name FROM categories")
    temp_items = cur.fetchall()
    categories = []
    for item in temp_items:
        categories.append(item[0])
    return categories

def defineUser(username, kat):
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    data = username + ' ' + kat
    cur.execute('SELECT * FROM Users WHERE ("firstName" || " " || "lastName" || " " || "category") = (?)', (data,))
    c = cur.fetchone()
    if c:
        user = temp.User()
        user.set_full_data(*c)
        return user
    else:
        return None



def get_users():
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    cur.execute('SELECT ("firstName" || " " || "lastName") FROM Users')
    c = cur.fetchall()
    users  = {}
    for user in c:
        name, surname = user[0].split()
        users[name] = surname
    return users


def giveUsers():
    inf = {}
    for key in giveElements():
        inf[key] = typeFinder(key)
    return inf

def typeFinder(kat):
    db = sqlite.connect(const.dbPath)
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


def isEmptyKat(kat):
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    cur.execute('SELECT * FROM Users WHERE category = (?)', (kat,))
    if cur.fetchone():
        return False
    else:
        return True

def delete_kat(kat):
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    cur.execute("DELETE FROM categories WHERE name = ?", (kat,))
    db.commit()

def addUser(user):
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    name = user.name +' '+ user.surname
    try:
        cur.execute('SELECT * FROM Users WHERE ("firstName" || " " || "lastName") = (?)', (name,))
    except Exception as e:
        logger.error('DBTESTING ERROR: ' + str(e))
    if not cur.fetchone():
        try:
            cur.execute('INSERT INTO Users (firstName, lastName, category, rate, link) VALUES (?,?,?,?,?)', (
                user.name,
                user.surname,
                user.kat,
                user.rate,
                user.link))

            db.commit()


        except Exception as e:
            logger.error('USER ADDING ERROR' + str(e))
    else:
        logger.warning('IN THE BASE YET\n'+
                   user.name + " " + user.surname)

def add_kat(kat):
    db = sqlite.connect(const.dbPath)
    cur = db.cursor()
    try:
        cur.execute('SELECT * FROM categories WHERE name = (?)', (kat.lower(),))
    except Exception as e:
        logger.error('CANT CONNECT DATABASE: ' + str(e))
    if not cur.fetchone():
        try:
            cur.execute('INSERT  INTO categories (name) VALUES (?)', (kat,))
            db.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False
    else:
        logger.warning('KAT ALREADY EXISTS')
        return False