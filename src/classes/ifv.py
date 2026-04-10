# wa-adjacent IFV classes
from .exceptions import *

class IFV:
    def __init__(self):
        self.initialized = False
    def fromAttributeValues(self, id:str, thread = None, ifvauthor = None, ifvlink = None):
        self.id = id
        self.thread = thread
        self.ifvauthor = ifvauthor
        self.ifvlink = ifvlink
        self.initialized = True
        return self
    def fromSQLValues(self, values:tuple):
        self.id = values[0]
        self.thread = values[1]
        self.ifvauthor = values[2]
        self.ifvlink = values[3]
        self.initialized = True
        return self
    def toSQLValues(self):
        if self.initialized:
            return (self.id,self.thread,self.ifvauthor,self.ifvlink)
        else:
            raise exceptions.UninitializedException()