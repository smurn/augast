'''
Created on 19.11.2015

@author: stefan
'''
import ast

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


EXEC = "exec"
DEFINED = "defined"
MIXED = "mixed"

SPECIAL = { # default is EXEC
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
    for (t, f), k in dict(SPECIAL).items():
        if t == ast.FunctionDef:
            SPECIAL[(ast.AsyncFunctionDef, f)] = k


ASSIGNED = "assigned"
READ = "read"
GLOBAL = "global"
NONLOCAL = "nonlocal"


def _name_ctx(node):
    if isinstance(node.ctx, (ast.Load, ast.AugLoad)):
        return READ
    else:
        return ASSIGNED
    

NAME_FIELDS = {
    (ast.FunctionDef, "name"): lambda n:ASSIGNED,
    (ast.ClassDef, "name"): lambda n:ASSIGNED,
    (ast.Global, "names"): lambda n:GLOBAL,
    (ast.Nonlocal, "names"): lambda n:NONLOCAL,
    (ast.Name, "id"): _name_ctx,
    (ast.ExceptHandler, "name"): lambda n:ASSIGNED,
    (ast.arg, "arg"): lambda n:ASSIGNED,
    (ast.alias, "asname"): lambda n:ASSIGNED # "name" too, but only if "asname" is None
}

