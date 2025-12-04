from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "bunkify_secret"


# ---------- DATABASE CONNECTION ----------
def connect():
    return sqlite3.connect("database.db")


# ---------- CREATE TABLES ----------
with connect() as db:
    db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS subjects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        name TEXT,
        total INTEGER,
        attended INTEGER
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        subject TEXT,
        action TEXT,
        time TEXT
    )
    """)


# ---------- FUNCTIONS ----------
def get_percent(attended, total):
    if total == 0:
        return 0
    return round((attended / total) * 100, 2)


def reaction(percent):
    if percent < 60:
        return "😡"
    elif percent < 75:
        return "🙂"
    else:
        return "😎"


def risk(percent):
    if percent < 60:
        return "HIGH RISK"
    elif percent < 75:
        return "MEDIUM RISK"
    else:
        return "SAFE"


# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = connect()
        user = db.execute("SELECT * FROM users WHERE email=? AND password=?",
                          (email, password)).fetchone()

        if user:
            session["user"] = email
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid login!")

    return render_template("login.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = connect()
        try:
            db.execute("INSERT INTO users (email, password) VALUES (?, ?)",
                       (email, password))
            db.commit()
            return redirect("/")
        except:
            return render_template("register.html", error="User already exists")

    return render_template("register.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    db = connect()
    subjects = db.execute("SELECT * FROM subjects WHERE user=?",
                          (session["user"],)).fetchall()

    quote = [
        "Success is built on discipline 📚",
        "Don’t bunk too much 🙂",
        "Small steps every day 💪",
        "Consistency is power 🔥"
    ]

    return render_template("dashboard.html",
                           subjects=subjects,
                           get_percent=get_percent,
                           reaction=reaction,
                           risk=risk,
                           quote=quote[datetime.now().second % 4])


# ---------- ADD SUBJECT ----------
@app.route("/add", methods=["GET", "POST"])
def add_subject():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        total = int(request.form["total"])
        attended = int(request.form["attended"])

        db = connect()
        db.execute("INSERT INTO subjects (user, name, total, attended) VALUES (?, ?, ?, ?)",
                   (session["user"], name, total, attended))

        db.execute("INSERT INTO history (user, subject, action, time) VALUES (?, ?, ?, ?)",
                   (session["user"], name, "Added", datetime.now().strftime("%d-%m-%Y %H:%M")))

        db.commit()
        return redirect("/dashboard")

    return render_template("add_subject.html")


# ---------- EDIT SUBJECT ----------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_subject(id):
    if "user" not in session:
        return redirect("/")

    db = connect()
    subject = db.execute("SELECT * FROM subjects WHERE id=?",
                         (id,)).fetchone()

    if request.method == "POST":
        name = request.form["name"]
        total = request.form["total"]
        attended = request.form["attended"]

        db.execute("UPDATE subjects SET name=?, total=?, attended=? WHERE id=?",
                   (name, total, attended, id))

        db.execute("INSERT INTO history (user, subject, action, time) VALUES (?, ?, ?, ?)",
                   (session["user"], name, "Edited", datetime.now().strftime("%d-%m-%Y %H:%M")))

        db.commit()
        return redirect("/dashboard")

    return render_template("edit_subject.html", subject=subject)


# ---------- DELETE SUBJECT ----------
@app.route("/delete/<int:id>")
def delete_subject(id):
    if "user" not in session:
        return redirect("/")

    db = connect()
    sub = db.execute("SELECT name FROM subjects WHERE id=?", (id,)).fetchone()

    if sub:
        db.execute("DELETE FROM subjects WHERE id=?", (id,))
        db.execute("INSERT INTO history (user, subject, action, time) VALUES (?, ?, ?, ?)",
                   (session["user"], sub[0], "Deleted", datetime.now().strftime("%d-%m-%Y %H:%M")))
        db.commit()

    return redirect("/dashboard")


# ---------- HISTORY ----------
@app.route("/history")
def show_history():
    if "user" not in session:
        return redirect("/")

    db = connect()
    data = db.execute("SELECT * FROM history WHERE user=? ORDER BY id DESC",
                      (session["user"],)).fetchall()

    return render_template("history.html", history=data)


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()
