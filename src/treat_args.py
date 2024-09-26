# -*- coding: utf-8 -*-
import argparse
from numbers import Real
from csv import reader

from params import _str2bool, _str2real, _str2enum
from constants import (NetworkModel, NetworkSlacks)

def _treat_args(W_RANK:int, W_SIZE:int) -> dict:
    """
        Treat arguments given through the console
    """
    if W_SIZE > 1:
        if W_RANK == 0:
            raise ValueError("Only one process must be launched. " +
                             f"The number of processes is {W_SIZE}"
            )
        quit()

    class DummyParams:
        '''A dummy class with all attributes of Params.
        This dummy class is simply used
        to get the attributes of Params and treat the arguments
        from the command line.
        The default values of the attributes here are set to arbitrary values.
        '''
        EXP_NAME: str = 'nan'
        T: int = 0
        TIME_LIMIT: Real = -1.000
        CASE: str = 'nan'
        PS: str = 'nan'
        IN_DIR: str = 'nan'
        OUT_DIR: str = 'nan'
        THREADS: int = 1000
        VERBOSE: bool = True
        DISCRETIZATION: Real = -1.0
        MILP_GAP: Real = -1e-4
        DEFICIT_COST: Real = -1e8
        REDUCE_SYSTEM: bool = True
        POWER_BASE: Real = -100.0
        SCAL_OBJ_F: Real = -1e-3
        MIN_GEN_CUT_MW: Real = -1.00
        PTDF_COEFF_TOL: Real = -1e-4
        MAX_NUMBER_OF_CONNECTIONS: int = 10000
        MAX_PROCESS_REDUCE_NETWORK: int = -1
        NETWORK_MODEL: NetworkModel = NetworkModel.B_THETA
        NETWORK_SLACKS: NetworkSlacks = NetworkSlacks.BUS_SLACKS


    _dummy_params = DummyParams()

    _enums = (NetworkModel, NetworkSlacks)

    CLI = argparse.ArgumentParser(
                    prog = 'ward_UC',
                    description = 'Apply Ward reduction to UC models',
                    epilog = 'For help, refer to https://github.com/colonetti/wardUC',
                    formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=8,
                                                                                    width=100))

    CLI.add_argument(
        '--params_file',
        '--PARAMS_FILE',
        nargs='?',
        type=str,
        default='',
        help = 'A file containing parameters values in keyword formart (name=value)'
    )

    for attr in [_a for _a in dir(_dummy_params) if _a[0] != '_']:
        if isinstance(getattr(_dummy_params, attr), bool):
            CLI.add_argument(
                '--' + attr.lower(),
                '--' + attr.upper(),
                nargs='?',
                type=_str2bool,
                const=True,
                default=getattr(_dummy_params, attr),
                choices = [False, True]
            )
        elif isinstance(getattr(_dummy_params, attr), int):
            CLI.add_argument(
                '--' + attr.lower(),
                '--' + attr.upper(),
                nargs='?',
                type=int,
                default=getattr(_dummy_params, attr),
                metavar="[0, ..., 1000]"
            )
        elif isinstance(getattr(_dummy_params, attr), Real):
            CLI.add_argument(
                '--' + attr.lower(),
                '--' + attr.upper(),
                nargs='?',
                type=_str2real,
                default=getattr(_dummy_params, attr),
                metavar=">=0"
            )
        elif isinstance(getattr(_dummy_params, attr), _enums):
            found = False
            for _en in _enums:
                for _opt in _en:
                    if _opt == getattr(_dummy_params, attr):
                        found = True
                        break
                if found:
                    break
            CLI.add_argument(
                '--' + attr.lower(),
                '--' + attr.upper(),
                nargs='?',
                type=_str2enum,
                default=getattr(_dummy_params, attr),
                choices=list(_en.__members__.keys())+[_n.lower() for _n in _en.__members__.keys()]
            )
        else:
            CLI.add_argument(
                '--' + attr.lower(),
                '--' + attr.upper(),
                nargs='?',
                type=type(getattr(_dummy_params, attr)),
                default=getattr(_dummy_params, attr)
            )

    args = CLI.parse_args()

    args = {opt.dest: getattr(args, opt.dest)
                            for opt in CLI._option_string_actions.values()
                            if hasattr(args, opt.dest) and opt.default != getattr(args, opt.dest)}

    if 'params_file' in args.keys():
        valid_params = [opt.dest for opt in CLI._option_string_actions.values()]
        with open(args['params_file'], encoding="ISO-8859-1") as csv_file:
            csv_reader = reader(csv_file, delimiter = '=')
            for row in [r for r in csv_reader if len(r) > 0 and len(r[0]) > 0 and r[0][0] != "#"]:
                if row[0].strip() in valid_params:
                    args[row[0].strip()] = row[1].split(' ')
                else:
                    raise AttributeError(f"Parameter {row[0]} is invalid.\n" +
                                         "The .txt file used to overwrite attribute values must "+
                                         "have no header, one pair attribute=value " +
                                         "should be given in each line\n" +
                                         "Attributes and values are separated by = signs and "+
                                         "no special characters are allowed\n" +
                                         "Lines starting with # are ignored"
                                         )

    return args
