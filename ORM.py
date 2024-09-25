from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:your_password@localhost/fitness_center_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Define the Member model
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    joined_at = db.Column(db.DateTime, nullable=False)

# Define the WorkoutSession model
class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    session_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    type = db.Column(db.String(50), nullable=False)

# Marshmallow Schemas for serializing data
class MemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Member
        load_instance = True

class WorkoutSessionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WorkoutSession
        load_instance = True

# Initialize schemas
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

# Route to create a new member (POST)
@app.route('/members', methods=['POST'])
def add_member():
    name = request.json['name']
    email = request.json['email']
    joined_at = request.json['joined_at']
    
    new_member = Member(name=name, email=email, joined_at=joined_at)
    db.session.add(new_member)
    db.session.commit()
    
    return member_schema.jsonify(new_member)

# Route to get all members (GET)
@app.route('/members', methods=['GET'])
def get_members():
    all_members = Member.query.all()
    return members_schema.jsonify(all_members)

# Route to update a member (PUT)
@app.route('/members/<id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get(id)
    
    if not member:
        return jsonify({"error": "Member not found"}), 404
    
    member.name = request.json['name']
    member.email = request.json['email']
    
    db.session.commit()
    
    return member_schema.jsonify(member)

# Route to delete a member (DELETE)
@app.route('/members/<id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get(id)
    
    if not member:
        return jsonify({"error": "Member not found"}), 404
    
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({"message": "Member deleted successfully"})

# Route to create a workout session (POST)
@app.route('/workout_sessions', methods=['POST'])
def add_workout_session():
    member_id = request.json['member_id']
    session_date = request.json['session_date']
    duration = request.json['duration']
    type = request.json['type']
    
    new_session = WorkoutSession(member_id=member_id, session_date=session_date, duration=duration, type=type)
    db.session.add(new_session)
    db.session.commit()
    
    return workout_session_schema.jsonify(new_session)

# Route to get all workout sessions (GET)
@app.route('/workout_sessions', methods=['GET'])
def get_workout_sessions():
    all_sessions = WorkoutSession.query.all()
    return workout_sessions_schema.jsonify(all_sessions)

# Route to get all workout sessions for a specific member (GET)
@app.route('/members/<id>/workout_sessions', methods=['GET'])
def get_workout_sessions_for_member(id):
    sessions = WorkoutSession.query.filter_by(member_id=id).all()
    if not sessions:
        return jsonify({"error": "No sessions found for this member"}), 404
    
    return workout_sessions_schema.jsonify(sessions)

# Ensure app.run is at the end
if __name__ == '__main__':
    app.run(debug=True)
