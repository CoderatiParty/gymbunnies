import os
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort, session, get_flashed_messages
from flask_login import login_required, current_user
from .models import Workout, Exercise, User, UserConnection, ConnectionRequest
from . import db
import json
from datetime import datetime
from sqlalchemy.exc import IntegrityError

"""
The above lines are used to import built-in functions from Flask
"""

views = Blueprint('views', __name__, url_prefix='/views') # Sets the prefix for the standard routes


@views.route('/<int:user_id>', methods=['GET', 'POST'])
@login_required
def home(user_id):
    """
    Defines the home route and the variables called within it. Sets POST and GET methods
    """
    user = User.query.get_or_404(user_id)
    total_user_connections = len(UserConnection.query.filter_by(user_id=user_id).all())
    connection_request_sent = ConnectionRequest.query.filter_by(sender_id=current_user.id).first() is not None
    pending_connection_request = ConnectionRequest.query.filter_by(sender_id=user.id).first() is not None

    # Check if any of the profile fields are missing
    if not user.gym or not user.phone or not user.date_of_birth:
        # Only show the flash message to the user whose profile is being viewed
        if current_user.id == user_id:
            flash("Profile incomplete.", "error")

    # Query workouts for the specified user
    workouts = Workout.query.filter_by(user_id=user_id)\
                            .filter(Workout.workout_date != None)\
                            .order_by(Workout.workout_date)\
                            .all()

    # Calculate the total number of workouts for the user
    total_workouts = len(workouts)

    # Check if the displayed user is connected to the current user
    user_is_connected = UserConnection.query.filter_by(user_id=current_user.id, connected_user_id=user_id).first() is not None

    return render_template("home.html", user=user, workouts=workouts, total_workouts=total_workouts, total_user_connections=total_user_connections, user_is_connected=user_is_connected, connection_request_sent=connection_request_sent, pending_connection_request=pending_connection_request)


@views.route('/edit_user/<int:user_id>', methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    """
    Defines the edit user route and the variables called within it. Sets POST and GET methods
    """
    user = User.query.get_or_404(user_id)
    total_user_connections = len(UserConnection.query.filter_by(user_id=user_id).all())
    total_workouts = Workout.query.filter(Workout.user_id == current_user.id, Workout.workout_date != None).count()

    if request.method == "POST":
        user.email = request.form.get('email')
        user.first_name = request.form.get('firstName')
        user.last_name = request.form.get('lastName')
        user.phone = request.form.get('phone')
        user.gym = request.form.get('gym')

        # Convert date of birth string to Python date object
        date_of_birth_str = request.form.get('dob')
        if date_of_birth_str:
            user.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()

        db.session.commit()

        return redirect(url_for("views.home", user_id=current_user.id))
    
    return render_template("edit_user.html", user=current_user, total_workouts=total_workouts, total_user_connections=total_user_connections)


@views.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    """
    Defines the delete user route and the variables called within it
    """
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("auth.sign_up"))


@views.route("/add_workout", methods=["GET", "POST"])
@login_required
def add_workout():
    """
     # Defines the add workout route and the variables called within it. Sets POST and GET methods
    """
    user_id = current_user.id  # Get the current user's ID
    user_connections = UserConnection.query.filter_by(user_id=user_id).all()
    total_user_connections = len(user_connections)
    total_workouts = Workout.query.filter(Workout.user_id == current_user.id, Workout.workout_date != None).count()

    if request.method == "POST":
        if request.form.get("cancel"):  # Check if cancel button is clicked
            return redirect(url_for("views.home", user_id=current_user.id))  # Redirect to home page
        workout_date_str = request.form.get("workoutDate")
        
        # Check if workout date string is not empty
        if workout_date_str:
            # Convert workout_date string to datetime object
            workout_date = datetime.strptime(workout_date_str, "%Y-%m-%d").date()
        else:
            workout_date = None  # Set workout_date to None if string is empty
        workout = Workout(
            workout_date=workout_date,
            workout_type=request.form.get("workoutType"),
            workout_duration=request.form.get("workoutDuration"),
            user_id=current_user.id  # Assign the current user's ID to user_id
        )
        db.session.add(workout)
        db.session.commit()

        exercise = Exercise(
            exercise_type=request.form.get("exerciseType"),
            weight=request.form.get("weight"),
            reps=request.form.get("reps"),
            sets=request.form.get("sets"),
            distance=request.form.get("distance"),
            workout_id=workout.id
        )
        db.session.add(exercise)
        db.session.commit()

        return redirect(url_for("views.home", user_id=current_user.id))
    
    return render_template("add_workout.html", user=current_user, total_workouts=total_workouts, total_user_connections=total_user_connections)


@views.route('/edit_workout/<int:workout_id>', methods=["GET", "POST"])
@login_required
def edit_workout(workout_id):
    """
    Defines the edit workout route and the variables called within it. Sets POST and GET methods
    """
    user_id = current_user.id  # Get the current user's ID
    user_connections = UserConnection.query.filter_by(user_id=user_id).all()
    total_user_connections = len(user_connections)
    workout = Workout.query.get_or_404(workout_id)
    total_workouts = Workout.query.filter(Workout.user_id == current_user.id, Workout.workout_date != None).count()

    if request.method == "POST":
        if request.form.get("cancel"):  # Check if cancel button is clicked
            return redirect(url_for("views.home", user_id=current_user.id))  # Redirect to home page
        
        workout.workout_date_str = request.form.get("workoutDate")
        # Check if workout date string is not empty
        if workout.workout_date_str:
            # Convert workout_date string to datetime object
            workout.workout_date = datetime.strptime(workout.workout_date_str, "%Y-%m-%d").date()
        else:
            workout.workout_date = None  # Set workout_date to None if string is empty

        workout.workout_type=request.form.get("workoutType")
        workout.workout_duration=request.form.get("workoutDuration")
        workout.user_id=current_user.id  # Assign the current user's ID to user_id
        db.session.commit()

        return redirect(url_for("views.home", user_id=current_user.id))
    
    return render_template("edit_workout.html", workout=workout, user=current_user, current_workout_type=workout.workout_type, total_workouts=total_workouts, total_user_connections=total_user_connections)


@views.route('/delete_workout/<int:workout_id>')
@login_required
def delete_workout(workout_id):
    """
    Defines the delete workout route and the variables called within it
    """
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    db.session.commit()

    return redirect(url_for("views.home", user_id=current_user.id))


@views.route("/add_exercise/<int:workout_id>", methods=["GET", "POST"])
@login_required
def add_exercise(workout_id):
    """
    Defines the add exercise route and the variables called within it. Sets POST and GET methods
    """
    user_id = current_user.id  # Get the current user's ID
    user_connections = UserConnection.query.filter_by(user_id=user_id).all()
    total_user_connections = len(user_connections)
    workout = Workout.query.get_or_404(workout_id)
    total_workouts = Workout.query.filter(Workout.user_id == current_user.id, Workout.workout_date != None).count()

    if request.method == "POST":
        exercise = Exercise(
            exercise_type=request.form.get("exerciseType"),
            weight=request.form.get("weight"),
            reps=request.form.get("reps"),
            sets=request.form.get("sets"),
            distance=request.form.get("distance"),
            workout_id=workout.id
        )
        db.session.add(exercise)
        db.session.commit()

        return redirect(url_for("views.home", user_id=current_user.id))
    
    return render_template("add_exercise.html", user=current_user, workout=workout, total_workouts=total_workouts, total_user_connections=total_user_connections)


@views.route('/edit_exercise/<int:exercise_id>', methods=["GET", "POST"])
@login_required
def edit_exercise(exercise_id):
    """
    Defines the edit exercise route and the variables called within it. Sets POST and GET methods
    """
    user_id = current_user.id  # Get the current user's ID
    user_connections = UserConnection.query.filter_by(user_id=user_id).all()
    total_user_connections = len(user_connections)
    exercise = Exercise.query.get_or_404(exercise_id)
    total_workouts = Workout.query.filter(Workout.user_id == current_user.id, Workout.workout_date != None).count()

    if request.method == "POST":
        if request.form.get("cancel"):  # Check if cancel button is clicked
            return redirect(url_for("views.home", user_id=current_user.id))  # Redirect to home page
        exercise.exercise_type=request.form.get("exerciseType")
        exercise.weight=request.form.get("weight")
        exercise.reps=request.form.get("reps")
        exercise.sets=request.form.get("sets")
        exercise.distance=request.form.get("distance")
        db.session.commit()

        return redirect(url_for("views.home", user_id=current_user.id))
    
    return render_template("edit_exercise.html", exercise=exercise, user=current_user, total_workouts=total_workouts, total_user_connections=total_user_connections)


@views.route('/delete_exercise/<int:exercise_id>')
@login_required
def delete_exercise(exercise_id):
    """
    Defines the delete exercise route and the variables called within it. Sets POST and GET methods
    """
    exercise = Exercise.query.get_or_404(exercise_id)
    db.session.delete(exercise)
    db.session.commit()

    return redirect(url_for("views.home", user_id=current_user.id))


@views.route('/users')
def view_all_users():
    """
    Defines the users list route and the variables called within it. Sets POST and GET methods
    """
    users = User.query.all()
    total_workouts = {}  # Dictionary to store total workouts for each user
    workouts = {}  # Dictionary to store workouts for each user
    total_user_connections = {}  # Dictionary to store total connections for each user

    # Pre-fetch connections for the current user
    current_user_connections = list(connection.connected_user_id for connection in current_user.connections)

    for user in users:
        # Query workouts for each user without filtering by current user's ID
        user_workouts = Workout.query.filter_by(user_id=user.id).filter(Workout.workout_date != None).order_by(Workout.workout_date).all()
        # Store workouts for each user
        workouts[user.id] = user_workouts
        # Count total workouts for each user
        total_workouts[user.id] = len(user_workouts)
        # Count total connections for each user
        total_user_connections[user.id] = len(user.connections)

        # Check if the displayed user is connected to the current user
        user.user_is_connected = user.id in current_user_connections

        # Check if the displayed user has a pending connection request from the current user
        user.connection_request_sent = ConnectionRequest.query.filter_by(sender_id=current_user.id, receiver_id=user.id).first() is not None

        # Check if there's a pending connection request from the other user to the current user
        user.pending_connection_request = ConnectionRequest.query.filter_by(sender_id=user.id, receiver_id=current_user.id).first() is not None

        connection_request_sent = ConnectionRequest.query.filter_by(sender_id=current_user.id).first() is not None
        pending_connection_request = ConnectionRequest.query.filter_by(sender_id=user.id).first() is not None

    # Sort users based on the selected option
    sort_option = request.args.get('sort_option')
    if sort_option == 'name_asc':
        users = sorted(users, key=lambda u: u.first_name)
    elif sort_option == 'name_desc':
        users = sorted(users, key=lambda u: u.first_name, reverse=True)
    elif sort_option == 'workouts_asc':
        users = sorted(users, key=lambda u: total_workouts.get(u.id, 0))
    elif sort_option == 'workouts_desc':
        users = sorted(users, key=lambda u: total_workouts.get(u.id, 0), reverse=True)

    return render_template('all_users.html', users=users, user=current_user, total_workouts=total_workouts, workouts=workouts, total_user_connections=total_user_connections, connection_request_sent=connection_request_sent, pending_connection_request=pending_connection_request)


"""
From here down to the corporate pages, the routes were built with the considerable assistance of ChatGPT
"""


@views.route('/add_connection', methods=['POST'])
@login_required
def add_connection():
    """
    Defines the add connection route and the variables called within it. Sets POST and GET methods
    """
    connected_user_id = request.form.get('connected_user_id')

    # Check if the user is trying to add themselves as a connection
    if int(connected_user_id) == current_user.id:
        flash("You cannot add yourself as a connection.", "error")
        return redirect(request.referrer)

    # Check if the user is already connected to the specified user
    existing_connection = UserConnection.query.filter_by(user_id=current_user.id, connected_user_id=connected_user_id).first()
    if existing_connection:
        flash("You are already connected to this user.", "error")
        return redirect(request.referrer)  # Redirect to a relevant page using GET method

    # Check if a connection request already exists
    existing_request = ConnectionRequest.query.filter_by(sender_id=current_user.id, receiver_id=connected_user_id).first()
    if existing_request:
        flash("A connection request has already been sent to this user.", "error")
        return redirect(request.referrer)  # Redirect to a relevant page using GET method

    try:
        # Check if a reverse connection already exists
        reverse_connection = UserConnection.query.filter_by(user_id=connected_user_id, connected_user_id=current_user.id).first()
        if reverse_connection:
            # Update the status of the existing connection to 'accepted'
            reverse_connection.status = 'accepted'
        else:
            # Create a new ConnectionRequest object and add it to the database
            connection_request = ConnectionRequest(sender_id=current_user.id, receiver_id=connected_user_id)
            db.session.add(connection_request)
            db.session.commit()
            flash("Connection request sent successfully.", "success")

        return redirect(request.referrer)  # Redirect to a relevant page using GET method
    
    except IntegrityError:
        # Handle the database error caused by attempting to add a duplicate connection
        db.session.rollback()
        flash("An error occurred while processing your request.", "error")

    return redirect(url_for('views.view_all_users'))  # Redirect to a relevant page using GET method


@views.route('/connection_requests')
@login_required
def connection_requests():
    """
    Defines the connection requests route and the variables called within it. Sets POST and GET methods
    """
    users = User.query.all()
    total_workouts = {}  # Dictionary to store total workouts for each user
    workouts = {}  # Dictionary to store workouts for each user
    total_user_connections = {}  # Dictionary to store total connections for each user

    # Pre-fetch connections for the current user
    current_user_connections = list(connection.connected_user_id for connection in current_user.connections)

    for user in users:
        # Query workouts for each user without filtering by current user's ID
        user_workouts = Workout.query.filter_by(user_id=user.id).filter(Workout.workout_date != None).order_by(Workout.workout_date).all()
        # Store workouts for each user
        workouts[user.id] = user_workouts
        # Count total workouts for each user
        total_workouts[user.id] = len(user_workouts)
        # Count total connections for each user
        total_user_connections[user.id] = len(user.connections)

        # Check if the displayed user is connected to the current user
        user.user_is_connected = user.id in current_user_connections

    # Fetch connection requests for the current user
    connection_requests = ConnectionRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()

    return render_template('connection_requests.html', connection_requests=connection_requests, users=users, user=current_user, total_workouts=total_workouts, workouts=workouts, total_user_connections=total_user_connections)


@views.route('/accept_connection_request/<int:request_id>', methods=['POST'])
@login_required
def accept_connection_request(request_id):
    """
    Defines the accepts route and the variables called within it. Sets POST and GET methods
    """
    connection_request = ConnectionRequest.query.get_or_404(request_id)
    if connection_request.receiver_id != current_user.id:
        abort(403)

    connection_request.status = 'accepted'
    # Create a UserConnection record for the receiver
    user_connection_receiver = UserConnection(user_id=connection_request.receiver_id, connected_user_id=connection_request.sender_id)
    db.session.add(user_connection_receiver)

    # Create a UserConnection record for the sender
    user_connection_sender = UserConnection(user_id=connection_request.sender_id, connected_user_id=connection_request.receiver_id)
    db.session.add(user_connection_sender)

    # Commit changes to the database
    db.session.commit()

    # Delete the connection request from the database
    db.session.delete(connection_request)
    db.session.commit()

    flash("Connection request accepted.", "success")

    return redirect(request.referrer)


@views.route('/reject_connection_request/<int:request_id>', methods=['POST'])
@login_required
def reject_connection_request(request_id):
    """
    Defines the rejections route and the variables called within it. Sets POST and GET methods
    """
    connection_request = ConnectionRequest.query.get_or_404(request_id)
    if connection_request.receiver_id != current_user.id:
        abort(403)

    connection_request.status = 'rejected'

    # Commit changes to the database
    db.session.commit()

    # Delete the connection request from the database
    db.session.delete(connection_request)
    db.session.commit()

    flash("Connection request rejected.", "success")

    return redirect(request.referrer)


@views.route('/user_connections/<int:user_id>')
def view_user_connections(user_id):
    """
    Defines the user connections route and the variables called within it
    """
    user = User.query.get_or_404(user_id)
    connection_request_sent = ConnectionRequest.query.filter_by(sender_id=current_user.id).first() is not None
    pending_connection_request = ConnectionRequest.query.filter_by(sender_id=user.id).first() is not None

    # Check if the displayed user is connected to the current user
    user_is_connected = UserConnection.query.filter_by(user_id=current_user.id, connected_user_id=user_id).first() is not None
    
    # Query user connections
    user_connections = UserConnection.query.filter_by(user_id=user_id).all()
    
    # Fetch connected users
    connected_users = [connection.connected_user for connection in user_connections]

    # Calculate total number of connections
    total_user_connections = len(user_connections)

    # Calculate total workouts for the user
    user_workouts = Workout.query.filter_by(user_id=user_id).filter(Workout.workout_date != None).all()
    total_workouts = {user_id: len(user_workouts)}

    # Calculate total workouts for connected users
    for connected_user in connected_users:
        connected_user_workouts = Workout.query.filter_by(user_id=connected_user.id).filter(Workout.workout_date != None).all()
        total_workouts[connected_user.id] = len(connected_user_workouts)

    return render_template('user_connections.html', user=user, connected_users=connected_users, total_workouts=total_workouts, total_user_connections=total_user_connections, user_is_connected=user_is_connected, connection_request_sent=connection_request_sent, pending_connection_request=pending_connection_request)


def update_connection_counts(user_id_1, user_id_2):
    """
    Used to setup inbound and outbound connection requests
    """
    user_1 = User.query.get(user_id_1)
    user_2 = User.query.get(user_id_2)

    if user_1:
        user_1.connections = UserConnection.query.filter_by(user_id=user_id_1).all()
        db.session.commit()

    if user_2:
        user_2.connections = UserConnection.query.filter_by(user_id=user_id_2).all()
        db.session.commit()


@views.route('/remove_connection', methods=['POST'])
@login_required
def remove_connection():
    """
    Defines the remove route and the variables called within it. Sets the POST method
    """
    connected_user_ids = request.form.getlist('connected_user_id[]')  # Get list of connected user IDs
    
    print("Connected User IDs to Remove:", connected_user_ids)  # Add this line to print the connected user IDs
    
    for connected_user_id in connected_user_ids:
        # Query the existing connections in both directions
        connection_1 = UserConnection.query.filter_by(user_id=current_user.id, connected_user_id=connected_user_id).first()
        connection_2 = UserConnection.query.filter_by(user_id=connected_user_id, connected_user_id=current_user.id).first()

        # Check if the connection exists in either direction
        if connection_1:
            # Delete the connection from the database
            db.session.delete(connection_1)
            db.session.commit()
        if connection_2:
            # Delete the connection from the database
            db.session.delete(connection_2)
            db.session.commit()
            flash("Connection removed.", "success")
        if not connection_1 and not connection_2:
            flash("Connection does not exist.", "error")

        # Update the total number of connections for both users
        update_connection_counts(current_user.id, connected_user_id)
        # After successfully removing the connection, set connection_request_sent to False
        connection_request_sent = ConnectionRequest.query.filter_by(sender_id=current_user.id).first() is not None

    return redirect(request.referrer)


"""
Below are the corporate pages routes. No login required to view them
"""


@views.route('/press')
def press():
    return render_template("press.html", user=current_user)


@views.route('/privacy')
def privacy():
    return render_template("privacy.html", user=current_user)


@views.route('/faq')
def faq():
    return render_template("faq.html", user=current_user)


@views.route('/user_agreement')
def user_agreement():
    return render_template("user_agreement.html", user=current_user)


@views.route('/', defaults={'path': ''})
@views.route('/<path:path>')
def catch_all(path):
    """
    Catch all routes that don't match any other routes.
    """
    return render_template('catch_all.html'), 404
