from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "bunkify_secret"

# ------------------ DATABASE ------------------

def get_db():
    conn = sqlite3.connect("bunkify.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            total INTEGER DEFAULT 0,
            attended INTEGER DEFAULT 0,
            bunked INTEGER DEFAULT 0
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject_name TEXT,
            date TEXT,
            action TEXT
        )
        """)


init_db()

# ------------------ HOME ------------------

@app.route('/')
def index():
    return render_template("index.html")

# ------------------ REGISTER ------------------

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        try:
            db.execute("INSERT INTO users (email, password) VALUES (?,?)",
                       (email, password))
            db.commit()
            flash("Account Created Successfully ✅")
            return redirect("/login")
        except:
            flash("Email already exists ❌")
            return redirect("/register")

    return render_template("register.html")


# ------------------ LOGIN ------------------

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_db().execute("SELECT * FROM users WHERE email=? AND password=?",
                                (email, password)).fetchone()

        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            return redirect("/dashboard")
        else:
            flash("Wrong login details ❌")

    return render_template("login.html")


# ------------------ LOGOUT ------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")


# ------------------ DASHBOARD ------------------

@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    subjects = get_db().execute("SELECT * FROM subjects WHERE user_id=?",
                                (session["user_id"],)).fetchall()

    return render_template("dashboard.html", subjects=subjects)


# ------------------ ADD SUBJECT ------------------

@app.route('/add-subject', methods=["POST"])
def add_subject():
    if "user_id" not in session:
        return redirect("/login")

    name = request.form["name"]

    get_db().execute("""
        INSERT INTO subjects (user_id,name)
        VALUES (?,?)
    """, (session["user_id"], name))

    get_db().commit()
    return redirect("/dashboard")


# ------------------ EDIT SUBJECT ------------------

@app.route('/edit-subject/<int:id>', methods=["GET", "POST"])
def edit_subject(id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    subject = db.execute("SELECT * FROM subjects WHERE id=? AND user_id=?",
                         (id, session["user_id"])).fetchone()

    if request.method == "POST":
        new_name = request.form["name"]

        db.execute("UPDATE subjects SET name=? WHERE id=? AND user_id=?",
                   (new_name, id, session["user_id"]))
        db.commit()
        return redirect("/dashboard")

    return render_template("edit_subject.html", subject=subject)


# ------------------ DELETE SUBJECT ------------------

@app.route('/delete-subject/<int:id>')
def delete_subject(id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    db.execute("DELETE FROM subjects WHERE id=? AND user_id=?",
               (id, session["user_id"]))

    db.execute("DELETE FROM history WHERE subject_name IN (SELECT name FROM subjects WHERE id=?)", (id,))

    db.commit()
    return redirect("/dashboard")


# ------------------ BUNK / ATTEND ------------------

@app.route('/mark/<int:id>/<string:action>')
def mark(id, action):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    subject = db.execute("SELECT * FROM subjects WHERE id=? AND user_id=?",
                         (id, session["user_id"])).fetchone()

    if not subject:
        return redirect("/dashboard")

    total = subject['total'] + 1
    attended = subject['attended']
    bunked = subject['bunked']

    if action == "bunk":
        bunked += 1
    else:
        attended += 1

    db.execute("""
        UPDATE subjects SET total=?, attended=?, bunked=?
        WHERE id=? AND user_id=?
    """, (total, attended, bunked, id, session["user_id"]))

    db.execute("""
        INSERT INTO history (user_id,subject_name,date,action)
        VALUES (?,?,?,?)
    """, (session["user_id"], subject['name'], str(datetime.now()), action))

    db.commit()

    return redirect("/dashboard")


# ------------------ HISTORY ------------------

@app.route('/history')
def history():
    if "user_id" not in session:
        return redirect("/login")

    rows = get_db().execute("SELECT * FROM history WHERE user_id=? ORDER BY id DESC",
                            (session["user_id"],)).fetchall()

    return render_template("history.html", history=rows)


# ------------------ QUOTES ------------------

quotes = [
    "Every class you attend is a step to success ✨",
    "Bunk less, achieve more 💪",
    "Attendance today = Opportunities tomorrow 🚀",
    "Don’t bunk your future 😎"
]

@app.route('/quote')
def quote():
    return {"quote": random.choice(quotes)}


# ------------------ ATTENDANCE + EMOJI ------------------

def get_emoji(percent):
    if percent < 50:
        return "😡"
    elif percent < 75:
        return "🙂"
    else:
        return "😎"


@app.route('/status/<int:id>')
def status(id):
    if "user_id" not in session:
        return redirect("/login")

    subject = get_db().execute("SELECT * FROM subjects WHERE id=? AND user_id=?",
                               (id, session["user_id"])).fetchone()

    if subject['total'] == 0:
        percent = 0
    else:
        percent = (subject['attended'] / subject['total']) * 100

    risk = "SAFE"
    if percent < 50:
        risk = "VERY HIGH RISK"
    elif percent < 75:
        risk = "MEDIUM RISK"

    return {
        "subject": subject["name"],
        "attendance": percent,
        "emoji": get_emoji(percent),
        "risk": risk
    }


# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(debug=True)
