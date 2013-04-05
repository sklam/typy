'''
foo (int) -> float
foo (float) -> float

def bar(x0: int):
    loop:
        x1 : x0 + x2
        x2 = foo(x1)
'''

from typy import *

tp = TypeProblem()

foo_signatures = 'int->float', 'float->float'
scalars = 'int', 'float'

x0 = tp.var('x0', scalars)
x1 = tp.var('x1', scalars)
x2 = tp.var('x2', scalars)
foo = tp.var('foo', foo_signatures)

tp.implies(foo['int->float'], x1['int'])
tp.implies(foo['float->float'], x1['int'] | x1['float'])

tp.known(x2['float'])
tp.known(x0['int'])

# coercion rules at phi node
tp.implies(x2['float'], ~x1['int'])  # reject demotion


for sln in tp.solve_true():
    print '====='
    print sln
