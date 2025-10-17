from flask import Flask, request, render_template as render, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, logout_user, current_user
)
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskBook.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'  # where to redirect if not logged in
login_manager.login_message_category = 'info'


# ---------- USER MODEL ----------
class User(db.Model, UserMixin):  # ✅ add UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.name}')"


# ---------- LOAD USER ----------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------- DATABASE SETUP ----------
with app.app_context():
    db.create_all()


# ---------- ROUTES ----------
@app.route('/')
def home():
    if current_user.is_authenticated:
        return render('home.html', user=current_user)
    return render('home.html')


@app.route('/signup')
def signup():
    return render('signup.html')


@app.route('/register', methods=['POST'])
def register():
    """
    Step 1: Save user data in session and show OTP form
    """
    username = request.form['username']
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # temporarily store user data
    session['temp_user'] = {
        'username': username,
        'name': name,
        'email': email,
        'password': password
    }

    # generate random 6-digit OTP
    otp = str(random.randint(100000, 999999))
    session['otp'] = otp

    # ⚠️ For testing only — display OTP on page
    return render('otp.html', otp=otp)


@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    """
    Step 2: Verify OTP and register user permanently
    """
    entered_otp = request.form['otp']
    saved_otp = session.get('otp')

    if entered_otp == saved_otp:
        user_data = session.get('temp_user')
        if not user_data:
            return "Session expired. Please register again."

        # create actual user record
        new_user = User(
            username=user_data['username'],
            name=user_data['name'],
            email=user_data['email'],
            password=user_data['password']
        )
        db.session.add(new_user)
        db.session.commit()

        # clean up session
        session.pop('temp_user', None)
        session.pop('otp', None)

        return redirect(url_for('login_page'))
    else:
        return "Invalid OTP. Please try again."


@app.route('/login')
def login_page():
    return render('login.html')


@app.route('/login-user', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        login_user(user)  # ✅ Flask-Login handles the session
        return redirect(url_for('home'))
    else:
        return "Invalid username or password"


@app.route('/dashboard')
@login_required  # ✅ user must be logged in to access
def dashboard():
    return f"Welcome, {current_user.name}! <a href='/logout'>Logout</a>"


@app.route('/logout')
@login_required
def logout():
    logout_user()  # ✅ clears user session
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True)
