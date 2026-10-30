from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from typing import Tuple
from datetime import datetime

app = Flask(__name__)
app.secret_key = "Change-this-to-a-long-random-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Adminuser(db.Model):
    adminid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), uniqe_key=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    