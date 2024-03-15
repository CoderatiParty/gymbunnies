import os
from gb_website import create_app, db # Instruction to import the application function from the gb_website directory

app = create_app() # Calls the app function

with app.app_context():
    db.create_all()