import re
import ast
import sys

def unindent(source):
    """
    Removes the indentation of the source code that is common to all lines.
    
    Does not work for all cases. Use for testing only.
    """
    
    def normalize(line):
        normalized = []
        for i, c in enumerate(line):
            if c == " ":
                normalized.append(" ")
            elif c == '\t':
                normalized.append(8 * " ")
            else:
                normalized.append(line[i:])
                break
        return "".join(normalized)
    
    def min_indent(lines):
        idendations = []
        for line in lines:
            if not line.strip():
                continue
            if line.strip().startswith("#"):
                continue
            idendations.append(count(line))
        if not idendations:
            return 0
        else:
            return min(idendations)
            
    def count(normalized):
        count = 0
        for c in normalized:
            if c == ' ':
                count += 1
            else:
                break
        return count
    
    def trim(normalized, indent):
        indent = min(count(normalized), indent)
        return normalized[indent:]
    
    lines = [normalize(line) for line in source.splitlines()]
    indent = min_indent(lines)    
    return "\n".join(trim(line, indent) for line in lines)

id_pattern = re.compile(r"\s*[a-zA-Z0-9_]+\s*")
subscript_pattern = re.compile(r"\[(\s*[0-9]+)\s*\]")
filter_pattern = re.compile(r"\{(\s*[a-zA-Z0-9_=]+)\s*\}")

def npath(node, path):
    """
    XPath inspired utility to find a specific node or attribute within
    an AST.
    
    The path is an expression that is applied to the given node.
    
    Attribute access and indexing in case of lists works like in Python:
    
     * `.name`
     * `[42]`
     
    It is also possible to filter for a specific expression or statement:
     
     * `[=]`
     * `[+]`
     * ...
     
     If there is only one node that matches, the result is a node, otherwise
     a list of nodes.
     
     A single `*` returns all nodes reachable from the current node in
     depth-first order.
    """
    
    def check_empty(node, path):
        if path:
            return None, None
        return 0, node
    
    def check_flatten(node, path):
        if not path.startswith(".**"):
            return None, None
        
        flat = []
        
        class Traverser(ast.NodeVisitor):
            def __init__(self, first):
                self.first = first
            def visit(self, node):
                if node is not self.first:
                    flat.append(node)
                return ast.NodeVisitor.visit(self, node)
        
        if not isinstance(node, list):
            node = [node]
            
        for n in node:
            Traverser(n).visit(n)
        
        return len(".**"), flat
    
    def check_attribute(node, path):
        if not path.startswith("."):
            return None, None
        match = id_pattern.match(path, 1)
        if not match:
            raise ValueError("Invalid attribute name %r" % path)
        name = match.group(0).strip()
        
        if not hasattr(node, name):
            raise ValueError("%r has no attribute %r. Path is %r" %(node, name, path))
        
        return match.end(0), getattr(node, name)
    
    def check_subscript(node, path):
        if not path.startswith("["):
            return None, None
        match = subscript_pattern.match(path)
        if not match:
            raise ValueError("Invalid subscript %r" % path)
        index = int(match.group(1).strip())

        return match.end(0), node[index]
    
    def check_filter(node, path):
        if not path.startswith("{"):
            return None, None
        match = filter_pattern.match(path)
        if not match:
            raise ValueError("Invalid filter %r" % path)
        criteria = match.group(1).strip()
        
        if not isinstance(node, list):
            node = [node]
            
        if "=" in criteria:
            attr, value = criteria.split("=")
            result = [n for n in node if str(getattr(n, attr, None)) == value]
        else:
            result = [n for n in node if n.__class__.__name__ == criteria]
            
        if not result:
            raise ValueError("No node of type %r found. Nodes: %s" %(criteria, node))
        
        if len(result) == 1:
            result = result[0]
        
        return match.end(0), result
    

        
    pos, nxt = check_empty(node, path)
    if pos is not None:
        return nxt
        
    if pos is None:
        pos, nxt = check_flatten(node, path)
        
    if pos is None:
        pos, nxt = check_attribute(node, path)
        
    if pos is None:
        pos, nxt = check_subscript(node, path)
    
    if pos is None:
        pos, nxt = check_filter(node, path)
    
    if pos is None:
        raise ValueError("Invalid npath: %r" % path)
    
    
    return npath(nxt, path[pos:])
        

def version(supported_versions, version=sys.version_info):
    """
    Decorator for tests that should only run on some versions of Python.
    
    @version("2.7+")
    def test():
        # runs on 2.7.0, 2.7.1, ..., 2.8.0, 2.8.1, ...
        # but not on 3.x
    
    @version("2.7+ 3.3+")
    def test():
        # runs on both 2.7 and newer and 3.3 and newer.
        
    
    """
    match = False
    for cond in supported_versions.split():
        c_match = True
        for i, number in enumerate(cond.split(".")):
            plus = number[-1] == "+"
            if plus: 
                number = number[:-1]
            number = int(number)
            if not plus:
                c_match = c_match and version[i] == number
            else:
                c_match = c_match and version[i] >= number
        match = match or c_match
    
    def wrapper_factory(f):
        if match:
            return f
        else:
            return None
        
    return wrapper_factory
        
        
    