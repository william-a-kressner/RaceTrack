import os

import flask
import sqlalchemy
from flask import Flask, render_template, redirect, request, session
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


mysql_db = sqlalchemy.create_engine(
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

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.authenticated = False


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
'''def to_arr(arr1, arr2):
    data1 = []
    for StudentInfo in arr1:
        data1.append(StudentInfo.total_tasks)
    data2 = []
    for RaceCar in arr2:
        data2.append((RaceCar.name, RaceCar.tasks_complete, data1[0]))
    return data2
'''


def get_racecars():
    data = []
    with mysql_db.connect() as conn:
        racecars = conn.execute(
            "SELECT * FROM racecars"
        ).fetchall()
        total_tasks = conn.execute(
            "SELECT total_tasks FROM studentinfo WHERE id=1"
        ).fetchone()

        for row in racecars:
            data.append((row[1], row[2], total_tasks[0]))
    return data

@login_manager.user_loader
#TODO Fix this!! Use new database. MUST ADD ID AS A FIELD TO USER TABLE!!
def user_loader(user_id):
    '''
    m_query = """SELECT * FROM user WHERE username=%s"""
    with mysql_db.connect() as conn:
        n_user = conn.execute(m_query, (user_id,)).fetchone()
        auth_user = User(n_user[1], n_user[2])
    return auth_user
    '''
    return User.query.get(user_id)

@app.route("/student")
#@login_required
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
    if 'logged_in' in session:
        data = get_racecars()
        #print(data)
        if session['username'] == "ginny.yeekee":
            return render_template("index.html", dbData=data, teacher=True)
        return render_template("index.html", dbData=data, teacher=False)
    else:
        return '<h1>Please log in.</h1>'

@app.route("/teacher")
#@login_required
def teacher():
    if 'logged_in' in session:
        if not session['username'] == "ginny.yeekee":
            flask.flash("You are not authorized.")
            return redirect("/student")
        data = get_racecars()
        #print(data)
        return render_template("index.html", dbData=data, teacher=True)
    else:
        return '<h1>Please log in. Current credentials are (' + session['username'] + ', ' + session['password'] + ')</h1>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with mysql_db.connect() as conn:
            form_uname = form.username.data
            form_pass = form.password.data
            m_query = """select * from user where username = %s and password=%s"""
            n_user: object = conn.execute(m_query, (form_uname, form_pass,)).fetchone()
            if n_user:
                #auth_user = User(n_user[0], n_user[1])
                #login_user(auth_user)
                session['logged_in'] = True
                session['username'] = n_user[0]
                session['password'] = n_user[1]
                if session['username'] == "ginny.yeekee":
                    return redirect("/teacher")
                elif session['username'] == "student":
                    return redirect("/student")
        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)


    '''user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                if current_user.username == "ginny.yeekee":
                    return redirect("/teacher")
                elif current_user.username == "student":
                    return redirect("student")

    #START TEST
    test = ""
    with mysql_db.connect() as conn:
        # Execute the query and fetch all results
        test_data = conn.execute(
            "SELECT * FROM user WHERE username = 'student'"
        ).fetchone()
        if test_data:
            test = "not null! Username is: " + test_data[0] + " and pass is " + test_data[1]
        else:
            test = "it's null"
        # Convert the results into a list of dicts representing votes
        #for row in test_data:
         #   test.append({"username": row[0], "password": row[1]})
    #END TEST'''



@app.route("/")
def home_page():
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RaceCar.sqlite'
    #db.create_all()
    '''
    try:
        if current_user.username == "student" or current_user.username == "ginny.yeekee":
            return redirect("/student")
    except AttributeError:
        #print("No one logged in")
        return redirect("/login")
    '''
    if 'logged_in' in session:
        if session['username'] == "ginny.yeekee":
            return redirect("/teacher")
        return redirect("/student")
    else:
        return redirect("/login")


@app.route("/logout", methods=['POST'])
#@login_required
def logout():
    if 'logged_in' in session:
        #logout_user()
        session.pop('logged_in', None)
        session.pop('username', None)
        session.pop('password', None)
        flask.flash("Logout successful.")
        return redirect("/")
    else:
        return '<h1>Please log in.</h1>'

@app.route("/process", methods=['POST'])
#@login_required
def new_student():
    if 'logged_in' in session:
        name = request.form['student_name']
        tasks_completed = int(request.form['tasks_completed'])
        m_query = """INSERT INTO racecars(name, tasks_complete) VALUES(%s, %s)"""
        with mysql_db.connect() as conn:
            conn.execute(m_query, (name, tasks_completed),)
        #student = RaceCar(name, tasks_completed)
        #db.session.add(student)
        #db.session.commit()
        data = get_racecars()
        flask.flash("Submission complete.")
        return render_template("index.html", dbData=data, teacher=True)
    else:
        return '<h1>Please log in.</h1>'

@app.route("/delete", methods=['POST'])
#@login_required
def delete():
    if 'logged_in' in session:
        id = request.form['id']
        id = id[:-7]
        print(id)
        m_query = """DELETE FROM racecars WHERE name=%s"""
        with mysql_db.connect() as conn:
            conn.execute(m_query, (id,))
        '''
        RaceCar.query.filter_by(name=id).delete()
        db.session.commit()
        '''
        data = get_racecars()
        flask.flash("Successfully deleted " + id + ". Please refresh.")
        return render_template("index.html", dbData=data, teacher=True)
    else:
        return '<h1>Please log in.</h1>'

@app.route("/increment", methods=['POST'])
#@login_required
def increment():
    if 'logged_in' in session:
        id = request.form['id']
        id = id[:-10]
        m_query = """UPDATE racecars SET tasks_complete=tasks_complete+1 WHERE name=%s"""
        with mysql_db.connect() as conn:
            conn.execute(m_query, (id,))
        '''
        student = RaceCar.query.filter_by(name=id).first()
        student.tasks_complete += 1
        db.session.commit()
        '''
        data = get_racecars()
        #print(data)
        return render_template("index.html", dbData=data, teacher=True)
    else:
        return '<h1>Please log in.</h1>'


@app.route("/decrement", methods=['POST'])
#@login_required
def decrement():
    if 'logged_in' in session:
        id = request.form['id']
        id = id[:-10]
        m_query = """UPDATE racecars SET tasks_complete=tasks_complete-1 WHERE name=%s"""
        with mysql_db.connect() as conn:
            conn.execute(m_query, (id,))
        '''
        student = RaceCar.query.filter_by(name=id).first()
        student.tasks_complete -= 1
        db.session.commit()
        '''
        data = get_racecars()
        #print(data)
        return render_template("index.html", dbData=data, teacher=True)
    else:
        return '<h1>Please log in.</h1>'

if __name__ == "__main__":
    app.run()
