
Lenatu - Abstract Syntax Tree Analyzer
=============================================================

Python's `AST` module is great, lenatu makes it even greater
by providing information that is difficult to extract from the
AST but often required.

----------------------
Let's get going!
----------------------

Lenatu can be installed as usual::

	pip install lenatu
	
We use the abstract syntax tree from the built-in `ast` module::

	code = "..."
	node = ast.parse(code)
	
	lenatu.analyze(node)
	
----------------------
Blocks
----------------------

Python's execution model has the concept of a block. A block is a sequence
of instructions that run within that block. Variables belong to a block.

Examples are functions and modules. The body of a `for` loop is not a block
by itself, which explains why variables are not local to the body.

The AST does not make blocks explicitly visible. Lenatu introduces a class
for that :class:`Block`.


Lenatu adds block information to the AST. Each `ast.stmt` and `ast.expr` node 
gets an additional attribute `executed_in` with the block in which the node is
executed in.

Certain blocks, like `ast.ClassDef` and `ast.FunctionDef`, define blocks. Those
have a `defined_block` attribute as well.

There are some 'helper' node types that contain
additional information about other nodes. For example, `ast.arguments` is
used to store the parameter information for `ast.FunctionDef`. These
get the `executed_in` of the node they belong to. If they belong to a
node that defines a block, they get the `defined_block` attribute as well.


.. class:: Block

    .. attribute:: defined_by
    
    	AST node that defines this block (for example a `ast.Module`
    	or `ast.FunctionDef`).

	.. attribute:: variables
	
		List of variable names that are bound to this block. 
			
		These variables are local to code executed in this block.
		
---------------
Variable Scopes
---------------

Variables are bound to a block. When a variable is used it is not immediately
clear from the AST alone to which block the variable is bound. 
If it is bound to the same
block the code is executed in, then the variable is local. If the variable
is bound to the module, then the variable is global.

A variable might also be bound to the block of an enclosing function. These we
refer to as 'free' variables or 'closure' variables.

Whenever a node has an `identifier` which refers to a variable, Lenatu finds
the block that the variable is bound to.

Unfortunately, the `ast` module is using `str` instances for identifiers. 
We cannot add a `block` attribute to them. We store this information in the
node that contains the identifier. For example, the `ast.Name` has an
attribute `id` that stores the variable. Lenatu adds another attribute called
`id_block` to the `ast.Name` instance that contains the block `id` is bound
to.

--------------------------
Additional Node Attributes
--------------------------

Lenatu is adding attributes to the nodes of the AST.

.. attribute:: executed_in

	Attribute of nodes, containing the :class:`Block` the node is executed in.
	
	`executed_in` is given for *all* nodes *except* the ones that define
	the top-level module:
	
	 * `ast.Module`
	 * `ast.Interactive`
	 * `ast.Expression`
	 * `ast.Suite`


.. attribute:: defined_block

	Attribute of nodes, containing the :class:`Block` the node is defining.
	
	`defined_block` is given for these blocks:
	
	 * `ast.Module`
	 * `ast.Interactive`
	 * `ast.Expression`
	 * `ast.Suite`
	 * `ast.FunctionDef`
	 * `ast.AsyncFunctionDef`
	 * `ast.ClassDef`
	 * `ast.Lambda`
	 * `ast.GeneratorExp`
	 * `ast.arguments`
	 * `ast.arg`

.. attribute:: XYZ_block

	Attribute of nodes that contain identifiers referring to variables.
	Contains the :class:`block` that variable is bound to.
	
	The name of the attribute is the name of the identifier attribute with
	`_block` at the end.
	
	In particular, these attributes are available:
	
	* `ast.FunctionDef.name_block`
	* `ast.AsyncFunctionDef.name_block`
	* `ast.ClassDef.name_block`
	* `ast.Global.names_block`    (list of blocks)
	* `ast.Nonlocal.names_block`    (list of blocks)
	* `ast.Name.id_block`
	* `ast.excepthandler.name_block`
	* `ast.arg.arg_block`
	* `ast.alias.name_block` (only if `asname` is `None`)
	* `ast.alias.asname_block`
