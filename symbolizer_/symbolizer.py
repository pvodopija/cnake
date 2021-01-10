from .symbols import Symbols
from visitor_.visitor import Visitor
from parser_ import ast

class Symbolizer(Visitor):
    def __init__(self, ast):
        self.ast = ast

    def visit_Program(self, parent, node):
        node.symbols = Symbols()

        for n in node.nodes:
            self.visit(node, n)

    def visit_Block(self, parent, node):
        if node.var_block is not None:

            if isinstance( parent, ast.FuncImpl ):
                node.symbols = parent.symbols
            else:
                node.symbols = Symbols()

            self.visit( node, node.var_block )
        else:
            node.symbols = parent.symbols
        
        
        self.visit( node, node.code_block )
        # for n in node.nodes:
        #     self.visit(node, n)
    
    def visit_VarBlock( self, parent, node ):
        node.symbols = parent.symbols

        for n in node.nodes:
            if isinstance( n, ast.Decl ):
                parent.symbols.put( n.id_.value, n.type_.value, id( parent.symbols ) )

            elif isinstance( n, ast.ArrayDecl ):
                parent.symbols.put( n.id_.value, n.type_.value, id( parent.symbols ) )

            # TODO: Check this.
            elif isinstance( n, ast.StringDecl ):
                parent.symbols.put( n.id_.value, 'string', id( parent.symbols ) )

    def visit_CodeBlock( self, parent, node ):
        node.symbols = parent.symbols

        for n in node.nodes:
            self.visit( node, n )
    
    def visit_FuncImpl(self, parent, node):
        node.symbols = Symbols()
        parent.symbols.put( node.id_.value, 'function', id( parent.symbols ) ) # TODO: CHANGE.
        self.visit(node, node.params)
        self.visit(node, node.block)
    
    def visit_Params(self, parent, node):
        node.symbols = parent.symbols
        for p in node.params:
            node.symbols.put( p.value, node.type_, id( node.symbols ) )
            self.visit(node, p)
            # self.visit(parent.block, p)

    def visit_Decl(self, parent, node):
        node.symbols = parent.symbols
        node.symbols.put( node.id_.value, node.type_.value, id( parent.symbols ) )
        self.visit( node, node.id_ )

    def visit_ArrayDecl(self, parent, node):
        node.symbols = parent.symbols
        parent.symbols.put(node.id_.value, node.type_.value, id( parent.symbols ) )
    
    def visit_StringDecl(self, parent, node):
        node.symbols = parent.symbols
        parent.symbols.put(node.id_.value, node.type_.value, id( parent.symbols ) )

    def visit_ArrayElem(self, parent, node):
        node.symbols = parent.symbols
        self.visit( node, node.id_ )
        self.visit( node, node.index )

    def visit_Assign(self, parent, node):
        node.symbols = parent.symbols
        self.visit( node, node.id_ )
        self.visit( node, node.expr )

    def visit_If(self, parent, node):
        node.symbols = parent.symbols
        
        self.visit( node, node.cond )

        self.visit(node, node.true)
        
        if node.false is not None:
            self.visit(node, node.false)

    def visit_While(self, parent, node):
        node.symbols = parent.symbols
        self.visit( node, node.cond )
        self.visit(node, node.block)

    def visit_For(self, parent, node):
        node.symbols = parent.symbols
        self.visit( node, node.init )
        self.visit( node, node.limit )
        self.visit(node, node.block)
    
    def visit_Repeat(self, parent, node):
        node.symbols = parent.symbols

        for n in node.instructions:
            self.visit( node, n )       
    
        self.visit( node, node.condition )

    def visit_Exit( self, parent, node ):
        node.symbols = parent.symbols
        if node.expr is not None:
            self.visit( node, node.expr )

    def visit_FuncCall(self, parent, node):
        node.symbols = parent.symbols
        self.visit( node, node.args )

    def visit_Args(self, parent, node):
        node.symbols = parent.symbols
        for arg in node.args:
            self.visit( node, arg )

    def visit_Argument(self, parent, node):
        node.symbols = parent.symbols
        self.visit( node, node.value )

    def visit_Elems(self, parent, node):
        pass

    def visit_Break(self, parent, node):
        pass

    def visit_Continue(self, parent, node):
        pass

    def visit_Return(self, parent, node):
        pass

    def visit_Type(self, parent, node):
        pass

    def visit_Int(self, parent, node):
        pass
    
    def visit_Boolean(self, parent, node):
        pass

    def visit_Char(self, parent, node):
        pass

    def visit_String(self, parent, node):
        pass

    def visit_Id(self, parent, node):
        node.symbols = parent.symbols

    def visit_BinOp(self, parent, node):
        node.symbols = parent.symbols
        self.visit( node, node.first )
        self.visit( node, node.second )

    def visit_UnOp(self, parent, node):
        node.symbols = parent.symbols
        self.visit( node, node.first )

    def symbolize(self):
        self.visit(None, self.ast)