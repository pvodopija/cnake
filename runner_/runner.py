from visitor_.visitor import Visitor
from parser_ import ast
from symbolizer_.symbols import Symbol, Symbols
import sys

class Runner(Visitor):
    def __init__(self, ast):
        self.ast = ast
        self.local = {}
        self.global_ = Symbols()
        self.break_ = False
        self.return_ = False

    def get_symbol( self, node, symbols ):
        return symbols.get( node.value )
        # id_ = node.value
        # for scope in reversed(self.scope):
        #     if scope in self.local:
        #         curr_scope = self.local[scope][-1]
        #         if id_ in curr_scope:
        #             return curr_scope[id_]
        # return self.global_[id_]

    def init_scope(self, node):
        scope = id(node)
        if scope not in self.local:
            self.local[scope] = []
        self.local[scope].append({})
        for s in node.symbols:
            self.local[scope][-1][s.id_] = s.copy()

    def clear_scope(self, node):
        scope = id(node)
        self.local[scope].pop()

    def visit_Program(self, parent, node):
        # for s in node.symbols:
        #     self.global_[s.id_] = s.copy()
        for n in node.nodes:
            if isinstance( n, ast.FuncImpl ):
                self.global_.put( n.id_.value, 'procedure' if n.ret_type is not None else 'function', id( self.global_ ), n )
            else:
                self.visit( node, n )
    
    def visit_Block(self, parent, node):
        # scope = id(node)
        # self.scope.append(scope)
        if node.var_block is not None:
            self.visit( node, node.var_block )
        
        return_ = self.visit( node, node.code_block )
        
        if isinstance( parent, ast.FuncCall ):
            self.return_ = False
        
        return return_

        # self.scope.pop()
    
    def visit_VarBlock( self, parent, node ):

        for n in node.nodes:
            if not isinstance( n, ast.StringDecl ):
                self.visit( node, n )
    
    def visit_CodeBlock( self, parent, node ):
        result = None

        for n in node.nodes:
            # if self.return_:
            #     break
            if isinstance( n, ast.Break ):
                self.break_ = True
                break
            elif isinstance( n, ast.Continue ):
                break
            elif isinstance( n, ( ast.Exit, ast.If, ast.While, ast.For, ast.Repeat ) ):
                result = self.visit( node, n )
                
                if self.return_ is True:
                    return result
            else:
                self.visit( node, n )
            
        return result

    def visit_Decl(self, parent, node):
        symbol_ = self.get_symbol( node.id_, parent.symbols )
        symbol_.value = None

    def visit_ArrayDecl(self, parent, node):
        symbol_ = self.get_symbol( node.id_, parent.symbols )
        size_ = self.visit( node, node.size )
        type_ = self.visit( node, node.type_ )
        
        symbol_.value = Symbols()
        
        # Parser created an array with zeros for us if the user didn't initialize instantly. We just need to assign it.
        elems_ = [ self.visit( node, e ) for e in node.elems.elems ]

        for i, e in enumerate( elems_ ):
            symbol_.value.put( i, type_, id( parent.symbols ), e )

    def visit_ArrayElem(self, parent, node):
        arrsymbol_ = self.visit( node, node.id_ )
        index_ = self.visit( node, node.index )
        index_ = int( index_.value )  - 1 if isinstance( index_, Symbol ) else index_ - 1   # Dumb pascal indexes start from 1.
        
        elsymbol_ = arrsymbol_.value.get( index_ ) 

        # print( elsymbol_ )

        return elsymbol_

    
    def visit_Elems( self, parent, node ):
        pass
        # return [ self.visit( node, n ) for n in node.elems ]

    def visit_Assign(self, parent, node):
        id_ = self.visit(node, node.id_)
        value = self.visit(node, node.expr)
        # print( 'Assign: ', id_, value )
        if isinstance(value, Symbol):
            value = value.value
        id_.value = value

        return id_

    def visit_If(self, parent, node):
        cond = self.visit(node, node.cond)
        result = None

        if isinstance( cond, Symbol ):
            cond = cond.value 

        if cond is True:
            result = self.visit(node, node.true)
        else:
            if node.false is not None:
                result = self.visit(node, node.false)
        
        return result

    def visit_While(self, parent, node):
        cond = self.visit(node, node.cond)
        result = None

        if isinstance( cond, Symbol ):
            cond = cond.value 
        
        while cond:
            result = self.visit(node, node.block)
            if self.return_ is True:
                return result

            cond = self.visit(node, node.cond)

    def visit_For(self, parent, node):
        i_ = self.visit(node, node.init)
        i_.value = int( i_.value )
        result = None

        limit_ = self.visit(node, node.limit)
        if isinstance( limit_, Symbol ):
            limit_ = int( limit_.value )

        condition = lambda x, y:  x <= y if node.step > 0 else x >= y

        while condition( i_.value, limit_ ):
            result = self.visit(node, node.block)
            if self.return_ == True:
                break
            i_.value += node.step
        
        return result
        # self.visit(node, node.block)
        # i_.value += node.step
    def visit_Repeat(self, parent, node):
        condition = self.visit( node, node.condition )
        result = None
        for n in node.instructions:
            result = self.visit( node, n )
            
            if self.return_ is True:
                return result
        
        while condition is not True:
            for n in node.instructions:
                result = self.visit( node, n )
                if self.break_ is True:
                    self.break_ = False
                    return
                elif self.return_ is True:
                    return result
            
            condition = self.visit( node, node.condition )

    def visit_FuncImpl(self, parent, node):
        # id_ = self.get_symbol( node.id_, node.symbols )
        # id_.params = node.params
        # id_.block = node.block
        self.visit( node, node.params )
        self.visit( node, node.block )

    def visit_FuncCall(self, parent, node):
        func = node.id_.value
        args = node.args.args

        if func in [ 'write', 'writeln' ]:
            values = self.visit( node, node.args )
            for val_ in values:
                print( val_.value if isinstance( val_, Symbol ) else val_, end = '', sep = '' )
            
            if func == 'writeln':
                print()
            # print( *values, end = '\n' if func == 'writeln' else '', sep = '' )
        
        elif func == 'readln':
            input_ = input()
            input_ = input_.split()     # Splits by space automatically.

            for i, arg in zip( input_, args ):
                symbol_ = None

                if isinstance( arg.value, ast.ArrayElem ):
                    symbol_ = self.visit( node, arg.value )
                else:
                    id_ = arg.value.value
                    symbol_ = node.symbols.get( id_ )

                symbol_.value = i
        elif func == 'read':
            arg = args[0].value
            input_ = ""

            while True:
                c = sys.stdin.read( 1 )     # Reads one byte at a time, similar to getchar().
                if c == '\n' or c == ' ':
                    break
                else:
                    input_ += c

            symbol_ = None

            if isinstance( arg, ast.ArrayElem ):
                symbol_ = self.visit( node, arg )
            else:
                id_ = arg.value
                symbol_ = node.symbols.get( id_ )
           
            symbol_.value = input_

        elif func == 'chr':
            val_ = self.visit( node, node.args )

            return chr( val_.pop() )

        elif func == 'ord':
            val_ = self.visit( node, node.args )

            return ord( val_.pop() )
        elif func == 'length':
            val_ = self.visit( node, node.args )[0]
            return len( val_ )

        elif func == 'insert':
            args_ = sefl.visit( node, node.args )
            val_, id_, index_ = args_[0], args[1], args[2]
            print( args_ )
            # arrsymbol_ = node.symbols.get( id_ )

        else:
            args_ = self.visit( node, node.args )   # Returns a list of arguments with concrete values( expressions and identifires are already calculated ).
            symbol_ = self.global_.get( func )      # Get a function context from global symbol table. Now I can get its symbol table and code block and execute it.
            params = self.visit( node, symbol_.value.params )

            # for k, v in symbol_.value.symbols.items():
            #     v.value_ = None
            
            for param, arg in zip( params, args_ ):
                param.value = arg 
            
            return_ = self.visit( node, symbol_.value.block )

            return return_

    def visit_Params(self, parent, node):
        return [ self.visit( node, p ) for p in node.params ]

    def visit_Args(self, parent, node):
        return [ self.visit( node, arg ) for arg in node.args ]
        # func = parent.id_.value
        # impl = self.global_[func]
        # for p, a in zip(impl.params.params, node.args):
        #     arg = self.visit(impl.block, a)
        #     id_ = self.visit(impl.block, p.id_)
        #     id_.value = arg
        #     if isinstance(arg, Symbol):
        #         id_.value = arg.value

    def visit_Argument(self, parent, node):
        arg = self.visit( node, node.value )
        val_ = arg.value if isinstance( node.value, ast.Id ) else arg
        fmt_ = node.formating[1]

        return '{:.2f}'.format( val_ ) if fmt_ is not None else val_
        # return round( val_, fmt_.value ) if fmt_ is not None else val_

    def visit_Elems(self, parent, node):
        pass

    def visit_Break(self, parent, node):
        self.break_ = True

    def visit_Continue(self, parent, node):
        pass

    def visit_Exit( self, parent, node ):
        self.return_ = True
        return self.visit( node, node.expr ) if node.expr is not None else None

    def visit_Return(self, parent, node):
        pass

    def visit_Type(self, parent, node):
        return node.value

    def visit_Int(self, parent, node):
        return node.value
    
    def visit_Boolean(self, parent, node):
        return True if node.value == 'true' else False


    def visit_Char(self, parent, node):
        return node.value

    def visit_String(self, parent, node):
        return node.value
    
    def visit_StringDecl(self, parent, node):
        return node.value

    def visit_Id(self, parent, node):
        return self.get_symbol( node, node.symbols )

    def visit_BinOp(self, parent, node):
        first = self.visit(node, node.first)
        if isinstance(first, Symbol):
            first = first.value
        second = self.visit(node, node.second)
        if isinstance(second, Symbol):
            second = second.value
        
        first, second = ( float( first ), float( second ) ) if '.' in ( str( first ) + str( second ) ) else ( int( first ), int( second ) ) # Checks if number is float and casts appropriately.
            
        if node.symbol == '+':
            return first + second
        elif node.symbol == '-':
            return first - second
        elif node.symbol == '*':
            return first * second
        elif node.symbol == 'div':
            return first // second
        elif node.symbol == 'mod':
            return first % second
        elif node.symbol == '/':
            return first / second
        elif node.symbol == '=':
            return first == second
        elif node.symbol == '<>':
            return first != second
        elif node.symbol == '<':
            return first < second
        elif node.symbol == '>':
            return first > second
        elif node.symbol == '<=':
            return first <= second
        elif node.symbol == '>=':
            return first >= second
        elif node.symbol == 'and':
            bool_first = first != 0
            bool_second = second != 0
            return bool_first and bool_second
        elif node.symbol == 'or':
            bool_first = first != 0
            bool_second = second != 0
            return bool_first or bool_second
        else:
            return None

    def visit_UnOp(self, parent, node):
        first = self.visit(node, node.first)
        backup_first = first
        if isinstance(first, Symbol):
            first = first.value
        if node.symbol == '-':
            return -first
        elif node.symbol == 'not':
            bool_first = first != 0
            return not bool_first
        elif node.symbol == '&':
            return backup_first
        else:
            return None

    def run(self):
        self.visit(None, self.ast)