from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "bunkify_secret_key"

# -------------------- DATABASE SETUP --------------------
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS subjects(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            subject TEXT,
            total INTEGER,
            attended INTEGER,
            bunked INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            subject TEXT,
            date TEXT,
            emoji TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------------------- OTP STORE --------------------
otp_store = {}

def generate_otp():
    return str(random.randint(100000, 999999))

# -------------------- MOTIVATION QUOTES --------------------
quotes = [
    "Discipline today, success tomorrow",
    "Every class counts 🤓",
    "No bunk, no backlog 🔥",
    "Attendance = Respect 💯",
    "Study now, party later 😎"
]

# -------------------- ROUTES --------------------
@app.route("/")
def home():
    return redirect("/login")

# --------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
        user = cur.fetchone()
        conn.close()
        if user:
            session['user'] = email
            return redirect("/dashboard")
        else:
            return render_template("login.html", msg="Invalid Credentials")
    return render_template("login.html")

# --------- REGISTER / SEND OTP ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        email = request.form['email']
        password = request.form['password']
        otp = generate_otp()
        otp_store[email] = {'otp': otp, 'password': password}
        print(f"OTP for {email}: {otp}")  # Mock email sending
        return render_template("verify_otp.html", email=email)
    return render_template("register.html")

@app.route("/verify_otp/<email>", methods=["POST"])
def verify_otp(email):
    entered_otp = request.form['otp']
    if email in otp_store and otp_store[email]['otp']==entered_otp:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users(email,password) VALUES(?,?)", (email, otp_store[email]['password']))
        conn.commit()
        conn.close()
        del otp_store[email]
        return redirect("/login")
    else:
        return render_template("verify_otp.html", email=email, msg="Invalid OTP")

# --------- FORGOT PASSWORD ----------
@app.route("/forgot", methods=["GET","POST"])
def forgot():
    if request.method=="POST":
        email = request.form['email']
        otp = generate_otp()
        otp_store[email] = {'otp': otp}
        print(f"Forgot Password OTP for {email}: {otp}")
        return render_template("reset_password.html", email=email)
    return render_template("forgot_password.html")

@app.route("/reset_password/<email>", methods=["POST"])
def reset_password(email):
    entered_otp = request.form['otp']
    new_password = request.form['new_password']
    if email in otp_store and otp_store[email]['otp']==entered_otp:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("UPDATE users SET password=? WHERE email=?", (new_password,email))
        conn.commit()
        conn.close()
        del otp_store[email]
        return redirect("/login")
    else:
        return render_template("reset_password.html", email=email, msg="Invalid OTP")

# --------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect("/login")
    email = session['user']
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM subjects WHERE email=?", (email,))
    subjects = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", subjects=subjects, quote=random.choice(quotes))

# --------- ADD SUBJECT ----------
@app.route("/add_subject", methods=["GET","POST"])
def add_subject():
    if 'user' not in session:
        return redirect("/login")
    if request.method=="POST":
        subject = request.form['subject']
        total = int(request.form['total'])
        attended = total - int(request.form['bunked'])
        bunked = int(request.form['bunked'])
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO subjects(email,subject,total,attended,bunked) VALUES(?,?,?,?,?)",
                    (session['user'], subject, total, attended, bunked))
        conn.commit()
        conn.close()
        return redirect("/dashboard")
    return render_template("add_subject.html")

# --------- EDIT SUBJECT ----------
@app.route("/edit/<subject>", methods=["GET","POST"])
def edit_subject(subject):
    if 'user' not in session:
        return redirect("/login")
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if request.method=="POST":
        total = int(request.form['total'])
        bunked = int(request.form['bunked'])
        attended = total - bunked
        cur.execute("UPDATE subjects SET total=?, bunked=?, attended=? WHERE email=? AND subject=?",
                    (total,bunked,attended,session['user'],subject))
        conn.commit()
        conn.close()
        return redirect("/dashboard")
    cur.execute("SELECT * FROM subjects WHERE email=? AND subject=?", (session['user'], subject))
    sub = cur.fetchone()
    conn.close()
    return render_template("edit_subject.html", subject=sub)

# --------- DELETE SUBJECT ----------
@app.route("/delete/<subject>", methods=["POST"])
def delete_subject(subject):
    if 'user' not in session:
        return redirect("/login")
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM subjects WHERE email=? AND subject=?", (session['user'],subject))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

# --------- BUNK CLASS ----------
@app.route("/bunk/<subject>", methods=["POST"])
def bunk_class(subject):
    if 'user' not in session:
        return redirect("/login")
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT total,attended,bunked FROM subjects WHERE email=? AND subject=?",
                (session['user'],subject))
    sub = cur.fetchone()
    total = sub[0]+1
    bunked = sub[2]+1
    attended = sub[1]
    cur.execute("UPDATE subjects SET total=?, bunked=?, attended=? WHERE email=? AND subject=?",
                (total,bunked,attended,session['user'],subject))
    emoji = "😎" if attended/total*100>=85 else "🙂" if attended/total*100>=75 else "😡"
    cur.execute("INSERT INTO history(email,subject,date,emoji) VALUES(?,?,?,?)",
                (session['user'],subject,str(datetime.now()),emoji))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

# --------- HISTORY ----------
@app.route("/history")
def history():
    if 'user' not in session:
        return redirect("/login")
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM history WHERE email=? ORDER BY id DESC", (session['user'],))
    data = cur.fetchall()
    conn.close()
    return render_template("history.html", history=data)

# --------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect("/login")

# --------- RUN APP ----------
if __name__=="__main__":
    app.run(debug=True)
