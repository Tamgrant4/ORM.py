# 1
# Task1
fitness_center/
├── app.py
├── config.py
├── models.py
└── requirements.txt

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:your_password@localhost/fitness_center_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

from models import Member, WorkoutSession

if __name__ == '__main__':
    app.run(debug=True)

from app import db

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    member = db.relationship('Member', backref=db.backref('sessions', lazy=True))

# Task 2
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from models import Member, WorkoutSession

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    new_member = Member(name=data['name'], email=data['email'], phone=data['phone'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'New member added successfully'}), 201

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([{'id': m.id, 'name': m.name, 'email': m.email, 'phone': m.phone} for m in members])

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({'message': 'Member not found'}), 404
    return jsonify({'id': member.id, 'name': member.name, 'email': member.email, 'phone': member.phone})

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.get_json()
    member = Member.query.get(id)
    if not member:
        return jsonify({'message': 'Member not found'}), 404
    member.name = data.get('name', member.name)
    member.email = data.get('email', member.email)
    member.phone = data.get('phone', member.phone)
    db.session.commit()
    return jsonify({'message': 'Member updated successfully'})

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({'message': 'Member not found'}), 404
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)

# Task 3
@app.route('/workouts', methods=['POST'])
def schedule_workout():
    data = request.get_json()
    new_workout = WorkoutSession(
        member_id=data['member_id'], 
        date=data['date'], 
        type=data['type'], 
        duration=data['duration']
    )
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({'message': 'Workout session scheduled successfully'}), 201

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = WorkoutSession.query.all()
    return jsonify([{
        'id': w.id, 
        'member_id': w.member_id, 
        'date': w.date, 
        'type': w.type, 
        'duration': w.duration
    } for w in workouts])

@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = WorkoutSession.query.get(id)
    if not workout:
        return jsonify({'message': 'Workout session not found'}), 404
    return jsonify({
        'id': workout.id, 
        'member_id': workout.member_id, 
        'date': workout.date, 
        'type': workout.type, 
        'duration': workout.duration
    })

@app.route('/workouts/<int:id>', methods=['PUT'])
def update_workout(id):
    data = request.get_json()
    workout = WorkoutSession.query.get(id)
    if not workout:
        return jsonify({'message': 'Workout session not found'}), 404
    workout.date = data.get('date', workout.date)
    workout.type = data.get('type', workout.type)
    workout.duration = data.get('duration', workout.duration)
    db.session.commit()
    return jsonify({'message': 'Workout session updated successfully'})

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = WorkoutSession.query.get(id)
    if not workout:
        return jsonify({'message': 'Workout session not found'}), 404
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout session deleted successfully'})

@app.route('/members/<int:member_id>/workouts', methods=['GET'])
def get_member_workouts(member_id):
    workouts = WorkoutSession.query.filter_by(member_id=member_id).all()
    return jsonify([{
        'id': w.id, 
        'date': w.date, 
        'type': w.type, 
        'duration': w.duration
    } for w in workouts])
