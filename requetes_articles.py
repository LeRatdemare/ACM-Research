import requests
from bs4 import BeautifulSoup



################################### INPUTS HERE ###################################



after_month = 1
after_year = 2000
before_month = 5
before_year = 2024
requete = '(collaboration OR teamwork OR "remote collaboration" OR "distance collaboration") AND (asymmetric OR dissimilar OR differential) AND (interaction OR system)'
### Attention, la combinaison de ces deux filtres peut fausser les résultats
filtre_ACM = False
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



def get_page_content(url):
    response = requests.get(url)
    page_content = response.text
    return page_content

def convert_to_http_chars(string):
    for char in http_chars:
        string = string.replace(char, http_chars[char])
    return string

def create_random_request(vocabulaire, requete):
    separators = [' AND ', ' OR ', ' NOT ']
    # La requête est une liste de 3 termes 


################################### MAIN ###################################



# url construction
http_chars = {':': '%3A', '(': '%28', ')': '%29', ' ': '+', "'": '%22', }
base_url = f"https://dl.acm.org/action/doSearch?fillQuickSearch=false&target=advanced&expand=dl&AfterMonth={after_month}&AfterYear={after_year}&BeforeMonth={before_month}&BeforeYear={before_year}&AllField="
requete = "Abstract:(" + requete + ")"
all_field = convert_to_http_chars(requete)
if articles_uniquement:
    all_field += "&ContentItemType=research-article"
if filtre_ACM:
    all_field += "&startPage=&SponsorAcronymRaw=acm"

# Soup
soup = BeautifulSoup(get_page_content(base_url+all_field), 'html.parser')
formatted_request = soup.title.text
nb_results = int(soup.find('span', {'class': 'hitsLength'}).text.replace(',', ''))
# print
print("-------------------\n")
print(f"Request: {formatted_request}\n")
print(f"Number of results: {nb_results}")

# print(soup.prettify())
# a_tags = soup.find_all('a')
# for a in a_tags:
#     print(a.get('href'))
#     print(a.text)
#     print('-------------------')