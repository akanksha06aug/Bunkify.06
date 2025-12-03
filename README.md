# 📚 BUNKIFY – College Class Bunk Predictor

BUNKIFY is a Flask-based college class bunk prediction system that helps students track bunked classes, attendance percentage, internal marks risk, and motivation status using emojis and quotes.

This project includes:
✅ Email + Password Login
✅ OTP based account creation
✅ Forgot Password + Resend OTP
✅ Add / Edit / Delete Subjects
✅ Track Bunked Classes
✅ Attendance Percentage Calculation
✅ Bunk History Tracking
✅ Teacher Emoji Reactions (😡 🙂 😎)
✅ Motivation Quotes
✅ Internal Marks Risk
✅ Ready for GitHub & Render Deployment

---

## 🔧 Technologies Used

• Python
• Flask
• HTML & CSS (No JavaScript used)
• SQLite
• GitHub
• Render for deployment

---

## 📁 Project Structure

```
BUNKIFY/
│
├── app.py
├── database.db
├── requirements.txt
├── README.md
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── verify_otp.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── dashboard.html
│   ├── add_subject.html
│   └── history.html
│
├── static/
│   └── style.css
```



## 🚀 How To Upload On GitHub

1. Go to [https://github.com](https://github.com)
2. Click **New Repository**
3. Name: `bunkify`
4. Click **Create**
5. Upload all project files
6. Click **Commit changes**

---

## 🌍 How To Deploy On Render

1. Go to [https://render.com](https://render.com)
2. Click **New Web Service**
3. Connect your GitHub account
4. Select **bunkify repository**
5. Add:
   • Start Command: `python app.py`
6. Click **Deploy**

Your live link will be generated 🔗

---

## 📊 Attendance & Risk Logic

• > 85% → 😎 Safe
• 75% – 85% → 🙂 Warning
• < 75% → 😡 Risk

Internal marks depend directly on attendance percentage.

---

## 👩‍💻 Developer


Project name: **BUNKIFY**
Group Project – B.Tech 2nd Year

---

## ⭐ Future Upgrades

• Charts & Graphs
• Excel export
• Teacher panel
• AI suggestions

---

**If you like this project – Give it a STAR ⭐ on GitHub**
