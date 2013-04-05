'''TyPy

Author: Siu Kwan Lam

Type inference building block in Python using pycosat.

Dependencies:

    sympy: For symbolic boolean algebra.
    pycosat: A python binding to PicoSAT. https://github.com/ContinuumIO/pycosat
'''

from collections import defaultdict
# dependencies
from sympy.logic.boolalg import Not, And, Or, Xor, Nand, Nor, Implies, to_cnf
from sympy.core import symbols
import pycosat

#
# Public classes
#

class TypeProblem(object):
    '''Represents a single type inference problem.
    '''
    def __init__(self):
        self._clauses = {}
        self._constrains = []

    def var(self, name, types):
        '''Declare a new type variable with a set of all possible types.
        
        Arguments:
            name: variable name
            types: a iterable of type, where type can be any hashable objects.
            
        Returns:
            a TypeVar object.
        '''
        clauses = self._set(name, types)
        return TypeVar(name, dict(zip(types, clauses)))

    def known(self, clause):
        '''Add a clause that is known to be true to the constrains.
        '''
        self._constrains.append(clause)

    def _set(self, name, types):
        exprs = [self._clause(name, t) for t in types]
        self._constrains.append(Xor(*exprs))
        return exprs

    def implies(self, p, q, converse=False):
        '''Add a implication constrains: p->q.
        If converse is True, also add q->p.
        
        p->q is equivalent to ~p | q.
        '''
        self._constrains.append(Implies(p, q))
        if converse:
            self._constrains.append(Implies(q, p))
    
    def solve(self):
        '''A generator function that returns a solution per iteration.
        Each solution is a list of tuples of (clause, boolean)
        where the boolean indicates whether the clause is true or not.
        The clause is a tuple of (variable name, type).
        '''
        posform = And(*self._constrains)
        slns, symdict = solve(posform)
        def interpret(sln):
            for symid in sln:
                symname = symdict[abs(symid)]
                yield self._clauses[symname], symid > 0
        return (list(interpret(sln)) for sln in slns)

    def solve_true(self):
        '''A generator function that returns a solution per iteration.
        Each solution is a list of tuples of (variable name, type).
        Only true clauses from the `solve()` is returned.
        '''
        for sln in self.solve():
            yield [clause for clause, cond in sln if cond]
        
    def _clause(self, *desc):
        clause = symbols('x%d' % len(self._clauses))
        self._clauses[clause.name] = desc
        return clause

class TypeVar(object):
    '''Represent a type variable.
    
    Given a TypeVar `x`.  To access the clause where `x` is of type `int`, do
    `x[int]`.

    NOTE: All TypeVar instance of the same name must be the same TypeVar.
    '''
    def __init__(self, name, clauses):
        "Only a TypeProblem instance can construct new TypeVar"
        self.name = name
        self.clauses = clauses

    def __getitem__(self, typ):
        '''Use to access individual type clauses for this type variable.
        
        Returns the clause representing "`self` is of `typ`".  The returned
        value is a sympy symbolic object that can be manipulated using `~` for
        `not`, `&` for `and` and `|` for `or`.
        '''
        return self.clauses[typ]

#
# Internal functions
#


def solve(expr):
    cnf, sym = to_pycosat_cnf(expr)
    slns = pycosat.itersolve(cnf)
    return slns, sym

def to_pycosat_cnf(expr):
    cnf = to_cnf(expr)
    assert isinstance(cnf, And)
    symdict = _symbol_dictionary()
    cnfs = [_flatten_cnf(symdict, x) for x in cnf.args]
    inv_symdict = dict((v, k) for k, v in symdict.iteritems())
    return cnfs, inv_symdict

class _defaultdict_id(object):
    def __call__(self):
        return len(self._dict) + 1

    def bind(self, defdict):
        self._dict = defdict

def _symbol_dictionary():
    ider =  _defaultdict_id()
    dd = defaultdict(ider)
    ider.bind(dd)
    return dd

def _flatten_cnf(symdict, expr):
    def _decision(arg):
        if arg.is_Atom:
            return symdict[arg.name]
        else:
            assert isinstance(arg, Not)
            return -symdict[arg.args[0].name]
    if isinstance(expr, Or):
        return [_decision(arg) for arg in expr.args]
    else:
        return [_decision(expr)]

