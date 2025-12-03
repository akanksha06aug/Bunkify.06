from flask import Flask, render_template, request, redirect, session
import sqlite3, random
from datetime import datetime

app = Flask(__name__)
app.secret_key="bunkify"

quotes = [
"📚 One class today = One less regret tomorrow",
"🔥 75% is law, not a suggestion",
"🎓 Your future self is watching",
"📖 Every class matters",
"⏳ Bunk today, beg tomorrow"
]

def db():
    return sqlite3.connect("users.db")

def create_tables():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS subjects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        subject TEXT,
        attended INTEGER,
        total INTEGER,
        bunked INTEGER
    )
    """)
    conn.commit()

create_tables()

# ---------- LOGIN ----------

@app.route("/",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]

        c=db().cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?",(email,password))
        user=c.fetchone()

        if user:
            session["user"]=email
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("login.html")

# ---------- REGISTER ----------

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]

        otp=random.randint(1000,9999)
        session["otp"]=otp
        session["new_user"]=(email,password)

        print("Your OTP:",otp)
        return redirect("/otp")

    return render_template("register.html")

@app.route("/otp",methods=["GET","POST"])
def otp():
    if request.method=="POST":
        user_otp=request.form["otp"]

        if str(session["otp"])==user_otp:
            email,password=session["new_user"]

            conn=db()
            conn.execute("INSERT INTO users(email,password) VALUES(?,?)",(email,password))
            conn.commit()

            return redirect("/")
        else:
            return render_template("otp.html",error="Wrong OTP")

    return render_template("otp.html")

# ---------- DASHBOARD ----------

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    email=session["user"]

    c=db().cursor()
    c.execute("SELECT * FROM subjects WHERE email=?",(email,))
    subjects=c.fetchall()

    final_data=[]

    for s in subjects:
        attended=s[3]
        total=s[4]
        bunked=s[5]

        percent=(attended/total)*100 if total>0 else 0

        if percent>=75:
            teacher="😌 Happy"
            risk="✅ Safe"
        elif percent>=60:
            teacher="😠 Angry"
            risk="⚠ Warning"
        else:
            teacher="🤬 Furious"
            risk="❌ Detained"

        final_data.append([s,round(percent,2),teacher,risk])

    return render_template("dashboard.html",data=final_data,
                           quote=random.choice(quotes))

# ---------- ADD SUBJECT ----------

@app.route("/add",methods=["GET","POST"])
def add():
    if request.method=="POST":
        subject=request.form["subject"]
        attended=request.form["attended"]
        total=request.form["total"]
        bunk=request.form["bunk"]
        email=session["user"]

        conn=db()
        conn.execute("INSERT INTO subjects(email,subject,attended,total,bunked) VALUES(?,?,?,?,?)",
                     (email,subject,attended,total,bunk))
        conn.commit()

        return redirect("/dashboard")

    return render_template("add_subject.html")

# ---------- EDIT SUBJECT ----------

@app.route("/edit/<id>",methods=["GET","POST"])
def edit(id):
    conn=db()
    c=conn.cursor()

    if request.method=="POST":
        attended=request.form["attended"]
        total=request.form["total"]
        bunk=request.form["bunk"]

        c.execute("UPDATE subjects SET attended=?, total=?, bunked=? WHERE id=?",
                  (attended,total,bunk,id))
        conn.commit()

        return redirect("/dashboard")

    c.execute("SELECT * FROM subjects WHERE id=?",(id,))
    subject=c.fetchone()

    return render_template("edit_subject.html",subject=subject)

# ---------- DELETE ----------

@app.route("/delete/<id>")
def delete(id):
    conn=db()
    conn.execute("DELETE FROM subjects WHERE id=?",(id,))
    conn.commit()
    return redirect("/dashboard")

# ---------- FORGOT ----------

@app.route("/forgot",methods=["GET","POST"])
def forgot():
    if request.method=="POST":
        email=request.form["email"]
        newpass="123456"

        conn=db()
        conn.execute("UPDATE users SET password=? WHERE email=?",(newpass,email))
        conn.commit()

        return "New password = 123456"

    return render_template("forgot.html")

# ---------- LOGOUT ----------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
