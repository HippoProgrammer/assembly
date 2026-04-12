# general classes for use with WA
from .exceptions import *
import logging

# set up a logger
logger = logging.getLogger(__name__) # get the logger for this script

class Proposal:
    def __init__(self):
        self.initialized = False
    def fromAttributeValues(self, id:str, council:int, name:str, category:str, author:str, legal:bool, quorum:bool, coauthors=[]):
        self.id = id
        self.council = council
        self.name = name
        self.category = category
        self.author = author
        self.coauthors = coauthors
        self.legal = legal
        self.quorum = quorum
        self.initialized = True
        return self
    def fromSQLValues(self, values:tuple):
        self.id = values[0]
        self.council = values[1]
        self.name = values[2]
        self.category = values[3]
        self.author = values[4]
        self.coauthors = values[5]
        self.legal = values[6]
        self.quorum = values[7]
        self.initialized = True
        return self
    def toSQLValues(self):
        if self.initialized:
            return (self.id,self.council,self.name,self.category,self.author,self.coauthors,self.legal,self.quorum)
        else:
            raise exceptions.UninitializedException()