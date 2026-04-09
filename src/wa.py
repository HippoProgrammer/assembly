# general classes for use with WA
class UninitializedException(Exception):
    pass

class Proposal:
    def __init__(self):
        self.initialized = False
    def fromAttributeValues(self, id:str, council:int, name:str, category:str, author:str, legal:bool, coauthors=[]):
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
        self.initialized = True
        return self
    def fromSQLValues(self, values:tuple):
        self.id = values[0]
        self.council = values[1]
        self.name = values[2]
        self.category = values[3]
        self.author = values[4]
        self.coauthor1 = values[5]
        self.coauthor2 = values[6]
        self.coauthor3 = values[7]
        self.legal = values[8]
        self.initialized = True
        return self
    def toSQLValues(self):
        if self.initialized:
            if self.legal: # convert to SQL format
                legal = 'TRUE'
            else:
                legal = 'FALSE'
            return (self.id,self.council,self.name,self.category,self.author,self.coauthor1,self.coauthor2,self.coauthor3,legal)
        else:
            raise UninitializedException()