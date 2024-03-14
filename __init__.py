from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail, Message
import secrets

"""
The above lines are used to import built-in functions from Flask
"""

db = SQLAlchemy() # Defines the database
DB_NAME = "database.db" # Names the database
mail = Mail() # Defines the mail function for password reset requests


def create_app():
    """
    This is the applications main function
    """
    app = Flask(__name__) # Creates the app
    app.config['SECRET_KEY'] = 'gymbunniesareusman' # Defines the secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # Defines the database
    app.config['MAIL_SERVER'] = 'smtp.zoho.eu' # Defines the server for outgoing mail
    app.config['MAIL_PORT'] = 465 # Sets the port
    app.config['MAIL_USE_SSL'] = True # Assigns SSL
    app.config['MAIL_USERNAME'] = 'info@hippobooks.co.uk' # Outgoing email address
    app.config['MAIL_PASSWORD'] = 'M3ssengerhblps' # Mail password
    db.init_app(app)

    from .views import views # Imports the views routes from the views file
    from .auth import auth # Imports the auth routes from the auth file

    mail = Mail(app) # Sets the mail function within the app

    app.register_blueprint(views, url_prefix='/') # Calls the Blueprint application from within Flask
    app.register_blueprint(auth, url_prefix='/') # Calls the Blueprint application from within Flask

    from .models import User # Imports the database 'User' from the models file
    
    with app.app_context(): # Calls the databaase tables and makes them assessible within the application
        db.create_all()

    login_manager = LoginManager()# Calls the login manager application
    login_manager.login_view = 'auth.login' # Sets the login route
    login_manager.init_app(app) # Sets the manager within the app

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    """
    The above decorator function used to link the user with the database
    """

    return app # Runs the app after setting the above


def create_database(app):
    """
    Initiates the database if it doesn't already exist
    """
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')