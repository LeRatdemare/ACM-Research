import random
from vocabulary import Vocabulary



#################################### CONSTANTES ####################################



KEEP_SIMILAR_WORD_PROBA = 0.7
KEEP_SAME_OPERATION_PROBA = 0.5



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
    
    def to_request(self):
        """
        :pre: -
        :return: La représentation de l'arbre correspondant à une requête de navigateur
        """
        if self.is_leaf():
            return self.value
        if self.is_operation():
            if self.value == "NOT":
                return f"NOT {self.children[0].to_request()}"
            return f"({self.children[0].to_request()} {self.value} {self.children[1].to_request()})"

    def get_random_node(self):
        """
        :pre: -
        :return: Un nœud aléatoire de l'arbre (y compris lui-même)
        """
        if self.is_leaf():
            return self
        return random.choice([self] + [c.get_random_node() for c in self.children])
    
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
                self.value = random.choice(self.vocabulary.get_similar_words(self.value))
            # Soit un mot aléatoire
            else:
                self.value = random.choice(self.vocabulary.get_words())
        # Si le nœud est une opération, on a une proba d'inverser l'opération
        if random.random() < KEEP_SAME_OPERATION_PROBA:
            self.value = "AND" if self.value == "OR" else "OR"
    
    def alter_structure(self, grow_proba=0.6, shrink_proba=0.3):
        """
        Modifie aléatoirement la structure de l'arbre
        :pre: -
        :return: None
        """
        # Si le nœud est une feuille, on le remplace par un nœud aléatoire qui n'est pas une feuille
        if self.is_leaf() and random.random() < grow_proba:
            self.value = random.choice(["AND", "OR"])
            self.children = [Node(random.choice(self.vocabulary.get_words()), [], self.vocabulary), Node(random.choice(self.vocabulary.get_words()), [], self.vocabulary)]
        # Si le nœud est une opération, on le remplace par une feuille aléatoire
        elif not self.is_leaf() and random.random() < shrink_proba:
            self.value = random.choice(self.vocabulary.get_words())
            self.children = []

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
        return repr(self)

    def __eq__(self, other):
        """
        :return: True si self et other ont la même structure
        """
        if not isinstance(other, Node):
            return False
        return self.value == other.value and self.children == other.children



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



#################################### VARIABLES ####################################



INCLUDED_VOCABULARY = {"asymetric":{"asym*","asymetric","asymetrical","mixed"},"collaboration":{"collaboration","teamwork","remote collaboration","distance collaboration"}, "interaction":{"intera*","interaction","interact","interactivity","interactiveness","interactive","interactiveness"}, "system":{"syst*","system","systems","systematic","systemic"}}
EXCLUDED_VOCABULARY = {"batman":"batman"}
VOCABULAIRE = INCLUDED_VOCABULARY
VOCABULAIRE.update(EXCLUDED_VOCABULARY)
# print(VOCABULAIRE)



#################################### TESTS ####################################



# treeA = Node("AND", [Node("NOT", [Node("OR", [Node("asymetric", []), Node("asymetrical", [])])]), Node("collaboration", [])])
# print("\n"+str(treeA)+"\n")
# print(serialize(treeA))
# # print(unserialize(serialize(treeA)) == treeA)
# print("\n"+treeA.to_request()+"\n")

# # Test avec une autre requête différente
# treeB = "OR,2,AND,2,NOT,1,OR,2,asymetric,0,asymetrical,0,collaboration,0,teamwork,0"
# print("\n"+str(unserialize(treeB))+"\n")
# print(treeB)
# # print(serialize(unserialize(treeB)) == treeB)
# print("\n"+unserialize(treeB).to_request()+"\n")

serialized_tree = "AND,2,NOT,1,batman,0,collaboration,0"
tree = unserialize(serialized_tree, Vocabulary(INCLUDED_VOCABULARY))
print(tree)
