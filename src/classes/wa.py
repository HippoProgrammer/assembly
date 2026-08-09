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

# general classes for use with WA
from .exceptions import *
import logging

class Proposal:
    def __init__(self):
        self.initialized = False
    def fromAttributeValues(self, id:str, council:int, name:str, category:str, author:str, legal:bool, quorum:bool, coauthors:list[str | None] = []):
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
    def fromSQLValues(self, values:tuple[str, int, str, str, str, bool, bool, list[str | None]]):
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
    def toSQLValues(self) -> tuple[str, int, str, str, str, bool, bool, list[str | None]]:
        if self.initialized:
            return (self.id,self.council,self.name,self.category,self.author,self.coauthors,self.legal,self.quorum)
        else:
            raise exceptions.UninitializedException()
class ProposalAtVote:
    def __init__(self):
        self.initialized = False
    def fromAttributeValues(self, id:str, council:int, name:str, category:str, author:str, promoted:int, coauthors:list[str | None] = []):
        self.id = id
        self.council = council
        self.name = name
        self.category = category
        self.author = author
        self.coauthors = coauthors
        self.promoted = promoted # time proposal came to vote
        self.initialized = True
    def fromSQLValues(self, values:tuple[str, int, str, str, str, int, list[str | None]]):
        self.id = values[0]
        self.council = values[1]
        self.name = values[2]
        self.category = values[3]
        self.author = values[4]
        self.coauthors = values[5]
        self.initialized = True
    def toSQLValues(self) -> tuple[str, int, str, str, str, int, list[str | None]]:
        if self.initialized:
            return (self.id,self.council,self.name,self.category,self.author,self.promoted,self.coauthors)
        else:
            raise exceptions.UninitializedException()