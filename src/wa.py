# general classes for use with WA
class Proposal(Object):
    def __init__(self, id:str, council:int, name:str, category:str, author:str, coauthors=[], legal:bool):
        while len(coauthors) < 3:
            coauthors.append('')
        self.id = id
        self.council = council
        self.name = name
        self.category = category
        self.author = author
        self.coauthors = coauthors
        self.legal = legal
        self.coauthor1 = coauthors[0]
        self.coauthor2 = coauthors[1]
        self.coauthor3 = coauthors[2]
    def values(self):
        return (self.id,self.council,self.name,self.category,self.author,self.coauthor1,self.coauthor2,self.coauthor3,self.legal)