from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:1q2w3e4r5t6y@localhost/fitness_center_db'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    membership_type = db.Column(db.String(50), nullable=False)
    active = db.Column(db.Boolean, default=True)
    workout_sessions = db.relationship('WorkoutSession', backref='member', lazy=True)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    workout_type = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer) 
    trainer = db.Column(db.String(100))
    notes = db.Column(db.Text)

class MemberSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Member

    id = ma.auto_field()
    name = ma.auto_field()
    email = ma.auto_field()
    join_date = ma.auto_field()
    membership_type = ma.auto_field()
    active = ma.auto_field()

class WorkoutSessionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = WorkoutSession

    id = ma.auto_field()
    member_id = ma.auto_field()
    date = ma.auto_field()
    workout_type = ma.auto_field()
    duration = ma.auto_field()
    trainer = ma.auto_field()
    notes = ma.auto_field()

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        data = request.get_json()
        new_member = Member(
            name=data['name'],
            email=data['email'],
            membership_type=data['membership_type']
        )
        db.session.add(new_member)
        db.session.commit()
        return member_schema.dump(new_member), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.dump(members)

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    member = Member.query.get_or_404(id)
    return member_schema.dump(member)

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    try:
        member = Member.query.get_or_404(id)
        data = request.get_json()
        
        for key, value in data.items():
            setattr(member, key, value)
        
        db.session.commit()
        return member_schema.dump(member)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return '', 204

@app.route('/workouts', methods=['POST'])
def add_workout():
    try:
        data = request.get_json()
        new_workout = WorkoutSession(
            member_id=data['member_id'],
            date=datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S'),
            workout_type=data['workout_type'],
            duration=data['duration'],
            trainer=data.get('trainer'),
            notes=data.get('notes')
        )
        db.session.add(new_workout)
        db.session.commit()
        return workout_session_schema.dump(new_workout), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/members/<int:member_id>/workouts', methods=['GET'])
def get_member_workouts(member_id):
    Member.query.get_or_404(member_id) 
    workouts = WorkoutSession.query.filter_by(member_id=member_id).all()
    return workout_sessions_schema.dump(workouts)

@app.route('/workouts/<int:id>', methods=['PUT'])
def update_workout(id):
    try:
        workout = WorkoutSession.query.get_or_404(id)
        data = request.get_json()
        
        if 'date' in data:
            data['date'] = datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')
        
        for key, value in data.items():
            setattr(workout, key, value)
        
        db.session.commit()
        return workout_session_schema.dump(workout)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)