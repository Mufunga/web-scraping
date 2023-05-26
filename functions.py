import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from slugify import slugify

BOOK_SITE ="https://books.toscrape.com/"
CSV_DIR= "data/csv"
IMG_DIR = "data/img"


def get_categories_urls():
    category_uls = []
    response = requests.get(BOOK_SITE)
    page_cat = response.content
    soup = BeautifulSoup(page_cat, "html.parser")
    ul_tag = soup.find("ul", class_="nav-list")
    li_tag = ul_tag.find_all("li")
    for ligne in li_tag:
        a_tag = ligne.find("a")["href"]
        les_urls_cat = "https://books.toscrape.com/" + a_tag
        category_uls.append(les_urls_cat)
    return category_uls


def get_books_urls_from_category(category_url):
    """Return the books urls_from_category"""
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
            #print (book_urls)
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

def scrape_book(book_urls):
    reponse = requests.get(book_urls)
    page = reponse.content
    soup = BeautifulSoup(page, "html.parser")
    td_list = soup.find_all("td")
    book_data = {}
    book_data ["title"]=soup.h1.text
    book_data ["upc"]=td_list[0].text
    book_data ["price_including_tax"]=td_list[3].text
    book_data ["price_excluding_tax"]=td_list[2].text
    book_data["number_available"] = td_list[5].text
    p_list=soup.find_all('p')
    book_data['product_description']=p_list[3].text
    a_list= soup.find_all("a")
    book_data["category"]= a_list[3].text
    book_data["review_rating"]= soup.find ("p",class_="star-rating").attrs["class"] [1]
    book_data ["image_url"] = soup.find('img')["src"]
    return book_data



def image_down(book_data :list[dict]):
    title =slugify (book_data.get("title"))
    image_url = book_data.get("image_url")
    image_path = "https://books.toscrape.com/" + image_url
    rep =requests.get(image_path)

    with open(f"{IMG_DIR}/{title}.jpeg", "wb") as img_file:
            img_file.write(rep.content)
            img_file.close
        
        
def save_book_data_to_csv(book_data:list[dict]):

    header = book_data[0].keys()
    category = slugify (book_data[0].get("category"))
    with open(f"{CSV_DIR}/{category}.csv", mode="w", encoding= "utf-8-sig", newline="") as file_csv:
        writer= csv.DictWriter(file_csv, fieldnames= header,dialect= "excel")
        writer.writeheader()
        writer.writerows(book_data)
    


def main():

    """Main function"""

    # Récupération de toutes les catés
    categories_urls = get_categories_urls()
    categories_urls.remove('https://books.toscrape.com/catalogue/category/books_1/index.html')

    Path(CSV_DIR).mkdir(parents=True, exist_ok=True)
    Path(IMG_DIR).mkdir(parents=True, exist_ok=True)

    # Pour chaque catégorie
    for category_url in categories_urls:

    #    Récupérer les urls de tous les livres de la catégorie
        books_urls_by_category = get_books_urls_from_category(category_url)
    #    Pour chaque urls des livres
        books_data: list = []
        for url_book in books_urls_by_category:
    #        Récupérer les data de chaque livre
            book_data = scrape_book(url_book)
            books_data.append(book_data)
            
    #    Sauvegarder en csv
        save_book_data_to_csv(books_data)

        #Boucle de recuperation de l'image et sauvegarde

        for book in books_data:
            image_down(book)
           


if __name__ == "__main__":
    main()