import requests
from bs4 import BeautifulSoup
import datetime
import time
import csv
from time import sleep

# import semantic_tree as st



################################### INPUTS HERE ###################################



after_month = 1
after_year = 1990
before_month = datetime.datetime.now().month
before_year = datetime.datetime.now().year
# requete = '((collaboration OR system) AND interactiveness) AND NOT (((((((batman AND thanos) OR batman) OR villains) OR (((joker OR batman) OR iron-man) OR batman)) OR (iron-man AND joker)) OR (((super-hero AND (thanos AND joker)) OR super-hero) AND (((villains OR (((batman OR iron-man) OR joker) AND (iron-man AND batman))) OR joker) AND (batman AND batman)))) AND joker)'
requete = '(collaboration OR teamwork OR collaborative OR collaborator) AND '
requete += '(asymmetric OR asymmetrical OR mixed OR different OR dissimilar OR incongruent OR unequal OR unmatched OR heterogeneous OR unsymmetrical OR unsymmetric) AND '
requete += '(device OR prototype OR system)'

nb_max_results_to_display = 20 # Plus ce nombre est grand, plus la requête sera longue à s'exécuter
### Attention, la combinaison de ces deux filtres peut fausser les résultats
sponsorise_ACM = False
articles_uniquement = False



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

def get_nb_pages(nb_results, nb_results_per_page):
    return (nb_results // nb_results_per_page) + 1

def get_page_content(url):
    response = requests.get(url)
    page_content = response.text
    return page_content

@timer_decorator
def get_page_content(url):
    response = requests.get(url)
    page_content = response.text
    return page_content

def replace_http_chars(string: str, http_chars: dict[str, str]):
    """
    Remplace les caractères spéciaux d'une string par leur équivalent en URL.

    :pre: http_chars est un dictionnaire de la forme {':': '%3A', '(': '%28', ')': '%29', ' ': '+', "'": '%22', }
    :return: la string avec les caractères spéciaux remplacés
    """
    for char in http_chars:
        string = string.replace(char, http_chars[char])
    return string

def construct_ACM_url(requete: str, nb_max_results_per_page=10, start_page=0, after_month=1, after_year=2000, before_month=datetime.datetime.now().month, before_year=datetime.datetime.now().year, sponsorise_ACM=False, articles_uniquement=False, http_chars: dict[str, str]={}):
    """ 
    Construit l'url pour faire une requête sur ACM à partir d'une requête ne contenant que les opérateurs AND, OR et NOT.
    
    :pre: requete est une string de la forme "(collaboration OR teamwork) AND (asym* or dissimilar) AND NOT (batman)"
    :return: l'url de la requête get tel qu'il aurait été généré par ACM DL
    """
    base_url = f"https://dl.acm.org/action/doSearch?pageSize={nb_max_results_per_page}&fillQuickSearch=false&target=advanced&expand=dl&AfterMonth={after_month}&AfterYear={after_year}&BeforeMonth={before_month}&BeforeYear={before_year}"
    requete = "Abstract:(" + requete + ")"
    all_field = "&AllField="+replace_http_chars(requete, http_chars)
    if articles_uniquement:
        base_url += "&ContentItemType=research-article"
    if sponsorise_ACM:
        base_url += "&SponsorAcronymRaw=acm"
    if start_page > 0:
        base_url += f"&startPage={start_page}"
    
    return base_url + all_field

### Récupération des infos avec BeautifulSoup4

def get_general_infos(soup: BeautifulSoup):
    """
    Récupère les informations générales sur la requête
    :pre: soup est l'objet contentant le contenu de la page
    :return: formatted_request, nb_results (-1 si non trouvé)
    """
    general_infos = {}
    # Requête au format ACM
    general_infos['formatted_request'] = soup.title.text
    # Nombre de résultats
    nb_results = soup.find('span', {'class': 'hitsLength'})
    if nb_results is None:
        nb_results = -1
    else:
        nb_results = int(nb_results.text.replace(',', ''))
    general_infos['nb_results'] = nb_results
    # Articles
    articles_lis = soup.find_all('li', {'class': 'search__item issue-item-container'})
    articles = []
    for article_li in articles_lis:
        info_block = article_li.find('div', {'class': 'issue-item__content'})
        article = {}
        try:
            article['doi'] = 'https://dl.acm.org'+article_li.find('span', {'class': 'hlFld-Title'}).a['href']
        except:
            article['doi'] = 'No doi'
        try:
            article['author1'] = article_li.find('span', {'class': 'hlFld-ContribAuthor'}).a.span.text
        except:
            article['author1'] = 'No author'
        try:
            article['title'] = info_block.find('a').text
        except:
            article['title'] = 'No title'
        
        item_detail = info_block.find('div', {'class': 'issue-item__detail'})
        try:
            article['publisher'] = item_detail.find('span').text
        except:
            article['publisher'] = 'No publisher'

        item_citations = article_li.find('div', {'class': 'issue-item__citation'}).find_all('div')
        try:
            article['date'] = item_citations[1].text
        except:
            article['date'] = 'No date'
        try:
            article['type'] = item_citations[0].text
        except:
            article['type'] = 'No date'

        articles.append(article)
    general_infos['articles'] = articles

    return general_infos

def display_general_infos(general_infos: dict):
    for article in general_infos['articles']:
        print(f"{article['title']} ===> {article['author1']} ===> {article['date']}")
    print("\n"+general_infos['formatted_request'])
    print(f"Nombre total de résultats: {general_infos['nb_results']}" if general_infos['nb_results'] != -1 else "Nombre de résultats indisponible")
    print(f"Nombre d'articles affichés: {len(general_infos['articles'])}")

def save_general_infos(general_infos: dict, path: str, mode='w'):
    with open(path, mode, newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        if mode == 'w':
            csv_writer.writerow(['Title', 'Author1', 'Date', 'Publisher', 'DOI'])
        for article in general_infos['articles']:
            csv_writer.writerow([article['title'], article['author1'], article['date'], article['publisher'], article['doi'], article['type']])

# def calculate_request_score(request: st.RequestTree) -> int:
#     """
#     Renvoie le score d'une requête
#     """
#     tree_size = len(request)
#     size_diff = len(request.get_include_tree()) - len(request.get_exclude_tree())
#     size_diff_squared = size_diff**2
#     inv_size_diff_squared = 1 / (1 + size_diff_squared) # +1 pour éviter la division par 0
#     return (tree_size)



################################### MAIN ###################################



# url construction
http_chars = {':': '%3A', '(': '%28', ')': '%29', ' ': '+', "'": '%22', }
url = construct_ACM_url(requete=requete, nb_max_results_per_page=nb_max_results_to_display, after_month=after_month, after_year=after_year, before_month=before_month, before_year=before_year, sponsorise_ACM=sponsorise_ACM, articles_uniquement=articles_uniquement, http_chars=http_chars)
print(requete)
print(url)

# récupération du contenu de la page
page_content = get_page_content(url)
soup = BeautifulSoup(page_content, 'html.parser')

# récupération des infos générales
general_infos = get_general_infos(soup)
display_general_infos(general_infos)
save_general_infos(general_infos, 'articles2.csv', mode='w')

for i in range(1, get_nb_pages(general_infos['nb_results'], nb_max_results_to_display)):
    url = construct_ACM_url(requete=requete, nb_max_results_per_page=nb_max_results_to_display, start_page=i, after_month=after_month, after_year=after_year, before_month=before_month, before_year=before_year, sponsorise_ACM=sponsorise_ACM, articles_uniquement=articles_uniquement, http_chars=http_chars)
    print(url)
    page_content = get_page_content(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    general_infos = get_general_infos(soup)
    display_general_infos(general_infos)
    save_general_infos(general_infos, 'articles2.csv', 'a')
    sleep(30)

# included_node = st.Node("collaboration", [], st.INCLUDED_VOCABULARY)
# excluded_node = st.Node("batman", [], st.EXCLUDED_VOCABULARY)
# initial_request = st.RequestTree(included_node, excluded_node)
# req = st.generate_best_request_genetic_algorithm(calculate_request_score, initial_request, nb_generations=25, population_size=100)

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
2) Adapter le code :
    - Pour pouvoir faire des requêtes sur d'autres sites (Google Scholar API, etc...)
    - Empêcher que le même mot soit utilisé plusieurs fois dans la requête
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