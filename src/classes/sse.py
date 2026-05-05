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

from .exceptions import *

class Event:
    def __init__(self):
        self.initialized = False
    def fromAttributeValues(self, event:int, time:int, category:str, data:list, actor = None, receptor = None, origin = None, destination = None):
        self.event = event
        self.time = time
        self.actor = actor
        self.receptor = receptor
        self.origin = origin
        self.destination = destination
        self.category = category
        self.data = data
        self.initialized = True
        return self
    def fromSQLValues(self, values:tuple):
        self.event = values[0]
        self.time = values[1]
        self.actor = values[2]
        self.receptor = values[3]
        self.origin = values[4]
        self.destination = values[5]
        self.category = values[6]
        self.data = values[7]
        self.initialized = True
        return self
    def toSQLValues(self):
        if self.initialized:
            return (self.event,self.time,self.actor,self.receptor,self.origin,self.destination,self.category,self.data)
        else:
            raise exceptions.UninitializedException()