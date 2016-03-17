'''
Created on 16.11.2015

@author: stefan
'''
import unittest
from lenatu import tools
import ast
import lenatu

class BlockDetector(unittest.TestCase):
    
    def setUp(self):
        self.cache = {}
    
    def test_Module_def(self):
        src = """
        pass
        """
        self.assertTrue(isinstance(self.get(src, ".defined_block"), lenatu.Block))
        

    def test_FunctionDef_def(self):
        src = """
        def foo():
            pass
        """
        self.assertNotSame(src,
                           ".defined_block",
                           ".**{FunctionDef}.defined_block")
        
    def test_ClassDef_def(self):
        src = """
        class foo():
            pass
        """
        self.assertNotSame(src,
                           ".defined_block",
                           ".**{ClassDef}.defined_block")
        
        
    def test_Lambda_def(self):
        src = """
        lambda x:None
        """
        self.assertNotSame(src,
                           ".defined_block",
                           ".**{Lambda}.defined_block")
        
    def test_Generator_def(self):
        src = """
        (x for x in y)
        """
        self.assertNotSame(src,
                           ".defined_block",
                           ".**{GeneratorExp}.defined_block")

    def test_Module_exec(self):
        src = ""
        node = self.get(src, "")
        self.assertFalse(hasattr(node, "executed_in"))
        

    def test_FunctionDef_exec(self):
        src = """
        def foo():
            pass
        """
        self.assertSame(src, ".defined_block", ".**{FunctionDef}.executed_in")


    def test_ClassDef_exec(self):
        src = """
        class foo():
            pass
        """
        self.assertSame(src, ".defined_block", ".**{ClassDef}.executed_in")
        
        
    def test_Lambda_exec(self):
        src = """
        lambda x: None
        """
        self.assertSame(src, ".defined_block", ".**{Lambda}.executed_in")
        
        
    def test_GeneratorExp_exec(self):
        src = """
        (x for x in x)
        """
        self.assertSame(src, ".defined_block", ".**{GeneratorExp}.executed_in")
        
    def test_Module_body(self):
        src = """
        1 + 2
        """
        self.assertSame(src, ".defined_block", ".**{BinOp}.executed_in")
    
    def test_FunctionDef_body(self):
        src = """
        def foo():
            1 + 2
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{BinOp}.executed_in")
        
    def test_FunctionDef_args(self):
        src = """
        def foo(x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{FunctionDef}.args.defined_block")
        self.assertSame(src, 
                        ".**{FunctionDef}.executed_in", 
                        ".**{FunctionDef}.args.executed_in")
        
    def test_ClassDef_body(self):
        src = """
        class foo():
            1 + 2
        """
        self.assertSame(src, 
                        ".**{ClassDef}.defined_block", 
                        ".**{BinOp}.executed_in")
        
    def test_Lambda_args(self):
        src = """
        lambda x : None
        """
        self.assertSame(src, 
                        ".**{Lambda}.defined_block", 
                        ".**{Lambda}.args.defined_block")
        self.assertSame(src, 
                        ".**{Lambda}.executed_in", 
                        ".**{Lambda}.args.executed_in")
        
    def test_GeneratorExp_elt(self):
        src = """
        (1+2 for x in x)
        """
        self.assertSame(src, 
                        ".**{GeneratorExp}.defined_block", 
                        ".**{BinOp}.executed_in")
        
    def test_GeneratorExp_comprehension(self):
        src = """
        (None for x in 1 + 2)
        """
        self.assertSame(src, 
                        ".**{GeneratorExp}.defined_block", 
                        ".**{GeneratorExp}.generators[0].executed_in")
        

    @tools.version("2.0+")
    def test_arguments_args_args_P2(self):
        src = """
        def foo(x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{FunctionDef}.args.args[0].executed_in")
        
    @tools.version("3.0+")
    def test_arguments_args_args_P3(self):
        src = """
        def foo(x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{FunctionDef}.args.args[0].defined_block")
        self.assertSame(src, 
                        ".**{FunctionDef}.executed_in", 
                        ".**{FunctionDef}.args.args[0].executed_in")
        
        
    @tools.version("3.4+")
    def test_arguments_args_vararg(self):
        """
        `vararg` only became a node in 3.4. it was an identifier attribute
        on `arguments` before. Those are covered by test_scope.
        """
        src = """
        def foo(*x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{FunctionDef}.args.vararg.defined_block")
        self.assertSame(src, 
                        ".**{FunctionDef}.executed_in", 
                        ".**{FunctionDef}.args.vararg.executed_in")
        
    @tools.version("3.0+")
    def test_arguments_kwonlyargs(self):
        src = """
        def foo(*x, a):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{FunctionDef}.args.kwonlyargs[0].defined_block")
        self.assertSame(src, 
                        ".**{FunctionDef}.executed_in", 
                        ".**{FunctionDef}.args.kwonlyargs[0].executed_in")
                

    def test_arguments_args(self):
        src = """
        def foo(**x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{FunctionDef}.args.defined_block")
        self.assertSame(src, 
                        ".**{FunctionDef}.executed_in", 
                        ".**{FunctionDef}.args.executed_in")
        
    @tools.version("3.4+")
    def test_arguments_args_kwarg(self):
        """
        `kwarg` only became a node in 3.4. it was an identifier attribute
        on `arguments` before. Those are covered by test_scope.
        """
        src = """
        def foo(**x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{FunctionDef}.args.kwarg.defined_block")
        self.assertSame(src, 
                        ".**{FunctionDef}.executed_in", 
                        ".**{FunctionDef}.args.kwarg.executed_in")
        
    @tools.version("3.0+")
    def test_arguments_vararg_annotation(self):
        """
        The way vararg and kwarg annotations were modelled in the AST changed
        from 3.3 to 3.4, but this test should work for both.
        """
        src = """
        def foo(*x:y):
            pass
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{id=y}.executed_in")
        
    
    @tools.version("3.0+")
    def test_arguments_kwarg_annotation(self):
        """
        The way vararg and kwarg annotations were modelled in the AST changed
        from 3.3 to 3.4, but this test should work for both.
        """
        src = """
        def foo(**x:y):
            pass
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{id=y}.executed_in")
        
    @tools.version("3.0+")
    def test_arg_annotation(self):
        src = """
        def foo(x:1+2):
            pass
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{arg}.annotation.executed_in")
        
    

        
        
              
    def get(self, src, path):
        node = self.parse(src)
        return tools.npath(node, path)
        
    def assertSame(self, src, path_a, path_b):
        node = self.parse(src)
        a = tools.npath(node, path_a)
        b = tools.npath(node, path_b)
        self.assertIs(a, b)
        
    def assertNotSame(self, src, path_a, path_b):
        node = self.parse(src)
        a = tools.npath(node, path_a)
        b = tools.npath(node, path_b)
        self.assertIsNot(a, b)

    def parse(self, src):
        if src not in self.cache:
            src = tools.unindent(src)
            node = ast.parse(src)
            lenatu.augment(node)
            self.cache[src] = node
        else:
            node = self.cache[src]
        return node