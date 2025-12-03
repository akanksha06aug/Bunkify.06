from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import math

app = Flask(__name__)
app.secret_key = "bunkify_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bunkify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ MODELS --------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100))
    name = db.Column(db.String(100))
    total_classes = db.Column(db.Integer, default=0)
    attended_classes = db.Column(db.Integer, default=0)
    bunked_classes = db.Column(db.Integer, default=0)


class BunkHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    date = db.Column(db.String(50))
    emoji = db.Column(db.String(10))
    user_email = db.Column(db.String(100))


# ------------------ MOTIVATION --------------------

quotes = [
    "Discipline today, success tomorrow",
    "Every class counts 🤓",
    "No bunk, no backlog 🔥",
    "Attendance = Respect 💯",
    "Study now, party later 😎"
]

# ------------------ OTP STORE --------------------

otp_store = {}

def generate_otp():
    return str(random.randint(100000, 999999))


# ------------------ ROUTES --------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to BUNKIFY API"})


# ------------------ SIGNUP (SEND OTP) --------------------

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    email = data["email"]
    otp = generate_otp()

    otp_store[email] = otp
    print(f"OTP for {email} is -> {otp}")  # Replace with email API if needed

    return jsonify({"message": "OTP sent successfully (check console)"})


@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data["email"]
    password = data["password"]
    otp = data["otp"]

    if email not in otp_store or otp_store[email] != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    del otp_store[email]

    return jsonify({"message": "Account created successfully"})


# ------------------ LOGIN --------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email, password=password).first()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 400

    session["user"] = email
    return jsonify({"message": "Login successful"})


# ------------------ FORGOT PASSWORD (OTP) --------------------

@app.route("/forgot-password/send-otp", methods=["POST"])
def forgot_send_otp():
    email = request.json["email"]

    if not User.query.filter_by(email=email).first():
        return jsonify({"error": "User not found"}), 404

    otp = generate_otp()
    otp_store[email] = otp
    print(f"Forgot Password OTP for {email} -> {otp}")

    return jsonify({"message": "OTP sent for password reset"})


@app.route("/forgot-password/reset", methods=["POST"])
def reset_password():
    data = request.json
    email = data["email"]
    otp = data["otp"]
    new_password = data["new_password"]

    if email not in otp_store or otp_store[email] != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    user = User.query.filter_by(email=email).first()
    user.password = new_password
    db.session.commit()

    del otp_store[email]
    return jsonify({"message": "Password reset successful"})


# ------------------ ADD SUBJECT --------------------

@app.route("/add-subject", methods=["POST"])
def add_subject():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.json
    subject = Subject(
        user_email=session["user"],
        name=data["name"],
        total_classes=data["total"],
        attended_classes=data["attended"],
        bunked_classes=data["bunked"]
    )

    db.session.add(subject)
    db.session.commit()

    return jsonify({"message": "Subject added"})


# ------------------ UPDATE SUBJECT --------------------

@app.route("/edit-subject/<int:id>", methods=["PUT"])
def edit_subject(id):
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    subject = Subject.query.get_or_404(id)
    data = request.json

    subject.total_classes = data["total"]
    subject.attended_classes = data["attended"]
    subject.bunked_classes = data["bunked"]

    db.session.commit()

    return jsonify({"message": "Subject updated"})


# ------------------ DELETE SUBJECT --------------------

@app.route("/delete-subject/<int:id>", methods=["DELETE"])
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()

    return jsonify({"message": "Subject deleted"})


# ------------------ BUNK A CLASS --------------------

@app.route("/bunk/<int:id>", methods=["POST"])
def bunk_class(id):
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    subject = Subject.query.get(id)
    subject.total_classes += 1
    subject.bunked_classes += 1

    percent = attendance(subject.attended_classes, subject.total_classes)
    emoji = teacher_reaction(percent)

    history = BunkHistory(
        subject=subject.name,
        date=str(datetime.now()),
        emoji=emoji,
        user_email=session["user"]
    )

    db.session.add(history)
    db.session.commit()

    return jsonify({
        "message": "Class bunked",
        "emoji": emoji,
        "quote": random.choice(quotes)
    })


# ------------------ ATTEND CLASS --------------------

@app.route("/attend/<int:id>", methods=["POST"])
def attend_class(id):
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    subject = Subject.query.get(id)
    subject.total_classes += 1
    subject.attended_classes += 1

    percent = attendance(subject.attended_classes, subject.total_classes)
    emoji = teacher_reaction(percent)

    db.session.commit()

    return jsonify({
        "message": "Class attended",
        "emoji": emoji,
        "attendance": percent
    })


# ------------------ DASHBOARD --------------------

@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    subjects = Subject.query.filter_by(user_email=session["user"]).all()

    result = []
    for s in subjects:
        percent = attendance(s.attended_classes, s.total_classes)

        result.append({
            "id": s.id,
            "name": s.name,
            "total": s.total_classes,
            "attended": s.attended_classes,
            "bunked": s.bunked_classes,
            "percentage": percent,
            "internal_marks_risk": internal_risk(percent)
        })

    return jsonify(result)


# ------------------ HISTORY --------------------

@app.route("/history", methods=["GET"])
def history():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    data = BunkHistory.query.filter_by(user_email=session["user"]).all()

    return jsonify([
        {
            "subject": h.subject,
            "date": h.date,
            "emoji": h.emoji
        } for h in data
    ])


# ------------------ LOGIC --------------------

def attendance(attended, total):
    if total == 0:
        return 0
    return round((attended / total) * 100, 2)


def teacher_reaction(percentage):
    if percentage >= 85:
        return "😎"
    elif percentage >= 75:
        return "🙂"
    else:
        return "😡"


def internal_risk(percent):
    if percent < 60:
        return "HIGH RISK"
    elif percent < 75:
        return "MEDIUM RISK"
    else:
        return "SAFE"


# ------------------ MAIN --------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
