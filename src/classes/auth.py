'''This file is part of assembly.
Copyright (C) 2026 HippoProgrammer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.'''

# auth classes
from .exceptions import *
import logging

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