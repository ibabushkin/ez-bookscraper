# -*- coding: utf-8 -*-
import os
from os.path import isfile
from string import punctuation
import requests

from ThreadFinder import scrape_recent, scrape_all
import Database


class Category(object):
    """A category that can contain various amounts of books,
    as well as other categories.
    """
    def __init__(self, dirname, level=1):
        """Set everything up
        """
        self.name = dirname.split("/")[-1]
        self.level = level
        self.tags = []
        self.read_tags(dirname + "/tags")
        self.children = [Category(dirname + "/" + n, level+1)
                         for n in os.listdir(dirname) if "tags" not in n]
        self.children.sort(key=lambda x: x.name)
        self.books = []

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def read_tags(self, filename):
        """Get all tags from a file.
        """
        with open(filename, "r") as f:
            self.tags = [t for t in f.read().split("\n") if t]

    def sort_books(self, books):
        """Sort the books according to the tags.
        """
        rest = books
        for child in self.children:
            rest = child.sort_books(rest)
        for book in rest[:]:
            if self.match(book.name):
                self.books.append(book)
                rest.remove(book)
        self.books.sort(key=lambda x: x.name)
        return rest

    def match(self, book_name):
        """Check whether our book matches the category.
        """
        # exclude = set(punctuation)
        book_name = ''.join(ch for ch in book_name if ch not in "./\\")
        for tag in self.tags:
            if " " in tag and tag in book_name.lower():
                return True
            elif tag in book_name.lower().split(" "):
                return True
        return False

    def print_it(self):
        """Return a nice representation.
        """
        header = "=" * self.level
        ret = header + " " + self.name + " " + header + "\n"
        for book in self.books:
            ret += book.print_it()
        for child in self.children:
            ret += child.print_it()
        return ret


def generate(force=False):
    """Generate a wiki article with all books.
    """
    cat = Category("Books")
    if force or scrape_recent() > 0:
        if force:
            scrape_all()
        rest = Database.get_books()
        cat.sort_books(rest)
        ret = cat.print_it()
        ret += "= Misc =\n"
        for book in rest:
            ret += book.print_it()
        post_to_wiki(ret)
    else:
        print("Nothing to do!")


def password_wrapper():
    """Get a password + username for wiki access.
    """
    if isfile("password"):
        return tuple(open("password").read().split("\n")[:2])
    else:
        return (input("Username: "), input("Password: "))


def post_to_wiki(text):
    """Post a new index to the wiki.
    """
    user, passw = password_wrapper()
    baseurl = "https://evilzone.org/wiki/"
    params = "?action=login&lgname=%s&lgpassword=%s&format=json" % (user, passw)

    # Login request
    r1 = requests.post(baseurl+"api.php"+params)
    token = r1.json()["login"]["token"]

    # Confirm token; should give "Success"
    params2 = params + "&lgtoken=%s" % token
    r2 = requests.post(baseurl+"api.php"+params2, cookies=r1.cookies)

    params3 = "?format=json&action=query&meta=tokens&continue="
    r3 = requests.post(baseurl+"api.php"+params3, cookies=r2.cookies)
    edit_token = r3.json()["query"]["tokens"]["csrftoken"]

    edit_cookie = r2.cookies.copy()
    edit_cookie.update(r3.cookies)

    # save action
    headers = {"content-type": "application/x-www-form-urlencoded"}
    payload = {"action": "edit",
               "assert": "user",
               "format": "json",
               "text": text,
               "summary": "Generated index",
               "title": "The big ebook index",
               "token": edit_token
               }
    r4 = requests.post(baseurl+'api.php',
                       headers=headers, data=payload, cookies=edit_cookie)
    print(r4.json()["edit"]["result"])
