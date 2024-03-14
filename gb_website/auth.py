from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
import secrets

"""
The above lines are used to import built-in functions from Flask
"""

auth = Blueprint('auth', __name__) # Sets the prefix for the login routes


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Defines the login route and the variables called within it. Sets POST and GET methods
    """
    if request.method == 'POST': # Checks for POST method
        email = request.form.get('email') # Captures the variable email from the form input
        password = request.form.get('password') # Captures the variable password from the form input

        user = User.query.filter_by(email=email).first() # Checks the email exists
        if user:
            if check_password_hash(user.password, password): # Checks the password is correct
                login_user(user, remember=True)
                if current_user.is_authenticated:  # Checks if the user is authenticated
                    return redirect(url_for('views.home', user_id=current_user.id))
            else:
                flash('Incorrect password, try again.', category='error') # Notifies user of issues
        else:
            flash('Email does not exist. Please sign up.', category='error') # Notifies user of issues
            return redirect(url_for('auth.sign_up')) # Redirects user to sign-up page

    return render_template("login.html", user=current_user) # Sets the frontend


@auth.route('/logout')
@login_required # Decorator to confirm user needs to be authenticated to access the route
def logout():
    """
    Logout route
    """
    logout_user()
    return redirect(url_for('auth.login')) # Redirects user to login page


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """
    Sign up route. Sets POST and GET methods
    """
    if request.method == 'POST': # Checks for POST method
        email = request.form.get('email') # Captures variable from form input
        first_name = request.form.get('firstName') # Captures variable from form input
        last_name = request.form.get('lastName') # Captures variable from form input
        password1 = request.form.get('password1') # Captures variable from form input
        password2 = request.form.get('password2') # Captures variable from form input

        user = User.query.filter_by(email=email).first() # Validates information inputed into form
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error') # User advised
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256')) # Method to encrypt password
            db.session.add(new_user) # Adds user details to database
            db.session.commit() # Commits changes
            login_user(new_user, remember=True) # Cookie to log user to the session
            return redirect(url_for('views.home', user_id=current_user.id)) # Redirects successful user to next page

    return render_template("sign_up.html", user=current_user) # Sets the frontend


@auth.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    """
    Forgotten password route. Sets POST and GET methods
    """
    if request.method == 'POST': # Checks for POST method
        email = request.form['email'] # Captures variable from form input

        user = User.query.filter_by(email=email).first() # Validates information inputed into form
        if user:
            token = secrets.token_urlsafe(32)  # Encrypts the password reset email
            send_password_reset_email(email, token) # Calls password reset email function
            flash('Password reset instructions have been sent to your email.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not recognised. Please sign up.', category='error') # Notifies user of issues
            return redirect(url_for('auth.sign-up')) # Redirects successful user to next page
        
    return render_template("forgotten_password.html", user=current_user) # Sets the frontend


def send_password_reset_email(email, token):
    """
    Function to send password reset email. Defines parameters
    """
    msg = Message('GymBunnies Password Reset', sender='info@hippobooks.co.uk', recipients=[email])
    reset_url = url_for('auth.update_password', token=token, _external=True)
    msg.body = f'Fear not! \n\nWe will have you back in your account and tracking your fitness goals in no time! \n\nSimply click the following link to reset your password: {reset_url} \n\nKind regards, \n\nThe GymBunnies IT Team'
    mail.send(msg)


@auth.route('/update_password/<token>', methods=['GET', 'POST'])
def update_password(token):
    """
    Update password route. Sets POST and GET methods
    """
    if request.method == 'POST': # Checks for POST method
        password1 = request.form.get('password1') # Captures information inputed into form
        password2 = request.form.get('password2') # Captures information inputed into form

        if password1 != password2: # Validates information inputed into form
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            update_user = User(password=generate_password_hash(
                password1, method='pbkdf2:sha256')) # Updates password
            db.session.commit() # Commits new record to the database
            login_user(update_user, remember=True) # Sets cookie
            return redirect(url_for('views.home', user=current_user.id)) # Redirects successful user to next page
        
    return render_template("update_password.html", user=current_user) # Sets the frontend