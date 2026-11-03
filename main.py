from flask import Flask, render_template, url_for, request, session, redirect, abort

from flask_sqlalchemy import SQLAlchemy

import json
import bcrypt

from uuid import uuid4
from datetime import datetime
from typing import Tuple

#all this code under here to make it possible to login and make a user and hash
#i have created everything here and is used by me to learn backend coding here.

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = "Change-this-to-a-long-random-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # lagrer data i kolonner/column i id tall/integer
    username = db.Column(db.String(150), unique=True, nullable=False)
    # lagrer data i kolonner/column i username string
    password = db.Column(db.String(255), nullable=False)
    #lagrer data i kolonner/column i password string

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    request_id = db.Column(db.String(80), nullable=False)
    #this identifies the id because og request of id
    history = db.Column(db.Text(), nullable=True)
    #this stores information about the change very important for history of logins and registers.
    model_name = db.Column(db.String(80), nullable=False)
    #this finds out with model name which database model that was changed
    original_id = db.Column(db.Integer)
    #what was the original id of the affetced user like integer
    db_event_name = db.Column(db.String(80), nullable=False)
    #just finds out if it is register edit delete or login


    def __repr__(self):
        return f'<AuditLog {self.id}: {self.db_event_name}>'


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
                return redirect("/wrong")
#this is for writing username and if it is taken on the website it will return message if not it will go further down

            hashed_password = hash_pwd(password).decode("utf-8")
            new_user = User(username=username, password=hashed_password)
            if not password.isdigit():
                return redirect("/wrong.html")
            
            if not username.isalpha():
                return redirect("/wrong.html")
            else:
                db.session.add(new_user)
                db.session.commit()
                create_log(new_user.id, "register", {
                    "username": new_user.username,
                    "action": "New account created"
                })
                #we need to create_log here så the log knows whats going on like newuserid would be displayed username in database.
                return redirect("/Success")
#this code makes it possible to write a new username and password if it was valid then it will return Account was created. 

        elif action == "login":
            user = User.query.filter_by(username=username).first()
            
            if user and check_pwd(password, user.password.encode("utf-8")):
                session.clear()
                session["user_id"] = user.id
                create_log(user.id, "login", {
                    "username": user.username,
                    "action": "User logged in"
                })
                #here the same process is going on it sends this to the log and connects with the function so it can display it in database who logged in.
                return redirect("/home")
            else:
                return redirect("/wrong")
    return render_template("index.html")

def create_log(user_id, action, history=None):

    log = AuditLog(
        request_id=str(uuid4()),
        model_name="User",
        original_id=user_id,
        db_event_name=action,
        history=json.dumps(history) if history else None   
        #the whole code over here is the functions that make the log work and sends it to database
    )
    db.session.add(log)
    db.session.commit()
    print(log)
    # this adds and commits the log auditlog updates that happens when code is getting used like logging in.

    return render_template("index.html")












#HASHING CODE UNDER HERE

        # handles the function
def hash_pwd(password:int, rounds=12) -> bytes:
    pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=rounds))
    return pwd

def check_pwd(password:int,hash:bytes) -> bool:
    return bcrypt.checkpw(password.encode(),hash)
#koden over her gir passordet en hash som kan lagres og sjekke om passordet stemmer med hashet på chech_pwd


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








# denne koden brukes når du har laget konto eller logget inn så vil du ha en bank som kan ha penger siden du har lagt til fra før
#eller en ny bank hvis det er en ny registrert user.


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
        if bank:
            db.session.delete(bank)
        create_log(user_id, "delete")
        db.session.delete(user_to_delete)
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

@app.route("/adminpin", methods=["POST"])
def adminpin():
    adminpin == 1234

    if request.method == "POST":
        pass
    #not done

    

@app.route("/clear", methods=["POST"])
def clear():
    session.clear()
    return redirect("/")
    
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
# Make webiste look like ATM from 90s DONE
# make a admin pin with the pin buttons NOT DONE AND DIFFICULT TO DO SO WOULD BE EXTRA MISSION IF DONE
# create a list/track og recent action, small display/scrolling box showing past events DONE 
# create a custom deposit field for money NOT DONE





#viktig å vite
#flask + sqlalchemy: lagrer brukere i test db og gjør så innlogging funker på min nettside
#userauth: denne lagrer brukerene jeg lager og der har jeg en funksjon som gjør se det er maks 3 innlogginger og 15 minutter låsing hvis over 3 innloggingsforsøk
#låsingen funker ikke enda da
