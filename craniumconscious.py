from flask import *
import os
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

@login_manager.user_loader
def load_user(id):
    return Person.query.get(int(id))


#DATABASE MODELS
class Person(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    gad7_score = db.Column(db.Integer)
    phq9_score = db.Column(db.Integer)
    journal_entries = db.relationship('JournalEntry', backref='user', lazy=True)
    
    def is_active(self):
        return True
    
    def get_id(self):
        return str(self.id)

    def password_hash(self, passwd):
        self.password = generate_password_hash(passwd)

    def check_password(self, passwd):
        return check_password_hash(self.password, passwd)

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
        if user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Incorrect password.")
            return redirect(url_for("index"))
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
        user = Person(email=email, username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("gad"))
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/home')
@login_required
def home():
    #shouldnt need more code 
    return render_template (
        "HomePage.html"
    )
    
@app.route('/gad', methods=['POST', 'GET'])
@login_required
def gad():
    
    if request.method == 'POST':
        q1 = int(request.form.get('q1'))
        q2 = int(request.form.get('q2'))
        q3 = int(request.form.get('q3'))
        q4 = int(request.form.get('q4'))
        q5 = int(request.form.get('q5'))
        q6 = int(request.form.get('q6'))
        q7 = int(request.form.get('q7'))
        
        gad_score = q1 + q2 + q3 + q4 + q5 + q6 + q7
        current_user.gad7_score = gad_score
        db.session.commit()

    return render_template (
        "GAD-7.html"
    )
    
@app.route('/phq', methods=['POST', 'GET'])
@login_required
def phq():
    phq_score = 0
    
    if request.method == 'POST':
        q1 = int(request.form.get('q1'))
        q2 = int(request.form.get('q2'))
        q3 = int(request.form.get('q3'))
        q4 = int(request.form.get('q4'))
        q5 = int(request.form.get('q5'))
        q6 = int(request.form.get('q6'))
        q7 = int(request.form.get('q7'))
        q8 = int(request.form.get('q8'))
        q9 = int(request.form.get('q9'))
        
        phq_score = q1 + q2 + q3 + q4 + q5 + q6 + q7 + q8 + q9
        
        current_user.phq9_score = phq_score
        db.session.commit()

    return render_template (
        "PHQ-9.html",
    )
    
@app.route('/journal')
@login_required
def journal():
    
    # get current date
    today = datetime.date.today() #YYYY-MM-DD

    
    return render_template (
        "Journal.html",
        today = today,
    )
    
@app.route('/todo')
@login_required
def todo():
    #dont really need any more code here unless we want lists to persist
    return render_template (
        "ToDoList.html"
    )
    
@app.route('/moodtracker', methods = ['POST', 'GET'])
@login_required
def moodtracker():
    
    day_mood_list = [2, 2, 2, 2, 2, 2, 2]
    
    # get current date aand week starts and ends YYYY-MM-DD
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday() + 1)
    day_2 = week_start + datetime.timedelta(days=1)
    day_3 = day_2 + datetime.timedelta(days=1)
    day_4 = day_3 + datetime.timedelta(days=1)
    day_5 = day_4 + datetime.timedelta(days=1)
    day_6 = day_5 + datetime.timedelta(days=1)
    week_end = day_6 + datetime.timedelta(days=1)
    
    current_week = True
    
    
    #insert code to load previous tracked moods from this week and stuff//
    entry_1 = JournalEntry.query.filter_by(user_id=current_user.id, date=week_start).first()
    if entry_1:
        if entry_1.mood is not None:
            day_mood_list[0] = entry_1.mood
    entry_2 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_2).first()
    if entry_2:
        if entry_2.mood is not None:
            day_mood_list[1] = entry_2.mood
    entry_3 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_3).first()
    if entry_3:
        if entry_3.mood is not None:
            day_mood_list[2] = entry_3.mood
    entry_4 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_4).first()
    if entry_4:
        if entry_4.mood is not None:
            day_mood_list[3] = entry_4.mood
    entry_5 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_5).first()
    if entry_5:
        if entry_5.mood is not None:
            day_mood_list[4] = entry_5.mood
    entry_6 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_6).first()
    if entry_6:
        if entry_6.mood is not None:
            day_mood_list[5] = entry_6.mood
    entry_7 = JournalEntry.query.filter_by(user_id=current_user.id, date=week_end).first()
    if entry_7:
        if entry_7.mood is not None:
            day_mood_list[6] = entry_7.mood
    
    
    if request.method == 'POST':
        if "mood-submit" in request.form:
            selected_mood = int(request.form.get('mood'))
            entry = JournalEntry.query.filter_by(user_id=current_user.id, date=today).first()
            if entry:
                entry.mood = selected_mood
                db.session.commit()
            else:
                new_entry = JournalEntry(
                    mood=selected_mood,
                    date=today,
                    user=current_user
                )
                db.session.add(new_entry)
                db.session.commit()
                
            day_mood_list[today.weekday() + 1] = selected_mood  
            
            return render_template (
                "MoodTracker.html",
                today = today,
                week_start = week_start,
                week_end = week_end,
                day_mood_list = day_mood_list,
                current_week = current_week
            )
            
        elif 'prev-button' in request.form:
            return redirect(url_for("prev", week_start=week_start, week_end=week_end))
                    
        elif 'next-button' in request.form:
            return redirect(url_for("next", week_start=week_start, week_end=week_end))
    
    return render_template (
        "MoodTracker.html",
        today = today,
        week_start = week_start,
        week_end = week_end,
        day_mood_list = day_mood_list,
        current_week = current_week
    )
    
@app.route('/next', methods = ['POST', 'GET'])
@login_required
def next():
    day_mood_list = [2, 2, 2, 2, 2, 2, 2]
    week_start_str = request.args.get('week_start')
    week_end_str = request.args.get('week_end')
    week_start = datetime.datetime.strptime(week_start_str, "%Y-%m-%d").date()
    week_end = datetime.datetime.strptime(week_end_str, "%Y-%m-%d").date()

    week_start = week_start + datetime.timedelta(days=7)
    day_2 = week_start + datetime.timedelta(days=1)
    day_3 = day_2 + datetime.timedelta(days=1)
    day_4 = day_3 + datetime.timedelta(days=1)
    day_5 = day_4 + datetime.timedelta(days=1)
    day_6 = day_5 + datetime.timedelta(days=1)
    week_end = day_6 + datetime.timedelta(days=1)
    
    today = datetime.date.today()
    curr_week_start = today - datetime.timedelta(days=today.weekday() + 1)
    current_week = False
    
    if curr_week_start == week_start:
        return redirect(url_for("moodtracker"))

    #insert code to load previous tracked moods from this week and stuff//
    entry_1 = JournalEntry.query.filter_by(user_id=current_user.id, date=week_start).first()
    if entry_1:
        if entry_1.mood is not None:
            day_mood_list[0] = entry_1.mood
    entry_2 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_2).first()
    if entry_2:
        if entry_2.mood is not None:
            day_mood_list[1] = entry_2.mood
    entry_3 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_3).first()
    if entry_3:
        if entry_3.mood is not None:
            day_mood_list[2] = entry_3.mood
    entry_4 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_4).first()
    if entry_4:
        if entry_4.mood is not None:
            day_mood_list[3] = entry_4.mood
    entry_5 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_5).first()
    if entry_5:
        if entry_5.mood is not None:
            day_mood_list[4] = entry_5.mood
    entry_6 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_6).first()
    if entry_6:
        if entry_6.mood is not None:
            day_mood_list[5] = entry_6.mood
    entry_7 = JournalEntry.query.filter_by(user_id=current_user.id, date=week_end).first()
    if entry_7:
        if entry_7.mood is not None:
            day_mood_list[6] = entry_7.mood
                
    if request.method == 'POST':
        if 'prev-button' in request.form:
            return redirect(url_for("prev", week_start=week_start, week_end=week_end))
                    
        elif 'next-button' in request.form:
            return redirect(url_for("next", week_start=week_start, week_end=week_end))
                
    return render_template (
        "MoodTracker.html",
        week_start = week_start,
        week_end = week_end,
        day_mood_list = day_mood_list,
        current_week=current_week
    )

@app.route('/prev', methods = ['POST', 'GET'])
@login_required
def prev():
    day_mood_list = [2, 2, 2, 2, 2, 2, 2]
    week_start_str = request.args.get('week_start')
    week_end_str = request.args.get('week_end')
    week_start = datetime.datetime.strptime(week_start_str, "%Y-%m-%d").date()
    week_end = datetime.datetime.strptime(week_end_str, "%Y-%m-%d").date()
    
    week_start = week_start - datetime.timedelta(days=7)
    day_2 = week_start + datetime.timedelta(days=1)
    day_3 = day_2 + datetime.timedelta(days=1)
    day_4 = day_3 + datetime.timedelta(days=1)
    day_5 = day_4 + datetime.timedelta(days=1)
    day_6 = day_5 + datetime.timedelta(days=1)
    week_end = day_6 + datetime.timedelta(days=1)
    
    today = datetime.date.today()
    curr_week_start = today - datetime.timedelta(days=today.weekday() + 1)
    current_week = False
    
    if curr_week_start == week_start:
        return redirect(url_for("moodtracker"))

    #insert code to load previous tracked moods from this week and stuff//
    entry_1 = JournalEntry.query.filter_by(user_id=current_user.id, date=week_start).first()
    if entry_1:
        if entry_1.mood is not None:
            day_mood_list[0] = entry_1.mood
    entry_2 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_2).first()
    if entry_2:
        if entry_2.mood is not None:
            day_mood_list[1] = entry_2.mood
    entry_3 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_3).first()
    if entry_3:
        if entry_3.mood is not None:
            day_mood_list[2] = entry_3.mood
    entry_4 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_4).first()
    if entry_4:
        if entry_4.mood is not None:
            day_mood_list[3] = entry_4.mood
    entry_5 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_5).first()
    if entry_5:
        if entry_5.mood is not None:
            day_mood_list[4] = entry_5.mood
    entry_6 = JournalEntry.query.filter_by(user_id=current_user.id, date=day_6).first()
    if entry_6:
        if entry_6.mood is not None:
            day_mood_list[5] = entry_6.mood
    entry_7 = JournalEntry.query.filter_by(user_id=current_user.id, date=week_end).first()
    if entry_7:
        if entry_7.mood is not None:
            day_mood_list[6] = entry_7.mood
            
    if request.method == 'POST':
        if 'prev-button' in request.form:
            return redirect(url_for("prev", week_start=week_start, week_end=week_end))
                    
        elif 'next-button' in request.form:
            return redirect(url_for("next", week_start=week_start, week_end=week_end))
                
    return render_template (
        "MoodTracker.html",
        week_start = week_start,
        week_end = week_end,
        day_mood_list = day_mood_list,
        current_week=current_week
    )

    
@app.route('/mindfulactivities', methods = ['GET'])
@login_required
def mindfulactivities():
    #this shouldnt need more code
    return render_template (
        "MindfulActivities.html"
    )
    
@app.route('/poetry', methods = ['POST', 'GET'])
@login_required
def poetry():
    
    if request.method == 'POST':
        if "Like" in request.form.values():
            like = True
            dislike = False
        if "Dislike" in request.form.values():
            dislike = True
            like = False
        
    return render_template (
        "Poetry.html"
    )
    
@app.route('/quotes', methods = ['POST', 'GET'])
@login_required
def quotes():
    
    if request.method == 'POST':
        if "Like" in request.form.values():
            like = True
            dislike = False
        if "Dislike" in request.form.values():
            dislike = True
            like = False
    
    return render_template (
        "quotes.html"
    )
    
@app.route('/crisissupport')
def crisis():
    #this shouldnt need more code, unless we want the website to automatically update based on users locations
    if current_user.is_authenticated:
        logged_in = True
    else:
        logged_in = False
        
    return render_template (
        "CrisisSupportInformation.html",
        logged_in=logged_in
    )