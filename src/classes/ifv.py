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

# wa-adjacent IFV classes
from .exceptions import *
import logging

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