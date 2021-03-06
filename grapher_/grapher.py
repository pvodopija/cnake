from graphviz import Digraph, Source
from visitor_.visitor import Visitor

class Grapher( Visitor ):
    def __init__(self, ast):
        self.ast = ast
        self._count = 1
        self.dot = Digraph()
        self.dot.node_attr['shape'] = 'box'
        self.dot.node_attr['height'] = '0.1'
        self.dot.edge_attr['arrowsize'] = '0.5'

    def add_node(self, parent, node, name=None):
        node._index = self._count
        self._count += 1
        caption = type(node).__name__

        if name is not None:
            caption = '{} : {}'.format(caption, name)
            
        self.dot.node('node{}'.format(node._index), caption)

        if parent is not None:
            self.add_edge(parent, node)

    def add_edge(self, parent, node):
        src, dest = parent._index, node._index
        self.dot.edge('node{}'.format(src), 'node{}'.format(dest))

    def visit_Program(self, parent, node):
        self.add_node(parent, node)
        for n in node.nodes:
            self.visit(node, n)
    
    def visit_FuncImpl(self, parent, node):
        self.add_node(parent, node)
        self.visit(node, node.id_)
        self.visit(node, node.params)
        if node.ret_type != None:
            self.visit(node, node.ret_type)
        self.visit(node, node.block)

    def visit_Block(self, parent, node):
        self.add_node(parent, node)
        if node.var_block != None:
            self.visit( node, node.var_block )
        self.visit( node, node.code_block )
        # for n in node.nodes:
        #     self.visit(node, n)

    def visit_VarBlock(self, parent, node):
        self.add_node(parent, node)

        for var in node.nodes:
            self.visit(node, var)

    def visit_CodeBlock(self, parent, node):
        self.add_node(parent, node)
        
        for instr in node.nodes:
            self.visit(node, instr)


    def visit_Params(self, parent, node):
        self.add_node(parent, node)
        for p in node.params:
            self.visit(node, p)
        
        # self.visit( node, node.type_ )

    def visit_Decl(self, parent, node):
        self.add_node(parent, node)
        self.visit(node, node.type_)
        self.visit(node, node.id_)

    def visit_ArrayDecl(self, parent, node):
        self.add_node(parent, node)
        self.visit(node, node.type_)
        self.visit(node, node.id_)

        if node.size is not None:
            self.visit(node, node.size)
        if node.elems is not None:
            self.visit(node, node.elems)

    def visit_StringDecl( self, parent, node ):
        self.add_node( parent, node )
        self.visit( node, node.id_ )

        self.visit( node, node.size )

    def visit_ArrayElem(self, parent, node):
        self.add_node(parent, node)
        self.visit(node, node.id_)
        self.visit(node, node.index)

    def visit_Assign(self, parent, node):
        self.add_node(parent, node)
        self.visit(node, node.id_)
        self.visit(node, node.expr)

    def visit_If(self, parent, node):
        self.add_node(parent, node)
        self.visit(node, node.cond)
        self.visit(node, node.true)
        if node.false is not None:
            self.visit(node, node.false)

    def visit_While(self, parent, node):
        self.add_node(parent, node)
        self.visit(node, node.cond)
        self.visit(node, node.block)
    
    def visit_Repeat(self, parent, node):
        self.add_node(parent, node)
        self.visit( node, node.condition )
        
        for instr_node in node.instructions:
            self.visit( node, instr_node )

    def visit_For(self, parent, node):
        self.add_node(parent, node)
        self.visit(node, node.init)
        self.visit(node, node.limit)
        self.visit(node, node.block)

    def visit_FuncCall(self, parent, node):
        self.add_node(parent, node)
        self.visit(node, node.id_)
        self.visit(node, node.args)

    def visit_Args(self, parent, node):
        self.add_node(parent, node)
        for a in node.args:
            self.visit(node, a)

    def visit_Argument(self, parent, node):
        self.visit( parent, node.value )

    def visit_Elems(self, parent, node):
        self.add_node(parent, node)
        if node.elems is not None:
            for e in node.elems:
                self.visit(node, e)

    def visit_Break(self, parent, node):
        self.add_node(parent, node)

    def visit_Continue(self, parent, node):
        self.add_node(parent, node)

    def visit_Exit(self, parent, node):
        self.add_node(parent, node)

        if node.expr is not None:
            self.visit(node, node.expr)

    def visit_Return(self, parent, node):
        self.add_node(parent, node)
        if node.expr is not None:
            self.visit(node, node.expr)

    def visit_Type(self, parent, node):
        name = node.value
        self.add_node(parent, node, name)

    def visit_Int(self, parent, node):
        name = node.value
        self.add_node(parent, node, name)

    def visit_Boolean(self, parent, node):
        name = node.value
        self.add_node(parent, node, name)

    def visit_Char(self, parent, node):
        name = node.value
        self.add_node(parent, node, name)

    def visit_String(self, parent, node):
        name = node.value
        self.add_node(parent, node, name)

    def visit_Id(self, parent, node):
        name = node.value
        self.add_node(parent, node, name)
 
    def visit_BinOp(self, parent, node):
        name = node.symbol
        self.add_node(parent, node, name)
        self.visit(node, node.first)
        self.visit(node, node.second)

    def visit_UnOp(self, parent, node):
        name = node.symbol
        self.add_node(parent, node, name)
        self.visit(node, node.first)

    def graph(self):
        self.visit(None, self.ast)
        s = Source(self.dot.source, filename='graph', format='png')
        return s