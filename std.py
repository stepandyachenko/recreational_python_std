from dataclasses import dataclass
import io
from rich.console import Console
from rich.table import Table
import sys
import time

INDENT="  "
SEPARATOR="-"*40
rConsole = Console()
STAT_TABLE_MAX_WIDTH = 15

sys.setrecursionlimit(20000000)
sys.set_int_max_str_digits(100000000)

def capture_output():
    sys.stdout = io.StringIO()

def stop_capturing_and_return_output():
    if type(sys.stdout) == io.StringIO:
        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        return output
    else: return "you messed up"

def fit_str_in_n_symbols(s, n):
    if len(s) > n:
        return s[:int((n - 1)/2)] + "…" + s[int(-((n - 1)/2 + 2*(1-n%2))):]
    return s

@dataclass
class FAD:#Functions, Arguments, Decorators container
    funcs: list
    args: list
    decors: list

def run_many(fad:FAD):
    print(SEPARATOR)
    for f in fad.funcs:
        print(f"running {f.__name__}…")
        for arg in fad.args:
            capture_output()
            if fad.decors:
                for d in fad.decors:    
                    d(f, arg)
            else:
                f(arg)
            was_printed = stop_capturing_and_return_output()
            print(f"{INDENT}for {arg} …")
            for line in was_printed.split('\n'):
                 if len(line) > 0: print(f"{INDENT*2}{line}")
        print(f"finished {f.__name__}\n{SEPARATOR}")

def compare_returns(fad:FAD, disable_output=True):
    assert len(fad.funcs) >= 2, "expected at least 2 functions"
    assert fad.args, "expected at least 1 argument"

    table = Table(style='plum3')
    for column in ["function"] + [str(arg) for arg in fad.args]: table.add_column(column, header_style="cyan1")
    
    if disable_output: capture_output()
    for f in fad.funcs:
        results = {}
        unique_results = {}
        for arg in fad.args:
            results[arg] = f(arg)
        row = []
        for arg in results:
            res = str(results[arg])
            row.append(fit_str_in_n_symbols(res, STAT_TABLE_MAX_WIDTH))
        table.add_row(f.__name__, *tuple(row), style="bright_green")
    if disable_output: stop_capturing_and_return_output()
    rConsole.print(table)
    #print(SEPARATOR)

def compare_time_per_arg(fad:FAD, disable_output=True):
    table = Table(style='plum3')
    for column in ["~~~"] + [str(arg) for arg in fad.args]: table.add_column(column, header_style='orange1')
    arg_time = {arg:{} for arg in fad.args}
    
    if disable_output: capture_output()
    for f in fad.funcs:
        for arg in fad.args:
            _, time_elapsed = d_return_result_and_time(f, arg)
            arg_time[arg][f.__name__] = time_elapsed
        table.add_row(*tuple([f.__name__] + [f"{str(arg_time[arg][f.__name__])}ns\n{str(arg_time[arg][f.__name__] / (10**9))}s" for arg in fad.args]), style='bright_green')
    if disable_output: stop_capturing_and_return_output()

    rConsole.print(table)

def compare_avg_time(fad:FAD, disable_output=True):
    table = Table(style='plum3')
    for column in ["function", "avg time, s", "avg time, ns"]: table.add_column(column, header_style='yellow')
    avg_time = {}
    if disable_output: capture_output()
    for f in fad.funcs:
        i = 0
        for arg in fad.args:
            if f not in avg_time: avg_time[f] = 0
            avg_time[f] += d_return_result_and_time(f, arg)[1]
            i += 1
        avg_time[f] /= i
        row = [str(round(avg_time[f] / 10**9, 3)), str(avg_time[f])]
        for res in row:
            res = fit_str_in_n_symbols(res, STAT_TABLE_MAX_WIDTH)
        table.add_row(f.__name__, *tuple(row), style='bright_green')
    if disable_output: stop_capturing_and_return_output()
    rConsole.print(table)

def d_return_result_and_time(f, *args):
    x = time.time_ns()
    result = f(*args)
    time_elapsed = time.time_ns() - x
    return result, time_elapsed

def d_log_time(f, *args):
    if args:
        x = time.time_ns()
        result, time_elapsed = d_return_result_and_time(f, *args)
        print(f"\"{f.__name__}\" took {round(time_elapsed / 10**9, 3)} seconds or {time_elapsed} nanoseconds")
        return result
    else:
        def wrapper(*args):
            wrapper.__name__ = f.__name__
            result, time_elapsed = d_return_result_and_time(f, *args)
            print(f"\"{f.__name__}\" took {round(time_elapsed / 10**9, 3)} seconds or {time_elapsed} nanoseconds")
            return result
        return wrapper

def d_log_return(f, *args):
    if args:
        result = f(*args)
        print(f"\"{f.__name__}\" returned {result if result != None else "nothing"}")
        return result
    else:
        def wrapper(*args):
            wrapper.__name__ = f.__name__
            result = f(*args)
            print(f"\"{f.__name__}\" returned {result if result != None else "nothing"}")
            return result
        return wrapper

def d_log_return_and_time(f, *args):
    if args:
        result, time_elapsed = d_return_result_and_time(f, *args)
        print(f"\"{f.__name__}\":\n{INDENT}-returned {result}\n{INDENT}-took {round(time_elapsed / 10**9, 3)} seconds or {time_elapsed} nanoseconds")
        return result
    else:
        def wrapper(*args):
            wrapper.__name__ = f.__name__
            result, time_elapsed = d_return_result_and_time(f, *args)
            print(f"\"{f.__name__}\":\n{INDENT}-returned {result}\n{INDENT}-took {round(time_elapsed / 10**9, 3)} seconds or {time_elapsed} nanoseconds")
            return result
        return wrapper