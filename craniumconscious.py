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

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    gad7_score = db.Column(db.Integer)
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
    
    if request.method == 'POST':
        if "Log In" in request.form.values():
            return redirect(url_for("loginpage"))
    
        if "Sign Up" in request.form.values():
            return redirect(url_for("signup"))
    
    return render_template (
        "index.html"
    )

@app.route('/loginpage')
def loginpage():
    
    if request.method == 'POST':
        if "Login" in request.form.values():
            username = request.form.get("username")
            password = request.form.get("password")
            return redirect(url_for("login", username=username, password=password))
        
    return render_template (
        "LogInPage.html"
    )
    
@app.route('/login')
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    user = Person.query.filter_by(username=username).first()
    
    if user:
        login_user(user)
        return redirect(url_for('home'))
    else:
        flash("No user found.")
        return redirect(url_for("index"))
    
@app.route('/signup')
def signup():
    
    if request.method == 'POST':
        if "Sign Up" in request.form.values():
            email = request.form.get("email")
            username = request.form.get("username")
            password = request.form.get("username")
            return redirect(url_for("login", username=username, password=password, email=email))
    
    
    return render_template (
        "SignUpPage.html"
    )
    

@app.route('/register')
def register():
    email = request.args.get('email')
    username = request.args.get('username')
    password = request.args.get('password')
    user = Person.query.filter_by(username=username).first()
    
    if user:
        flash("User already exists.")
        return redirect(url_for('index'))
    elif user is None:
        user = Person(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("gad"))
    
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
    #Insert code to get the result integer and put it into the database
    
    return render_template (
        "GAD-7.html"
    )
    
@app.route('/phq')
def phq():
    #Insert code to get the result integer and put it into the database
    
    return render_template (
        "PHQ_9.html"
    )
    
@app.route('/journal')
def journal():
    #insert code to load journal and reminder information and display it
    #insert a bunch of database stuff and grabbing info from submissions
    
    return render_template (
        "Journal.html"
    )
    
@app.route('/todo')
def todo():
    #dont really need any more code here unless we want lists to persist
    return render_template (
        "ToDoList.html"
    )
    
@app.route('/moodtracker')
def moodtracker():
    
    #insert code to load previous tracked moods from this week and stuff
    
    if request.method == 'POST':
        selected_mood = request.form.get('mood')
        
        #do things with mood, like add to database and stuff
    
    return render_template (
        "MoodTracker.html"
    )
    
@app.route('/mindfulactivites')
def mindfulactivites():
    #this shouldnt need more code
    return render_template (
        "MindfulActivites.html"
    )
    
@app.route('/poetry')
def poetry():
    
    if request.method == 'POST':
        if "Like" in request.form.values():
            like = True
            dislike = False
            #do something machine learning or whatever
        if "Dislike" in request.form.values():
            dislike = True
            like = False
            #do something machine learning or whatever
        
    return render_template (
        "Poetry.html"
    )
    
@app.route('/quotes')
def quotes():
    
    if request.method == 'POST':
        if "Like" in request.form.values():
            like = True
            dislike = False
            #do something machine learning or whatever
        if "Dislike" in request.form.values():
            dislike = True
            like = False
            #do something machine learning or whatever
    
    return render_template (
        "Quotes.html"
    )
    
@app.route('/crisissupport')
def crisis():
    #this shouldnt need more code, unless we want the website to automatically update based on users locations
    
    return render_template (
        "CrisisSupportInformation.html"
    )