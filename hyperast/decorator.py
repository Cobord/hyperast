from typing import Callable
from hyperast.builder import Builder

################################################################################
# inspection functions
import inspect

def arity(f: Callable):
    sig = inspect.signature(f)
    positional_args = sum(
        1 for param in sig.parameters.values()
        if param.kind in [param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD] and param.default is param.empty
    )
    return positional_args

################################################################################
# Interface module

# a global builder variable.
# when None, the hypergraph decorator will initialize it, call a function, then set back to None
# when a Builder, it will be
builder = None

def node(*args, **kwargs):
    global builder
    return builder.node(*args, **kwargs)

def edge(*args, **kwargs):
    global builder
    return builder.edge(*args, **kwargs)

def operation(*args, **kwargs):
    global builder
    return builder.operation(*args, **kwargs)

def unify(*args):
    """ Unify a number of nodes by adding to the quotient graph """
    global builder
    builder.unify(*args)

# decorator
def hypergraph(f: Callable):
    def hypergraph_wrapper(*args, **kwargs):
        global builder

        if builder is None:
            # this is the top-level invocation of @hypergraph when builder is
            # unset, so we have to create it.
            builder = Builder()

            # called without the *args (nodes); we need to create them
            if len(args) > 0:
                raise ValueError("Functions annotated with @hypergraph should be called without positional args")
            source = [ builder.node() for x in range(arity(f)) ]
            builder.source = source
            target = f(*source, **kwargs) # get targets by running the function
            builder.target = [] if target is None else target

            # finally, unset builder and return
            result = builder
            builder = None
            return result
        else:
            # In this branch, we're in a nested call, so we use the existing
            # builder which is already set
            target = f(*args, **kwargs)
            return target

    return hypergraph_wrapper
