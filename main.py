import sqlalchemy
from flask import Flask, render_template, redirect, request, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

# initialize some properties of the app including bootstrap, secret key, and database
app = Flask(__name__)
Bootstrap(app)
SECRET_KEY = b'z\x19h\xaa\x03\xbe\xdeU\x14\xc3&^~\xf9\x01\xde'
app.config['SECRET_KEY'] = SECRET_KEY
mysql_db = sqlalchemy.create_engine(
    sqlalchemy.engine.url.URL(
        drivername="mysql+pymysql",
        username="root",
        password="mysql-pass",
        database="racetrack_mysql_db",
        query={"unix_socket": "/cloudsql/{}".format("racetrack-278014:us-east1:racetrack-mysql-db")},
    ),
)


# class representing the login form that is utilized in the login method.
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


# helper function that generates racecar tuples that are interpreted by index.html
# creates them in the form (name, tasks_complete, total_tasks)
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


# The student page. If not logged in, routes to login page. If you are the teacher, sends you to the teacher page
@app.route("/student")
def start():
    if 'logged_in' in session:
        data = get_racecars()
        if session['username'] == "ginny.yeekee":
            return render_template("index.html", dbData=data, teacher=True)
        return render_template("index.html", dbData=data, teacher=False)
    else:
        return redirect("/login")


# The teacher page. Student account will be redirected to student page. If not logged in, routes to login page.
@app.route("/teacher")
def teacher():
    if 'logged_in' in session:
        if not session['username'] == "ginny.yeekee":
            return redirect("/student")
        data = get_racecars()
        return render_template("index.html", dbData=data, teacher=True)
    else:
        return redirect("/login")


# Login method pulls data from form if submitted and tries to login with the given credentials. Else, it returns the
# login form.
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
                session['logged_in'] = True
                session['username'] = n_user[0]
                session['password'] = n_user[1]
                session.modified = True
                if session['username'] == "ginny.yeekee":
                    return redirect("/teacher")
                elif session['username'] == "student":
                    return redirect("/student")
        return '<h1>Invalid username or password</h1>'
    return render_template('login.html', form=form)


# The home page redirects to teacher, student, or login screen depending on who is logged in.
@app.route("/")
def home_page():
    if 'logged_in' in session:
        if session['username'] == "ginny.yeekee":
            return redirect("/teacher")
        return redirect("/student")
    else:
        return redirect("/login")


# Simple logout method. Clears session variables.
@app.route("/logout", methods=['POST'])
def logout():
    if 'logged_in' in session:
        session.pop('logged_in', None)
        session.pop('username', None)
        session.pop('password', None)
        return redirect("/")
    else:
        return redirect("/login")


# Processes new student request from js and adds to database.
@app.route("/process", methods=['POST'])
def new_student():
    if 'logged_in' in session:
        name = request.form['student_name']
        tasks_completed = int(request.form['tasks_completed'])
        m_query = """INSERT INTO racecars(name, tasks_complete) VALUES(%s, %s)"""
        with mysql_db.connect() as conn:
            conn.execute(m_query, (name, tasks_completed), )

        data = get_racecars()
        return render_template("index.html", dbData=data, teacher=True)
    else:
        return redirect("/login")


# Deletes a student with a given id.
@app.route("/delete", methods=['POST'])
def delete():
    if 'logged_in' in session:
        id = request.form['id']
        id = id[:-7]
        print(id)
        m_query = """DELETE FROM racecars WHERE name=%s"""
        with mysql_db.connect() as conn:
            conn.execute(m_query, (id,))

        data = get_racecars()
        return render_template("index.html", dbData=data, teacher=True)
    else:
        return redirect("/login")


# Increments the number of tasks a student has completed.
@app.route("/increment", methods=['POST'])
def increment():
    if 'logged_in' in session:
        id = request.form['id']
        id = id[:-10]
        m_query = """UPDATE racecars SET tasks_complete=tasks_complete+1 WHERE name=%s"""
        with mysql_db.connect() as conn:
            conn.execute(m_query, (id,))

        data = get_racecars()
        return render_template("index.html", dbData=data, teacher=True)
    else:
        return redirect("/login")


# Decrements the number of tasks a student has completed.
@app.route("/decrement", methods=['POST'])
def decrement():
    if 'logged_in' in session:
        id = request.form['id']
        id = id[:-10]
        m_query = """UPDATE racecars SET tasks_complete=tasks_complete-1 WHERE name=%s"""
        with mysql_db.connect() as conn:
            conn.execute(m_query, (id,))

        data = get_racecars()
        return render_template("index.html", dbData=data, teacher=True)
    else:
        return redirect("/login")


if __name__ == "__main__":
    app.run()
