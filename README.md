# BUNKIFY — Smart Attendance & Bunk Tracker

A Flask based mini project which allows students to manage their
attendance, bunk history and internal marks risk.

## Features
- Login/Register with Email
- OTP verification
- Add/Edit/Delete Subjects
- Bunk History stored in Database
- Attendance percentage calculation
- Teacher reaction emojis
- Internal marks risk detection
- Motivational quotes
- Edit & Delete subjects
- Forgot password

## Technologies Used
- Python
- Flask
- HTML
- CSS
- SQLite
- Render

## How to Run

pip install flask
pip install gunicorn
python app.py

Open → http://127.0.0.1:5000

## Deployment
Deployed using Render

Start command:
gunicorn app:app

Build command:
pip install -r requirements.txt

