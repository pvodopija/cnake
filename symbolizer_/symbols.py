class Symbol:

    def __init__( self, id, type, scope, value = None ):

        self.id = id
        self.type = type
        self.scope = scope
        self.value = value

    def __str__( self ):
        return "<{} {} {} {}>".format( self.id, self.type, self.scope, self.value )

    def copy( self ):
        return Symbol( self.id, self.type, self.scope )


class Symbols:
    def __init__(self):
        self.symbols = {}

    def put( self, id_, type_, scope, value = None ):
        self.symbols[id_] = Symbol(id_, type_, scope, value )

    def get(self, id_):
        return self.symbols[id_]

    def contains(self, id_):
        return id_ in self.symbols

    def remove(self, id_):
        del self.symbols[id_]
    
    def values( self ):
        return self.symbols.values()
    
    def keys( self ):
        return self.symbols.keys()
    
    def items( self ):
        return self.symbols.items()
    
    def __len__(self):
        return len(self.symbols)
    
    def __str__(self):
        out = ""
        for _, value in self.symbols.items():
            if len(out) > 0:
                out += "\n"
            out += str(value)
        return out

    def __iter__(self):
        return iter(self.symbols.values())

    def __next__(self):
        return next(self.symbols.values())
