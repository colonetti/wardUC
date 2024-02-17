from typing import Union
from numbers import Real
import json
import csv

def convert_from_csv_to_json(csv_file_path_generators: str) -> dict:

    data = {"SOURCE": "",
            "Parameters": {
                "Version": "0",
                "Power balance penalty ($/MW)": 0,
                "Time horizon (h)": 0
                },
            "Generators": {},
            "Transmission lines": {},
            "Contingencies": {},
            "Buses": {},
            "Reserves": {}
            }

    f = open(csv_file_path_generators, mode = 'r', encoding = 'ISO-8859-1')
    reader = csv.reader(f, delimiter = ';')
    row = next(reader)  # sep=; or <BEGIN>
    while row[0].strip() != '<BEGIN>':
        row = next(reader)  # <BEGIN>
    row = next(reader)

    while row[0] != '<Thermal generating units>':
        row = next(reader)

    row = next(reader) # header

    header = {"Plant's Name": -9, "Plant\'s ID": -9, "Unit's ID": -9, 'Bus': -9,
            'Minimum power output (MW)': 1e3, 'Maximum power output (MW)': -1e3,
            "Ramp-up limit (MW/h)": -9, "Ramp-down limit (MW/h)": -9,
            "Minimum up-time (h)": -9, "Minimum down-time (h)": -9,
            "Standard linear generation cost ($/MWh)": -9,
            "Constant cost ($)": -9, "Start-up cost ($)": -9, "Shut-down cost ($)": -9,
            'Minimum reactive generation (MVAr)': 0, 'Maximum reactive generation (MVAr)': 0,
            'Maximum apparent power (MVA)': 0}

    for h in header:
        header[h] = row.index(h)

    row = next(reader) # either first unit or end

    while row[0] != '</Thermal generating units>':
        P_ID = int(row[header["Plant\'s ID"]])  # plant id
        U_ID = int(row[header["Unit's ID"]])    # unit id

        data["Generators"] = {"g_" + str(P_ID) + "_" + str(U_ID):
                              {"Bus": row[header['Bus']],
                               "Production cost curve (MW)": [],
                               "Production cost curve ($)": [],
                               "Startup costs (\$)": [],
                               "Startup delays (h)": [],
                               "Ramp up limit (MW)": 0,
                               "Ramp down limit (MW)": 0,
                               "Startup limit (MW)": 0,
                               "Shutdown limit (MW)": 0,
                               "Minimum uptime (h)": 0,
                               "Minimum downtime (h)": 0,
                               "Reserve eligibility": [],
                               "Initial status (h)": 0,
                               "Initial power (MW)": 0.0
                               }
                              }

        self.UNIT_NAME[(P_ID, U_ID)] = row[header["Plant's Name"]].strip() + '-G-' + str(U_ID)
        self.UNIT_ID[(P_ID, U_ID)] = U_ID
        self.PLANT_NAME[(P_ID, U_ID)] = row[header["Plant's Name"]].strip()
        self.PLANT_ID[(P_ID, U_ID)] = int(row[header["Plant\'s ID"]])
        self.MIN_P[(P_ID, U_ID)] = float(row[header['Minimum power output (MW)']])/params.POWER_BASE
        self.MAX_P[(P_ID, U_ID)] = float(row[header['Maximum power output (MW)']])/params.POWER_BASE

        self.MIN_REAC_POWER[(P_ID, U_ID)] =float(row[header['Minimum reactive generation (MVAr)']])\
                                                                                /params.POWER_BASE
        self.MAX_REAC_POWER[(P_ID, U_ID)] =float(row[header['Maximum reactive generation (MVAr)']])\
                                                                                /params.POWER_BASE
        self.MAX_S[(P_ID, U_ID)] = float(row[header['Maximum apparent power (MVA)']])\
                                                                                /params.POWER_BASE

        self.RAMP_UP[(P_ID,U_ID)]=(params.DISCRETIZATION*float(row[header["Ramp-up limit (MW/h)"]])/
                                                                    params.POWER_BASE)
        self.RAMP_DOWN[(P_ID, U_ID)] = (params.DISCRETIZATION*
                                    float(row[header["Ramp-down limit (MW/h)"]])/params.POWER_BASE)

        self.MIN_UP[(P_ID, U_ID)] = int(row[header["Minimum up-time (h)"]])
        self.MIN_DOWN[(P_ID, U_ID)] = int(row[header["Minimum down-time (h)"]])
        self.BUS[(P_ID, U_ID)] = [int(row[header['Bus']])]
        self.BUS_COEFF[(P_ID, U_ID)] = {int(row[header['Bus']]): 1.00}

        self.GEN_COST[(P_ID, U_ID)] = params.SCAL_OBJ_FUNC*params.DISCRETIZATION*params.POWER_BASE*\
                                    float(row[header["Standard linear generation cost ($/MWh)"]])
        self.CONST_COST[(P_ID, U_ID)] = float(row[header["Constant cost ($)"]])*params.SCAL_OBJ_FUNC
        self.STUP_COST[(P_ID, U_ID)] = float(row[header["Start-up cost ($)"]])*params.SCAL_OBJ_FUNC
        self.STDW_COST[(P_ID, U_ID)] = float(row[header["Shut-down cost ($)"]])*params.SCAL_OBJ_FUNC

        row = next(reader)

    f.close()
    del f


    if scaling_factor is None:
        scaling_factor = max(min(gen["Production cost curve ($)"][-1]
                                        for gen in data["Generators"].values()
                                            if gen["Production cost curve ($)"][-1] > 0), 1)

    if deficit_cost is not None:
        data['Parameters']['Power balance penalty ($/MW)'] = deficit_cost

    for g, gen in data["Generators"].items():
        gen["Production cost curve (MW)"] = [0
                                        if gen["Production cost curve (MW)"][0] < min_gen_cut_MW
                                            or len(gen["Production cost curve (MW)"]) == 1
                                            else gen["Production cost curve (MW)"][0],
                                                gen["Production cost curve (MW)"][-1]]
        unitary_cost = gen["Production cost curve ($)"][0]/scaling_factor
        gen["Production cost curve ($)"] = [unitary_cost*gen["Production cost curve (MW)"][0],
                                                unitary_cost*gen["Production cost curve (MW)"][-1]]

        if (gen["Production cost curve (MW)"][0] < min_gen_cut_MW):
            gen["Minimum uptime (h)"] = 1
            gen["Minimum downtime (h)"] = 1

        if (gen["Minimum uptime (h)"] <= 1 and gen["Minimum downtime (h)"] <= 1
                and gen["Production cost curve (MW)"][0] < min_gen_cut_MW):
            gen["Startup costs ($)"] = [0]
        else:
            gen["Startup costs ($)"] = [gen["Startup costs ($)"][-1]/scaling_factor]

        gen["Startup delays (h)"] = [1]

        gen["Startup limit (MW)"] = gen["Production cost curve (MW)"][0]
        gen["Shutdown limit (MW)"] = gen["Production cost curve (MW)"][0]

    data['Contingencies'] = {}

    for l, line in data["Transmission lines"].items():
        if "Normal flow limit (MW)" in line.keys():
            line["Emergency flow limit (MW)"] = line["Normal flow limit (MW)"]
        if "Flow limit penalty ($/MW)" in line.keys():
            line["Flow limit penalty ($/MW)"] = data['Parameters']['Power balance penalty ($/MW)']

def _modify_json(json_file_path: str,
                 min_gen_cut_MW: Real=1.00,
                 scaling_factor: Real=None,
                 deficit_cost: Real=None
    ) -> dict:
    """
    Convert a `UnitCommitment.jl <https://github.com/ANL-CEEESA/UnitCommitment.jl>`__
    security-constrained unit-commitment instance in a json file to a json file in the same
    format but modified to be used in the pddip package. With the output json file, the
    instance can be run in `UnitCommitment.jl <https://github.com/ANL-CEEESA/UnitCommitment.jl>`__.
    """

    f = open(json_file_path)
    data = json.load(f)
    f.close()
    del f

    if scaling_factor is None:
        scaling_factor = max(min(gen["Production cost curve ($)"][-1]
                                        for gen in data["Generators"].values()
                                            if gen["Production cost curve ($)"][-1] > 0), 1)

    if deficit_cost is not None:
        data['Parameters']['Power balance penalty ($/MW)'] = deficit_cost

    for g, gen in data["Generators"].items():
        gen["Production cost curve (MW)"] = [0
                                        if gen["Production cost curve (MW)"][0] < min_gen_cut_MW
                                            or len(gen["Production cost curve (MW)"]) == 1
                                            else gen["Production cost curve (MW)"][0],
                                                gen["Production cost curve (MW)"][-1]]
        unitary_cost = gen["Production cost curve ($)"][0]/scaling_factor
        gen["Production cost curve ($)"] = [unitary_cost*gen["Production cost curve (MW)"][0],
                                                unitary_cost*gen["Production cost curve (MW)"][-1]]

        if (gen["Production cost curve (MW)"][0] < min_gen_cut_MW):
            gen["Minimum uptime (h)"] = 1
            gen["Minimum downtime (h)"] = 1

        if (gen["Minimum uptime (h)"] <= 1 and gen["Minimum downtime (h)"] <= 1
                and gen["Production cost curve (MW)"][0] < min_gen_cut_MW):
            gen["Startup costs ($)"] = [0]
        else:
            gen["Startup costs ($)"] = [gen["Startup costs ($)"][-1]/scaling_factor]

        gen["Startup delays (h)"] = [1]

        gen["Startup limit (MW)"] = gen["Production cost curve (MW)"][0]
        gen["Shutdown limit (MW)"] = gen["Production cost curve (MW)"][0]

    data['Contingencies'] = {}

    for l, line in data["Transmission lines"].items():
        if "Normal flow limit (MW)" in line.keys():
            line["Emergency flow limit (MW)"] = line["Normal flow limit (MW)"]
        if "Flow limit penalty ($/MW)" in line.keys():
            line["Flow limit penalty ($/MW)"] = data['Parameters']['Power balance penalty ($/MW)']


    return data

def modify_json(json_file_path:str,
                            json_out_file_path:str,
                            min_gen_cut_MW:Real = 1.00,
                            scaling_factor:Union[Real, None] = None,
                            deficit_cost:Union[Real, None] = None
    ) -> None:
    """
    Convert a `UnitCommitment.jl <https://github.com/ANL-CEEESA/UnitCommitment.jl>`__
    security-constrained unit-commitment instance in a json file to a json file in the same
    format but modified to be used in the pddip package. With the output json file, the
    instance can be run in `UnitCommitment.jl <https://github.com/ANL-CEEESA/UnitCommitment.jl>`__.

    The unit-commitment problems currently supported by pddip are deterministic, and the package
    focuses on cost-based, centrally dispatched markets where generation costs are
    represented by a single linear function (as opposed to piecewise linear functions).
    Thus, the main differences between the unit-commitment instances in
    `UnitCommitment.jl <https://github.com/ANL-CEEESA/UnitCommitment.jl>`__ and the instances
    generated after running this function are that the contingencies are ignored, and the piecewise
    cost function is replaced by a single linear function.

    :param json_file_path: abs path of the json file
    :type json_file_path: str
    :param json_out_file_path: abs path of the output json file
    :type json_out_file_path: str
    :param min_gen_cut_MW: threshold in MW for the minimum generation of units.
            Units whose minimum generation, as given in the json file, is strictly less than
            this threshold have their minimum generation are replaced by 0 (default: 1.0)
    :type min_gen_cut_MW: Real
    :param scaling_factor: scaling to be applied to the unitary generation costs of the
            thermal generating units. The costs given in the json file will be divided
            by this value. If no value is provided, the scaling factor is computed as the
            maximum of generating-unit-wise minimum linear cost (default: )
    :type scaling_factor: Union[Real, NoneType]
    :param deficit_cost: unitary cost in $/MW of generation surpluses and load
            curtailments. If nothing is provided, then the deficit cost is computed as
            the maximum linear cost of all units plus 1000 (default: )
    :type deficit_cost: Union[Real, NoneType]

    :return: None
    :rtype: NoneType

    Examples
    --------
    >>> modify_json('/home/user/ieee118.json', '/home/user/ieee118_modified.json')
    """

    with open(json_out_file_path, 'w', encoding='utf-8') as f:
        json.dump(_modify_json(json_file_path=json_file_path,
                                min_gen_cut_MW=min_gen_cut_MW,
                                scaling_factor=scaling_factor,
                                deficit_cost=deficit_cost),
                                f,
                                ensure_ascii=False,
                                indent=4)

def convert_from_json_to_csv(
                system_name: str,
                case_name: str,
                json_file_path: str,
                out_dir: str,
                min_gen_cut_MW: Real=1.0,
                scaling_factor: Union[Real, None]=None,
                deficit_cost: Union[Real, None]=None
    ) -> None:
    """
    Convert a `UnitCommitment.jl <https://github.com/ANL-CEEESA/UnitCommitment.jl>`__
    security-constrained unit-commitment instance in a json file to csv files in pddip formart.

    The unit-commitment problems currently supported by pddip are deterministic, and the package
    focuses on cost-based, centrally dispatched markets where generation costs are
    represented by a single linear function (as opposed to piecewise linear functions).
    Thus, the main differences between the unit-commitment instances in
    `UnitCommitment.jl <https://github.com/ANL-CEEESA/UnitCommitment.jl>`__, and the instances
    generated after running this method are that the contingencies are ignored and the piecewise
    cost function is replaced by a single linear function.

    :param system_name: power system name
    :type system_name: str
    :param case_name: name of the of case of the power system under study
    :type case_name: str
    :param json_file_path: abs path of the json file
    :type json_file_path: str
    :param out_dir: abs path of the dir to which the csv files are to be written
    :type out_dir: str
    :param min_gen_cut_MW: threshold in MW for the minimum generation of units.
        Units whose minimum generation, as given in the json file, is strictly less than
        this threshold have their minimum generation are replaced by 0
    :type min_gen_cut_MW: Real
    :param scaling_factor: scaling to be applied to the unitary generation costs of the
        thermal generating units. The costs given in the json file will be divided
        by this value. If no value is provided, the scaling factor is computed as the
        maximum of generating-unit-wise minimum linear cost
    :type scaling_factor: Union[Real, None]
    :param deficit_cost: unitary cost in $/MW of generation surpluses and load
        curtailment. If nothing is provided, then the deficit cost is computed as
        the maximum linear cost of all units plus 1000
    :type deficit_cost: Union[Real, None]

    :return: None
    :rtype: NoneType

    Examples
    --------
    >>> convert_from_json_to_csv('ieee118', '1', '/home/user/ieee118.json', '/home/user/')
    """

    data = _modify_json(json_file_path=json_file_path,
                        min_gen_cut_MW=min_gen_cut_MW,
                        scaling_factor=scaling_factor,
                        deficit_cost=deficit_cost
    )

    f = open(out_dir + "powerPlants - " + system_name + ".csv", 'w', encoding = 'ISO-8859-1')
    f.write('<BEGIN>;\n')
    f.write('<Hydro plants>;\n')
    f.write("ID;Name;Minimum reservoir volume (hm3);Maximum reservoir volume (hm3);")
    f.write("Name of downriver reservoir;Water travelling time (h);")
    f.write("Run-of-river plant? TRUE or FALSE;Minimum forebay level (m);")
    f.write("Maximum forebay level (m);")
    f.write("Maximum spillage (m3/s);Basin;Influence of spillage on the HPF? Yes or No;")
    f.write("Maximum spillage - HPF;Downriver plant of bypass discharge;")
    f.write("Maximum bypass discharge (m3/s);Water travel time in the bypass process (h);")
    f.write("Downriver reservoir of pump units;Upriver reservoir of pump units;")
    f.write("Water travel time in pumping (h);Comments\n")
    f.write('</Hydro plants>;\n')
    f.write('<Thermal plants>;\n')
    f.write("ID;Name;Minimum power output (MW);Maximum power output (MW);")
    f.write("Unitary linear cost ($/MW);Ramp-up limit (MW/h);Ramp-down limit (MW/h);")
    f.write("Minimum up-time (h);Minimum down-time (h);Bus id;Constant cost ($);Start-up cost ($);")
    f.write("Shut-down cost ($);Reserve eligibility;Comments\n")

    i = 0
    for g, gen in data["Generators"].items():
        f.write(g.replace("g","") + ";")
        f.write(g + ";")
        f.write(str(gen["Production cost curve (MW)"][0]) + ";")
        f.write(str(gen["Production cost curve (MW)"][1]) + ";")
        # to get the unitary cost, the total cost must be divided by the appropriate amount of
        # generation
        if gen["Production cost curve (MW)"][1] > 0:
            f.write(str(gen["Production cost curve ($)"][1]/gen["Production cost curve (MW)"][1]))
        else:
            f.write(str(gen["Production cost curve ($)"][1]))
        f.write(";")
        f.write(str(gen["Ramp up limit (MW)"]) + ";")
        f.write(str(gen["Ramp down limit (MW)"]) + ";")
        f.write(str(gen["Minimum uptime (h)"]) + ";")
        f.write(str(gen["Minimum downtime (h)"]) + ";")
        f.write(gen["Bus"].replace("b","") + ";")
        f.write("0;")
        f.write(str(gen["Startup costs ($)"][0]) + ";")
        f.write("0;")
        assert len(gen["Reserve eligibility"]) <= 1
        if len(gen["Reserve eligibility"]) == 1:
            f.write(gen["Reserve eligibility"][0] + ";")
        else:
            f.write("None;")
        f.write("\n")
        i += 1
    f.write("</Thermal plants>\n")
    f.write("<Deficit cost>\n")
    f.write("Deficit cost  in ($/(MWh/h))\n")
    f.write(str(data['Parameters']['Power balance penalty ($/MW)']) + "\n")
    f.write("</Deficit cost>\n")

    f.write("</END>")
    f.close()
    del f

    f = open(out_dir + 'case ' + case_name + '/'
                "initial states of thermal units - " + system_name + " - case "+case_name+".csv",
                'w', encoding = 'ISO-8859-1')
    f.write("<BEGIN>\n")
    f.write("<Thermal plants>\n")
    f.write("ID;Name;Generation in time t = -1 in MW;")
    f.write("State in t = -1. Either 1, if up, or 0, if down;")
    f.write("Start-up trajectory (TRUE or FALSE);Shut-down trajectory (TRUE or FALSE);")
    f.write("Number of hours (> 0) in the state of t = -1\n")
    i = 0
    for g, gen in data["Generators"].items():
        f.write(g.replace("g","") + ";")
        f.write(g + ";")
        f.write(str(gen["Initial power (MW)"]) + ";")
        if float(gen["Initial status (h)"]) <= 0:
            f.write("0;FALSE;FALSE;")
            f.write(str(-1*int(gen["Initial status (h)"])) + ";")
        else:
            f.write("1;FALSE;FALSE;")
            f.write(str(int(gen["Initial status (h)"])) + ";")
        f.write("\n")
        i += 1
    f.write("</Thermal plants>\n")
    f.write("</END>")
    f.close()
    del f

    f = open(out_dir + "network - " + system_name + ".csv", 'w', encoding = 'ISO-8859-1')
    ref_defined = False
    f.write("<BEGIN>\n")
    f.write("<Buses>\n")
    f.write("ID;Name;Reference bus;Base voltage (kV);Area;Subsystem market - Name;")
    f.write("Subsystem market - ID\n")

    for bus in data["Buses"].keys():
        f.write(bus.replace("b", "") + ";")
        f.write("Bus" + str(bus.replace("b", "")) + ";")
        if not(ref_defined):
            f.write("Ref;")
            ref_defined = True
        else:
            f.write(";")
        f.write("45;")
        f.write("1;")
        f.write("sys1;")
        f.write("1\n")
    f.write("</Buses>\n")
    f.write("<AC Transmission lines>\n")
    f.write("From (ID);From (Name);To (ID);To (Name);Line rating (MW);")
    f.write("Reactance (p.u.) - 100-MVA base\n")
    i = 0
    for l, line in data["Transmission lines"].items():
        b_from_id = int(line["Source bus"].replace("b", ""))
        b_from_name = line["Source bus"].replace("b", "Bus")
        b_to_id = int(line["Target bus"].replace("b", ""))
        b_to_name = line["Target bus"].replace("b", "Bus")
        f.write(str(b_from_id) + ';')
        f.write(str(b_from_name) + ';')
        f.write(str(b_to_id) + ';')
        f.write(str(b_to_name) + ';')
        if "Normal flow limit (MW)" in line.keys():
            f.write(str(line["Normal flow limit (MW)"]) + ';')
        else:
            f.write('99999;')
        f.write(str(1/(line["Susceptance (S)"]/100)) + ';')
        f.write("\n")
        i += 1
    f.write("</AC Transmission lines>\n")
    f.write("</END>\n")
    f.write("<DC Links>\n")
    f.write("From (ID);From (Name);To (ID);To (Name);Rating (MW)\n")
    f.write("</DC Links>")

    f.close()
    del f

    f = open(out_dir + 'case ' + case_name + '/'+
                "gross load - " + system_name + " - case " + case_name + ".csv",
                                                                    'w', encoding = 'ISO-8859-1')
    f.write('<BEGIN>\n')
    f.write('Bus/Hour;')
    for t in range(int(data["Parameters"]["Time horizon (h)"])):
        f.write(str(t) + ';')

    f.write("\n")

    for b_name, load in data["Buses"].items():
        f.write("Bus" + str(b_name.replace("b", "")) + ";")
        if isinstance(load["Load (MW)"], list):
            for t in range(data["Parameters"]["Time horizon (h)"]):
                f.write(str(load["Load (MW)"][t]) + ";")
        else:
            for t in range(data["Parameters"]["Time horizon (h)"]):
                f.write(str(load["Load (MW)"]) + ";")
        f.write("\n")
    f.write("</END>")
    f.close()
    del f

    f = open(out_dir + 'case ' + case_name + '/'+
                "reserves - " + system_name + " - case " + case_name + ".csv",
                                                                    'w', encoding = 'ISO-8859-1')
    f.write('<BEGIN>\n')
    f.write('Reserve ID;Hour;Reservse (MW)\n')
    for reserve in data['Reserves'].keys():
        assert data['Reserves'][reserve]['Type'] == 'Spinning'
        assert len(data['Reserves']['r1']['Amount (MW)']) == data["Parameters"]["Time horizon (h)"]
        for t, r in enumerate(data['Reserves']['r1']['Amount (MW)']):
            f.write(reserve + ";" + str(t) + ";" + str(r) + "\n")
    f.write("</END>")
    f.close()
    del f
