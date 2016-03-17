'''
Created on 17.03.2016

@author: stefan
'''
import unittest
from lenatu import tools
import lenatu
import ast

class TestScope(unittest.TestCase):
    
    def setUp(self):
        self.cache = {}


    def test_module_global(self):
        src = """
        x = 1
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{Name}.id_block")
        
    def test_implicit_local(self):
        src = """
        def f():
            x = 1
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{Name}.id_block")
    
    def test_implicit_global(self):
        src = """
        def f():
            x + 1
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{Name}.id_block")
        
    @tools.version("3.0+")
    def test_parameter_arg(self):
        src = """
        def f(x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{arg}.arg_block")
       
    @tools.version("2.0+") 
    def test_parameter_P2(self):
        src = """
        def f(x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{id=x}.id_block")
    
    @tools.version("2.0+")
    def test_vararg_P2(self):
        src = """
        def f(*x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{vararg=x}.vararg_block")
        
    @tools.version("3.0+")
    def test_vararg_P3(self):
        src = """
        def f(*x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{arg=x}.arg_block")
        
    @tools.version("2.0+")
    def test_kwarg_P2(self):
        src = """
        def f(**x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{kwarg=x}.kwarg_block")
        
    @tools.version("3.0+")
    def test_kwarg_P3(self):
        src = """
        def f(**x):
            pass
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{arg=x}.arg_block")
        
    def test_default(self):
        src = """
        def foo(x=y):
            pass
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{id=y}.id_block")  
        
    @tools.version("3.0+")
    def test_arg_annotation(self):
        src = """
        def foo(x:y):
            pass
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{arg}.annotation.id_block")
    
    def test_implicit_closure(self):
        src = """
        def f():
            x = 1
            def g():
                x + 1
        """
        self.assertSame(src, 
                        ".**{name=f}.defined_block", 
                        ".**{name=g}.**{id=x}.id_block")
        
    @tools.version("3.0+")
    def test_explict_closure(self):
        src = """
        def f():
            x = 1
            def g():
                nonlocal x
                x = 2
        """
        self.assertSame(src, 
                        ".**{name=f}.defined_block", 
                        ".**{name=g}.**{id=x}.id_block")
    
    def test_local_hides_closure(self):
        src = """
        def f():
            x = 1
            def g():
                x = 2
        """
        self.assertSame(src, 
                        ".**{name=g}.defined_block", 
                        ".**{name=g}.**{id=x}.id_block") 
        
    def test_explicit_global_closure(self):
        src = """
        def f():
            x = 1
            def g():
                global x
                x + 1
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{name=g}.**{id=x}.id_block") 
        
    def test_class(self):
        src = """
        class f():
            pass
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{ClassDef}.name_block") 
        
    def test_class_member(self):
        src = """
        class f():
            x = 1
        """
        self.assertSame(src, 
                        ".**{ClassDef}.defined_block", 
                        ".**{id=x}.id_block")
        
    def test_class_uses_closure(self):
        src = """
        def f(x):
            class g():
                y = x + 1
        """
        self.assertSame(src, 
                        ".**{FunctionDef}.defined_block", 
                        ".**{ClassDef}.**{id=x}.id_block")
    
    def test_class_members_no_closure(self):
        src = """
        class f():
            x = 1
            def g():
                y = x + 1
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{name=g}.**{id=x}.id_block")
        
    def test_class_bypassed(self):
        src = """
        def f():
            x = 1
            class g():
                x = 2
                def h():
                    print(x)
        """
        self.assertSame(src, 
                        ".**{name=f}.defined_block", 
                        ".**{name=h}.**{id=x}.id_block")
        
    def test_import(self):
        src = """
        def f():
            import x
        """
        self.assertSame(src, 
                        ".**{name=f}.defined_block", 
                        ".**{alias}.name_block")
        
    def test_import_as(self):
        src = """
        def f():
            import x as y
        """
        self.assertSame(src, 
                        ".**{name=f}.defined_block", 
                        ".**{alias}.asname_block")
        
    def test_except(self):
        src = """
        def f():
            try:
                pass
            except ValueError as e:
                pass
        """
        self.assertSame(src, 
                        ".**{name=f}.defined_block", 
                        ".**{ExceptHandler}.name_block")
        
    @tools.version("3.0+")
    def test_except_nonlocal(self):
        src = """
        def f():
            nonlocal e
            try:
                pass
            except ValueError as e:
                pass
        """
        self.assertSame(src, 
                        ".defined_block", 
                        ".**{ExceptHandler}.name_block")
        
    def test_generator_element(self):
        src = """
        def f():
            (x for x in y)
        """
        self.assertSame(src, 
                        ".**{GeneratorExp}.defined_block", 
                        ".**{GeneratorExp}.elt.id_block")
        
    def test_generator_iterable(self):
        src = """
        def f(y):
            (x for x in y)
        """
        self.assertSame(src, 
                        ".**{name=f}.defined_block", 
                        ".**{GeneratorExp}.generators.**{id=y}.id_block")
        
        
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