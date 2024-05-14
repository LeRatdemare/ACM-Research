class Vocabulary:
    def __init__(self, content: dict[str, list[str]]={}):
        """
        :pre: words est un dictionnaire. Chaque élément contient une catégorie et une liste de mots similaires. Chaque liste contient le nom de la catégorie.
        """
        self.content = content
        self.n_words = sum(len(content[category]) for category in content.keys())
        assert self.is_valid()

    def is_valid(self):
        """
        :pre: -
        :return: True si le vocabulaire est valide. False sinon.
        """
        for category, words in self.content.items():
            if not isinstance(category, str) or not isinstance(words, list):
                return False
            for word in words:
                if not isinstance(word, str):
                    return False
            if category not in words:
                return False
        return True
    
    def get_words(self)->list[str]:
        """
        :pre: -
        :return: La liste de tous les mots du vocabulaire.
        """
        return [word for words in self.content.values() for word in words]
    
    def get_categorie(self, word:str)->str:
        """
        :pre: word est un str.
        :return: La catégorie du mot word.
        """
        for category, words in self.content.items():
            if word in words:
                return category
        return None
    
    def get_similar_words(self, word:str)->list[str]:
        """
        :pre: word est un str.
        :return: La liste des mots similaires à word.
        """
        for words in self.content.values():
            if word in words:
                return words
        return []
    
    def __len__(self):
        return self.n_words