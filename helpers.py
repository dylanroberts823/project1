import hashlib, binascii, os, requests

master_word = 'adfjkdsajf'
#Note: I attempted using and storing hash and salts, but mySQL did not allow me to store the byte database
#I couldn't even create varbinary columns :(
def generate_passkey(password):
    passkey = password+master_word
    return passkey

def check_password(password_to_check, passkey):
    # Use the exact same setup you used to generate the key, but this time put in the password to check
    new_key = password_to_check+master_word
    return new_key==passkey

def get_api_info(book_isbn):
    #Use the key to get the book data from the API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "oq9wEzUiZfG9ezeNGThi9g", "isbns": book_isbn})
    #Turn that data into a json object
    res = res.json()
    #Return the first result
    return res['books'][0]
