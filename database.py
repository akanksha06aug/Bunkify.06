import sqlite3, datetime

def connect():
    return sqlite3.connect("bunkify.db")

def create_user(email,password):
    db = connect()
    db.execute("CREATE TABLE IF NOT EXISTS users(email TEXT, password TEXT)")
    db.execute("INSERT INTO users VALUES (?,?)",[email,password])
    db.commit()

def user_exists(email):
    db = connect()
    data = db.execute("SELECT * FROM users WHERE email=?",[email]).fetchone()
    return data

def validate_user(email,password):
    db = connect()
    data = db.execute("SELECT * FROM users WHERE email=? AND password=?",[email,password]).fetchone()
    return data

def change_password(email,new):
    db = connect()
    db.execute("UPDATE users SET password=? WHERE email=?",[new,email])
    db.commit()

# -------- SUBJECTS --------
def add_subject(user,name,total,attended):
    db = connect()
    db.execute("""CREATE TABLE IF NOT EXISTS subjects(
        user TEXT,name TEXT,total INT,attended INT)""")
    db.execute("INSERT INTO subjects VALUES (?,?,?,?)",[user,name,total,attended])
    db.commit()

def get_subjects(user):
    db = connect()
    return db.execute("SELECT * FROM subjects WHERE user=?",[user]).fetchall()

def bunk_class(user,name):
    db = connect()
    db.execute("UPDATE subjects SET total = total + 1 WHERE user=? AND name=?",[user,name])
    db.commit()

def attend_class(user,name):
    db = connect()
    db.execute("UPDATE subjects SET total = total + 1, attended=attended + 1 WHERE user=? AND name=?",[user,name])
    db.commit()

# -------- HISTORY --------
def add_history(user,subject,status):
    db = connect()
    db.execute("""CREATE TABLE IF NOT EXISTS history(
        user TEXT,subject TEXT,status TEXT,time TEXT)""")

    time = datetime.datetime.now().strftime("%d %b %Y %I:%M %p")
    db.execute("INSERT INTO history VALUES(?,?,?,?)",[user,subject,status,time])
    db.commit()

def get_history(user):
    db = connect()
    return db.execute("SELECT * FROM history WHERE user=?",[user]).fetchall()
