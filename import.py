#Credits to Faab for inspiration on making this neater with the open/with function
#https://github.com/Faaab/cs50w-project1/blob/master/import.py

import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
                                                # database engine object from SQLAlchemy that manages connections to the database
                                                # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))  # create a 'scoped session' that ensures different users' interactions with the

def main():                                                # database are kept separate
    #create table
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL)")

    with open('books.csv', 'r') as books_csv:
        reader = csv.reader(books_csv)

        # Skip first row in csv, since this holds names of columns, not actual data
        next(reader)

        #Printing (had to leave while all the lines printed)
        #Commented out print function, can bring back if desired
        for isbn, title, author, year in reader:
            db.execute("INSERT INTO books (isbn, author, title, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
            #print(f"Added {title} by {author} from year {year}")
        db.commit()

if __name__ == "__main__":
    main()
