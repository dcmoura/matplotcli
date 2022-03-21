import sys
import json
import re
import argparse


def make_imports(vars):
    """initializes dict of variables for user code with imports"""
    exec(
        """
from matplotlib.pyplot import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from math import *
import numpy as np
""",
        {},
        vars,
    )


def make_str_valid_varname(s):
    """makes a string a valid python identifier"""
    # remove invalid characters (except spaces in-between)
    s = re.sub(r"[^0-9a-zA-Z_\s]", " ", s).strip()

    # replace spaces by underscores (instead of dropping spaces) for readability
    s = re.sub(r"\s+", "_", s)

    # if first char is not letter or underscore then add underscore to make it valid
    if not re.match("^[a-zA-Z_]", s):
        s = "_" + s

    return s


def read_data(vars):
    """reads json lines from stdin"""
    lines = [json.loads(line) for line in sys.stdin]
    col_names = {key for line in lines for key in line.keys()}
    data = {
        make_str_valid_varname(col): [line.get(col) for line in lines]
        for col in col_names
    }
    vars.update({"col_names": tuple(data.keys()), "data": data})
    vars.update(data)  # for not having to go through `data` to access input columns


def parse_args():
    """defines and parses command-line arguments"""
    parser = argparse.ArgumentParser(
        description="""plt reads JSON lines from the stdin and 
        executes python code with calls to matplotlib.pyplot functions to 
        generate plots. For more information and examples visit:
        https://github.com/dcmoura/matplotcli"""
    )
    parser.add_argument(
        "code",
        help="""
        python code with calls to matplotlib.pyplot to generate plots. 
        Example: plt "plot(x,y); xlabel('time (s)')" < data.json
        """,
    )
    parser.add_argument(
        "--no-import",
        action="store_true",
        help="do not import (matplotlib) modules before executing the code",
    )
    parser.add_argument(
        "--no-input",
        action="store_true",
        help="do not read input data from stdin before executing the code",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="do not call matplotlib.pyplot.show() after executing the code",
    )
    return parser.parse_args()


def main():
    sys.tracebacklimit = 1  # keep error traces short
    args = parse_args()  # parses cmd-line arguments
    vars = dict()  # variables to execute the user code
    if not args.no_import:
        make_imports(vars)  # add imports to the variables
    if not args.no_input:
        read_data(vars)  # add the input data to the variables
    exec(args.code, vars, vars)  # execute user code
    if not args.no_show:
        # tries showing the plot (assuming default/typical imports)
        try:
            exec("show()", vars, vars)
        except NameError:
            try:
                sys.stderr.write("Could not find show(), trying plt.show()\n")
                exec("plt.show()", vars, vars)
            except NameError:
                sys.stderr.write(
                    "Could not find plt.show(), skipping...\n",
                )


if __name__ == "__main__":
    main()
