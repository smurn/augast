from lenatu.block import Block, augment_blocks
from lenatu.scope import augment_scopes

def augment(node):
    augment_blocks(node)
    augment_scopes(node.defined_block)