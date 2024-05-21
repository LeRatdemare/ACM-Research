import random
from vocabulary import Vocabulary
from colorama import Fore
import sympy as sp
from typing import Callable



#################################### CONSTANTES ####################################



### VOCABULARY ###
INCLUDED_VOCABULARY:Vocabulary = Vocabulary.load("data/included_vocabulary.json")
EXCLUDED_VOCABULARY:Vocabulary = Vocabulary.load("data/excluded_vocabulary.json")
# Merge dictionaries into one
VOCABULARY = INCLUDED_VOCABULARY + EXCLUDED_VOCABULARY

### PROBABILITIES ###
KEEP_SIMILAR_WORD_PROBA = 0.7
ALTER_STRUCTURE_PROBA = 0.5
GROW_PROBA = 0.5



#################################### CLASSES ####################################



class Node:
    """ Un nœud de l'arbre syntaxique """

    def __init__(self, value, children: list, vocabulary: Vocabulary):
        """
        :pre: value est un str ou un int. children est une liste de Node. Le nœud résultant est valide.
        """
        self.value = value
        self.children = children
        self.vocabulary = vocabulary
        assert self.is_valid()

    def is_leaf(self):
        """
        :pre: -
        :return: True si le nœud courant est une feuille. False sinon.
        """
        return len(self.children) == 0

    def is_operation(self):
        """
        :pre: -
        :return: True si le nœud courant représente une opération valide. False sinon.
        """
        if len(self.children) == 2:
            return self.value in {"AND", "OR"}
        elif len(self.children) == 1:
            return self.value == "NOT"
        else:
            return False

    def is_valid(self):
        """
        :pre: -
        :return: True si le nœud (et ses enfants, récursivement) est valide. False sinon.
        """
        # if not self.is_variable() and not self.is_constant() and not self.is_operation():
        if not self.is_leaf() and not self.is_operation():
            return False
        for child in self.children:
            if not child.is_valid():
                return False
        return True
    
    def alter_value(self):
        """
        Modifie aléatoirement de la valeur du noeud
        :pre: -
        :return: None
        """
        # Si le nœud est une feuille, on le remplace par une feuille aléatoire
        if self.is_leaf():
            # On choisit aléatoirement soit un synonyme
            if random.random() < KEEP_SIMILAR_WORD_PROBA:
                self.value = random.choice(list(self.vocabulary.get_similar_words(self.value)))
            # Soit un mot aléatoire
            else:
                # On choisit un mot différent du vocabulaire
                self.value = random.choice([word for word in self.vocabulary.get_words() if word != self.value])
        # Si le nœud est une opération, on l'inverse
        else:
            self.value = "AND" if self.value == "OR" else "OR"
        assert self.is_valid()
    
    def alter_structure(self, grow_proba=GROW_PROBA, log=False):
        """
        Modifie aléatoirement la structure de l'arbre
        :pre: -
        :return: None
        """
        # Si le nœud est une feuille, on le remplace par une opération
        if self.is_leaf():
            # Le 1er enfant est l'ancienne valeur et le second est mot aléatoire différent de la valeur
            self.children = [Node(self.value, [], self.vocabulary), Node(random.choice([word for word in self.vocabulary.get_words() if word != self.value]), [], self.vocabulary)]
            self.value = random.choice(["AND", "OR"])
            if log:
                print("Growing...")
        # Si le nœud est une opération
        else:
             # On a une proba qu'il grandisse
            if random.random() < grow_proba:
                if log:
                    print("Growing...")
                self.children = [Node(self.value, self.children, self.vocabulary), Node(random.choice([word for word in self.vocabulary.get_words() if word != self.value]), [], self.vocabulary)]
                self.value = random.choice(["AND", "OR"])
            
            # On a une proba qu'il rétrécisse
            else:
                child_to_keep = random.choice(self.children)
                if log:
                    print("Shrinking...")
                    print("Child to keep:", child_to_keep)
                self.children = child_to_keep.children
                self.value = child_to_keep.value
        assert self.is_valid()
    
    def get_all_nodes(self):
        """
        :pre: -
        :return: Une liste de tous les nœuds de l'arbre contenant l'arbre lui-même
        """
        return [self] + [c for child in self.children for c in child.get_all_nodes()]

    def get_random_node(self):
        """
        :pre: -
        :return: Un nœud aléatoire de l'arbre (y compris lui-même)
        """
        if self.is_leaf():
            return self
        return random.choice(self.get_all_nodes())

    def alter_random_node(self, structure_proba=ALTER_STRUCTURE_PROBA, log=False):
        """
        Modifie aléatoirement un nœud de l'arbre
        :pre: -
        :return: None
        """
        node = self.get_random_node()
        if log:
            print(f"Altering node [{node}]...")
        if random.random() < structure_proba:
            node.alter_structure(log=log)
            if log:
                print(f"Altered structure...")
        else:
            node.alter_value()
            if log:
                print(f"Altered value...")

    def to_request(self):
        """
        :pre: -
        :return: La représentation de l'arbre correspondant à une requête de navigateur
        """
        if self.is_leaf():
            if Vocabulary.is_word(self.value):
                return self.value
            else:
                return '"' + self.value + '"'
        if self.is_operation():
            if self.value == "NOT":
                return f"NOT {self.children[0].to_request()}"
            return f"({self.children[0].to_request()} {self.value} {self.children[1].to_request()})"
    
    def get_sympy_symbols(self) -> dict[str, sp.Symbol]:
        """
        :pre: -
        :return: Un dictionnaire de tous les termes de l'arbre et de leur équivalent en symboles sympy
        """
        symbols = {}
        for node in self.get_all_nodes():
            if node.is_leaf():
                symbols[node.value] = sp.symbols(node.value.replace(" ", "_"))
        return symbols

    def get_simplified_request(self):
        """
        :pre: -
        :return: La requête correspondant à l'arbre, simplifiée
        """
        sympy_tree = to_sympy(self)
        simplified_sympy = sp.to_cnf(sympy_tree, simplify=True, force=True)
        return sympy_to_request(simplified_sympy)

    def copy(self):
        """
        :pre: -
        :return: Une copie de l'arbre
        """
        return unserialize(serialize(self), self.vocabulary)

    def __repr__(self):
        """ Donne une représentation textuelle et visuelle de l'arbre, pour le debugging """
        out = f"{self.value}"
        for c in self.children:
            c_repr = repr(c).split("\n")
            out += "\n|> " + c_repr[0]
            if len(c_repr) > 1:
                out += "\n" + "\n".join(["|  " + l for l in c_repr[1:]])
        return out

    def __str__(self):
        """ Donne une représentation textuelle et visuelle de l'arbre, pour le debugging """
        # return repr(self)
        return self.to_request()

    def __eq__(self, other):
        """
        :return: True si self et other ont la même structure
        """
        if not isinstance(other, Node):
            return False
        return self.value == other.value and self.children == other.children
    
    def __len__(self):
        """
        :return: Le nombre de nœuds de l'arbre
        """
        return len(self.get_all_nodes())

class RequestTree(Node):
    """
    Arbre dont l'opération est un AND et qui ne contient qu'un seul
    "NOT" à la racine du 2ème enfant.
    """
    def __init__(self, initial_included_node:Node, initial_excluded_node:Node):
        super().__init__("AND", [initial_included_node, Node("NOT", [initial_excluded_node], initial_excluded_node.vocabulary)], initial_included_node.vocabulary + initial_excluded_node.vocabulary)
        # Remarque : Le vocabulaire est de cet arbre n'a pas vraiment d'intérêt
    
    def get_include_tree(self):
        return self.children[0]
    
    def get_exclude_tree(self):
        return self.children[1].children[0]
    
    def alter_random_node(self, structure_proba=ALTER_STRUCTURE_PROBA, log=False):
        """
        Modifie aléatoirement un nœud de l'arbre en évitant de modifier le NOT
        et sans changer la structure de l'arbre. C'est-à-dire que l'on veut garder
        les 2 moitiés bien séparées avec chacune son vocabulaire. Il est cependant
        possible de modifier la valeur de la racine de l'arbre.
        :pre: -
        :return: None
        """
        # Sélection d'un nœud aléatoire
        node = self.get_random_node()
        while node.value == "NOT": # On évite de modifier le NOT
            node = self.get_random_node()
        if log:
            print(f"Altering node [{node}]...")
        # Si le nœud est la racine, on n'autorise que le changement de valeur
        if node==self:
            node.alter_value()
            if log:
                print(f"Altered value...")
        # Sinon, on autorise la modification de la valeur ou de la structure
        elif random.random() < structure_proba:
            node.alter_structure(log=log)
            if log:
                print(f"Altered structure...")
        else:
            node.alter_value()
            if log:
                print(f"Altered value...")

    def to_colored_request(self):
        """
        Renvoie la requête correspondant à l'arbre.
        Affiche la partie "NOT" en rouge et la partie "AND" en vert.
        """
        return Fore.GREEN + self.children[0].to_request() + Fore.BLUE + f" {self.value} " + Fore.RED + self.children[1].to_request() + Fore.RESET

    def apply_alterations(self, nb_alterations=100, log=False):
        for i in range(nb_alterations):
            if log:
                print("\n\n------------------------------"+Fore.YELLOW+f"Requête {i+1}"+Fore.RESET+"------------------------------")
                print("Tree before alteration:",end="")
                print(f"{self}")
            self.alter_random_node(log=log)
            if log:
                print("Tree after alteration:",end="")
                print(f"{self}")
                print("------------------------------"+Fore.YELLOW+f"Requête {i+1}"+Fore.RESET+"------------------------------")

    def copy(self):
        return RequestTree(self.get_include_tree().copy(), self.get_exclude_tree().copy())

    def __str__(self):
        return self.to_colored_request()



#################################### FUNCTIONS ####################################



def serialize(tree: Node) -> str:
    """ Crée une représentation "plate" de l'arbre, via un parcours préfixe
    :pre: tree est une Node valide
    :return: une représentation de l'arbre
    """
    serialized_repr = f"{tree.value},{len(tree.children)}"
    for child in tree.children:
        serialized_repr += ","
        serialized_repr += serialize(child)
    return serialized_repr

def unserialize(serialized_repr, vocabulary: Vocabulary) -> Node: 
    """
    :pre: serialized_repr est une sortie de serialize 
    :return: l'arbre qui a été donné à serialize 
    pour tout arbre X, on doit avoir que X == unserialize(serialize(X)). 
    """

    def calc_size(tree: Node):
        """ Calcule la taille de l'arbre """
        if tree.is_leaf():
            return 1
        return 1 + sum([calc_size(c) for c in tree.children])
    
    def unserialize_rec(serialized_tree, indice):
        val = serialized_tree[indice] #0
        nb_childs = int(serialized_tree[indice+1]) #1 
        indice += 2
        
        if nb_childs == 0: #feuille : noeud avec une liste vide
            return Node(val,[], vocabulary)
                
        children = [] #noeud : noeud avec plusieurs enfants
        
        for _ in range(nb_childs):
            child = unserialize_rec(serialized_tree, indice)
            # On avance de 2 fois la taille de l'enfant car pour chaque noeud et chaque feuille il y a un nombre d'enfants
            indice += calc_size(child)*2
            children.append(child)

        node = Node(val, children, vocabulary)
        return node
            
    return unserialize_rec(serialized_repr.split(',') , 0)

def to_sympy(node: Node):
    """
    :pre: -
    :return: L'expression sympy correspondant à l'arbre
    """
    def to_sympy_rec(node: Node, symbols: dict[str, sp.Symbol]):
        """
        :pre: symbols est un dictionnaire de tous les termes de l'arbre et de leur équivalent en symboles sympy
        :return: L'expression sympy correspondant à l'arbre
        """
        if node.is_leaf():
            return symbols[node.value]
        if node.is_operation():
            if node.value == "NOT":
                return ~to_sympy_rec(node.children[0], symbols)
            if node.value == "AND":
                return to_sympy_rec(node.children[0], symbols) & to_sympy_rec(node.children[1], symbols)
            if node.value == "OR":
                return to_sympy_rec(node.children[0], symbols) | to_sympy_rec(node.children[1], symbols)
    symbols = node.get_sympy_symbols()
    sympy_expr = to_sympy_rec(node, symbols)
    return sympy_expr

def sympy_to_request(expr: sp.Expr)->str:
    """
    :pre: expr est une expression sympy
    :return: La requête correspondant à l'expression sympy
    """
    def sympy_to_request_rec(expr: sp.Expr, symbols: dict[str, sp.Symbol]):
        """
        :pre: symbols est un dictionnaire de tous les termes de la requête et de leur équivalent en symboles sympy
        :return: La requête correspondant à l'expression sympy
        """
        if expr.is_Symbol:
            for symbol in symbols:
                if symbols[symbol] == expr:
                    return symbol
        if isinstance(expr, sp.Not):
            return f"NOT {sympy_to_request_rec(expr.args[0], symbols)}"
        if isinstance(expr, sp.And):
            return "("+' AND '.join(sympy_to_request_rec(arg, symbols) for arg in expr.args)+")"
        if isinstance(expr, sp.Or):
            return "("+' OR '.join(sympy_to_request_rec(arg, symbols) for arg in expr.args)+")"
    symbols = {str(symbol).replace("_", " "): symbol for symbol in expr.free_symbols}
    return sympy_to_request_rec(expr, symbols)

def generate_best_request_genetic_algorithm(score_function: Callable[[RequestTree], int], initial_request:RequestTree, nb_generations=100, population_size=100, nb_max_alterations_per_gen=5, nb_max_initial_alterations=10)->RequestTree:
    """
    Génère la meilleure requête possible en utilisant un algorithme génétique.
    :pre: score_function est une fonction qui prend une requête en entrée et renvoie un score
    :return: La meilleure requête trouvée
    """

    def generate_population(population_size, initial_request:RequestTree)->list[RequestTree]:
        population = [initial_request]
        for _ in range(population_size-1):
            population.append(initial_request.copy())
            nb_alterations = random.randint(0, nb_max_initial_alterations)
            for _ in range(nb_alterations):
                population[-1].alter_random_node()
        return population
    
    def mutate(request:RequestTree)->RequestTree:
        request.alter_random_node()
        return request
    
    def disp_population(population: list[RequestTree]):
        # On affiche entièrement les 2 premières requêtes ainsi que le nombre de nœuds de toutes les autres

        ch = f"[{population[0].get_simplified_request()},{population[1].get_simplified_request()}"
        for i in range(2, len(population)):
            ch += f",{len(population[i].get_all_nodes())}"
        print(ch+"]")

    ten_percent = population_size//10
    population = generate_population(population_size, initial_request)
    print(f"Initial population:")
    disp_population(population)
    for num_generation in range(nb_generations):
        # On commence par trier la population en utilisant la fonction score
        population.sort(key=score_function, reverse=True)
        # Ensuite, on garde les 10% meilleurs
        population = population[:ten_percent]
        # On duplique les 10% meilleurs pour retrouver la taille initiale de la population
        while len(population) < population_size:
            population.append(population[random.randint(0, ten_percent-1)].copy())
        # On génère des mutations sur les 90% précédemment créés
        for i in range(ten_percent, population_size):
            for _ in range(random.randint(0, nb_max_alterations_per_gen)):
                population[i] = mutate(population[i])
        print(f"Generation {num_generation+1}:")
        disp_population(population)
    
    # On retourne la meilleure requête trouvée
    return max(population, key=score_function)



#################################### TESTS ####################################



def run_tests():
    initial_include_tree = Node("collaboration", [], INCLUDED_VOCABULARY)
    initial_exclude_tree = Node("batman", [], EXCLUDED_VOCABULARY)
    request_tree = RequestTree(initial_include_tree, initial_exclude_tree)

    print(Fore.YELLOW+"\nInitial request:"+Fore.RESET)
    print(request_tree.to_colored_request())
    print(repr(request_tree))

    nb_alterations = int(input("\nChoose the number of alterations to apply to the request: "))
    request_tree.apply_alterations(nb_alterations, log=False)

    print(Fore.YELLOW+f"\nRequest after {nb_alterations} alterations:"+Fore.RESET)
    print(request_tree.to_colored_request())
    print(repr(request_tree))

    sympy_tree = to_sympy(request_tree)
    print(f"Représentation sympy: {sympy_tree}")
    simplified_sympy = sp.to_cnf(sympy_tree, simplify=True, force=True)
    print(f"\nVersion simplifiée: {simplified_sympy}")
    print(f"\nRequête correspondante: {sympy_to_request(simplified_sympy)}")