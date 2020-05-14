import os
import requests
from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

#set up book database
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"oq9wEzUiZfG9ezeNGThi9g": "oq9wEzUiZfG9ezeNGThi9g", "isbns": "9781632168146"})

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['DATABASE_URL'] = "postgres://nlxqqpgfkqhxib:7d97bfa8bbfe8a46ac6dc258d70ae1abaf0b991922b8e05751179a1a80961169@ec2-52-202-22-140.compute-1.amazonaws.com:5432/d1r47q8b8p5c3q"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#test the key
print(res.json())

#DATABASE_URL: postgres://nlxqqpgfkqhxib:7d97bfa8bbfe8a46ac6dc258d70ae1abaf0b991922b8e05751179a1a80961169@ec2-52-202-22-140.compute-1.amazonaws.com:5432/d1r47q8b8p5c3q
#GoodReads API: oq9wEzUiZfG9ezeNGThi9g

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sign_in")
def sign_in():
    return render_template("sign_in.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/hello", methods=["POST"])
def hello():
    name = request.form.get("name")
    return render_template("hello.html", name=name)

@app.route("/confirmation")
def register():
    return render_template("register.html")
