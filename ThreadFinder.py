import requests
from bs4 import BeautifulSoup


def scrape(n):
    """get all threads from a forum page.
    """
    thread_urls = []
    page_urls = []
    url = "http://www.evilzone.org/ebooks/" + str(n)
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for link in soup.find_all("a"):
        url = link.get("href")
        if url:
            if check_url(url):
                thread_urls.append(Book(link.text, url[:url.find("?")]))
            if check_page_url(url):
                page_urls.append(url)
    return (thread_urls, page_urls[-1])


def scrape_all():
    """Get all potentially relevant threads from the ebook board.
    """
    threads = []
    num_page = 0
    last_url = ""
    while ("/ebooks/" + str(num_page)) not in last_url:
        ts, last_url = scrape(num_page)
        # print "Current: " + str(num_page)
        threads += ts
        num_page += 25
    ts, last_url = scrape(num_page)
    return threads + ts


def check_url(url):
    """Ugly checking whether we really want that url.
    """
    return "/ebooks/" in url and \
        "#new" not in url and \
        "#msg" not in url and \
        "sort" not in url and \
        "ebook-request-topic" not in url and \
        "board-rules" not in url and \
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
        print("* [" + self.link + " " + self.name + "]")

if __name__ == '__main__':
    for i in scrape_all():
        i.print_it()