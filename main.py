import requests
from bs4 import BeautifulSoup
import time
import json
import re

start = time.time()
count = 0

URL = 'https://www.empik.com/ksiazki,31,s?hideUnavailable=true&sort=scoreDesc&resultsPP=60'
print(URL)
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find_all('div', class_="search-content js-search-content")


class Book:
    description = ""
    title = ""
    authors = []
    image = ""

    def __init__(self, id, category, is_top, link):
        self.id = id
        self.category = category
        self.is_top = is_top
        self.link = link

    def set_description(self, description):
        self.description = description

    def set_title(self, title):
        self.title = title

    def set_authors(self, authors):
        self.authors = authors

    def set_image(self, image):
        self.image = image

    def as_json(self):
        return dict(
            id=self.id,
            title=self.title,
            category=self.category,
            is_top=self.is_top,
            link=self.link,
            description=self.description,
            authors=self.authors,
            image=self.image)


def get_books(results, count, file):
    book_list = []
    for result in results:
        books = result.find_all('div', class_="search-list-item js-reco-product ta-product-tile")
        for book in books:
            id = book["data-product-id"]
            category = book["data-product-category"].split("/")[1:]
            is_top = book.find('div', class_="ribbon ta-ribbon ribbon--bestseller") is not None
            link = "https://www.empik.com" + book.find('a')["href"]
            book_object = Book(id, category, is_top, link)
            book_list.append(book_object)

    for book in book_list:
        page = requests.get(book.link)
        soup = BeautifulSoup(page.content, 'html.parser')
        tab = soup.find('section', class_="cssTabs__content cssTabs__content--1")
        book.set_description(tab.text.strip().replace("\n", " "))
        title_details = soup.find_all('div', class_="col-xs-12 col-md-5 col-lg-5 pull-left cover-aside")
        for det in title_details:
            details = det.find_all('div', class_="productBaseInfo")
            for info in details:
                title = info.find("h1", class_="productBaseInfo__title ta-product-title").text.strip().replace("\n",
                                                                                                               "").replace(
                    "(okładka", "").replace("twarda)", "").replace("miękka)", "").strip()
                authors_details = info.find_all("div", class_="productBaseInfo__subtitle")
                for det in authors_details:
                    authors = det.find('span')
                    authors = authors["content"].strip().replace(u"\xa0", u" ").split(";")
                    book.set_authors(authors)

                book.set_title(title)
        img_details = soup.find_all('div', class_="image")
        for img in img_details:
            image = img.find("img")["lazy-img"]
            book.set_image(image)

        pretty = json.dumps(book.as_json(), ensure_ascii=False, indent=4, sort_keys=True)
        file.write(pretty)
        file.write(",\n")
        count = count + 1
        print(count, book.title)

    return book_list, count


with open('books.json', 'a', encoding="utf-8") as file:
    file.write("[")
    fetched, count = get_books(results, count, file)

    for i in range(2101, 67741, 60):
        URL = 'https://www.empik.com/ksiazki,31,s,%s?hideUnavailable=true&sort=scoreDesc&resultsPP=60' % i
        print(URL)
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find_all('div', class_="search-content js-search-content")
        fetched, count = get_books(results, count, file)

    file.write("]")

end = time.time()
print(end - start)
print(count)
