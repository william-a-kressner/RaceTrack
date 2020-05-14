import flask
from flask import Flask, render_template, redirect
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, login_user, current_user, UserMixin, AnonymousUserMixin, \
    logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.functions import user
import os
from flask_wtf import FlaskForm
from werkzeug.local import LocalProxy
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class User(UserMixin, db.Model):
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
def to_arr(arr1, arr2):
    data1 = []
    for StudentInfo in arr1:
        data1.append(StudentInfo.total_tasks)
    print(data1)
    data2 = []
    for RaceCar in arr2:
        data2.append((RaceCar.name, RaceCar.tasks_complete, data1[0]))
    return data2

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
    #test = RaceCar("Bob", 5)
    #db.session.add(test)
    #db.session.commit()
    data = to_arr(StudentInfo.query.all(), RaceCar.query.all())
    print(data)
    return render_template("index.html", dbData=data)

@app.route("/teacher")
@login_required
def teacher():
    if not current_user.username == "ginny.yeekee":
        flask.flash("You are not authorized.")
        return redirect("/student")
    data = to_arr(StudentInfo.query.all(), RaceCar.query.all())
    print(data)
    return render_template("index.html", dbData=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                if current_user.username == "ginny.yeekee":
                    return redirect("/teacher")
                elif current_user.username == "student":
                    return redirect("student")
        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)


@app.route("/")
def home_page():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/william/RaceCar.sqlite'
    db.create_all()
    try:
        if current_user.username == "student" or current_user.username == "ginny.yeekee":
            return redirect("/student")
    except AttributeError:
        #print("No one logged in")
        return redirect("/login")


@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    flask.flash("Logout successful.")
    return redirect("/")

if __name__ == "__main__":
    app.run()
