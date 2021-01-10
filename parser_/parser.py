from . import ast
from lexer.lexer import Class
from functools import wraps
import pickle

class Parser:
    def __init__( self, tokens ):
        self.tokens = tokens
        self.curr = tokens.pop( 0 )
        self.prev = None
        self.semicolomn_counter = 0

    def restorable( call ):
        @wraps( call )
        def wrapper( self, *args, **kwargs ):
            state = pickle.dumps( self.__dict__ )
            result = call( self, *args, **kwargs )
            self.__dict__ = pickle.loads( state )
            return result
        return wrapper

    def eat( self, class_ ):
        if self.curr.class_ == class_:
            self.prev = self.curr
            
            if self.curr.class_ == Class.SEMICOLON:
                self.semicolomn_counter += 1
            
            self.curr = self.tokens.pop( 0 )
        else:
            self.die_type( class_.name, self.curr.class_.name )

    def program( self ):
        nodes = []

        while self.curr.class_ not in [ Class.EOF, Class.DOT ]:

            if self.curr.class_ in [ Class.FUNCTION, Class.PROCEDURE ]:
                nodes.append( self.funproc() )

            else:
                block = ast.Block( self.var(), self.code() )
                nodes.append( block )

        return ast.Program( nodes )
    
    def funproc( self ):
        is_fun = False
        if self.curr.class_ == Class.FUNCTION:
            is_fun = True
            self.eat( Class.FUNCTION )
        else:
            self.eat( Class.PROCEDURE )

        id_ = ast.Id( self.curr.lexeme )
        self.eat( Class.ID )
        self.eat( Class.LPAREN )

        parameters = list()

        while self.curr.class_ != Class.COLON:

            if self.curr.class_ != Class.COMMA:
                parameters.append( ast.Id( self.curr.lexeme ) )

            self.eat( self.curr.class_ )
            
        self.eat( Class.COLON )

        type_ = ast.Type( self.curr.lexeme )
        self.eat( Class.TYPE )
        self.eat( Class.RPAREN )

        return_type = None
        if is_fun:
            self.eat( Class.COLON )
            return_type = ast.Type( self.curr.lexeme )
            self.eat( Class.TYPE )

        self.eat( Class.SEMICOLON )
        
        block = ast.Block( self.var(), self.code() )

        self.eat( Class.SEMICOLON )

        return ast.FuncImpl( id_, ast.Params( parameters, type_ ), return_type, block )
    
    # ids: array [ start..end ] of type_;
    def parse_array( self ):
        self.eat( Class.ARRAY );

        self.eat( Class.LBRACKET );
        start = self.curr.lexeme;
        self.eat( Class.INTEGER );
        self.eat( Class.DOT ); self.eat( Class.DOT );
        end = self.curr.lexeme
        self.eat( Class.INTEGER )
        self.eat( Class.RBRACKET );

        self.eat( Class.OF )
        type_ = self.curr.lexeme
        self.eat( Class.TYPE )

        # Are we initializing instantly?
        elems = [ ast.Int( 0 ) ] * ( end - start + 1 )
        if self.curr.class_ == Class.EQ:
            elems = []
            self.eat( self.curr.class_ )
            self.eat( Class.LPAREN )

            for i in range( end - start ):
                elems.append( ast.Int( self.curr.lexeme ) )
                self.eat( self.curr.class_ )
                self.eat( Class.COMMA )
            
            elems.append( ast.Int( self.curr.lexeme ) )
            self.eat( self.curr.class_ )
            self.eat( Class.RPAREN )

        
        return ( start, end, type_, elems )

    def var( self ):
        # Var block is optional so we can return None.
        if self.curr.class_ == Class.VAR:
           self.eat( self.curr.class_ )
        else:
            return None

        declarations = list()

        while self.curr.class_ != Class.BEGIN: 
            identifiers = list()

            while self.curr.class_ != Class.COLON:

                if self.curr.class_ != Class.COMMA:
                    identifiers.append( ast.Id( self.curr.lexeme ) )

                self.eat( self.curr.class_ )
                
            self.eat( Class.COLON )

            type_ = None
            if self.curr.class_ == Class.ARRAY:
                ( start, end, type__, elements ) = self.parse_array()

                for id_ in identifiers:
                    declarations.append( ast.ArrayDecl( ast.Type( type__ ), id_, ast.Int( end - start + 1 ), ast.Elems( elements ) ) )
            else:
                type_ = ast.Type( self.curr.lexeme )
                self.eat( Class.TYPE )

                if self.prev.lexeme == 'string':
                    string_len = None

                    if self.curr.class_ == Class.LBRACKET:
                        self.eat( self.curr.class_ )
                        string_len = self.curr.lexeme
                        self.eat( Class.INTEGER )
                        self.eat( Class.RBRACKET )
                    
                    for id_ in identifiers:
                        declarations.append( ast.StringDecl( id_, ast.Int( string_len ), None ) )

                else:
                    for id_ in identifiers:
                        declarations.append( ast.Decl( type_, id_ ) )
            
            self.eat( Class.SEMICOLON )

        return ast.VarBlock( declarations )                     # __new__() will return None if there are no declarations.

    
    def code( self ):
        self.eat( Class.BEGIN )
        instructions = self.parse_instructions( Class.END )
        self.eat( Class.END )

        return ast.CodeBlock( instructions )

    # Had to split code() in this functions because stupid repeat doesn't use blocks( works more like a jump to a label ).
    def parse_instructions( self, stop_class ):
        instructions = list()

        while self.curr.class_ != stop_class:
            # This covers function/procedure calls and variable assigment.
            if self.curr.class_ == Class.ID:
                instr = self.id_()

            # This covers Flow Control statements( if, for, while ... ).
            elif self.curr.class_ == Class.IF:
                instr = self.if_()

            elif self.curr.class_ == Class.FOR:
                instr = self.for_()
                
            elif self.curr.class_ == Class.WHILE:
                instr = self.while_()
                
            elif self.curr.class_ == Class.REPEAT:
                instr = self.repeat_()

            elif self.curr.class_ == Class.EXIT:
                instr = self.exit_()
            
            elif self.curr.class_ == Class.BREAK:
                self.eat( Class.BREAK )
                instr = ast.Break()
            
            elif self.curr.class_ == Class.CONTINUE:
                self.eat( Class.CONTINUE )
                instr = ast.Continue()

            self.eat( Class.SEMICOLON )
            instructions.append( instr )
        
        return instructions

    def id_( self ):
        # is_array_elem = self.prev.class_ != Class.TYPE
        id_ = ast.Id( self.curr.lexeme )
        self.eat( Class.ID )

        if self.curr.class_ == Class.LPAREN and self.prev.class_ != Class.PROCEDURE:# self.is_func_call():
            self.eat( Class.LPAREN )
            args = self.args()
            self.eat( Class.RPAREN )

            return ast.FuncCall( id_, args, None )

        elif self.curr.class_ == Class.LBRACKET: # and is_array_elem:
            self.eat( Class.LBRACKET )
            index = self.expr()
            self.eat( Class.RBRACKET )
            id_ = ast.ArrayElem( id_, index )

        if self.curr.class_ == Class.ASSIGN:
            self.eat( Class.ASSIGN )
            expr = self.logic()     # Assigment can be logical expression. logic() returns normal expression if not logical.

            return ast.Assign( id_, expr )

        else:
            return id_

    def if_( self ):
        self.eat( Class.IF )
        cond = self.logic()
        self.eat( Class.THEN )

        true_block = ast.Block( self.var(), self.code() )
        false_block = None

        if self.curr.class_ == Class.ELSE:
            self.eat( Class.ELSE )
            false_block = ast.Block( self.var(), self.code() )

        return ast.If( cond, true_block, false_block )

    def while_( self ):
        self.eat( Class.WHILE )
        cond = self.logic()
        self.eat( Class.DO )
        block = ast.Block( self.var(), self.code() )

        return ast.While( cond, block )

    def for_( self ):
        self.eat( Class.FOR )
        init = self.id_()
        step = 1

        if self.curr.class_ == Class.DOWNTO:
            self.eat( Class.DOWNTO )
            step = -1
        else:
            self.eat( Class.TO )
        
        limit = self.expr()
        # cond = self.logic()
        self.eat( Class.DO )
        block = ast.Block( self.var(), self.code() )

        return ast.For( init, limit, block, step )
    
    def repeat_( self ):
        self.eat( Class.REPEAT )
        instructions = self.parse_instructions( Class.UNTIL )
        self.eat( Class.UNTIL )

        condition = self.logic()

        return ast.Repeat( condition, instructions )

    def exit_( self ):
        self.eat( Class.EXIT )
        expr = None

        if self.curr.class_ == Class.LPAREN:
            self.eat( Class.LPAREN )
            expr = self.logic()
            self.eat( Class.RPAREN )
        
        return ast.Exit( expr )
    # def block( self ):
    #     nodes = []
    #     while self.curr.class_ != Class.RBRACE:
    #         if self.curr.class_ == Class.IF:
    #             nodes.append( self.if_() )
    #         elif self.curr.class_ == Class.WHILE:
    #             nodes.append( self.while_() )
    #         elif self.curr.class_ == Class.FOR:
    #             nodes.append( self.for_() )
    #         elif self.curr.class_ == Class.BREAK:
    #             nodes.append( self.break_() )
    #         elif self.curr.class_ == Class.CONTINUE:
    #             nodes.append( self.continue_() )
    #         elif self.curr.class_ == Class.RETURN:
    #             nodes.append( self.return_() )
    #         elif self.curr.class_ == Class.TYPE:
    #             nodes.append( self.decl() )
    #         elif self.curr.class_ == Class.ID:
    #             nodes.append( self.id_() )
    #             self.eat( Class.SEMICOLON )
    #         else:
    #             self.die_deriv( self.block.__name__ )
    #     return Block( nodes )

    # def params( self ):
    #     params = []
    #     while self.curr.class_ != Class.RPAREN:
    #         if len( params ) > 0:
    #             self.eat( Class.COMMA )
    #         type_ = self.type_()
    #         id_ = self.id_()
    #         params.append( Decl( type_, id_ ) )
    #     return Params( params )

    def args( self ):
        args = []
        while self.curr.class_ != Class.RPAREN:
            if len( args ) > 0:
                self.eat( Class.COMMA )

            value =  self.expr()
            fmt1, fmt2 = None, None

            # This is stupid handler for stupid float rounding...
            if self.curr.class_ == Class.COLON:
                self.eat( Class.COLON )
                fmt1 = ast.Int( self.curr.lexeme )
                self.eat( Class.INTEGER )
                
                self.eat( Class.COLON )
                fmt2 = ast.Int( self.curr.lexeme )
                self.eat( Class.INTEGER )

            args.append( ast.Argument( value, ( fmt1, fmt2 ) ) )

        return ast.Args( args )

    # def elems( self ):
    #     elems = []
    #     while self.curr.class_ != Class.RBRACE:
    #         if len( elems ) > 0:
    #             self.eat( Class.COMMA )
    #         elems.append( self.expr() )
    #     return Elems( elems )

    # def return_( self ):
    #     self.eat( Class.RETURN )
    #     expr = self.expr()
    #     self.eat( Class.SEMICOLON )
    #     return Return( expr )

    # def break_( self ):
    #     self.eat( Class.BREAK )
    #     self.eat( Class.SEMICOLON )
    #     return Break()

    # def continue_( self ):
    #     self.eat( Class.CONTINUE )
    #     self.eat( Class.SEMICOLON )
    #     return Continue()

    # def type_( self ):
    #     type_ = Type( self.curr.lexeme )
    #     self.eat( Class.TYPE )
    #     return type_

    def factor( self ):
        if self.curr.class_ == Class.INTEGER:
            value = ast.Int( self.curr.lexeme )
            self.eat( Class.INTEGER )

            return value

        elif self.curr.class_ == Class.CHAR:
            value = ast.Char( self.curr.lexeme )
            self.eat( Class.CHAR )

            return value
            
        elif self.curr.class_ == Class.STRING:
            value = ast.String( self.curr.lexeme )
            self.eat( Class.STRING )

            return value

        elif self.curr.class_ == Class.BOOLEAN:
            value = ast.Boolean( self.curr.lexeme )
            self.eat( Class.BOOLEAN )

            return value

        elif self.curr.class_ == Class.ID:
            return self.id_()

        elif self.curr.class_ in [ Class.MINUS, Class.NOT ]:
            op = self.curr
            self.eat( self.curr.class_ )
            first = None

            if self.curr.class_ == Class.LPAREN:
                self.eat( Class.LPAREN )
                first = self.logic()
                self.eat( Class.RPAREN )

            else:
                first = self.factor()

            return ast.UnOp( op.lexeme, first )
        elif self.curr.class_ == Class.LPAREN:

            self.eat( Class.LPAREN )
            first = self.logic()
            self.eat( Class.RPAREN )

            return first
            
        elif self.curr.class_ == Class.SEMICOLON:
            return None

        else:
            self.die_deriv( self.factor.__name__ )

    def term( self ):
        first = self.factor()
        while self.curr.class_ in [ Class.STAR, Class.FWDSLASH, Class.MOD, Class.DIV ]:

            if self.curr.class_ == Class.STAR:
                op = self.curr.lexeme
                self.eat( Class.STAR )
                second = self.factor()
                first = ast.BinOp( op, first, second )

            elif self.curr.class_ == Class.FWDSLASH:
                op = self.curr.lexeme
                self.eat( Class.FWDSLASH )
                second = self.factor()
                first = ast.BinOp( op, first, second )

            elif self.curr.class_ == Class.MOD:
                op = self.curr.lexeme
                self.eat( Class.MOD )
                second = self.factor()
                first = ast.BinOp( op, first, second )
            
            elif self.curr.class_ == Class.DIV:
                op = self.curr.lexeme
                self.eat( Class.DIV )
                second = self.factor()
                first = ast.BinOp( op, first, second )
            

        return first

    def expr( self ):
        first = self.term()

        while self.curr.class_ in [ Class.PLUS, Class.MINUS ]:

            if self.curr.class_ == Class.PLUS:
                op = self.curr.lexeme
                self.eat( Class.PLUS )
                second = self.term()
                first = ast.BinOp( op, first, second )

            elif self.curr.class_ == Class.MINUS:
                op = self.curr.lexeme
                self.eat( Class.MINUS )
                second = self.term()
                first = ast.BinOp( op, first, second )

        return first

    def compare( self ):
        first = self.expr()
        if self.curr.class_ == Class.EQ:
            op = self.curr.lexeme
            self.eat( Class.EQ )
            second = self.expr()
            return ast.BinOp( op, first, second )
        elif self.curr.class_ == Class.NEQ:
            op = self.curr.lexeme
            self.eat( Class.NEQ )
            second = self.expr()
            return ast.BinOp( op, first, second )
        elif self.curr.class_ == Class.LT:
            op = self.curr.lexeme
            self.eat( Class.LT )
            second = self.expr()
            return ast.BinOp( op, first, second )
        elif self.curr.class_ == Class.GT:
            op = self.curr.lexeme
            self.eat( Class.GT )
            second = self.expr()
            return ast.BinOp( op, first, second )
        elif self.curr.class_ == Class.LTE:
            op = self.curr.lexeme
            self.eat( Class.LTE )
            second = self.expr()
            return ast.BinOp( op, first, second )
        elif self.curr.class_ == Class.GTE:
            op = self.curr.lexeme
            self.eat( Class.GTE )
            second = self.expr()
            return ast.BinOp( op, first, second )
        else:
            return first

    def logic_term( self ):
        first = self.compare()
        while self.curr.class_ == Class.AND:
            op = self.curr.lexeme
            self.eat( Class.AND )
            second = self.compare()
            first = ast.BinOp( op, first, second )
        return first

    def logic( self ):
        first = self.logic_term()
        while self.curr.class_ == Class.OR:
            op = self.curr.lexeme
            self.eat( Class.OR )
            second = self.logic_term()
            first = ast.BinOp( op, first, second )
        return first

    @restorable
    def is_func_call( self ):
        try:
            self.eat( Class.LPAREN )
            self.args()
            self.eat( Class.RPAREN )

            return self.curr.class_ != Class.LPAREN
        except:
            return False

    def parse( self ):
        return self.program()

    def die( self, text ):
        print( f'Error occured after { self.semicolomn_counter } \';\'' )
        raise SystemExit( text )

    def die_deriv( self, fun ):
        self.die( "Derivation error: {}".format( fun ) )

    def die_type( self, expected, found ):
        self.die( "Expected: {}, Found: {}".format( expected, found ) )

    # def decl( self ):
    #     type_ = self.type_()
    #     id_ = self.id_()
    #     if self.curr.class_ == Class.LBRACKET:
    #         self.eat( Class.LBRACKET )
    #         size = None
    #         if self.curr.class_ != Class.RBRACKET:
    #             size = self.expr()
    #         self.eat( Class.RBRACKET )
    #         elems = None
    #         if self.curr.class_ == Class.ASSIGN:
    #             self.eat( Class.ASSIGN )
    #             self.eat( Class.LPAREN )
    #             elems = self.elems()
    #             self.eat( Class.RBRACE )
    #         self.eat( Class.SEMICOLON )
    #         return ArrayDecl( type_, id_, size, elems )
    #     elif self.curr.class_ == Class.LPAREN:
    #         self.eat( Class.LPAREN )
    #         params = self.params()
    #         self.eat( Class.RPAREN )
    #         self.eat( Class.LBRACE )
    #         block = self.block()
    #         self.eat( Class.RBRACE )
    #         return FuncImpl( type_, id_, params, block )
    #     else:
    #         self.eat( Class.SEMICOLON )
    #         return Decl( type_, id_ )
