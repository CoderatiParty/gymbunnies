from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy import event

"""
The above lines are used to import built-in functions from Flask
"""

class Workout(db.Model):
    """
    Class function defining the model for the Workout database
    """
    id = db.Column(db.Integer, primary_key=True) # Sets a primary identifier as an integer
    workout_date = db.Column(db.Date)
    workout_type = db.Column(db.Enum('Arms', 'Back', 'Cardio', 'Chest', 'Core', 'Fullbody', 'Legs', 'Lower', 'Pull', 'Push', 'Upper', name='workout_type_enum'), default='select', nullable=False) # Specific options for the workout type
    workout_duration = db.Column(db.String(7))
    exercises = db.relationship('Exercise', backref='workout', cascade="all, delete", lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Linked to the User database as a foreign key


class Exercise(db.Model):
    """
    Class function defining the model for the Exercise database
    """
    id = db.Column(db.Integer, primary_key=True) # Sets a primary identifier as an integer
    exercise_type = db.Column(db.String(100))
    weight = db.Column(db.String(7))
    reps = db.Column(db.String(3))
    sets = db.Column(db.String(3))
    distance = db.Column(db.String(10))
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id', ondelete="CASCADE"), nullable=False) # Linked to the Workout database as a foreign key. Can't be zero. Records deleted if corresponding Workout deleted


class User(db.Model, UserMixin):
    """
    Class function defining the model for the User database
    """
    id = db.Column(db.Integer, primary_key=True) # Sets a primary identifier as an integer
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    profile_pic = db.Column(db.LargeBinary)
    gym = db.Column(db.String(150))
    phone = db.Column(db.String(11))
    date_of_birth = db.Column(db.Date)
    workouts = db.relationship('Workout', backref="user", cascade="all, delete", lazy=True) # Workout records deleted if corresponding User deleted
    # Defines relationships for connections and connection requests. Courtesy of Chat GPT
    sent_connection_requests = db.relationship('ConnectionRequest', foreign_keys='ConnectionRequest.sender_id', back_populates='sender', cascade="all, delete-orphan")
    received_connection_requests = db.relationship('ConnectionRequest', foreign_keys='ConnectionRequest.receiver_id', back_populates='receiver', cascade="all, delete-orphan")
    connections = db.relationship('UserConnection', foreign_keys='UserConnection.user_id', back_populates='user')
    connected_to = db.relationship('UserConnection', foreign_keys='UserConnection.connected_user_id', back_populates='connected_user')


    def calculate_age(self):
        """
        A function to workout the users current age. Courtesy of Chat GPT
        """
        if self.date_of_birth:
            today = datetime.today()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            return age
        return None
    

class ConnectionRequest(db.Model):
    """
    Class function defining the model for the user connection requests database. Courtesy of Chat GPT
    """
    id = db.Column(db.Integer, primary_key=True) # Sets a primary identifier as an integer. Courtesy of Chat GPT
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')
    request_date = db.Column(db.DateTime, default=datetime.now)  # Automatically set to current time. Courtesy of Chat GPT

    # Define relationships to access sender and receiver
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')


class UserConnection(db.Model):
    """
    Class function defining the model for the user connections database. Courtesy of Chat GPT
    """
    id = db.Column(db.Integer, primary_key=True) # Sets a primary identifier as an integer
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    connected_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')

    __table_args__ = (db.UniqueConstraint('user_id', 'connected_user_id'),) # A constraint to ensure uniqueness of user_id and connected_user_id pair. Courtesy of Chat GPT

    # Define relationships to access the users
    user = db.relationship('User', foreign_keys=[user_id], back_populates='connections')
    connected_user = db.relationship('User', foreign_keys=[connected_user_id], back_populates='connected_to')


@event.listens_for(User.date_of_birth, 'set') # An event listener used to check when a user has entered theor date of birth. Courtesy of Chat GPT
def update_age(target, value, oldvalue, initiator):
    """
    Updates the users current age. Courtesy of Chat GPT
    """
    target.age = target.calculate_age()