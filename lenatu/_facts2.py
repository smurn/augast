'''
Created on 19.11.2015

@author: stefan
'''

import sys

if sys.version_info < (3,0):
        
    import ast
    
    # --------------------
    # Definition of blocks
    # --------------------
    
    #: AST types that define a new block
    DEFINER = (
        ast.Module,
        ast.Interactive,
        ast.Expression,
        ast.Suite,
        ast.FunctionDef,
        ast.ClassDef,
        ast.Lambda,
        ast.GeneratorExp
    )
    
    # -----------------------------------
    # Block to which a child node belongs
    # -----------------------------------
    
    
    #: child node belongs to the block that executed the parent 
    EXEC = "exec"
    
    #: child node belongs to the block that the parent defines
    DEFINED = "defined"
    
    #: the child node has children that belong to both, the block that the parent
    #: executes in, and the block the parent defines.
    MIXED = "mixed"
    
    #: maps (node-type, attribute-name) to either EXEC, DEFINED, or MIXED.
    #: If a combination is missing, it is EXEC.
    CHILD_BLOCK = { # default is EXEC
        (ast.Module, "body"): DEFINED,
        (ast.Interactive, "body"): DEFINED,
        (ast.Expression, "body"):DEFINED,
        (ast.Suite, "body"):DEFINED,
        (ast.FunctionDef, "body"):DEFINED,
        (ast.FunctionDef, "args"):MIXED,
        (ast.ClassDef, "body"):DEFINED,
        (ast.Lambda, "body"):DEFINED,
        (ast.Lambda, "args"):MIXED,
        (ast.GeneratorExp, "elt"):DEFINED,
        (ast.GeneratorExp, "generators"):DEFINED,
        (ast.arguments, "args"):DEFINED,
        (ast.arguments, "vararg"):DEFINED,
        (ast.arguments, "kwarg"):DEFINED
    }
    
    
    
    # -------------------------------------------------
    # Identifier that refer to variables.
    # -------------------------------------------------
    
    #: Code assigns the variable
    ASSIGNED = "assigned"
    
    #: Code reads the variable
    READ = "read"
    
    #: Code explicitly declares the variable as global
    GLOBAL = "global"
    
    #: Code explicitly declares the variable as nonlocal
    NONLOCAL = "nonlocal"
    
    
    def _name_fields(node):
        if isinstance(node.ctx, (ast.Load, ast.AugLoad)):
            return [("id", READ, EXEC)]
        else:
            return [("id", ASSIGNED, EXEC)]
    
    def _alias_fields(node):
        if node.asname is None:
            return [("name", ASSIGNED, EXEC)]
        else:
            return [("asname", ASSIGNED, EXEC)]
            
    
    #: Maps node-type to a function that takes the node (of that type) as
    #: a parameter. The function returns a list of (attribute-name, usage) tuples
    #: for each attribute of that node which is referring to a variable.
    NAME_FIELDS = {
        ast.FunctionDef: lambda n:[("name", ASSIGNED, EXEC)],
        ast.ClassDef: lambda n:[("name", ASSIGNED, EXEC)],
        ast.Global: lambda n:[("names", GLOBAL, EXEC)],
        ast.Name: _name_fields,
        ast.ExceptHandler: lambda n:[("name", ASSIGNED, EXEC)],
        ast.arguments: lambda n:[("vararg", ASSIGNED, DEFINED), ("kwarg", ASSIGNED, DEFINED)],
        ast.alias: _alias_fields
    }
    
    
    def is_local_variable(usages):
        """
        Given the set of usages of a variable within a block, return if this
        variable is in the scope of this block.
        """
        return ASSIGNED in usages and GLOBAL not in usages and NONLOCAL not in usages
    
    
    def are_locals_visible_to_childen(block):
        """
        Are variables that are local to the given block visible to blocks declared
        within this block?
        
        This is the case for all blocks but those of classes.
        """
        return not isinstance(block.defined_by, ast.ClassDef)