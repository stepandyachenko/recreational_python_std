from dataclasses import dataclass
import io
import sys
import time

sys.setrecursionlimit(20000000)
sys.set_int_max_str_digits(100000000)

@dataclass
class FAD:#Functions, Arguments, Decorators container
    funcs: list
    args: list
    decors: list

def run_many(fad:FAD):
    print("-"*40)
    for f in fad.funcs:
        print(f"running {f.__name__}...")
        for arg in fad.args:
            sys.stdout = io.StringIO()
            if fad.decors:
                for d in fad.decors:    
                    d(f, arg)
            else:
                f(arg)
            was_printed = sys.stdout.getvalue()
            sys.stdout = sys.__stdout__
            print(f"  for {arg} ...")
            for line in was_printed.split('\n'):
                print(f"    {line}")
        print(f"finished {f.__name__}\n{"-"*40}")

def compare_returns(fad:FAD):
    funcs = fad.funcs
    args = fad.args
    assert len(funcs) >= 2, "expected at least 2 functions"
    assert args, "expected at least 1 argument"
    for arg in args:
        print("-"*40)
        print(f"for argument set {arg if type(arg) is list else f'[{arg}]'}:")
        results = {}
        unique_results = {}
        for f in funcs:
            results[f] = f(arg)
            if not results[f] in unique_results: unique_results[results[f]] = []
            unique_results[results[f]].append(f)
        if len(unique_results) == 1:
            print(f"\tall functions returned the same result: {results[funcs[0]]}")
        else:
            for ur in unique_results:
                print(f"\tfunction {[f.__name__ for f in unique_results[ur]]} returned {ur}")
    print("-"*40)

def d_log_time(f, *args):
    if args:
        x = time.time_ns()
        result = f(*args)
        time_elapsed = time.time_ns() - x
        print(f"\"{f.__name__}\" took {round(time_elapsed / 10**9, 3)} seconds or {time_elapsed} nanoseconds")
    else:
        def wrapper(*args):
            x = time.time_ns()
            result = f(*args)
            time_elapsed = time.time_ns() - x
            print(f"\"{f.__name__}\" took {round(time_elapsed / 10**9, 3)} seconds or {time_elapsed} nanoseconds")
            return result
        return wrapper

def d_log_return(f, *args):
    if args:
        result = f(*args)
        print(f"\"{f.__name__}\" returned {result if result != None else "nothing"}")
        return result
    else:
        f_name = f.__name__
        print(args)
        def wrapper(*args):
            result = f(*args)
            print(f"\"{f_name}\" returned {result if result != None else "nothing"}")
            return result
        return wrapper

def d_log_time_and_return(f, *args):
    if args:
        x = time.time_ns()
        result = f(*args)
        time_elapsed = time.time_ns() - x
        print(f"\"{f.__name__}\":\n\t-took {round(time_elapsed / 10**9, 3)} seconds or {time_elapsed} nanoseconds\n\t-returned {result}")
        return result
    else:
        def wrapper(*args):
            x = time.time_ns()
            result = f(*args)
            time_elapsed = time.time_ns() - x
            print(f"\"{f.__name__}\":\n\t-took {round(time_elapsed / 10**9, 3)} seconds or {time_elapsed} nanoseconds\n\t-returned {result}")
            return result
        return wrapper