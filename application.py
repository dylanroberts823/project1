import os
import requests
from flask import Flask, session, render_template, request
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

@app.route("/", methods=["GET", "POST"])
def index():

    #First, if someone is trying to register
    if request.method == "POST":

        #Check if all the fields are filled in
        if not request.form.get("username"):
            return render_template("sorry.html", tease = "What's in a name? Your user.", error = "Please fill in your username.")

        if not request.form.get("password"):
            return render_template("sorry.html", tease = "*Knocks on door* What's the secret password? I don't know, you need to fill that in.", error = "Please fill in your password.")

        if not request.form.get("conf_password"):
            return render_template("sorry.html", tease="Don't be lazy upsie-dazy. Write it twice, it'll be real nice.", error = "Please fill in your confirmation password.")

        #Save their data into variables
        username = request.form.get("username")
        password = request.form.get("password")
        conf_password = request.form.get("conf_password")


        #Check that their passwords match
        if not password == conf_password:
            return render_template("sorry.html", tease = "C'mon, copy paste can do better than that", error = "Password and confirmation password don't match. Please fill them in again.")

        ## DEBUG:
        #print(f"Added {username} by {password} from year {conf_password}")



        #Then, check if that user already exists

        #Then, hash and save their password

        #Now that they're registered, display the congratulations page before moving on

    #If they just brought up the page, then don't do anything, just wait
    else:
        return render_template("index.html")



@app.route("/sign_in")
def sign_in():
    return render_template("sign_in.html")

@app.route("/register")
def register():
    return render_template("register.html")

#@app.route("/hello", methods=["POST"])
#def hello():
#    name = request.form.get("name")
#    return render_template("hello.html", name=name)

#@app.route("/sorry", methods = ["GET"])
#def sorry():
#    return render_template("sorry.html")

@app.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/user_reviews")
def user_reviews():
    return render_template("user_reviews.html")
