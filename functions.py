import requests
from bs4 import BeautifulSoup
import csv


def scrape_book(book_url):
    reponse = requests.get(url)
    page = reponse.content
    soup = BeautifulSoup(page, "html.parser")
    td_list = soup.find_all("td")
    book_data = {"url": book_url, "title": soup.h1.text, "upc": td_list[0].text, "price_including_tax": td_list[3].text,
                 "price_excluding_tax": td_list[2].text, "number_available": td_list[5].text}
    p_list = soup.find_all("p")
    book_data["product_description"] = p_list[3].text
    a_list = soup.find_all("a")
    book_data["category"] = a_list[3].text
    book_data["review_rating"] = soup.find("p", class_="star-rating").attrs["class"][1]
    book_data["image_url"] = soup.find("img")["src"]
    return book_data


url = "https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html"

def data_book_csv():
    rows = [scrape_book(url)]
    with open('live_data.csv', mode='w') as csv_file:
        fieldnames = ["url", "title", "upc", "price_including_tax", "price_excluding_tax", "number_available","product_description","category",  "review_rating",  "image_url"]

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames,deliiter=',')

        writer.writeheader()
        writer.writerow(scrape_book(url))
#data_book_csv()
book_site = "https://books.toscrape.com/"
def scrape_category_uls():
    category_uls = []
    response = requests.get(book_site)
    page_cat = response.content
    soup = BeautifulSoup(page_cat, "html.parser")
    ul_tag = soup.find("ul", class_="nav-list")
    li_tag = ul_tag.find_all("li")
    for ligne in li_tag:
        a_tag = ligne.find("a")["href"]
        les_urls_cat = "https://books.toscrape.com/" + a_tag
        category_uls.append(les_urls_cat)
    return category_uls
link_categories_books= scrape_category_uls()
#print(link_categories_books)

def scrape_category_books(category_url):
    book_urls = []
    a_tag_temp = "index.html"
    while True:
        response = requests.get(category_url)
        book_page = response.content
        soup = BeautifulSoup(book_page, "html.parser")
        link_book_categories = soup.find("ol")
        articles = link_book_categories.find_all("article", class_="product_pod")
        for article in articles:
            lien = article.find("a")["href"]
            chemin = lien.split("../")
            book_url = "https://books.toscrape.com/catalogue/" + chemin[3]
            print (book_urls)
            book_urls.append(book_url)
        next_b = soup.find("li", class_="next")
        if next_b:
            a_tag = next_b.find("a")["href"]
            next_url_page = category_url.replace(a_tag_temp, a_tag)
            a_tag_temp = a_tag
            category_url = next_url_page
        else:
            break
    return book_urls
for links in link_categories_books:
    scrape_category_books(links)
    


#page_url = "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"
#category_urls = scrape_category_books(page_url)
#for link_url in category_urls:
   # scrape_book(link_url)
    #break
   # print(link_url)