import os
import requests
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
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

@app.route("/", methods=["GET"])
def index():
    #If the user isn't signed in, prompt them
    if session.get("USERNAME") is None:
        return redirect(url_for('sign_in'))
    #Else, move them to the home page
    else:
        return redirect(url_for('home'))

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

            #Now that they're registered, store their sessiona and go to home page
            session["USERNAME"] = username
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

        #Since the password is right, store session and redirect them to home
        if check_password(password, passkey.passkey):
            session["USERNAME"] = username
            return redirect(url_for('home'))

        #Since that's not the case, return invalid credentials
        return render_template("sign_in.html", error = "Invalid credentials. Please try again.")

    #If they just brought up the page, then don't do anything, just wait
    else:
        return render_template("sign_in.html")

@app.route("/logout", methods=["GET"])
def logout():
    session.pop("USERNAME", None)
    #If someone is trying to access the page, let them
    return redirect(url_for('sign_in'))

#will need to remove get
@app.route("/home", methods=["GET"])
def home():
    #Make sure user is signed in
    if session.get("USERNAME") is None:
        return redirect(url_for('sign_in'))
    print("Username: ", session.get("USERNAME"))
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
    #Make sure user is signed in
    if session.get("USERNAME") is None:
        return redirect(url_for('sign_in'))

    #Make sur book exists
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("books.html", error = "Sorry, that book doesn't match our records. Please try another.")

    #Get the book information
    res = get_api_info(book.isbn)

    #Get the reviews
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book.id}).fetchall()

    #Get the rest of the book information
    return render_template("books.html", res = res, book = book, reviews = reviews)

#add filter for user id
@app.route("/books/write_review/<int:book_id>", methods=["GET", "POST"])
def write_review(book_id):
    #Make sure user is signed in
    if session.get("USERNAME") is None:
        return redirect(url_for('sign_in'))
    #If we're pulling up the review page, let the form be generated
    if request.method == "GET":
        #Make sure user didn't already write a review
        user = session.get("USERNAME")
        #If they didn't write a review, generate this template
        if db.execute("SELECT * FROM reviews WHERE author = :user AND book_id = :book_id", {"user": user, "book_id": book_id}).rowcount == 0:
            ratings = [1,2,3,4,5]
            return render_template("write_review.html", ratings=ratings)
        else:
            return render_template("sorry.html", error = "You already reviewed that book.")
    #Else, we're trying to submit
    if request.method == "POST":
        username = session.get("USERNAME")
        user_id = db.execute("SELECT id FROM users WHERE username = username", {"username": username}).fetchone()
        user_id = user_id.id
        author = session.get("USERNAME")
        title = request.form.get("title")
        rating = request.form.get("rating")
        text = request.form.get("text")
        db.execute("INSERT INTO reviews (user_id, author, title, rating, text, book_id) VALUES (:user_id, :author,:title, :rating, :text, :book_id)",
            {"user_id": user_id, "author": author, "title": title, "rating": rating, "text": text, "book_id": book_id})
        db.commit()
        return redirect(url_for('book', book_id = book_id))


@app.route("/api/<string:isbn>")
def book_api(isbn):
    #Return details about a single books
    #Make sure book exists
    if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0:
        return render_template("sorry.html", error = "That ISBN doesn't match out database.")

    #Since the book exists, retrieve it and then send its data
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    res = get_api_info(book.isbn)
    print(res)
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": res["work_reviews_count"],
        "average_rating": res["average_rating"],
    })
