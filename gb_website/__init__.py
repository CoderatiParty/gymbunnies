import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
if os.path.exists("env.py"):
    import env
from flask_login import LoginManager
from flask_mail import Mail
from os import path, environ


db = SQLAlchemy()  # Defines the database
DB_NAME = "database.db"  # Names the database
mail = Mail()

def create_app():
    """
    This is the application's main function
    """
    app = Flask(__name__)  # Creates the app
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY") # Defines the secret key

    if os.environ.get("DEVELOPMENT") == "True":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
    else:
        uri = os.environ.get("DATABASE_URL")
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = uri

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL") # Defines the database
    app.config['MAIL_SERVER'] = 'smtp.zoho.eu'  # Defines the server for outgoing mail
    app.config['MAIL_PORT'] = 465  # Sets the port
    app.config['MAIL_USE_SSL'] = True  # Assigns SSL
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Outgoing email address
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Mail password

    db.init_app(app)

    from .views import views  # Imports the views routes from the views file
    from .auth import auth  # Imports the auth routes from the auth file

    app.register_blueprint(views, url_prefix='/')  # Calls the Blueprint application from within Flask
    app.register_blueprint(auth, url_prefix='/')  # Calls the Blueprint application from within Flask

    mail = Mail(app)  # Sets the mail function within the app

    login_manager = LoginManager()  # Calls the login manager application
    login_manager.login_view = 'auth.login'  # Sets the login route
    login_manager.init_app(app)  # Sets the manager within the app

    from .models import User  # Imports the database 'User' from the models file

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    """
    The above decorator function is used to link the user with the database
    """

    return app  # Runs the app after setting the above

def create_database(app):
    """
    Initiates the database if it doesn't already exist
    """
    if not path.exists('website/' + DB_NAME):
        with app.app_context():  # Establish application context
            db.create_all()  # Perform database operations within application context
        print('Created Database!')