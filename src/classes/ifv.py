# wa-adjacent IFV classes
from .exceptions import *

class IFV:
    def __init__(self):
        self.initialized = False
    def fromAttributeValues(self, id:str, name:str, thread = None, ifvauthor = None, ifvlink = None):
        self.id = id
        self.name = name
        self.thread = thread
        self.ifvauthor = ifvauthor
        self.ifvlink = ifvlink
        self.initialized = True
        return self
    def fromSQLValues(self, values:tuple):
        self.id = values[0]
        self.name = values[1]
        self.thread = values[2]
        self.ifvauthor = values[3]
        self.ifvlink = values[4]
        self.initialized = True
        return self
    def toSQLValues(self):
        if self.initialized:
            return (self.id,self.name,self.thread,self.ifvauthor,self.ifvlink)
        else:
            raise exceptions.UninitializedException()