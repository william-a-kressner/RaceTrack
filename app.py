from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, or_
import os

app = Flask(__name__)
db = SQLAlchemy(app)

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
def to_arr(arr):
    data = []
    for Post in arr:
        data.append((Post.name, Post.tags, Post.post))
    return data

@app.route("/student")
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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/william/RaceCar.sqlite'
    db.create_all()
    test = RaceCar("Bob", 5)
    db.session.add(test)
    db.session.commit()
    '''data = to_arr(Post.query.all())
    data.__repr__()'''
    return render_template("index.html")

@app.route("/teacher")
def teacher():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
