from lenatu.facts import *  # @UnusedWildImport

class Block:
    """
    A block is a sequence of statements that form a unit (think stack-frame). 
    
    The bodies of modules, classes, and functions are in blocks belonging to those. Generators
    have a block too.
    
    Blocks can be nested, and are important to decide the scope of a variable.
    
    .. attribute:: defined_by
    
        Node that defines this block. For example a `ast.Function` or `ast.Module`.
    """
    
    def __init__(self, defined_by):
        self.defined_by = defined_by



def visit(node, executed_in=None, defined_block=None):
    """
    :param node: The node we visit
    :param executed_in The block this node is executed in
    :param defined_block The block this node helps to define.
    
    We differentiate between three types of AST nodes:
    
    * Regular nodes like `ast.BinOp` that are executed in a block,
      as are all the nodes they reference.
      
      `visit` is invoked with `executed_in`, but `defined_block` is
      `None.
      
    * Nodes that define a new block, such as `ast.Module` and 
      `ast.FunctionDef`. There are two blocks involved here, the block
      in which they are executed, and the new block they define for their
      body. Some attributes will belong to the new block, others to the
      block in which the node is executed in. Some will be of the third
      type (see below).
      
      `visit` is invoked with `executed_in`, but `defined_block` is
      `None. The later might seem surprising, but the caller does not have
      the defined block, the `visit` of a definer node will create it.
      
    * Nodes that provide additional information to a definer block, such
      as `ast.Arg`. These are similar to definer blocks as they are 
      have attributes that belong to the new block, others to the
      block in which the definer block is executed in.
      
      `visit` is invoked with `executed_in` set to the block in which
      the definer block they belong to is executed in. `defined_block`
      is set to the block defined by their definer node.
      
    """
    if executed_in is None and not isinstance(node, ast.mod):
        raise ValueError("Expected top-level node (one of the ast.mod types)")
    
    if executed_in is not None:
        node.executed_in = executed_in
        
    if isinstance(node, DEFINER):
        defined_block = Block(node)
        
    if defined_block is not None:
        node.defined_block = defined_block
        
    for field, value in ast.iter_fields(node):
        kind = SPECIAL.get((type(node), field), EXEC)
        
        if kind == EXEC:
            visit_helper(value, executed_in=executed_in, defined_block=None)
        elif kind == DEFINED:
            visit_helper(value, executed_in=defined_block, defined_block=None)
        elif kind == MIXED:
            visit_helper(value, executed_in=executed_in, defined_block=defined_block)
        else:
            raise ValueError("unexpected field kind %r" % kind)


def visit_helper(value, executed_in=None, defined_block=None):
    if isinstance(value, list):
        for v in value:
            visit_helper(v, executed_in=executed_in, defined_block=defined_block)
    
    elif isinstance(value, ast.AST):
        visit(value, executed_in=executed_in, defined_block=defined_block)


def augment(node):
    """
    Analyze the AST add/overwrite the attributes described in the documentation.
    """
    visit(node)

                
__all__ = ["augment"]