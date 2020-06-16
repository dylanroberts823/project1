import hashlib, binascii, os, requests

def generate_passkey(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    passkey = salt + key
    return passkey

def check_password(password_to_check, passkey):
    # Use the exact same setup you used to generate the key, but this time put in the password to check
    salt = passkey[:32]
    key = passkey[32:]
    new_key = hashlib.pbkdf2_hmac('sha256', password_to_check.encode('utf-8'), b'salt', 100000)
    return new_key==key

def get_api_info(book_isbn):
    #Use the key to get the book data from the API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "oq9wEzUiZfG9ezeNGThi9g", "isbns": book_isbn})
    #Turn that data into a json object
    res = res.json()
    #Return the first result
    return res['books'][0]
