import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from slugify import slugify

BOOK_SITE ="https://books.toscrape.com/"
CSV_DIR= "data/csv"
IMG_DIR = "data/img"

def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    if not response.ok:
        print("erreur")
        exit()
    content = response.content
    return BeautifulSoup(content, "html.parser")


def get_categories_urls():
    category_uls = []
    soup = get_soup(BOOK_SITE)
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
        soup = get_soup(category_url)
        link_book_categories = soup.find("ol")
        articles = link_book_categories.find_all("article", class_="product_pod")
        for article in articles:
            lien = article.find("a")["href"]
            chemin = lien.split("../")
            book_url = "https://books.toscrape.com/catalogue/" + chemin[3]
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
    
    soup = get_soup(book_urls)
    td_list = soup.find_all("td")
    book_data = {}
    book_data ["title"]=soup.h1.text
    book_data ["upc"]=td_list[0].text
    book_data ["price_including_tax"]=td_list[3].text
    book_data ["price_excluding_tax"]=td_list[2].text
    book_data["number_available"] = td_list[5].text
    instock_split = book_data["number_available"].split()
    split_availlable = slugify(instock_split[2])
    book_data["number_available"] = split_availlable
    p_list=soup.find_all('p')
    book_data['product_description']=p_list[3].text
    a_list= soup.find_all("a")
    book_data["category"]= a_list[3].text
    book_data["review_rating"]= soup.find ("p",class_="star-rating").attrs["class"] [1]
    book_data["review_rating"] = transform_review_rating_to_number( book_data["review_rating"])
    book_data ["image_url"] = soup.find('img')["src"]
    url_split= book_data["image_url"].split("../")
    book_data ["image_url"] = "https://books.toscrape.com/"+ url_split[2]
    return book_data

def transform_review_rating_to_number(review_rating: str) -> int:

    """Transform a rating string to rating number"""
    rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return rating.get(review_rating, "Valeur Inexistante")



def image_down(book_data :list[dict]):
    title =slugify (book_data.get("title"))
    image_url = book_data.get("image_url")
    image_path = image_url
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
            print(book_data["category"] + '  ' "data book  encours de telechargement veuillez patientez...")
            
    #    Sauvegarder en csv
        save_book_data_to_csv(books_data)
        print(book_data["category"] + '  ' "data book  enregister sous format CSV veuillez patienter...")

        #Boucle de recuperation de l'image et sauvegarde

        for book in books_data:
            image_down(book)
           


if __name__ == "__main__":
    main()
    