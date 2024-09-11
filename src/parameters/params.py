# -*- coding: utf-8 -*-

import os
from typing import Union
from numbers import Real
from csv import reader
from timeit import default_timer as dt

from constants import (NetworkModel, NetworkSlacks)


def _str2bool(v: Union[bool, str]):
    """Converts usual string representations of the boolean values to either True or False"""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ValueError(f"Boolean value expected. Got {v} of type {type(v)}.")


def _str2real(v: str):
    """Converts usual string representations of the boolean values to either True or False"""

    try:
        _v = int(v)
    except ValueError:
        return float(v)

    if float(v) != int(v):
        return float(v)

    return int(v)


def _str2enum(v: str):
    """Get the right member of an enumeration from string v"""
    _enums = (NetworkModel, NetworkSlacks)

    for (_en, _name) in [(_en, _opt.name) for _en in _enums for _opt in _en]:
        if _name == v.upper():
            return v.upper()

    raise ValueError(f"Value {v} is not valid value")


def _check_choices(params: "Params"):
    """
    Checks whether the parameters chosen in params are valid
    """

    if not os.path.isdir(params.IN_DIR):
        raise FileNotFoundError('no directory for power system ' + params.PS +
                                ' has been found in the input directory ' +
                                params.IN_DIR.replace(params.PS + "/", "")
    )

    for attr in ['DISCRETIZATION', 'MILP_GAP',
                 'DEFICIT_COST', 'SCAL_OBJ_F', 'TIME_LIMIT', 'POWER_BASE']:
        value = getattr(params, attr)
        if not (isinstance(value, Real)):
            raise TypeError(f"{attr} must be a real number and not a {type(value)}")
        if value < 0:
            raise ValueError(f"{attr} must be nonnegative")

        if attr == 'POWER_BASE' and value != 100:
            print('The power base chosen is different from 100 MVA (it is ' +
                  str(value) + ' MVA). If this is correct, then proceed, otherwise ' +
                  ' choose a different value for it.')

    _enums_types = {"NETWORK_MODEL": NetworkModel, "NETWORK_SLACKS": NetworkSlacks}
    for attr in ['NETWORK_MODEL', "NETWORK_SLACKS"]:
        if not (isinstance(getattr(params, attr), _enums_types[attr])):
            raise AttributeError(
                f"Parameter {attr} must be a member of {_enums_types[attr]}." +
                f" The choices for this parameter are " +
                f"{[_opt.name for _opt in _enums_types[attr]]}."
                + f" The current value is {getattr(params, attr)} " +
                f"({type(getattr(params, attr))})."
            )


def _set_attr_from_console(parameter_class: "Params",
                           W_RANK: int,
                           args: dict):
    """Set attributes of object parameter_class according to args
    The corresponding values keys of args that match attributes
    """

    _enums = (NetworkModel, NetworkSlacks)

    for k, v in args.items():
        k = k.upper()
        if hasattr(parameter_class, k):
            old_value = getattr(parameter_class, k)
            if not (isinstance(old_value, _enums)):
                if isinstance(old_value, list) and (not (isinstance(v, list)) or len(v) == 1):
                    if not (isinstance(v, list)):
                        v = _str2bool(v) if isinstance(old_value[0], bool) else v
                    else:
                        v = _str2bool(v[0]) if isinstance(old_value[0], bool) else v[0]
                    v = len(old_value) * [type(old_value[0])(v)]
                    setattr(parameter_class, k, v)
                    if W_RANK == 0:
                        print(f"Attribute {k} changed from {old_value} to {v}", flush=True)

                elif isinstance(old_value, list) and isinstance(v, list):
                    v = [1] + ([_str2bool(_v) for _v in v]
                               if isinstance(old_value[0], bool)
                               else [type(old_value[0])(_v) for _v in v])
                    v[W_RANK] = v[W_RANK]
                    setattr(parameter_class, k, v)
                    if W_RANK == 0:
                        print(f"Attribute {k} changed from {old_value} to {v}", flush=True)

                elif not (isinstance(old_value, list)) and isinstance(v, list):
                    v = [1] + v if isinstance(old_value, bool) else [1] + [_str2bool(_v) for _v in
                                                                           v]
                    setattr(parameter_class, k, v[W_RANK])
                    if W_RANK == 0:
                        print(f"Attribute {k} changed from {old_value} to {v[W_RANK]}", flush=True)

                elif isinstance(old_value, bool):
                    v = _str2bool(v)
                    setattr(parameter_class, k, v)
                    if W_RANK == 0:
                        print(f"Attribute {k} changed from {old_value} to {v}", flush=True)

                else:
                    v = type(old_value)(v)
                    setattr(parameter_class, k, v)
                    if W_RANK == 0:
                        print(f"Attribute {k} changed from {old_value} to {v}", flush=True)
            else:
                found = False
                for (_en, _name) in [(_en, _opt.name) for _en in _enums for _opt in _en]:
                    if _name == v.upper():
                        setattr(parameter_class, k, getattr(_en, _name))
                        found = True
                        break

                if W_RANK == 0:
                    if found:
                        print(f"Attribute {k} changed from {old_value} to " +
                              f"{getattr(parameter_class, k)}", flush=True)
                    else:
                        raise AttributeError(f"Error setting attribute {k}")


def _set_params_from_file(params, file_name):
    """
        check if there is a params.txt file at the system folder
        in case there is such a file, read its contents and
        overwrite the parameters according to them
    """

    print(f"\n\nAttributes found in file {params.IN_DIR + params.CASE + '/params.txt'}" +
          " will overwrite default values of parameters")
    with open(file_name, encoding="ISO-8859-1") as csv_file:
        csv_reader = reader(csv_file, delimiter='=')
        for row in [r for r in csv_reader if len(r) > 0 and len(r[0]) > 0 and r[0][0] != "#"]:
            if hasattr(params, row[0].strip()):
                if not (isinstance(getattr(params, row[0].strip()), dict)):
                    old_value = getattr(params, row[0].strip())
                    new_value = type(getattr(params, row[0].strip()))(row[1].strip())
                    setattr(params, row[0].strip(), new_value)
                    print(f"Attribute {row[0].strip()} changed from {old_value} to {new_value}",
                          flush=True)
                else:
                    # if it is a dict
                    old_value = dict(getattr(params, row[0].strip()).items())
                    keys = list(old_value.keys())
                    if isinstance(getattr(params, row[0].strip())[keys[0]], bool):
                        if not row[1].strip() in ('True', 'False', '1', '0'):
                            s = (f"Error reading file {file_name}." +
                                f"Accepted values for {row[0].strip()} are " +
                                f"{('True', 'False', '1', '0')}"
                            )
                            raise ValueError(s)
                        new_value = row[1].strip() in ('True', '1')
                    else:
                        new_value = type(getattr(params, row[0].strip())[keys[0]])(row[1].strip())
                    for k in keys:
                        getattr(params, row[0].strip())[k] = new_value

                    print(f"Attribute {row[0].strip()} changed from {old_value} to {new_value}",
                          flush=True)
            else:
                raise AttributeError(f"Params has no attribute {row[0]}.\n" +
                                     "The .txt file used to overwrite attribute values must " +
                                     "have no header, one pair attribute=value " +
                                     "should be given in each line\n" +
                                     "Attributes and values are separated by = signs and " +
                                     "no special characters are allowed\n" +
                                     "Lines starting with # are ignored")


class Params:
    """
    The attributes of an instance of this class contain the values for the parameters of the
    algorithm and the optimization model.

    :param args: Argument-value pairs for the solution process and the optimization
                model.
    :type args: dict or None

    :return: an object of Params containing all choices for the optimization model and
                algorithm that are shared across all processes.
    :rtype: Params
    """

    def __init__(
            self: "Params",
            args: dict=None
    ) -> None:

        #: Name that uniquely identifies the current experiment.
        #: If an output directory, OUT_DIR, is not
        #: provided, then an output directory EXP_NAME will be created, defaults to "exp1".
        self.EXP_NAME: str = 'exp_1'

        #: Number of periods in the scheduling horizon, defaults to 1.
        self.T: int = 1

        self.TIME_LIMIT: Real = 3600.0  #: Time limit in seconds, defaults to 3600.0.
        self.CASE: str = '1'            #: ID of the case under study, defaults to "1".

        #: Name of the power system under study, defaults to "14nodes".
        self.PS: str = '14nodes'

        #: dir where the input files are located, defaults to ''.
        #: If not given, the input directory is assumed to be in the parent directory
        self.IN_DIR: str = ''

        #: dir to which the output is to be written to, defaults to ''.
        #: If not given, an directory will be created in the parent directory
        self.OUT_DIR: str = ''

        #: Maximum number of threads available to each process, defaults to 0.
        self.THREADS: int = 0

        #: Flag that indicates whether the optimization solvers console
        #: output is enabled, defaults to True.
        self.VERBOSE: bool = True

        #: Length in hours of each time period in the scheduling horizon, defaults to 1.0.
        self.DISCRETIZATION: Real = 1.0

        #: Relative gap tolerance for the UC MILP, defaults to 1e-4.
        self.MILP_GAP: Real = 1e-4

        #: Unitary cost for load curtailment and generation surplus, defaults to 1e8.
        self.DEFICIT_COST: Real = 1e8

        #: Flag to indicate whether the transmission system should be reduced, defaults to True.
        self.REDUCE_SYSTEM: bool = True

        self.POWER_BASE: Real = 100.0  #: Power base in MVA, defaults to 100.

        #: Scaling factor applied to the objective function.
        #: The objective function is multiplied by this factor, defaults to 1e-3.
        self.SCAL_OBJ_F: Real = 1e-3

        #: Threshold for the minimum generation of generating units. Units whose minimum generation
        #: is strictly less than this value are assumed to have no minimum generation, i.e., the
        #: minimum generation is replaced by 0, default to 0.00.
        self.MIN_GEN_CUT_MW: Real = 0.00

        #: Threshold for the coefficient of the PTDF matrix. Coefficients whose magnitudes are less
        #: than this value are substituted by 0, defaults to 1e-5.
        self.PTDF_COEFF_TOL: Real = 1e-4

        #: In the strategy used to reduce the network, it is possible to determine the maximum
        #: number of connections that the network nodes may have after the reduction is applied,
        #: defaults to 20.
        self.MAX_NUMBER_OF_CONNECTIONS: int = 20

        #: Maximum number of processes launched to identify inactive transmission line bounds,
        #: defaults to 1.
        self.MAX_PROCESS_REDUCE_NETWORK: int = 1

        #: Network model used, default to `NetworkModel.B_THETA`.
        self.NETWORK_MODEL: NetworkModel = NetworkModel.B_THETA

        #: Network slacks to be included (default = `NetworkSlacks.BUS_SLACKS`).
        self.NETWORK_SLACKS: NetworkSlacks = NetworkSlacks.BUS_SLACKS

        if args is not None:
            _set_attr_from_console(self, W_RANK=0, args=args)

        self.IN_DIR: str = (os.path.abspath(os.path.join(__file__, "../../..")).replace("\\", "/")
                            + '/input/' + self.PS + '/'
                            if (self.IN_DIR is None or self.IN_DIR == '')
                            else self.IN_DIR
                            )

        if not (os.path.isdir(self.IN_DIR + 'case ' + str(self.CASE) + '/')):
            os.makedirs(self.IN_DIR + 'case ' + str(self.CASE) + '/')

        if os.path.isfile(self.IN_DIR + "params.txt"):
            _set_params_from_file(self, self.IN_DIR + "/params.txt")

        if os.path.isfile(self.IN_DIR + "case " + self.CASE + "/params.txt"):
            _set_params_from_file(self, self.IN_DIR + "case " + self.CASE + "/params.txt")

        if self.OUT_DIR == '' or self.OUT_DIR is None:
            self.OUT_DIR = (
                            os.path.abspath(os.path.join(__file__, "../../..")).replace("\\", "/")
                            + '/output/' + self.PS + '/case '
                            + self.CASE + '/' + self.EXP_NAME + '/'
            )

        if not (os.path.isdir(self.OUT_DIR)):
            os.makedirs(self.OUT_DIR)

        _check_choices(self)

        self._START: Real = dt()
        self._LAST_TIME: Real = self._START + self.TIME_LIMIT

        print("\n\n", flush=True)

    def __str__(self):
        """str"""
        return "Params"
