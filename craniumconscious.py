from flask import *
import os
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return Person.query.get(int(id))


#DATABASE MODELS
class Person(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    def is_active(self):
        return True
    
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    gad7_score = db.Column(db.Integer, nullable=False)
    phq9_score = db.Column(db.Interger)
    diary_entries = db.relationship('DiaryEntry', backref='user', lazy=True)
    reminders = db.relationship('Reminder', backref='user', lazy=True)

class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(20), nullable=False)
    remind_me_to_tell_my_therapist = db.Column(db.String(80))
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)


with app.app_context():
    db.create_all()
    
@app.route('/')
def index():
    
    return render_template (
        "index.html"
    )

@app.route('/loginpage')
def loginpage():
    
    return render_template (
        "LogInPage.html"
    )
    
@app.route('/login')
def login():
    username = request.args.get('username')
    user = Person.query.filter_by(username=username).first()
    
    if user:
        login_user(user)
        return redirect(url_for('home'))
    else:
        flash("No user found.")
        return redirect(url_for("loginpage"))
    
@app.route('/signup')
def signup():
    
    return render_template (
        "SignUpPage.html"
    )
    

@app.route('/register')
def register():
    username = request.args.get('username')
    user = Person.query.filter_by(username=username).first()
    
    if user:
        flash("User already exists.")
        return redirect(url_for('loginpage/'))
    elif user is None:
        user = Person(username=username)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("home"))
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/home')
def home():
    
    return render_template (
        "HomePage.html"
    )
    
@app.route('/gad')
def gad():
    
    return render_template (
        "GAD-7.html"
    )
    
@app.route('/phq')
def phq():
    
    return render_template (
        "PHQ_9.html"
    )
    
@app.route('/calendar')
def calendar():
    
    return render_template (
        "Calendar.html"
    )
    
@app.route('/todo')
def todo():
    
    return render_template (
        "ToDoList.html"
    )
    
@app.route('/moodtracker')
def moodtracker():
    
    return render_template (
        "MoodTracker.html"
    )
    
@app.route('/poetry')
def poetry():
    
    return render_template (
        "Poetry.html"
    )
    
@app.route('/quotes')
def quotes():
    
    return render_template (
        "Quotes.html"
    )
    
@app.route('/crisissupport')
def crisis():
    
    return render_template (
        "CrisisSupportInformation.html"
    )