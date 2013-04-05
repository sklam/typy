'''
add (int, int) -> int
add (float, float) -> float

def foo(x:int, y): 
    z = add(x, y)
'''
from typy import *

tp = TypeProblem()

scalars = 'int', 'float'
add_signatures = 'int,int->int', 'float,float->float'

x = tp.var('x', scalars)
y = tp.var('y', scalars)
z = tp.var('z', scalars)
add = tp.var('add', add_signatures)

# constrains on arguments
tp.implies(add['int,int->int'], x['int'] & y['int'], converse=True)
tp.implies(add['float,float->float'],
           (x['float']|x['int']) & (y['float']|y['int']))

# constrains on return
tp.implies(add['float,float->float'], z['float'])
tp.implies(add['int,int->int'], z['int'])

tp.known(x['int'])

for sln in tp.solve_true():
    print '====='
    print sln

