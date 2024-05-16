import requests
from bs4 import BeautifulSoup
import datetime
import time



################################### INPUTS HERE ###################################



after_month = 1
after_year = 2000
before_month = datetime.datetime.now().month
before_year = datetime.datetime.now().year
requete = '(collaboration OR teamwork OR "remote collaboration" OR "distance collaboration") AND (asymmetric OR dissimilar OR differential)'
nb_max_results = 10000
### Attention, la combinaison de ces deux filtres peut fausser les résultats
sponsorise_ACM = False
articles_uniquement = False


# class Requete:
#     def __init__(self, terme1, separateur, terme2):
#         self.terme1 = terme1
#         self.separateur = separateur
#         self.terme2 = terme2
#     def combine(self, separateur:str, requete2)->Requete:
#         pass
    
#     def __str__(self):
#         return f"{self.terme1} {self.separateur} {self.terme2}"
        


################################### FUNCTIONS ###################################

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time} seconds\n")
        return result
    return wrapper

@timer_decorator
def get_page_content(url):
    response = requests.get(url)
    page_content = response.text
    return page_content

def convert_to_http_chars(string):
    for char in http_chars:
        string = string.replace(char, http_chars[char])
    return string



################################### MAIN ###################################



# url construction
http_chars = {':': '%3A', '(': '%28', ')': '%29', ' ': '+', "'": '%22', }
base_url = f"https://dl.acm.org/action/doSearch?pageSize={nb_max_results}&fillQuickSearch=false&target=advanced&expand=dl&AfterMonth={after_month}&AfterYear={after_year}&BeforeMonth={before_month}&BeforeYear={before_year}&AllField="
requete = "Abstract:(" + requete + ")"
all_field = convert_to_http_chars(requete)
if articles_uniquement:
    all_field += "&ContentItemType=research-article"
if sponsorise_ACM:
    all_field += "&startPage=&SponsorAcronymRaw=acm"

# Soup
soup = BeautifulSoup(get_page_content(base_url+all_field), 'html.parser')
formatted_request = soup.title.text
failed_to_get_nb_results = False
try:
    nb_results = int(soup.find('span', {'class': 'hitsLength'}).text.replace(',', ''))
except:
    nb_results = -1
    failed_to_get_nb_results = True

# On peut également une liste d'informations sur chaque article
articles_lis = soup.find_all('li', {'class': 'search__item issue-item-container'})
articles = []
for article_li in articles_lis:
    article = {}
    try:
        article['title'] = 'https://dl.acm.org'+article_li.find('span', {'class': 'hlFld-Title'}).a['href']
    except:
        article['title'] = 'No title'
    try:
        article['author1'] = article_li.find('span', {'class': 'hlFld-ContribAuthor'}).a.span.text
    except:
        article['author1'] = 'No author'
    print(f"{article['title']} ===> {article['author1']}")
    articles.append(article)

# print
print("-------------------\n")
print(f"Request: {formatted_request}\n")
if failed_to_get_nb_results:
    print("Failed to get the number of results")
else:
    print(f"Number of results: {nb_results}")
print("Number of articles on page: ", len(articles))

# print(soup.prettify())
# a_tags = soup.find_all('a')
# for a in a_tags:
#     print(a.get('href'))
#     print(a.text)
#     print('-------------------')

"""
TODO :
1) Récupérer dans un CSV/json/etc... :
    - Titre du papier
    - 1er auteur
    - Date de publication
    - DOI
    - Abstract
    - Lien vers le papier
    - Les mots-clés
    - (références ?)
2) Adapter le code pour pouvoir faire des requêtes sur d'autres sites (Google Scholar API, etc...)
3) Créer une interface graphique pour entrer les requêtes
4) Comprendre le doSearch de ACM -> action="/action/doSearch" 
    - select => name="expand" ; option values: ["dl","all"]
    - select => name="field1" ; option values: ["Abstract","DOI","AllField"]
    - input => name="text1" ; value="ma requete"
    - select => name="searchArea[0]" ; option values: ["SeriesKey"]
    - select => name="operator[0]" ; option values: ["And"]
    - input => name="text[0]" ; value="ACM"
    - radio => name="EpubDate" ; value=true or false
5) Fonction score
    - Nombre de résultats
    - 1er auteurs qui reviennent le plus dans les résultats
    - Date moyenne des résultats
    - Metrics (total downloads, total citations)
""" 