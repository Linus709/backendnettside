from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from typing import Tuple
from datetime import datetime

#all this code under here to make it possible to login and make a user and hash

app = Flask(__name__)
app.secret_key = "Change-this-to-a-long-random-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # lagrer data i kolonner/column i id tall/integer 
    username = db.Column(db.String(150), unique=True, nullable=False)
    # lagrer data i kolonner/column i username string
    password = db.Column(db.String(150), nullable=False)
    #lagrer data i kolonner/column i password string

    def __repr__(self):
        return f'<User {self.username}>'


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        action = request.form.get("action")
#Code over makes so request method under works so when i write username in register code it will work because it is defined

        print(f"DEBUG -> Username: {username}, Password: {password}, Action: {action}")

        if action == "register":

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return app.redirect("/wrong")
#this is for writing username and if it is taken on the website it will return message if not it will go further down

            hashed_password = hash_pwd(password).decode("utf-8")
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return app.redirect("/Success")
#this code makes it possible to write a new username and password if it was valid then it will return Account was created. 

        elif action == "login":
            user = User.query.filter_by(username=username).first()
            
            if user and check_pwd(password, user.password.encode("utf-8")):
                session.clear()
                session["user_id"] = user.id
                return app.redirect("/home")
            else:
                return app.redirect("/wrong")


    return render_template("index.html")


#HASHING CODE UNDER HERE

        # handles the function
def hash_pwd(password:str, rounds=12) -> bytes:
    pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=rounds))
    return pwd

def check_pwd(password:str,hash:bytes) -> bool:
    return bcrypt.checkpw(password.encode(),hash)
#koden over her gir passordet en hash som kan lagres og sjekke om passordet stemmer med hashet på chech_pwd

class UserAuth:
    def __init__(self):
        self.users = {}
        self.login_attempts = {}
        self.max_attempts = 3
        self.lockout_minutes = 15

    def add_user(self, username: str, password: str) -> bool:
        if username in self.users:
            return False

        self.users[username] = {
            'pwd_hash': hash_pwd(password),
            'created_at': datetime.now(),
            'pwd_rounds': 12
        }
        return True

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        if self._is_locked(username):
            return False, "Too many attempts, account locked!"

        if username not in self.users:
            return False, "Invalid user info..."

        user = self.users[username]

        if not check_pwd(password, user['pwd_hash']):
            self._track_attempts(username)
            return False, "Invalid user info..."

        if username in self.login_attempts:
            del self.login_attempts[username]

        self._upgrade_hash(username, password)
        return True, "Success!"

    def _is_locked(self, username: str) -> bool:
        if username not in self.login_attempts:
            return False

        attempts, last_attempt = self.login_attempts[username]

        if attempts >= self.max_attempts:
            mins_passed = (datetime.now() - last_attempt).total_seconds() / 60

            if mins_passed < self.lockout_minutes:
                return True

            del self.login_attempts[username]

        return False

    def _track_attempts(self, username: str):
        now = datetime.now()

        if username in self.login_attempts:
            attempts, _ = self.login_attempts[username]
            self.login_attempts[username] = (attempts + 1, now)
        else:
            self.login_attempts[username] = (1, now)

    def _upgrade_hash(self, username: str, password: str):
        user = self.users[username]
        min_rounds = 14

        if user['pwd_rounds'] < min_rounds:
            user['pwd_hash'] = hash_pwd(password, min_rounds)
            user['pwd_rounds'] = min_rounds








# denne koden brukes når du har laget konto og skal logge inn så hvis du skriver på username og password og det finnes når
# du trykker login så viser den welcome back username else invalid username or password.

#code to add buttons and a table for money under her


class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    #user id will find the user who is logged in and remember it.
    total = db.Column(db.Integer, default=0)


@app.route("/home", methods=["GET", "POST"])
def home():

    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    bank = Bank.query.filter_by(user_id=user_id).first()
    #denne filtrer til at den vet user id som er de som er logget inn med penger


    # If there is no bank account, create one
    if bank is None:
        bank = Bank(user_id=user_id, total=0)
        #denne gjør så if user id total = 0 så lag en ny bank 
        db.session.add(bank)
        bank.total = 0
        db.session.commit()

    # When a button is clicked
    if request.method == "POST":
        Money = request.form.get("Money")

        if Money in ["1000", "100", "10", "1"]:
            bank.total = bank.total + int(Money)
            db.session.commit()

            return redirect("/home")
    
    return render_template("home.html", total=bank.total)

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()
    return redirect("/")



#DELETE BUTTON CODE 
@app.route('/delete', methods=["POST"])
def delete():
    id = session.get("user_id")
    user_id = session["user_id"]
    bank = Bank.query.filter_by(user_id=user_id).first()
#this gets the user id that is logged in now
    if id is None:
        return redirect("/")
# if there is no id go back home

    user_to_delete = User.query.get_or_404(id)
#if you are deleting a user you must query first and this searchs the database of user given id
    try:
        db.session.delete(user_to_delete)
        bank.total = 0
        db.session.commit()
        session.clear()
        print("USER DELETED SUCCESSFULLY!")
        return redirect("/")
# this is the code that will delete the user and clear logs the user out and removes everything stored in flask session

    except:
        db.session.rollback()
        #this code just makes sure that if it didnt work we keep those ncommited changes
        print("it didnt work!")
        return redirect("/home")


#This button code will reset your bank money
@app.route("/Bankreset", methods=["POST"])
def bankreset():
    if "user_id" not in session:
            return redirect("/")
    
    user_id = session["user_id"]
    #this 2 codes make so it knows about the user that is logged in now and the bank login username and password
    bank = Bank.query.filter_by(user_id=user_id).first()
    
    if bank:
        bank.total = 0
        #sets bank total at 0 and commits to database and prints out in my terminal that it worked then last keeps me at home html
        db.session.commit()
        print("bankreset DONE")
    return redirect("/home")


    
@app.route("/wrong")
def wrong ():
    return render_template("wrong.html")

@app.route("/Success")
def Success ():
    return render_template("Success.html")


with app.app_context():
    db.create_all()
#this code over will automatically create the database

if __name__ == "__main__":
    app.run(debug=True)




# my webiste
# register users  DONE
# log in users    DONE
# save users using sqlite DONE
# seperate balance for each user    DONE
# add money with buttons   DONE
# remember money after restarting  DONE 
# log out   DONE
# secure password storage DONE
# Make webiste look like ATM from 90s NOT DONE

#how to make website look like atm from 90s
#commonly displayed colors are green, amber/orange or blue text against dark background

#viktig å vite
#flask + sqlalchemy: lagrer brukere i test db og gjør så innlogging funker på min nettside
#userauth: denne lagrer brukerene jeg lager og der har jeg en funksjon som gjør se det er maks 3 innlogginger og 15 minutter låsing hvis over 3 innloggingsforsøk
#låsingen funker ikke enda da
