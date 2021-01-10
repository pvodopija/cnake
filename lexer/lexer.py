from enum import Enum, auto

class Class( Enum ):
    # Syntax
    ASSIGN = auto()         # :=
    COLON = auto()          # :
    DOT = auto()            # .
    SEMICOLON = auto()      # ;
    COMMA = auto()          # ,
    BEGIN = auto()          # begin
    END = auto()            # end
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    NEWLINE = auto()        # \n

    # Data types.
    VAR = auto()            # var
    TYPE = auto()           
    INTEGER = auto()
    REAL = auto()
    BOOLEAN = auto()
    CHAR = auto()
    STRING = auto()

    # Identifier ( variable and function names )
    ID = auto()

    # Arithmetic operators.
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    FWDSLASH = auto()       # /
    DIV = auto()            # div
    MOD = auto()            # mod

    # Logic operators.
    NOT = auto()
    AND = auto()
    OR = auto()
    XOR = auto()

    # Relational operators.
    EQ = auto()             # =
    NEQ = auto()            # <>
    LT = auto()             # <   
    GT = auto()             # >
    LTE = auto()            # >=
    GTE = auto()            # <=

    # Flow control keywords.
    REPEAT = auto()
    UNTIL = auto()
    WHILE = auto()
    FOR = auto()
    TO = auto()
    DOWNTO = auto()
    BREAK = auto()
    CONTINUE = auto()
    DO = auto()
    IF = auto()             
    ELSE = auto()
    THEN = auto()
    FUNCTION = auto()
    PROCEDURE = auto()
    EXIT = auto()

    # Array declarations.
    ARRAY = auto()
    OF = auto()

    # End Of File.
    EOF = auto()

class Token:

    def __init__( self, class_, lexeme ):
        self.class_ = class_
        self.lexeme = lexeme

    def __str__( self ):
        return "<{} {}>".format( self.class_, self.lexeme )
    
    def __repr__( self ):
        return self.__str__()

class Lexer:
    def __init__( self, text ):
        self.text = text
        self.pos = -1
        self.len = len( text )
        self.line_number = 0

    
    def next_char( self ):
        
        self.pos += 1

        if self.pos >= self.len:
            return None

        if self.text[ self.pos ] == '\n':
            self.line_number += 1

        return self.text[ self.pos ]
    


    def read_space( self ):
        
        while self.pos + 1 < self.len and self.text[ self.pos + 1 ].isspace():
           self.next_char()



    def read_int( self ):
        
        lexeme = self.text[ self.pos ]
        
        while self.pos + 1 < self.len and self.text[ self.pos + 1 ].isdigit():
            lexeme += self.next_char()

        return int( lexeme )



    def read_keyword( self ):
        
        lexeme = self.text[ self.pos ]

        # If not a keyword, then its an identifier.
        while self.pos + 1 < self.len and self.text[ self.pos + 1 ].isalnum() or self.text[ self.pos + 1 ] == '_':
            lexeme += self.next_char()

        # Block syntax.
        if lexeme == 'begin':
            return Token( Class.BEGIN, lexeme )
        elif lexeme == 'end':
            return Token( Class.END, lexeme )

        # Data types.
        elif lexeme == 'var':
            return Token( Class.VAR, lexeme )
        
        elif lexeme == 'integer' or lexeme == 'real' or lexeme == 'boolean' or lexeme == 'char' or lexeme == 'string':
            return Token( Class.TYPE, lexeme )
        
        # Array declarations.
        elif lexeme == 'array':
            return Token( Class.ARRAY, lexeme )
        elif lexeme == 'of':
            return Token( Class.OF, lexeme )
        
        # Arithmetic operators.
        elif lexeme == 'div':
            return Token( Class.DIV, lexeme )
        elif lexeme == 'mod':
            return Token( Class.MOD, lexeme )

        # Logic operators.
        elif lexeme == 'not':
            return Token( Class.NOT, lexeme )
        elif lexeme == 'and':
            return Token( Class.AND, lexeme )
        elif lexeme == 'or':
            return Token( Class.OR, lexeme )
        elif lexeme == 'xor':
            return Token( Class.MOD, lexeme )

        # Flow control.
        elif lexeme == 'if':
            return Token( Class.IF, lexeme )
        elif lexeme == 'else':
            return Token( Class.ELSE, lexeme )
        elif lexeme == 'then':
            return Token( Class.THEN, lexeme )
        elif lexeme == 'repeat':
            return Token( Class.REPEAT, lexeme )
        elif lexeme == 'until':
            return Token( Class.UNTIL, lexeme )
        elif lexeme == 'while':
            return Token( Class.WHILE, lexeme )
        elif lexeme == 'for':
            return Token( Class.FOR, lexeme )
        elif lexeme == 'to':
            return Token( Class.TO, lexeme )
        elif lexeme == 'downto':
            return Token( Class.DOWNTO, lexeme )
        elif lexeme == 'do':
            return Token( Class.DO, lexeme )    
        elif lexeme == 'break':
            return Token( Class.BREAK, lexeme )
        elif lexeme == 'continue':
            return Token( Class.CONTINUE, lexeme )
        elif lexeme == 'function':
            return Token( Class.FUNCTION, lexeme )
        elif lexeme == 'procedure':
            return Token( Class.PROCEDURE, lexeme )
        elif lexeme == 'true' or lexeme == 'false':
            return Token( Class.BOOLEAN, lexeme)
        elif lexeme == 'exit':
            return Token( Class.EXIT, lexeme )
        
        return Token( Class.ID, lexeme )



    def read_string( self ):
        lexeme = ''
        while self.pos + 1 < self.len and self.text[ self.pos + 1 ] != '\'':
            lexeme += self.next_char()
        self.pos += 1
        return lexeme

    def die( self, char ):
        raise SystemExit( f'Unexpected character { char } at line at line { self.line_number }' )

    def next_token( self ):

        self.read_space()
        
        curr = self.next_char()

        if curr is None:
            return Token( Class.EOF, curr )

        token = None

        # Boolean type is handled in keywords.
        if curr.isalpha():
            token = self.read_keyword()
        elif curr.isdigit():
            token = Token( Class.INTEGER, self.read_int() )
        elif curr == '\'':
            if self.text[ self.pos + 2 ] == '\'':
                token = Token( Class.CHAR, self.read_string() )
            else:
                token = Token( Class.STRING, self.read_string() )

        # Syntax.
        elif curr == ':':
            curr = self.next_char()
            if curr == '=':
                token = Token( Class.ASSIGN, ':=' )
            else:
                token = Token( Class.COLON, ':' )
                self.pos -= 1
        elif curr == '.':
            token = Token( Class.DOT, curr )
        elif curr == ';':
            token = Token( Class.SEMICOLON, curr )
        elif curr == ',':
            token = Token( Class.COMMA, curr )
        elif curr == '(':
            token = Token( Class.LPAREN, curr )
        elif curr == ')':
            token = Token( Class.RPAREN, curr )
        elif curr == '[':
            token = Token( Class.LBRACKET, curr )
        elif curr == ']':
            token = Token( Class.RBRACKET, curr )
        # elif curr == '\n':
        #     token = Token( Class.NEWLINE, '\\n' )

        # Arithmetic operators.
        elif curr == '+':
            token = Token( Class.PLUS, curr ) 
        elif curr == '-':
            token = Token( Class.MINUS, curr )
        elif curr == '*':
            token = Token( Class.STAR, curr )
        elif curr == '/':
            token = Token( Class.FWDSLASH, curr )
        
        # Relational operators.
        elif curr == '=':
            token = Token( Class.EQ, curr )
        elif curr == '<':
            curr = self.next_char()
            if curr == '>':
                token = Token( Class.NEQ, '<>' )
            elif curr == '=':
                token = Token( Class.LTE, '<=' )
            else:
                token = Token( Class.LT, '<' )
                self.pos -= 1
        elif curr == '>':
            curr = self.next_char()
            if curr == '=':
                token = Token( Class.GTE, '>=' )
            else:
                token = Token( Class.GT, '>' )
                self.pos -= 1

        else:
            self.die( curr )


        return token
    

    def tokenize( self ):
        tokens = []
        
        while True:
            curr = self.next_token()
            tokens.append( curr )
            # print( curr )
            if curr.class_ == Class.EOF:
                break

        return tokens