from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from typing import Tuple
from datetime import datetime

#all this code under here to make it possible to login and make a user

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

            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return app.redirect("/Success")
#this code makes it possible to write a new username and password if it was valid then it will return Account was created. 

        elif action == "login":
            user = User.query.filter_by(username=username, password=password).first()
            
            if user:
                session.clear()
                session["user_id"] = user.id
                return app.redirect("/home")
            else:
                return app.redirect("/wrong")
# denne koden brukes når du har laget konto og skal logge inn så hvis du skriver på username og password og det finnes når
# du trykker login så viser den welcome back username else invalid username or password.
    return render_template("index.html")



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
        db.session.commit()

    # When a button is clicked
    if request.method == "POST":
        Money = request.form.get("Money")

        if Money in ["1000000", "500000", "100000"]:
            bank.total = bank.total + int(Money)
            db.session.commit()

        return redirect("/home")

    return render_template("home.html", total=bank.total)

@app.route("/wrong")
def wrong ():
    return render_template("wrong.html")

@app.route("/Success")
def Success ():
    return render_template("Success.html")

with app.app_context():
    db.create_all()
#this code over will automatically create the database



#hashing code under here


# handles the function
def hash_pwd(password:str, rounds=12) -> bytes:
    pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    print(pwd)
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
        #max login attempts is 3 and lock out is 15 just variables over to define code under


def add_user(self, username:str, password:str) -> bool:
    if username in self.users:
        return False


    self.users[username] = {
        'pwd_hash': hash_pwd(password),
        'created_at': datetime.now(),
        'pwd_rounds': 12
    }
    return True
# this code over is just creating a new user first checks if there is a user if not then a new with hash password saved in new account

# this code is checking if user exists, user is locked and password is right
def login(self, username:str, password:str) -> Tuple[bool, str]:
    if self._is_locked(username):
        return False,"To many attempts, account locked!"

    if username not in self.users:
        return False, "ivalid user info..." 

    user = self.users[username]
    if not check_pwd(password=['pwd_hash']):
        self._track_simple_attempts(username)
        return False, "Invalid user info..."

    

def _is_locked(self, username:str) -> bool:
    if username not in self.login_attemots:
        return False

    attempts, last_attempt = self.login_attempts[username]
    if attempts >= self.max_attempts:
            mins_passed = (datetime.now() - last_attempt).total_seconds() / 60
            if mins_passed < self.lockout_minutes:
                return True
            del self.login_attempts[username]
        return False
#this code over here adds a fucntion so if you write the password wrong 3 times it locks you out in 15minutes


def _track_attempts(self, username:str):
    now = datetime.now()
    if username in self.login_attempts[username]:
        attempts, _ = self.login_attempts[username]
        self.login_attempts[username] = (attempts + 1, now)
    else:
        self.login_attempts[username] = (1, now)
#this code over holds track of how many attempts have been made to login

    #if there is more users this will upgrade the security
    def _upgrade_hash(self, username:str, password:str):
        user = self.users[username]
        min_rounds = 14
        #i can raise this number over here to increase the security of the hash
        if user['pwd_hash'] < min_rounds:
            user['pwd_hash'] = hash_pwd(password, min_rounds)
            user['pwd_hash']


if __name__ == "__main__":
    app.run(debug=True)




# my webiste
# register users  DONE
# log in users    DONE
# save users using sqlite DONE
# seperate balance for each user    DONE
# add money with buttons   DONE
# remember money after restarting  DONE 
# log out   NO
# secure password storage ONGOING