import unittest
from lenatu import tools
import ast

class TestUnindent(unittest.TestCase):

    def testEmptyString(self):
        self.assertEqual("", tools.unindent(""))
        
    def testOneLineNoIndent(self):
        self.assertEqual("x=1", tools.unindent("x=1"))
        
    def testOneLineSpaces(self):
        self.assertEqual("x=1", tools.unindent("  x=1"))
        
    def testOneLineTabs(self):
        self.assertEqual("x=1", tools.unindent("\t\tx=1"))
        
    def testOneLineMix(self):
        self.assertEqual("x=1", tools.unindent(" \t \t  x=1"))
        
    def testTwoLines(self):
        self.assertEqual("x=1\ny=2", tools.unindent("x=1\ny=2"))
        
    def testTwoLinesSpaces(self):
        self.assertEqual("x=1\ny=2", tools.unindent("  x=1\n  y=2"))
        
    def testTwoLinesTabs(self):
        self.assertEqual("x=1\ny=2", tools.unindent("\tx=1\n\ty=2"))
        
    def testTwoLinesMixed(self):
        self.assertEqual("x=1\ny=2", tools.unindent("\tx=1\n        y=2"))

    def testStructurePreserved(self):
        self.assertEqual("def foo():\n  x=1", tools.unindent("def foo():\n  x=1"))
        
    def testStructurePreservedSpaces(self):
        self.assertEqual("def foo():\n  x=1", tools.unindent("  def foo():\n    x=1"))

    def testStructurePreservedTabs(self):
        self.assertEqual("def foo():\n  x=1", tools.unindent("\tdef foo():\n\t  x=1"))
        
    def testIgnoreEmtptyLines(self):
        self.assertEqual("\nx=1", tools.unindent("\n   x=1"))
        
    def testIgnoreComments(self):
        self.assertEqual("#comment\nx=1", tools.unindent("#comment\n   x=1"))
        
    def testPartiallyIndendedComment(self):
        self.assertEqual("#comment\nx=1", tools.unindent(" #comment\n   x=1"))
        
        
class TestNPath(unittest.TestCase):
    
    def test_empty(self):
        n = ast.Module()
        self.assertEqual(n, tools.npath(n, ""))
        
    def test_attribute(self):
        n = ast.FunctionDef(name="hi")
        self.assertEqual("hi", tools.npath(n, ".name"))
        
    def test_nested_attribute(self):
        n = ast.Return(value=ast.Name(id="hi"))
        self.assertEqual("hi", tools.npath(n, ".value.id"))
        
    def test_subscript(self):
        n = ast.FunctionDef(body=[ast.Name(id="a"), ast.Name(id="b")])
        self.assertEqual("a", tools.npath(n, ".body[0].id"))
        self.assertEqual("b", tools.npath(n, ".body[1].id"))
        
    def test_filter(self):
        n = [ast.Name(), ast.Assign(), ast.Return]
        self.assertEqual(n[1], tools.npath(n, "{Assign}"))
        
    def test_flatten(self):
        n = ast.Module()
        f = ast.FunctionDef()
        e1 = ast.Expr()
        a1 = ast.Name()
        e2 = ast.Expr()
        a2 = ast.Name()
        n.body = [f]
        f.body = [e1, e2]
        e1.value = a1
        e2.value = a2
        
        expected = [f, e1, a1, e2, a2]
        actual =  tools.npath(n, ".**")
        self.assertEqual(expected, actual)