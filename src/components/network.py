# -*- coding: utf-8 -*-
from numbers import Real
from math import pi
import numpy as np
import networkx as nx

from src.params import Params
from components.thermal import Thermals

def _get_isolated_subsystems(network:"Network") -> dict:
    """
    Within a power system, there might be several subsystems that are not connected to any
    other portion of the system through an AC branch (a transmission line or a transformer).
    Thus, each of these isolated subsystems has a separated PTDF matrix
    """
    G = nx.Graph()

    G.add_edges_from([network.LINE_F_T[l] for l in network.LINE_ID])

    disjoint_subsystems = {}

    isolated_buses = set(network.BUS_ID)

    components = [G.subgraph(c).copy() for c in nx.connected_components(G)]
    for idx, component in enumerate(components):
        isolated_buses = isolated_buses - set(component.nodes())
        disjoint_subsystems[idx] = {'nodes': list(component.nodes()),
                                                                'edges': list(component.edges())}

    isolated_buses = list(isolated_buses)
    isolated_buses.sort()

    max_id = max(disjoint_subsystems.keys()) + 1

    for bus in isolated_buses:
        disjoint_subsystems[bus + max_id] = {'nodes': [bus], 'edges': []}

    return disjoint_subsystems


def get_buses_bounds_on_injections(
        params:Params,
        network:"Network",
        thermals:Thermals
    ):
    """
        for each bus in the system, get the most negative (largest load) and most positive
        (largest generation) injections based on the elements connected to the bus

        the bounds are given as minimum and maximum over the entire scheduling horizon
        and also as per-period bounds

        in computing these bounds, transmission elements are not considered
    """

    # get first the minimum and maximum injections for each period of the scheduling horizon
    min_inj_per_period = {bus: {t: 0 for t in range(params.T)} for bus in network.BUS_ID}
    max_inj_per_period = {bus: {t: 0 for t in range(params.T)} for bus in network.BUS_ID}

    for g in thermals.UNIT_NAME.keys():
        for bus in thermals.BUS[g]:
            for t in range(params.T):
                max_inj_per_period[bus][t] += thermals.BUS_COEFF[g][bus]*thermals.MAX_P[g]

    non_zero_inj_buses = [bus for bus in network.BUS_ID
                            if np.max(np.abs(network.NET_LOAD[network.BUS_HEADER[bus],:]),axis=0)>0]
    for t in range(params.T):
        for bus in non_zero_inj_buses:
            min_inj_per_period[bus][t] = (min_inj_per_period[bus][t]
                                                    - network.NET_LOAD[network.BUS_HEADER[bus], t])
            max_inj_per_period[bus][t] = (max_inj_per_period[bus][t]
                                                    - network.NET_LOAD[network.BUS_HEADER[bus], t])

    # now compute the bounds over the entire scheduling horizon by basically taking the
    # minimum of the minimums and the maximum of the maximums
    min_inj = {bus: min(min_inj_per_period[bus][t] for t in range(params.T))
                                                                        for bus in network.BUS_ID}
    max_inj = {bus: max(max_inj_per_period[bus][t] for t in range(params.T))
                                                                        for bus in network.BUS_ID}

    return (min_inj, max_inj, min_inj_per_period, max_inj_per_period)

def add_new_parallel_line(
                        resistance_line_1, reactance_line_1,
                        shunt_conductance_line_1, shunt_susceptance_line_1,
                        normal_UB_line_1, normal_LB_line_1,
                        emerg_UB_line_1, emerg_LB_line_1,
                        resistance_line_2, reactance_line_2,
                        shunt_conductance_line_2, shunt_susceptance_line_2,
                        normal_UB_line_2, normal_LB_line_2,
                        emerg_UB_line_2, emerg_LB_line_2):
    """Add a new parallel line to the system. all parameters must be in p.u."""

    # squared norm 2 of the impedance of line 1
    sq_norm_2_imp_line_1 = resistance_line_1**2 + reactance_line_1**2
    cond_line_1 = resistance_line_1/sq_norm_2_imp_line_1
    suscep_line_1 = - reactance_line_1/sq_norm_2_imp_line_1
    # magnitude of line 1's admittance
    mag_admt_line_1 = (cond_line_1**2 + suscep_line_1**2)**(1/2)

    # squared norm 2 of the impedance of line 2
    sq_norm_2_imp_line_2 = resistance_line_2**2 + reactance_line_2**2
    cond_line_2 = resistance_line_2/sq_norm_2_imp_line_2
    suscep_line_2 = - reactance_line_2/sq_norm_2_imp_line_2
    # magnitude of line 2's admittance
    mag_admt_line_2 = (cond_line_2**2 + suscep_line_2**2)**(1/2)

    #### parameters of the equivalent line
    # squared norm 2 of the admittance of the equivalent line
    sq_norm_2_admt_eq_line = (cond_line_1 + cond_line_2)**2 + (suscep_line_1 + suscep_line_2)**2
    conductance_eq_line = cond_line_1 + cond_line_2
    susceptance_eq_line = suscep_line_1 + suscep_line_2
    resistance_eq_line = conductance_eq_line/sq_norm_2_admt_eq_line
    reactance_eq_line = - susceptance_eq_line/sq_norm_2_admt_eq_line
    shunt_conductance_eq_line = shunt_conductance_line_1 + shunt_conductance_line_2
    shunt_susceptance_eq_line = shunt_susceptance_line_1 + shunt_susceptance_line_2
    # magnitude of the equivalent line's admittance
    mag_admt_eq_line = sq_norm_2_admt_eq_line**(1/2)

    # the magnitude of the apparent power flowing in a line i,j is given by
    # |s_i_j| = |V_i| * |conj(y_i_j)| * |conj(V_i - V_j)|
    # given that two parallel lines have the same end-point voltages and that their equivalent
    # admittance is y_eq_i_j, for the total flow between i,j and there are at least two
    # parallel lines, |s_i_j| is
    # |s_i_j| = |V_i| * |conj(y_eq_i_j)| * |conj(V_i - V_j)|
    # and yet, the acceptable values for V_i and V_j will depend on the individual limits of the
    # lines. thus, given that |V_i| * |conj(V_i - V_j)| is the same for all parallel lines
    # connecting i,j, then a maximum value for this product can be found by taking the minimum of
    # max_mag_prod = min{S_max_l/|conj(y_i_j_l)| for all l in L_i_j},
    # where L_i_j is the set of parallel lines between i,j

    normal_UB_eq_line = np.array(len(normal_UB_line_1)*[0.000])
    normal_LB_eq_line = np.array(len(normal_UB_line_1)*[0.000])
    emerg_UB_eq_line = np.array(len(emerg_UB_line_1)*[0.000])
    emerg_LB_eq_line = np.array(len(emerg_UB_line_1)*[0.000])
    for t in range(len(emerg_UB_line_1)):
        max_mag_prod_normal_UB = min(normal_UB_line_1[t]/mag_admt_line_1,
                                                            normal_UB_line_2[t]/mag_admt_line_2)
        max_mag_prod_emerg_UB = min(emerg_UB_line_1[t]/mag_admt_line_1,
                                                            emerg_UB_line_2[t]/mag_admt_line_2)

        normal_UB_eq_line[t] = max_mag_prod_normal_UB*mag_admt_eq_line
        emerg_UB_eq_line[t] = max_mag_prod_emerg_UB*mag_admt_eq_line

        max_mag_prod_normal_LB = max(normal_LB_line_1[t]/mag_admt_line_1,
                                                            normal_LB_line_2[t]/mag_admt_line_2)
        max_mag_prod_emerg_LB = max(emerg_LB_line_1[t]/mag_admt_line_1,
                                                            emerg_LB_line_2[t]/mag_admt_line_2)

        normal_LB_eq_line[t] = max_mag_prod_normal_LB*mag_admt_eq_line
        emerg_LB_eq_line[t] = max_mag_prod_emerg_LB*mag_admt_eq_line

    return(resistance_eq_line, reactance_eq_line,
            conductance_eq_line, susceptance_eq_line,
            shunt_conductance_eq_line, shunt_susceptance_eq_line,
            normal_UB_eq_line, normal_LB_eq_line,
            emerg_UB_eq_line, emerg_LB_eq_line)

class Network:
    """
    An instance of this class contains all data related to the thermal generating units.
    Data for specific units can be accessed by using the unit ID as provided in the input file.

    :return: an object of Network containing all data of the network.
    :rtype: Network
    """

    def __init__(self:"Network"):

        self.BUS_ID : list[int] = []            #: IDs of the network buses (nodes).

        self.BUS_NAME : dict[int, str] = {}     #: String name of each bus.

        #: Reference buses. Buses in this list will have their respective voltage angles set to 0.
        self.REF_BUS_ID : list[int] = []

        #: IDs of the transmission lines whose 'from' bus' ID is the dicts' key.
        self.LINES_FROM_BUS : dict[int, list[int]] = {}

        #: IDs of the transmission lines whose 'to' bus' ID is the dicts' key.
        self.LINES_TO_BUS : dict[int, list[int]] = {}

        self.LINE_ID : list[int] = []                   #: IDs of the transmission lines.

        self.LINE_F_T : dict[int, tuple[int, int]] = {} #: Endpoints of the transmission line.

        #: Upper bound on the transmission line flow in pu. If a network reduction is used, then the
        #: upper bound might not be the same in all periods. Thus, the upper bound is represented as
        #: an numpy array whose length is the number of periods in the scheduling horizon
        self.LINE_FLOW_UB : dict[int, np.ndarray[np.float64]] = {}

        #: Lower bound on the transmission line flow in pu. If a network reduction is used, then the
        #: lower bound might not be the same in all periods. Thus, the lower bound is represented as
        #: an numpy array whose length is the number of periods in the scheduling horizon
        self.LINE_FLOW_LB : dict[int, np.ndarray[np.float64]] = {}

        self.LINE_X : dict[int, Real] = {}              #: Transmission line reactance in pu/rad.

        self.BUS_HEADER : dict[int, int] = {}   #: A mapping of bus ID to bus index in `BUS_ID`.

        #: A numpy array of np.float64 with shape (number of buses, number of periods) of the net
        #: load in pu.
        self.NET_LOAD : np.ndarray = []

        self.THETA_BOUND : Real = 50*24*pi      #: Maximum voltage angle in rad.

        #: The Power Transfer Distribution Factors (PTDF) matrix, also called
        #: Injection Shift Factor (ISF)
        self.PTDF : np.ndarray = []

        #: A flag that indicates whether at least one of the bounds of the transmission line in at
        #: least of the periods is possibly binding (active).
        self.ACTIVE_BOUNDS : dict[int, bool] = {}

        #: A flag that indicates whether the upper bound of the transmission line in each period
        #: is possibly binding (active). If False, then there is no feasible dispatch for each
        #: the transmission line's flow can reach the upper bound.
        self.ACTIVE_UB_PER_PERIOD : dict[int, list[bool]] = {}

        #: A flag that indicates whether the lower bound of the transmission line in each period
        #: is possibly binding (active).
        self.ACTIVE_LB_PER_PERIOD : dict[int, list[bool]] = {}

        #: A flag that indicates whether the upper bound of the transmission line in at
        #: least of the periods is possibly binding (active).
        self.ACTIVE_UB : dict[int, bool] = {}

        #: A flag that indicates whether the lower bound of the transmission line in at
        #: least of the periods is possibly binding (active).
        self.ACTIVE_LB : dict[int, bool] = {}

        #: Data of constraints resulting from the network reduction.
        self.SEC_CONSTRS : dict[int, dict] = {}

        self.RESERVES : dict[str, dict[int, Real]] = {}     #: Reserve requirements in pu.

    def add_new_bus(self:"Network", row:list[str], header:dict[str, int]) -> None:
        """Add a new bus to the system

        :param self: the instance of Network to which the new bus is to be added
        :type sel: Network
        :param params: contains the relevant parameters to process the data of the new bus
        :type params: Params
        :param row: contains all data for the new bus
        :type row: list
        :param header: a map of the attributes to the indices of `row`
        :type header: dict

        :return: None
        :rtype: NoneType
        """

        bus = int(row[header['ID']].strip())

        self.BUS_ID.append(bus)
        self.BUS_NAME[self.BUS_ID[-1]] = row[header['Name']].strip()

        (self.LINES_FROM_BUS[bus], self.LINES_TO_BUS[bus]) = ([], [])

        if row[header['Reference bus']].strip() == 'Ref':
            self.REF_BUS_ID.append(bus)

    def _add_new_line(self:"Network", params:Params, line_id:int,
                    from_id:int, to_id:int,
                        reactance:float, resistance:float, shunt_conduc:float, shunt_suscep:float,
                            line_rating:float, emergency_rating:float,
                                tap_setting:float, min_tap:float, max_tap:float,
                                    phase_shift:float, controlled_bus:int):
        """Add a new transmission line to the network"""

        if from_id < to_id:
            f, t = from_id, to_id
        else:
            f, t = to_id, from_id

        cap = line_rating

        if (f, t) in self.LINE_F_T.values():
            l = [l for l in self.LINE_ID if self.LINE_F_T[l] == (f, t)][0]

            (_, self.LINE_X[l], _1, _2, _3, _4, self.LINE_FLOW_UB[l], self.LINE_FLOW_LB[l],
                                    _5, _6) = add_new_parallel_line(
                                                    0, reactance, 0, 0,
                                                    np.array(params.T*[cap/params.POWER_BASE]),
                                                    -1*np.array(params.T*[cap/params.POWER_BASE]),
                                                    np.array(params.T*[cap/params.POWER_BASE]),
                                                    -1*np.array(params.T*[cap/params.POWER_BASE]),
                                                    0,
                                                    self.LINE_X[l], 0, 0,
                                                    self.LINE_FLOW_UB[l], self.LINE_FLOW_LB[l],
                                                    self.LINE_FLOW_UB[l], self.LINE_FLOW_LB[l])

            self.ACTIVE_BOUNDS[l] = self.ACTIVE_BOUNDS[l] or cap < 99999
            self.ACTIVE_UB[l], self.ACTIVE_LB[l] = self.ACTIVE_BOUNDS[l], self.ACTIVE_BOUNDS[l]

            self.ACTIVE_UB_PER_PERIOD[l] = {t: self.ACTIVE_BOUNDS[l] for t in range(params.T)}
            self.ACTIVE_LB_PER_PERIOD[l] = {t: self.ACTIVE_BOUNDS[l] for t in range(params.T)}

        else:
            l = line_id
            self.LINE_ID.append(l)
            self.LINE_F_T[l] = (f, t)
            self.LINE_FLOW_UB[l] = np.array(params.T*[cap/params.POWER_BASE])
            self.LINE_FLOW_LB[l] = -1*np.array(params.T*[cap/params.POWER_BASE])
            self.LINE_X[l] = reactance

            self.ACTIVE_BOUNDS[l] = cap*params.POWER_BASE < 99999
            self.ACTIVE_UB[l], self.ACTIVE_LB[l] = self.ACTIVE_BOUNDS[l], self.ACTIVE_BOUNDS[l]
            self.ACTIVE_UB_PER_PERIOD[l] = {t: self.ACTIVE_BOUNDS[l] for t in range(params.T)}
            self.ACTIVE_LB_PER_PERIOD[l] = {t: self.ACTIVE_BOUNDS[l] for t in range(params.T)}

    def add_new_line(self:"Network", params:Params, row:list[str], header:dict[str, int]) -> None:
        """Add a new line to the system

        :param self: the instance of Network to which the new line is to be added
        :type sel: Network
        :param params: contains the relevant parameters to process the data of the new line
        :type params: Params
        :param row: contains all data for the new line
        :type row: list
        :param header: a map of the attributes to the indices of `row`
        :type header: dict

        :return: None
        :rtype: NoneType
        """

        if int(row[header['From (ID)']].strip()) < int(row[header['To (ID)']].strip()):
            f, t = int(row[header['From (ID)']].strip()), int(row[header['To (ID)']].strip())
        else:
            f, t = int(row[header['To (ID)']].strip()), int(row[header['From (ID)']].strip())

        cap = float(row[header['Cap']].strip())/params.POWER_BASE
        x = float(row[header['Reac']].strip())*(100/params.POWER_BASE)

        if (f, t) in self.LINE_F_T.values():
            l = [l for l in self.LINE_ID if self.LINE_F_T[l] == (f, t)][0]

            (_, self.LINE_X[l], _1, _2, _3, _4, self.LINE_FLOW_UB[l], self.LINE_FLOW_LB[l],
                                    _5, _6) = add_new_parallel_line(
                                                    0, x, 0, 0,
                                                    np.array(params.T*[cap]),
                                                    -1*np.array(params.T*[cap]),
                                                    np.array(params.T*[cap]),
                                                    -1*np.array(params.T*[cap]),
                                                    0,
                                                    self.LINE_X[l], 0, 0,
                                                    self.LINE_FLOW_UB[l], self.LINE_FLOW_LB[l],
                                                    self.LINE_FLOW_UB[l], self.LINE_FLOW_LB[l])

            self.ACTIVE_BOUNDS[l] = self.ACTIVE_BOUNDS[l] or cap*params.POWER_BASE < 99999
            self.ACTIVE_UB[l] = self.ACTIVE_BOUNDS[l]
            self.ACTIVE_LB[l] = self.ACTIVE_BOUNDS[l]
            self.ACTIVE_UB_PER_PERIOD[l] = {t: self.ACTIVE_BOUNDS[l] for t in range(params.T)}
            self.ACTIVE_LB_PER_PERIOD[l] = {t: self.ACTIVE_BOUNDS[l] for t in range(params.T)}

        else:
            l = max(self.LINE_ID,default=0) + 1
            self.LINE_ID.append(l)
            self.LINE_F_T[l] = (f, t)
            self.LINE_FLOW_UB[l] = np.array(params.T*[cap])
            self.LINE_FLOW_LB[l] = -1*np.array(params.T*[cap])
            self.LINE_X[l] = x

            self.LINES_FROM_BUS[f].append(l)
            self.LINES_TO_BUS[t].append(l)

            self.ACTIVE_BOUNDS[l] = cap*params.POWER_BASE < 99999
            self.ACTIVE_UB[l], self.ACTIVE_LB[l] = self.ACTIVE_BOUNDS[l], self.ACTIVE_BOUNDS[l]
            self.ACTIVE_UB_PER_PERIOD[l] = {t: self.ACTIVE_BOUNDS[l] for t in range(params.T)}
            self.ACTIVE_LB_PER_PERIOD[l] = {t: self.ACTIVE_BOUNDS[l] for t in range(params.T)}

    def get_gen_buses(
            self:"Network",
            thermals:Thermals,
        ) -> set:
        """Get the buses to which controllable generating elements are connected to."""

        return {bus for g in thermals.UNIT_NAME.keys() for bus in thermals.BUS[g]}

    def get_load_buses(
            self:"Network"
        ) -> set:
        """Get the buses for which in at least one period there is a nonzero net load."""

        return {bus for bus in self.BUS_ID if np.max(self.NET_LOAD[self.BUS_HEADER[bus]][:]) > 0}

    def get_renewable_gen_buses(
            self:"Network"
        ) -> set:
        """Get the buses for which in at least one period there is a nonzero fixed generation.
        """
        return {bus for bus in self.BUS_ID if min(self.NET_LOAD[self.BUS_HEADER[bus]][:]) < 0}
