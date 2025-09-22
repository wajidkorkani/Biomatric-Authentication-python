from flask import Flask, render_template as render, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy as sql
import face_recognition
import numpy as np
import cv2
import os
import pickle

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biometric.db'
db = sql(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    face_encoding = db.Column(db.PickleType, nullable=False)  # store numpy array as pickle


# Home Page
@app.route('/')
def Home():
    if "user" in session:
        return f"Welcome {session['user']}!"
    return render("index.html")


@app.route('/register', methods=['GET', 'POST'])
def Register():
    if request.method == 'POST':
        username = request.form['username']

        # Capture image from webcam
        video = cv2.VideoCapture(0)
        ret, frame = video.read()
        video.release()

        if not ret:
            flash("Failed to capture image.")
            return redirect(url_for("Register"))

        # Convert to RGB
        rgb_frame = frame[:, :, ::-1]

        # Detect faces and get encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if face_encodings:
            encoding = face_encodings[0]

            # Save user to DB
            new_user = User(username=username, face_encoding=encoding)
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful. You can now login.")
            return redirect(url_for("Login"))
        else:
            flash("No face detected, please try again.")
            return redirect(url_for("Register"))

    return render("register.html")


# Login Route - Face Recognition
@app.route('/login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        # Capture image from webcam
        video = cv2.VideoCapture(0)
        ret, frame = video.read()
        video.release()

        if not ret:
            flash("Failed to capture image.")
            return redirect(url_for("Login"))

        # Encode the face
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)


        if face_encodings:
            login_encoding = face_encodings[0]

            # Compare with stored users
            users = User.query.all()
            for user in users:
                match = face_recognition.compare_faces([user.face_encoding], login_encoding)
                if match[0]:
                    session["user"] = user.username
                    flash("Login successful!")
                    return redirect(url_for("Home"))

        flash("Authentication failed. Try again.")
        return redirect(url_for("Login"))

    return render("login.html")


# Logout Route
@app.route('/logout')
def Logout():
    session.pop("user", None)
    flash("Logged out successfully.")
    return redirect(url_for("Home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
