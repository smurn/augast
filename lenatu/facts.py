'''
Created on 19.11.2015

@author: stefan
'''
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
if hasattr(ast, "AsyncFunctionDef"):
    DEFINER += (ast.AsyncFunctionDef, )


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
    (ast.arguments, "args"):MIXED,
    (ast.arguments, "vararg"):MIXED,
    (ast.arguments, "kwonlyargs"):MIXED,
    (ast.arguments, "kwarg"):MIXED,
    (ast.arg, "arg"):DEFINED,
}
if hasattr(ast, "AsyncFunctionDef"): 
    # Python 3.5+
    for (t, f), k in dict(CHILD_BLOCK).items():
        if t == ast.FunctionDef:
            CHILD_BLOCK[(ast.AsyncFunctionDef, f)] = k



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
        return [("id", READ)]
    else:
        return [("id", ASSIGNED)]

def alias_fields(node):
    if node.asname is None:
        return [("name", ASSIGNED)]
    else:
        return [("asname", ASSIGNED)]
        

#: Maps node-type to a function that takes the node (of that type) as
#: a parameter. The function returns a list of (attribute-name, usage) tuples
#: for each attribute of that node which is referring to a variable.
NAME_FIELDS = {
    ast.FunctionDef: lambda n:[("name", ASSIGNED)],
    ast.ClassDef: lambda n:[("name", ASSIGNED)],
    ast.Global: lambda n:[("names", GLOBAL)],
    ast.Nonlocal: lambda n:[("names", NONLOCAL)],
    ast.Name: _name_fields,
    ast.ExceptHandler: lambda n:[("name", ASSIGNED)],
    ast.arg: lambda n:[("arg", ASSIGNED)],
    ast.alias: alias_fields
}


