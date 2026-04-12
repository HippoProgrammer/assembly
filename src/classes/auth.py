# auth classes
from .exceptions import *
import logging

# set up a logger
logger = logging.getLogger(__name__) # get the logger for this script

class Permission:
    def __init__(self):
        self.initialized = False
    def fromAttributeValues(self, kind:str, identifier:int):
        self.kind = kind
        self.identifier = identifier
        self.initialized = True
        return self
    def fromSQLValues(self, values:tuple):
        self.kind = values[0]
        self.identifier = values[1]
        self.initialized = True
        return self
    def toSQLValues(self):
        if self.initialized:
            return (self.kind, self.identifier)
        else:
            raise exceptions.UninitializedException()

class Channel:
    def __init__(self):
        self.initialized = False
    def fromAttributeValues(self, kind:str, identifier:int):
        self.kind = kind
        self.identifier = identifier
        self.initialized = True
        return self
    def fromSQLValues(self, values:tuple):
        self.kind = values[0]
        self.identifier = values[1]
        self.initialized = True
        return self
    def toSQLValues(self):
        if self.initialized:
            return (self.kind, self.identifier)
        else:
            raise exceptions.UninitializedException()