from copy import deepcopy

class DataStruct:
    def __init__(self, structure: dict) -> None:
        self.structure = structure
        self.data = deepcopy(self.structure)
    def _from_values(self, values: dict):
        for key in (set(self.structure) & set(values)):
            self.structure[key] = values[key]
    def from_attribute_values(self, **kwargs):
        self._from_values(kwargs)
    def from_sql_values(self, values: dict):
        for key in (set(self.structure) & set(values)): 
# fix to match above

class IFV:
    def __init__(self):
        self.initialized = False
    def fromAttributeValues(self, id:str, name:str, thread:str | None = None, ifvauthor:str | None = None, ifvlink:str | None = None):
        self.id = id
        self.name = name
        self.thread = thread
        self.ifvauthor = ifvauthor
        self.ifvlink = ifvlink
        self.initialized = True
        return self
    def fromSQLValues(self, values:tuple[str, str, str | None, str | None, str | None]):
        self.id = values[0]
        self.name = values[1]
        self.thread = values[2]
        self.ifvauthor = values[3]
        self.ifvlink = values[4]
        self.initialized = True
        return self
    def toSQLValues(self) -> tuple[str, str, str, str | None, str | None, str | None]:
        if self.initialized:
            return (self.id,self.name,self.thread,self.ifvauthor,self.ifvlink)
        else:
            raise exceptions.UninitializedException()