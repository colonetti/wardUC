# -*- coding: utf-8 -*-
import os

from params import Params
from read_input.read_csv import (
                                read_generators,
                                read_network, gross_load_and_renewable_gen,
                                read_ini_state_thermal,
                                reset_gen_costs_of_thermals,
                                read_reserves
)
from read_input.convert_json import (convert_from_json_to_csv,
                                     modify_json, convert_from_csv_to_json
)
from components.thermal import Thermals
from components.network import Network


def read(args):
    """Read csv files with system's data and operating conditions"""

    # an instance of Params (params.py) with all parameters for the problem and the solution process
    params = Params(args=args)

    # objects for the configurations of thermal plants and the network model
    thermals, network = Thermals(), Network()

    if os.path.isdir(params.IN_DIR + "/csv_input/"):
        convert_from_csv_to_json(
                params,
                params.IN_DIR + "/csv_input/week 1/params.txt",
                params.IN_DIR + "/csv_input/thermal generating units - " +
                 params.PS + ".csv",
                params.IN_DIR +
                 "/csv_input/week 1/initial states of thermal units - " +
                 params.PS + " - week 1.csv",
                params.IN_DIR + "/csv_input/week 1/network - " + params.PS +
                 " - week 1.csv",
                params.IN_DIR + "/csv_input/week 1/gross load - " + params.PS +
                 ".csv")

    if os.path.isfile(params.IN_DIR + params.PS + '.json'):
        print("\n\nReading and converting json file", flush=True)
        data = convert_from_json_to_csv(params.PS, params.CASE, params.IN_DIR +
                                        params.PS + '.json',
                                 params.IN_DIR,
                                 min_gen_cut_MW=params.MIN_GEN_CUT_MW,
                                 scaling_factor=1.00,
                                 deficit_cost=(params.DEFICIT_COST
                                               if params.DEFICIT_COST != 1e8
                                                else None)
        )

        modify_json(params.IN_DIR + params.PS + '.json',
                    params.OUT_DIR + "/" + params.PS + '_modified.json',
                    min_gen_cut_MW=params.MIN_GEN_CUT_MW,
                    scaling_factor=1.00,
                    deficit_cost=(params.DEFICIT_COST
                                  if params.DEFICIT_COST != 1e8
                                    else None)
        )

    # read the parameters of the transmission network
    read_network(params.IN_DIR + 'network - ' + params.PS + '.csv', params,
                 network
    )

    # read data for the thermal generators
    read_generators(params.IN_DIR + 'powerPlants - ' + params.PS + '.csv',
                    params, thermals
    )

    for b, bus in enumerate(network.BUS_ID):
        network.BUS_HEADER[bus] = b

    if os.path.isfile(params.IN_DIR + 'case ' + str(params.CASE) + '/' +
                      "reserves - " + params.PS + " - case " + params.CASE +
                      ".csv"
    ):
        read_reserves(params.IN_DIR + 'case ' + str(params.CASE) + '/' +
                      "reserves - " + params.PS + " - case " + params.CASE +
                      ".csv",
                      params, network, thermals
        )
    else:
        print("No file for reserves found. "+
              "Assuming there is no reserve requirements.", flush =True)

    # read the gross load and renewable generation
    gross_load_and_renewable_gen(
                        params.IN_DIR + 'case ' + str(params.CASE) +'/' +
                        'gross load - '+
                        params.PS + ' - case ' + str(params.CASE) + '.csv',
                        params.IN_DIR + 'case ' + str(params.CASE) +'/'
                        + 'renewable generation - ' +
                        params.PS + ' - case ' + str(params.CASE) + '.csv',
                        params, network)

    # reset generation costs
    if os.path.isfile(params.IN_DIR + 'case ' + str(params.CASE) + '/' +
                      'reset generation costs of thermal units - ' +
                      params.PS + ' - case ' + str(params.CASE) + '.csv'):
        reset_gen_costs_of_thermals(params.IN_DIR + 'case '
                                    + str(params.CASE) + '/' +
                                   'reset generation costs of thermal units - '
                                   + params.PS +
                                    ' - case ' + str(params.CASE) + '.csv',
                                    params, thermals
        )
    else:
        print("No file of new unitary generation costs found. " +
              "Using default costs", flush=True)

    # read the initial state of the thermal units
    read_ini_state_thermal(params.IN_DIR + 'case ' + str(params.CASE) + '/' +
                           'initial states of thermal units - ' + params.PS +
                           ' - case ' + str(params.CASE) + '.csv',
                           params, thermals
    )

    return params, thermals, network
