class Node():
    pass

    def __str__( self ):
        return str( self.__dict__ )

class Program( Node ):
    def __init__( self, nodes ):
        self.nodes = nodes

class Block( Node ):
    def __init__( self, var_block, code_block ):
        self.var_block = var_block
        self.code_block = code_block

class CodeBlock( Node ):
    def __init__( self, nodes ):
        self.nodes = nodes

class VarBlock( Node ):
    def __new__( cls, nodes ):
        if len( nodes ) == 0:
            return None
        else:
            return super( VarBlock, cls ).__new__( cls )
    
    def __init__( self, nodes ):
        self.nodes = nodes

class Decl( Node ):
    def __init__( self, type_, id_ ):
        self.type_ = type_
        self.id_ = id_
    
    def __str__( self):
        return f'{ self.type_ } - { self.id_ }'

class ArrayDecl( Node ):
    def __init__( self, type_, id_, size, elems ):
        self.type_ = type_
        self.id_ = id_
        self.size = size
        self.elems = elems

    def __str__( self ):
        return f'{ self.id_ } - { self.type_ } [ { self.size } ]'
    
class StringDecl( Node ):
    def __init__( self, id_, size, elems ):
        self.id_ = id_
        self.size = size
        self.elems = elems

    def __str__( self ):
        return f'{ self.id_ } - String [ { self.size } ]'


class ArrayElem( Node ):
    def __init__( self, id_, index ):
        self.id_ = id_
        self.index = index

class Assign( Node ):
    def __init__( self, id_, expr ):
        self.id_ = id_
        self.expr = expr
    
    def __str__( self ):
        return f'{ self.id_ } = { self.expr }'

class If( Node ):
    def __init__( self, cond, true, false ):
        self.cond = cond
        self.true = true
        self.false = false

    def __str__( self ):
        return f'if( { self.cond } )'

class While( Node ):
    def __init__( self, cond, block ):
        self.cond = cond
        self.block = block

class For( Node ):
    def __init__( self, init, limit, block, step = 1 ):
        self.init = init
        self.limit = limit
        self.step = step
        self.block = block
    
    def __str__( self ):
        return f'for { self.init } to { self.limit } do'

class Repeat( Node ):
    def __init__( self, cond, instructions ):
        self.condition = cond
        self.instructions = instructions
    
    def __str__( self ):
        return f'repeat ... until( { self.cond } );'

class FuncImpl( Node ):
    def __init__( self, id_, params, ret_type, block ):
        self.id_ = id_
        self.params = params
        self.ret_type = ret_type      # None if procedure.
        self.block = block
    
    # def __str__( self ):
    #     if self.ret_type is None:
    #         return f'<Procedure { self.id_ }( { self.params } )> '
    #     else:
    #         return f'<Function { self.id_ }( { self.params } ), return: { self.ret_type } >'
        

class FuncCall( Node ):
    def __init__( self, id_, args, ret ):
        self.id_ = id_
        self.args = args
        self.ret = ret          # None if procedure.

    def __str__( self ):
        return f'<Function call: { self.id_}()>'

class Params( Node ):
    def __init__( self, params, type_ ):
        self.params = params
        self.type_ = type_

class Args( Node ):
    def __init__( self, args ):
        self.args = args

class Argument( Node ):
    def __init__( self, value, formating ):
        self.formating = formating
        self.value = value

class Elems( Node ):
    def __init__( self, elems):
        self.elems = elems

class Break( Node ):
    pass

class Continue( Node ):
    pass

class Exit( Node ):
    def __init__( self, expr ):
        self.expr = expr

class Return( Node ):
    def __init__( self, expr ):
        self.expr = expr

class Type( Node ):
    def __init__( self, value ):
        if value == 'integer':
            self.value = 'int'
        elif value == 'real':
            self.value = 'float'
        elif value == 'boolean':
            self.value = 'char'
        else:
            self.value = value

    def __str__( self ):
        return self.value

class Int( Node ):
    def __init__( self, value ):
        self.value = value
    
    def __str__( self ):
        return str( self.value )

class Boolean( Node ):
    def __init__( self, value ):
        self.value = value
    
    def __str__( self ):
        return str( self.value )

class Char( Node ):
    def __init__( self, value ):
        self.value = value
    
    def __str__( self ):
        return self.value

class String( Node ):
    def __init__( self, value ):
        self.value = value

    def __str__( self ):
        return self.value

class Id( Node ):
    def __init__( self, value ):
        self.value = value
    
    def __str__( self ):
        return self.value

class BinOp( Node ):
    def __init__(self, symbol, first, second):
        self.symbol = symbol
        self.first = first
        self.second = second
    
    # Using this we can search the Symbol table when generating the code and determine the likely type of an operation.
    def get_one_operand_id( self ):
        id_ = self.first

        while isinstance( id_, BinOp ) or isinstance( id_, UnOp ):
            print( id_.first )
            id_ = id_.first
        
        return id_
    
    # def __str__( self ):
    #     return f'( { self.first } <{ self.symbol }> { self.second } )'

class UnOp( Node ):
    def __init__( self, symbol, first ):
        self.symbol = symbol
        self.first = first
    
    # Using this we can search the Symbol table when generating the code and determine the likely type of an operation.
    def get_one_operand_id( self ):
        id_ = self.first

        while isinstance( id_, BinOp ) or isinstance( id_, UnOp ):
            id_ = self.first
        
        return id_
    
    def __str__( self ):
        return f'{ self.symbol }{ self.first }'
        