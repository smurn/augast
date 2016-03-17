from lenatu._block import Block, augment_blocks
from lenatu._scope import augment_scopes

def augment(node):
    augment_blocks(node)
    augment_scopes(node.defined_block)
    
