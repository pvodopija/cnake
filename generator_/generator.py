from visitor_.visitor import Visitor
from symbolizer_.symbols import Symbols
from parser_ import ast
import re

class Generator( Visitor ):
    def __init__( self, ast ):
        self.ast = ast
        self.c = ""
        self.level = 0
        self.global_ = Symbols()
    
    def header( self ):
        return '''\
#include <stdio.h>
#include <string.h>

#define ord( x ) ( ( int ) x )
#define chr( x ) ( ( char ) x )
#define inc( x ) ( x++ )
#define dec( x ) ( x-- )
#define insert( src, dest, index ) ( dest[ index - 1 ] = src )
#define length( str ) ( strlen( str ) )

'''
    def append( self, text ):
        self.c += str( text )

    def newline( self ):
        self.append( '\n' )
        self.indent()

    def indent( self ):
        for i in range( self.level ):
            self.append( '\t' )

    def visit_Program( self, parent, node ):
        self.append( self.header() )

        for n in node.nodes:
            if isinstance( n, ast.FuncImpl ) is False:
                self.newline();self.newline()
                self.append( 'int main( void )')
                self.newline()

            self.visit( node, n )

        self.c = self.c[:-2]
        self.append( '\n\treturn 0;\n}' )
        
        self.newline()

    def visit_Block( self, parent, node ):
        self.level += 1
        self.append( '{' )
        self.newline()

        # for n in node.symbols:
        #     print( '\t' * self.level, n )

        if node.var_block is not None:
            self.visit( node, node.var_block )
            self.newline()

        self.visit( node, node.code_block )

        self.level -= 1
        self.c = self.c[:-1]
        self.append( '}' )

    def visit_VarBlock( self, parent, node ):
        for n in node.nodes:
            self.visit( node, n )
            self.append( ';' )
            self.newline()
    
    def visit_CodeBlock( self, parent, node ):
        for n in node.nodes:
            self.visit( node, n )
            if self.c[-1] != '}':
                self.append( ';' )
            self.newline()

    def visit_Decl( self, parent, node ):
        self.append( f'{ node.type_ } { node.id_ }' )
    
    def visit_StringDecl( self, parent, node ):
        self.append( f'char { node.id_ }[100]' )

    def visit_ArrayDecl( self, parent, node ):
        self.visit( node, node.type_ )
        self.visit( node, node.id_ )

        if node.elems is not None:
            self.append( '[] = { ' )
            self.visit( node, node.elems )
            self.append( ' }' )
        elif node.size is not None:
            self.append( ' = ' )
            self.visit( node, node.size )
            self.append( ' * [None]' )

    def visit_ArrayElem( self, parent, node ):
        self.visit( node, node.id_ )
        self.append( '[' )
        self.visit( node, node.index )
        self.append( ' - 1' )
        self.append( ']' )

    def visit_Assign( self, parent, node ):
        self.visit( node, node.id_ )
        self.append( ' = ' )
        self.visit( node, node.expr )

    def visit_If( self, parent, node ):
        self.append( 'if( ' )
        self.visit( node, node.cond )
        self.append( ' )' )
        self.newline()
        self.visit( node, node.true )
        if node.false is not None:
            self.newline()
            self.append( 'else' )
            self.newline()
            self.visit( node, node.false )

    def visit_While( self, parent, node ):
        self.append( 'while( ' )
        self.visit( node, node.cond )
        self.append( ' )' )
        self.newline()
        self.visit( node, node.block )
    
    def visit_Repeat( self, parent, node ):
        self.append( 'do' )
        self.newline()
        self.append( '{' )
        self.level += 1
        self.newline()
       
        for n in node.instructions:
            self.visit( node, n )
            if isinstance( n, ast.Block) is False:
                self.append( ';' )
                self.newline();
                

        self.level -= 1
        self.newline()
        self.append( ' } while( !' )
        self.visit( node, node.condition )
        self.append( ' );' )
        self.newline()
        

    def visit_For( self, parent, node ):
        id_ = node.init.id_
        cond_operator = '<=' if node.step > 0 else '>='

        self.append( f'for( ' ); 
        self.visit( node, node.init )
        self.append( f'; { id_ } { cond_operator } ' ) 
        self.visit( node, node.limit )
        self.append( f'; { id_ } += { node.step } ) ' )
        self.newline()
        self.visit( node, node.block )

    def visit_FuncImpl( self, parent, node ):
        ret_type = 'void' if node.ret_type == None else node.ret_type

        self.global_.put( node.id_.value, ret_type, id( self.global_ ) )

        self.append( f'{ ret_type } ' )
        self.append( node.id_.value )
        self.append( '( ' )
        self.visit( node, node.params )
        self.append( ' )' )
        self.newline()
        self.visit( node, node.block )
        self.newline()

    def visit_FuncCall( self, parent, node ):
        func = node.id_.value
        args = node.args.args

        type_map = { 'int': '%d', 'float': '%f', 'string': '%s', 'char': '%c' }
        format_ = ''

        # So many edge cases to handle for formating... Should be relatively clean.
        if func in [ 'write', 'writeln', 'read', 'readln' ]:
            for i, a in enumerate( args ):
                arg = a.value
                id_ = arg
                str_indexes = []

                # If argument is some kind of expression.
                if isinstance( arg, ast.BinOp ) or isinstance( arg, ast.UnOp ):
                    id_ = arg.get_one_operand_id()

                # If there is additonal fomating for floats.
                if a.formating[1] is not None:
                    format_ += f'%.{ a.formating[1] }f'

                # If the argument is single variable.
                elif isinstance( id_ , ast.Id ):
                    symbol_ = parent.symbols.get( id_.value )
                    format_ += type_map[ str( symbol_.type ) ]
                    if symbol_.type == 'string':
                        str_indexes.append( i )

                elif isinstance( id_, ast.ArrayElem ):
                    symbol_ = parent.symbols.get( id_.id_.value )
                    format_ += type_map[ symbol_.type ]

                # If the arguments is a function call.
                elif isinstance( arg, ast.FuncCall ):
                    if arg.id_.value == 'ord':
                        format_ += '%d'
                    elif arg.id_.value == 'chr':
                        format_ += '%c'
                    else:
                        symbol_ = self.global_.get( arg.id_.value )
                        type_ = symbol_.type.value
                        format_ += type_map[ type_ ]

                # If argument is some kind of constant( 5, 'a', "abc" )
                else:
                    if isinstance( arg, ast.Int ):
                        format_ += '%d' if isinstance( arg.value, int ) else '%f'
                    elif isinstance( arg , ast.String ):
                        format_ += '%s'
                    elif isinstance( arg, ast.Char ):
                        format_ += '%c'
                    else:
                        print( f'SOMETHING WENT WRONG! iter: { i }' )
            
            func_name = 'printf'
            address_sign = ''
            
            if func in [ 'read', 'readln' ]:
                func_name = 'scanf'
                address_sign = '&'

            if func == 'writeln':
                format_ += '\\n'
            
            self.append( f'{ func_name }( \"{ format_ }\"' )

            for i, n in enumerate( node.args.args ):
                self.append( ', ' + ( address_sign if i not in str_indexes else '' ) ) # Only strings dont have '&' when scanf() is called.
                self.visit( node, n )
            
            self.append( ' )' )
        else:
            self.append( func )
            self.append( '( ' )
            self.visit( node, node.args )
            self.append( ' )' )

    def visit_Params( self, parent, node ):
        for i, p in enumerate( node.params ):
            if i > 0:
                self.append( ', ' )
            # self.visit( p, p.value )
            self.append( f'{ node.type_ } { p }' )

    def visit_Args( self, parent, node ):
        for i, a in enumerate( node.args ):
            if i > 0:
                self.append( ', ' )
            self.visit( node, a )
    
    def visit_Argument( self, parent, node ):
        # if isinstance( node.value, ast.String ):
        #     self.append( '\"' )
        #     self.visit( parent, node.value )
        #     self.append( '\"' )

        # elif isinstance( node.value, ast.Char ):
        #     self.append( '\'' )
        #     self.visit( parent, node.value )
        #     self.append( '\'' )

        # else:
        self.visit( parent, node.value )

    def visit_Elems( self, parent, node ):
        for i, e in enumerate( node.elems ):
            if i > 0:
                self.append( ', ' )
            self.visit( node, e )

    def visit_Break( self, parent, node ):
        self.append( 'break' )

    def visit_Continue( self, parent, node ):
        self.append( 'continue' )
    
    def visit_Exit( self, parent, node ):
        self.append( 'return ' )
        if node.expr is not None:
            self.visit( node, node.expr )

    def visit_Return( self, parent, node ):
        self.append( 'return' )
        if node.expr is not None:
            self.append( ' ' )
            self.visit( node, node.expr )

    def visit_Type( self, parent, node ):
        self.append( node.value + ' ' )

    def visit_Int( self, parent, node ):
        self.append( node.value )
    
    def visit_Boolean( self, parent, node ):
        self.append( '0' if node.value == 'false' else '1' )

    def visit_Char( self, parent, node ):
        self.append( '\'' + node.value + '\'' )

    def visit_String( self, parent, node ):
        self.append( '\"' + node.value + '\"' )

    def visit_Id( self, parent, node ):
        self.append( node.value )

    def visit_BinOp( self, parent, node ):
        self.append( '( ' )

        self.visit( node, node.first )
        if node.symbol == '=':
            self.append( ' == ' )
        elif node.symbol == '<>':
            self.append( ' != ' )
        elif node.symbol == 'and':
            self.append( ' && ' )
        elif node.symbol == 'or':
            self.append( ' || ' )
        elif node.symbol == 'div':
            self.append( ' / ' )
        elif node.symbol == 'mod':
            self.append( ' % ' )
        else:
            self.append( f' { node.symbol} ' )
        self.visit( node, node.second )
        
        self.append( ' )' )

    def visit_UnOp( self, parent, node ):
        if node.symbol == 'not':
            self.append( '!' )
        elif node.symbol != '&':
            self.append( node.symbol )
        self.append( '( ' )
        self.visit( node, node.first )
        self.append( ' )' )


    def generate( self, path ):
        self.visit( None, self.ast )
        # self.c = re.sub( '\n\s*\n', '\n', self.c )
        with open( path, 'w' ) as source:
            source.write( self.c )
        return path