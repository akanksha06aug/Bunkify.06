from flask import Flask, render_template, request, redirect, session
import sqlite3, random, smtplib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "bunkify123"

##################################################
# DATABASE
##################################################

def get_db():
    return sqlite3.connect("users.db")


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS subjects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        subject TEXT,
        attended INTEGER,
        total INTEGER,
        bunk INTEGER
    )""")

    conn.commit()
    conn.close()

init_db()

##################################################
# UTILS
##################################################

def send_otp(email, otp):
    sender = "your_email@gmail.com"
    password = "your_app_password"

    message = f"Subject: Bunkify OTP\n\nYour OTP is: {otp}"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, email, message)


def attendance(attended, total):
    if total == 0:
        return 0
    return round((attended / total) * 100, 2)


def teacher_reaction(percentage):
    if percentage >= 85:
        return "😎 Teacher is proud!"
    elif percentage >= 75:
        return "🙂 You're safe!"
    elif percentage >= 65:
        return "😐 Warning level!"
    else:
        return "😡 You are in danger!"


def internal_risk(percentage):
    if percentage < 65:
        return "⚠ Internal marks at HIGH RISK"
    elif percentage < 75:
        return "⚠ Moderate Risk"
    else:
        return "✅ Low Risk"


quotes = [
    "📚 Success doesn’t come by default. Attend your class!",
    "🎓 Bunk today, regret tomorrow.",
    "✨ Discipline = Freedom",
    "💡 Each class is a step closer to success"
]

##################################################
# ROUTES
##################################################

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
        user = c.fetchone()

        if user:
            session["user"] = email
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        otp = random.randint(1000,9999)
        session["otp"] = otp
        session["temp_user"] = (email, password)

        send_otp(email, otp)

        return redirect("/verify")

    return render_template("register.html")


@app.route("/verify", methods=["GET","POST"])
def verify():
    if request.method == "POST":
        user_otp = request.form["otp"]

        if str(session["otp"]) == user_otp:
            email, password = session["temp_user"]

            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO users(email,password) VALUES(?,?)",(email,password))
            conn.commit()
            conn.close()

            return redirect("/")
        else:
            return render_template("otp.html", error="Wrong OTP")

    return render_template("otp.html")


@app.route("/forgot", methods=["GET","POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"]
        otp = random.randint(1000,9999)

        session["reset_email"] = email
        session["reset_otp"] = otp

        send_otp(email, otp)
        return redirect("/reset")

    return render_template("forgot.html")


@app.route("/reset", methods=["GET","POST"])
def reset():
    if request.method == "POST":
        otp = request.form["otp"]
        newpass = request.form["password"]

        if str(session["reset_otp"]) == otp:
            conn = get_db()
            c = conn.cursor()
            c.execute("UPDATE users SET password=? WHERE email=?",(newpass,session["reset_email"]))
            conn.commit()
            return redirect("/")
        else:
            return "Invalid OTP"

    return render_template("otp.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    email = session["user"]

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM subjects WHERE user_email=?", (email,))
    data = c.fetchall()

    new_data = []
    for s in data:
        percent = attendance(s[3], s[4])
        new_data.append((s, percent, teacher_reaction(percent), internal_risk(percent)))

    return render_template("dashboard.html", data=new_data, quote=random.choice(quotes))


@app.route("/add", methods=["GET","POST"])
def add_subject():
    if request.method == "POST":
        subject = request.form["subject"]
        attended = int(request.form["attended"])
        total = int(request.form["total"])
        bunk = int(request.form["bunk"])

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO subjects(user_email,subject,attended,total,bunk) VALUES(?,?,?,?,?)",
        (session["user"],subject,attended,total,bunk))

        conn.commit()

        return redirect("/dashboard")

    return render_template("add_subject.html")


@app.route("/delete/<id>")
def delete(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM subjects WHERE id=?",(id,))
    conn.commit()
    return redirect("/dashboard")


@app.route("/edit/<id>", methods=["GET","POST"])
def edit(id):
    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":
        a = request.form["attended"]
        t = request.form["total"]
        b = request.form["bunk"]

        c.execute("UPDATE subjects SET attended=?,total=?,bunk=? WHERE id=?",(a,t,b,id))
        conn.commit()
        return redirect("/dashboard")

    c.execute("SELECT * FROM subjects WHERE id=?",(id,))
    data = c.fetchone()

    return render_template("edit_subject.html", subject=data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()
