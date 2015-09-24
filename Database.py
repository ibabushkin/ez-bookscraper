# -*- coding: utf-8 -*-
import sqlite3
from os import remove
import ThreadFinder


def init_database():
    """Create the table we need.
    """
    connection = sqlite3.connect("books.db")
    c = connection.cursor()
    c.execute("CREATE TABLE books (name text, url text)")
    connection.commit()
    connection.close()


def clean():
    """Reset the Database.
    """
    remove("books.db")
    init_database()


def stats():
    """Print database statistics.
    """
    print("Number of books indexed: %d" % len(get_books()))


def get_books():
    """Get all saved books as Book() objects.
    """
    connection = sqlite3.connect("books.db")
    c = connection.cursor()
    c.execute("SELECT * FROM books")
    books = []
    while True:
        book = c.fetchone()
        if not book:
            break
        books.append(ThreadFinder.Book(book[0], book[1]))
    connection.close()
    return books


def insert_books(books):
    """Take a list of Book() objects and insert the ones that
    don't seem to be present already.
    """
    books1 = []
    connection = sqlite3.connect("books.db")
    c = connection.cursor()
    for b in books:
        book = (b.name, b.link)
        c.execute("SELECT * FROM books WHERE name=?", (b.name,))
        if not c.fetchone():
            books1.append(book)
    n = len(books1)
    print("Inserting %d books into database..." % n)
    c.executemany("INSERT INTO books VALUES (?,?)", books1)
    connection.commit()
    connection.close()
    return n
