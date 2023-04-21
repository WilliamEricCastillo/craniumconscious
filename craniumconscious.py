from flask import *
import os
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import datetime

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
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    gad7_score = db.Column(db.Integer)
    phq9_score = db.Column(db.Integer)
    journal_entries = db.relationship('JournalEntry', backref='user', lazy=True)
    
    def is_active(self):
        return True
    
    def get_id(self):
        return str(self.id)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    mood = db.Column(db.String(20))
    remind_me_to_tell_my_therapist = db.Column(db.String(80))
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)


with app.app_context():
    db.create_all()
    
@app.route('/', methods = ['POST', 'GET'])
def index():
    
    if request.method == 'POST':
        if "Log In" in request.form.values():
            return redirect(url_for("loginpage"))
    
        if "Sign Up" in request.form.values():
            return redirect(url_for("signup"))
    
    return render_template (
        "index.html"
    )

@app.route('/loginpage', methods = ['POST', 'GET'])
def loginpage():
    
    if request.method == 'POST':
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
    
@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        return redirect(url_for("register", username=username, password=password, email=email))
    
    
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
        return redirect(url_for('home'))
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
    #shouldnt need more code 
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
        "PHQ-9.html"
    )
    
@app.route('/journal')
def journal():
    
    # get current date
    today = datetime.date.today() #YYYY-MM-DD


    #insert code to load journal and reminder information and display it
    #insert a bunch of database stuff and grabbing info from submissions
    
    return render_template (
        "Journal.html",
        today = today,
    )
    
@app.route('/todo')
def todo():
    #dont really need any more code here unless we want lists to persist
    return render_template (
        "ToDoList.html"
    )
    
@app.route('/moodtracker', methods = ['POST', 'GET'])
def moodtracker():
    
    # get current date aand week starts and ends YYYY-MM-DD
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday() + 1)
    week_end = week_start + datetime.timedelta(days=6)
    
    #insert code to load previous tracked moods from this week and stuff//
    
    if request.method == 'POST':
        if "Submit" in request.form.values():
            selected_mood = request.form.get('mood')
            entry = JournalEntry.query.filter_by(user_id=user_id, date=date).first()
            if entry:
                entry.mood = selected_mood
                db.session.commit()
            else:
                new_entry = JournalEntry(
                    mood=selected_mood,
                    data=today,
                    user=current_user.id
                )
                db.session.add(new_entry)
                db.session.commit()
                
            
        
        #do things with mood, like add to database and stuff
    
    return render_template (
        "MoodTracker.html",
        today = today,
        week_start = week_start,
        week_end = week_end,
    )
    
@app.route('/mindfulactivities', methods = ['GET'])
def mindfulactivities():
    #this shouldnt need more code
    return render_template (
        "MindfulActivities.html"
    )
    
@app.route('/poetry', methods = ['POST', 'GET'])
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
    
@app.route('/quotes', methods = ['POST', 'GET'])
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
    
app.run(debug=True)