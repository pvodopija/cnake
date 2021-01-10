import sys
from lexer.lexer import Lexer
from parser_.parser import Parser
from grapher_.grapher import Grapher
from generator_.generator import Generator
from symbolizer_.symbolizer import Symbolizer
from runner_.runner import Runner

def main( argv ):
    with open( argv[1] ) as file:
        text = file.read()

        # print( text )
        lexer = Lexer( text )
        tokens = lexer.tokenize()

        # print( tokens )
        # print( '#' * 100 )

        parser = Parser( tokens )
        ast = parser.parse()
        
        # grapher = Grapher( ast )
        # source = grapher.graph()
        # source.view()
        
        symbolizer = Symbolizer( ast )
        symbolizer.symbolize()

        # print( '#' * 100 )
        
        generator = Generator( ast )
        generator.generate( argv[2] )

        # # print( '#' * 100 )

        runner = Runner( ast )
        runner.run()


if __name__ == "__main__":
    main( sys.argv )