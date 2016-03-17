import sys

if sys.version_info >= (3,0):
    from lenatu._facts3 import *
else:
    from lenatu._facts2 import *
    
