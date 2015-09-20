# -*- coding: utf-8 -*-
import os

from ThreadFinder import scrape_all


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
        self.books = []

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
        return rest

    def match(self, book_name):
        """Check whether our book matches the category.
        """
        for tag in self.tags:
            if tag in book_name.lower().split(" "):
                return True
        return False

    def print_it(self):
        header = "=" * self.level
        print(header + " " + self.name + " " + header)
        for book in self.books:
            book.print_it()
        for child in self.children:
            child.print_it()

if __name__ == "__main__":
    cat = Category("Books")
    books = scrape_all()
    rest = cat.sort_books(books)
    cat.print_it()
    print("= Misc =")
    for book in rest:
        book.print_it()
