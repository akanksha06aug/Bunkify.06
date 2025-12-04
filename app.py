from flask import Flask, render_template, request, redirect, session, flash
from database import *
import random, datetime

app = Flask(__name__)
app.secret_key = "bunkify123"

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if user_exists(email):
            flash("User already exists")
            return redirect("/register")

        otp = random.randint(1000,9999)
        session["otp"] = otp
        session["email"] = email
        session["password"] = password

        print("OTP:", otp)  # For testing

        return redirect("/otp")

    return render_template("register.html")

# ---------------- OTP ----------------
@app.route("/otp", methods=["GET","POST"])
def otp():
    if request.method == "POST":
        user_otp = request.form["otp"]

        if str(user_otp) == str(session["otp"]):
            create_user(session["email"], session["password"])
            flash("Account created successfully")
            return redirect("/")
        else:
            flash("Wrong OTP")

    return render_template("otp.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    if validate_user(email, password):
        session["user"] = email
        return redirect("/dashboard")
    else:
        flash("Invalid Login")
        return redirect("/")


# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot", methods=["GET","POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"]

        if user_exists(email):
            otp = random.randint(1000,9999)
            session["reset_otp"] = otp
            session["reset_email"] = email
            print("Reset OTP:", otp)
            return redirect("/reset_otp")
        else:
            flash("Email not found")

    return render_template("forgot.html")


@app.route("/reset_otp", methods=["GET","POST"])
def reset_otp():
    if request.method == "POST":
        otp = request.form["otp"]
        new_pass = request.form["newpass"]

        if otp == str(session["reset_otp"]):
            change_password(session["reset_email"], new_pass)
            flash("Password Reset Successful")
            return redirect("/")
        else:
            flash("Wrong OTP")

    return render_template("otp.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    subjects = get_subjects(session["user"])
    quote = random.choice(quotes)

    return render_template("dashboard.html", subjects=subjects, quote=quote)


# ---------------- ADD SUBJECT ----------------
@app.route("/add_subject", methods=["POST"])
def add_subject_route():
    name = request.form["name"]
    total = int(request.form["total"])
    attended = int(request.form["attended"])

    add_subject(session["user"], name, total, attended)
    return redirect("/dashboard")


# ---------------- BUNK ----------------
@app.route("/bunk/<subject>")
def bunk(subject):
    bunk_class(session["user"], subject)
    add_history(session["user"], subject, "BUNKED 😈")
    return redirect("/dashboard")

# ---------------- ATTEND ----------------
@app.route("/attend/<subject>")
def attend(subject):
    attend_class(session["user"], subject)
    add_history(session["user"], subject, "ATTENDED 😇")
    return redirect("/dashboard")

# ---------------- HISTORY ----------------
@app.route("/history")
def history_page():
    hist = get_history(session["user"])
    return render_template("history.html", history=hist)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


quotes = [
    "Don't bunk too much 😎",
    "Your future is watching you!",
    "One more class = less tension",
    "Attendance = Respect"
]

if __name__ == "__main__":
    app.run(debug=True)
        
