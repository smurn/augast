import ast
from lenatu import _facts as facts
import collections


def _nodes_of_block(block):
    """
    Returns nodes that define or execute the given block.
    """
    def visit(node):
        if getattr(node, "executed_in", block) is block or getattr(node, "defined_block", None) is block:
            yield node
            for child in ast.iter_child_nodes(node):
                yield from visit(child)

    return visit(block.defined_by)
    
    
def _variable_accesses_in(block):
    """
    Returns (node, attribute, variable-name, usage) tuples for all
    accesses to variables by code executed in the given block.
    """
    for node in _nodes_of_block(block):
        
        defined_block = getattr(node, "defined_block", None)
        executed_in = getattr(node, "executed_in", None)
        
        f = facts.NAME_FIELDS.get(type(node), lambda _:[])
        for attribute, usage, which_block in f(node):
            
            accessed_block = defined_block if which_block == facts.DEFINED else executed_in
            if (accessed_block == block):  
                value = getattr(node, attribute)
                if isinstance(value, list):
                    for v in value:
                        yield (node, attribute, v, usage)
                else:
                    yield (node, attribute, value, usage)

    
def _blocks_defined_in(block):
    """
    Returns blocks that are directly defined in the given block.
    """
    def visit(node):
        if getattr(node, "executed_in", None) is block or getattr(node, "defined_block", None) is block:
        
            if getattr(node, "executed_in", None) is block and getattr(node, "defined_block", block) is not block:
                yield node.defined_block
                # no need to look inside the children of this node. We'll only find
                # the same block again.
            else:
                for child in ast.iter_child_nodes(node):
                    yield from visit(child)
                           
    return visit(block.defined_by)
    
    
def _scope_lookup(identifier, usages, blocks):
    """
    Find the block the given identifier belongs to.
        
    We search backwards, starting with block[-1]. block[0] must be a module.
    
    Blocks from classes are ignored (with the exception of `block[-1]).
    """
    
    if not isinstance(blocks[0].defined_by, ast.Module):
        raise ValueError("block[0] should be a module.")

    if facts.GLOBAL in usages:
        return blocks[0]
    
    for block in reversed(blocks):
        if block == blocks[-1]:
            if facts.NONLOCAL in usages:
                continue # don't look in the local block
        else:
            if not facts.are_locals_visible_to_childen(block):
                continue # skip over enclosing class-blocks 
            
        if identifier in block.local_variables:
            return block
    else:
        # identifier is a global variable which isn't assigned directly in the module.
        return blocks[0]

            
def _assign_scopes(block, enclosing_blocks):
    """
    Sets `block.local_variables` and the `xyz_block` attributes of all
    nodes executed within `block`.
    
    :param enclosing_blocks: Enclosing blocks (without `block`). The module
        is `enclosing_blocks[0]` and the direct parent is `enclosing_blocks[-1]`.
        Empty if `block` is the module.
        All these blocks must have `local_variables` set already.
    """
    
    usages = collections.defaultdict(set)
    for _, _, identifier, usage in _variable_accesses_in(block):
        usages[identifier].add(usage) 
    
    
    local_variables = [identifier for identifier, usages in usages.items() if facts.is_local_variable(usages)]
    block.local_variables = local_variables
            
    # Variables used in this block are local to one of these blocks
    candidate_blocks = enclosing_blocks + [block]
        
    # For each used variable find the block that variable is defined in.
    scope_map = {identifier : _scope_lookup(identifier, usages, candidate_blocks) for identifier, usages in usages.items()}

    # Inject scopes into the AST nodes
    for node, attribute, _ , _ in _variable_accesses_in(block):
        variable = getattr(node, attribute)
        if isinstance(variable, list):
            scope = [scope_map[v] for v in variable]
        else:
            scope = scope_map[variable]
        setattr(node, attribute + "_block", scope)
        
            
def augment_scopes(block, enclosing_blocks=[]):
    """
    Augment the block and all sub-blocks with scope information.
    
    This will set the block's `local_variables` field and adds the 
    `xyz_block` attributes to the nodes.
    """
    _assign_scopes(block, enclosing_blocks)
    for child_block in _blocks_defined_in(block):
        augment_scopes(child_block, enclosing_blocks + [block])
    
    