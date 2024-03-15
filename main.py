import os
from gb_website import create_app, db # Instruction to import the application function from the gb_website directory

app = create_app() # Calls the app function

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    """
    Ensures app only runs directly and not when imported
    """
    app.run(
    host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=os.environ.get("DEBUG") # False when deploy
    )
 