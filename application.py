import os
import requests
from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import generate_passkey, check_password, get_api_info

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

#DATABASE_URL: postgres://nlxqqpgfkqhxib:7d97bfa8bbfe8a46ac6dc258d70ae1abaf0b991922b8e05751179a1a80961169@ec2-52-202-22-140.compute-1.amazonaws.com:5432/d1r47q8b8p5c3q
#GoodReads API: oq9wEzUiZfG9ezeNGThi9g

#Set a user variable to access
user = ""

@app.route("/", methods=["GET"])
def index():
    return redirect(url_for('register'))

@app.route("/register", methods=["GET", "POST"])
def register():
    #First, if someone is trying to register
    if request.method == "POST":
        #Check if all the fields are filled in
        if not request.form.get("username"):
            return render_template("register.html", error = "Please fill in your username.")

        if not request.form.get("password"):
            return render_template("register.html", error = "Please fill in your password.")

        if not request.form.get("conf_password"):
            return render_template("register.html", error = "Please fill in your confirmation password.")

        #Save their data into variables
        username = request.form.get("username")
        password = request.form.get("password")
        conf_password = request.form.get("conf_password")


        #Check that their passwords match
        if not password == conf_password:
            return render_template("register.html", error = "Password and confirmation password don't match. Please fill them in again.")

        #Then, check if that user already exists
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
            #Since they don't exist, hash and store their user
            passkey = generate_passkey(password)
            db.execute("INSERT INTO users (username, passkey) VALUES (:username, :passkey)", {"username": username, "passkey":passkey})
            db.commit()

            #Now that they're registered, go to home page
            return redirect(url_for('home'))

        #Since the user does exist, return invalid credentials
        else:
            return render_template("sign_in.html", error = "Sorry, that user already exists. Please try again.")

    #If they just brought up the page, then don't do anything, just wait
    else:
        return render_template("register.html")



@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():

    #First, if someone is trying to sign in
    if request.method == "POST":

        #Check if all the fields are filled in
        if not request.form.get("username"):
            return render_template("sign_in.html", error = "Please fill in your username.")

        elif not request.form.get("password"):
            return render_template("sign_in.html", error = "Please fill in your password.")

        #Save their data into variables
        username = request.form.get("username")
        password = request.form.get("password")

        #Then, check if that user already exists
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
            return render_template("sign_in.html", error = "Invalid credentials. Please try again.")

        #Since they do exist, check their password
        passkey = db.execute("SELECT passkey FROM users WHERE username = :username", {"username": username}).fetchone()

        if check_password(password, passkey.passkey):
            return redirect(url_for('home'))

        #Since that's not the case, return invalid credentials
        return render_template("sign_in.html", error = "Invalid credentials. Please try again.")

    #If they just brought up the page, then don't do anything, just wait
    else:
        return render_template("sign_in.html")

#will need to remove get
@app.route("/home", methods=["GET"])
def home():
    #If someone is trying to access the page, let them
    return render_template("home.html")

@app.route("/search", methods=["POST"])
def search():
    #Since someone is trying to search, retrieve the form values
    search_input = "%"+request.form.get("search_input")+"%"
    books = db.execute("SELECT * FROM books WHERE isbn LIKE :search_input OR title LIKE :search_input OR author LIKE :search_input OR year LIKE :search_input", {"search_input": search_input}).fetchall()
    return render_template("search.html", books = books)

@app.route("/books/<int:book_id>")
def book(book_id):
    #Make sur book exists
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("books.html", error = "Sorry, that book doesn't match our records. Please try another.")

    #Get the book information
    res = get_api_info(book.isbn)

    #Get the rest of the book information
    return render_template("books.html", res = res, book = book)


@app.route("/user_reviews")
def user_reviews():
    return render_template("user_reviews.html")
