import os

import flask
import sqlalchemy
from flask import Flask, render_template, redirect, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, login_user, current_user, UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Column, Integer, String
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


db_test = sqlalchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername="mysql+pymysql",
        username="root",
        password="mysql-pass",
        database="racetrack_mysql_db",
        query={"unix_socket": "/cloudsql/{}".format("racetrack-278014:us-east1:racetrack-mysql-db")},
    ),
    # ... Specify additional properties here.
    # ...
)


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


    data = to_arr(StudentInfo.query.all(), RaceCar.query.all())
    #print(data)
    if current_user.username == "ginny.yeekee":
        return render_template("index.html", dbData=data, teacher=True)
    return render_template("index.html", dbData=data, teacher=False)


@app.route("/teacher")
@login_required
def teacher():
    if not current_user.username == "ginny.yeekee":
        flask.flash("You are not authorized.")
        return redirect("/student")
    data = to_arr(StudentInfo.query.all(), RaceCar.query.all())
    #print(data)
    return render_template("index.html", dbData=data, teacher=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
#TODO Use the new database to pull data.
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

    #START TEST
    test = []
    with db_test.connect() as conn:
        # Execute the query and fetch all results
        test_data = conn.execute(
            "SELECT * FROM user"
        ).fetchall()
        # Convert the results into a list of dicts representing votes
        for row in test_data:
            test.append({"username": row[0], "password": row[1]})
    #END TEST

    return render_template('login.html', form=form, test=test)


@app.route("/")
def home_page():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RaceCar.sqlite'
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

@app.route("/process", methods=['POST'])
@login_required
def new_student():
    name = request.form['student_name']
    tasks_completed = request.form['tasks_completed']
    student = RaceCar(name, tasks_completed)
    db.session.add(student)
    db.session.commit()
    data = to_arr(StudentInfo.query.all(), RaceCar.query.all())
    flask.flash("Submission complete.")
    return render_template("index.html", dbData=data, teacher=True)

@app.route("/delete", methods=['POST'])
@login_required
def delete():
    id = request.form['id']
    id = id[:-7]
    print(id)
    RaceCar.query.filter_by(name=id).delete()
    db.session.commit()
    data = to_arr(StudentInfo.query.all(), RaceCar.query.all())
    flask.flash("Successfully deleted " + id + ". Please refresh.")
    return render_template("index.html", dbData=data, teacher=True)


@app.route("/increment", methods=['POST'])
@login_required
def increment():
    id = request.form['id']
    id = id[:-10]
    student = RaceCar.query.filter_by(name=id).first()
    student.tasks_complete += 1
    db.session.commit()
    data = to_arr(StudentInfo.query.all(), RaceCar.query.all())
    #print(data)
    return render_template("index.html", dbData=data, teacher=True)

@app.route("/decrement", methods=['POST'])
@login_required
def decrement():
    id = request.form['id']
    id = id[:-10]
    student = RaceCar.query.filter_by(name=id).first()
    student.tasks_complete -= 1
    db.session.commit()
    data = to_arr(StudentInfo.query.all(), RaceCar.query.all())
    #print(data)
    return render_template("index.html", dbData=data, teacher=True)


if __name__ == "__main__":
    app.run()
