# -*- coding: utf-8 -*-
from robobrowser import RoboBrowser
from robobrowser.forms.form import Form

import Database


def scrape(browser, n):
    """get all threads from a forum page.
    """
    thread_urls = []
    page_urls = []
    url = "http://www.evilzone.org/ebooks/" + str(n)
    browser.open(url)
    for link in browser.find_all("a"):
        url = link.get("href")
        if url:
            if check_url(url):
                thread_urls.append(Book(link.text, url[:url.find("?")]))
            if check_page_url(url):
                page_urls.append(url)
    return (thread_urls, page_urls[-1])


def login():
    """Login to evilzone and return a browser object.
    """
    browser = RoboBrowser(history=True)
    browser.open('https://www.evilzone.org/login')
    form = browser.get_form(0)
    assert isinstance(form, Form)

    form["user"] = input("EZ Username: ")
    form["passwrd"] = input("Password: ")

    browser.submit_form(form)
    return browser


def scrape_all():
    """Get all potentially relevant threads from the ebook board.
    """
    browser = login()
    threads = []
    num_page = 0
    last_url = ""
    while ("/ebooks/" + str(num_page)) not in last_url:
        ts, last_url = scrape(browser, num_page)
        print("Current: " + str(num_page))
        threads += ts
        num_page += 25
    ts, last_url = scrape(browser, num_page)
    threads += ts
    Database.insert_books(threads)


def scrape_recent():
    """Get all new threads from the ebook board.
    """
    # TODO: develop a more sophisticated mechanism instead of just
    # downloading the first page.
    print("Downloading last page...")
    browser = login()
    threads = scrape(browser, 0)[0]
    return Database.insert_books(threads)


def check_url(url):
    """Ugly checking whether we really want that url.
    """
    return "/ebooks/" in url and \
        "#new" not in url and \
        "#msg" not in url and \
        "sort" not in url and \
        "ebook-request-topic" not in url and \
        "board-rules" not in url and \
        "general-rules" not in url and \
        "searching-for-ebooks" not in url and \
        "ebook-index" not in url and \
        "/ebooks/?" not in url and \
        not check_page_url(url)


def check_page_url(url):
    """Ugly checking whether we see a page url.
    """
    start = url.find("/ebooks/")
    if start == -1:
        return False
    start += 8
    end = url.find("/", start)
    return url[start:end].isdigit()


class Book(object):
    """A book, as uploaded to EZ.
    """
    def __init__(self, name, dl_link):
        self.name = name
        self.link = dl_link

    def print_it(self):
        """Return a nice representation.
        """
        return "* [" + self.link + " " + self.name + "]\n"
