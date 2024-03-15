from gb_website import create_app, db # Instruction to import the application function from the gb_website directory

app = create_app() # Calls the app function

if __name__ == '__main__':
    """
    Ensures app only runs directly and not when imported
    """
    app.run(debug=False) # False when deploy
 