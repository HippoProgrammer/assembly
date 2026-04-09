# general classes for use with WA
class Proposal(Object):
    def __init__(self, id:str, council:int, name:str, category:str, author:str, coauthors=[], legal:bool):
        self.id = id
        self.council = council
        self.name = name
        self.category = category
        self.author = author
        self.coauthors = coauthors
        self.legal = legal