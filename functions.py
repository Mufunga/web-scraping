import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
BOOK_SITE ="https://books.toscrape.com/"
CSV_DIR= "C:/Users/MufungaK/Documents/OC/LIVRAIBLE/projet_2/data/csv"
IMG_DIR = "C:/Users/MufungaK/Documents/OC/LIVRAIBLE/projet_2/data/img"
#os.mkdir(path)
#print(path)

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
     


    
    
    
        #names_of_categories.append(categories_names)

    





def main():

    """Main function"""
    """create my CSV directory"""
    Path(CSV_DIR).mkdir(parents=True, exist_ok=True)


    # Récupération de toutes les catés
    categories_urls = get_categories_urls()
    categories_urls.remove('https://books.toscrape.com/catalogue/category/books_1/index.html')


    # Pour chaque catégorie
    for category_url in categories_urls:

    #    Récupérer les urls de tous les livres de la catégorie
        books_urls_by_category = get_books_urls_from_category(category_url)
    #    Pour chaque urls des livres
        for url_book in books_urls_by_category:
    #        Récupérer les data de chaque livre
            all_books_data = scrape_book(url_book)
            print (all_books_data)

    #    Sauvegarder en csv
    #rows = [scrape_book(url)]
    with open('C:/Users/MufungaK/Documents/OC/LIVRAIBLE/projet_2/csv_dir/cat_data_book4.csv', mode='w', encoding="utf-8") as csv_file:
            headers = ["url", "title", "upc", "price_including_tax", "price_excluding_tax", "number_available","product_description","category",  "review_rating",  "image_url"]

            writer = csv.DictWriter(csv_file, fieldnames=headers,delimiter=',')

            writer.writeheader()
            writer.writerows(all_books_data)
    #data_book_csv()

    #    Récupérer les images

#link_categories_books= get_categories_urls()
#print(link_categories_books)

#url = "https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html"

#if "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"  in link_categories_books:
  #cat_url ="https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"
  #cat_books_urls=get_books_urls_from_category(cat_url)
  #cat_books_data=[]
#for url in cat_books_urls:
   #cat_books_data.append(scrape_book(url))
    #print(cat_books_data)



#if __name__ == "__main__":

    #main()
    
#data_book_csv()



#print(link_categories_books)
   #print(all_books_url)
    


#page_url = "https://books.toscrape.com/catalogue/category/books_1/index.html"
#category_urls = scrape_category_books(page_url)
#print(category_urls)
#for link_url in category_urls:
   # scrape_book(link_url)
    #break
   #print(link_url)

