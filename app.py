import flask
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_required, login_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.functions import user
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class User(db.Model):
    __tablename__ = 'user'

    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


class RaceCar(db.Model):
    id = Column(Integer, primary_key=True)
    __tablename__ = 'racecars'
    name = Column(String)
    tasks_complete = Column(Integer)

    def __repr__(self):
        return "<RaceCar(name='%s', tasks_complete='%s')>" % (
            self.name, self.tasks_complete)

    def __init__(self, name, tasks_complete):
        self.name = name
        self.tasks_complete = tasks_complete

class StudentInfo(db.Model):
    id = Column(Integer, primary_key=True)
    __tablename__ = 'studentinfo'
    total_tasks = Column(Integer)
    number_students = Column(Integer)

    def __repr__(self):
        return "<StudentInfo(total_tasks='%s', number_students='%s')>" % (
            self.total_tasks, self.number_students)
    def __init__(self, total_tasks, number_students):
        self.total_tasks = total_tasks
        self.number_students = number_students

#convert an object to an array
'''def to_arr(arr):
    data = []
    for Post in arr:
        data.append((Post.name, Post.tags, Post.post))
    return data'''

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@app.route("/student")
@login_required
def start():
    '''cwd = os.getcwd()
    if os.path.exists(cwd):
        #create sqlite file
        database_file = open("RaceTrack.sqlite", "w+")
        path = os.path.join(cwd, "RackTrack.sqlite")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path
    else:
        print("Error.")
        exit(0)'''
    test = RaceCar("Bob", 5)
    db.session.add(test)
    db.session.commit()
    '''data = to_arr(Post.query.all())
    data.__repr__()'''
    return render_template("index.html")

@app.route("/teacher")
@login_required
def teacher():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)

        flask.flash('Logged in successfully.')
        return redirect("/")
    print("Failure?")
    return render_template("index.html")


@app.route("/")
def home_page():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/william/RaceCar.sqlite'
    db.create_all()
    if user_loader("ginny.yeekee").is_authenticated():
        return redirect("/teacher")
    elif user_loader("student").is_authenticated():
        return redirect("student")
    else:
        return redirect("/login")

if __name__ == "__main__":
    app.run()
