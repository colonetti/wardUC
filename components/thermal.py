# -*- coding: utf-8 -*-

from numbers import Real

from parameters.params import Params


class Thermals:
    """
    An instance of this class contains all data related to the thermal generating units.
    Data for specific units can be accessed by using the unit ID as provided in the input file.
    """

    def __init__(self: "Thermals"):

        #: IDs of all units in the system, as in the input files. If the input file was a json, then
        #: the IDs are the integer parts of the Generators; if pddip format was used, then the IDs
        #: are taken from column ID of csv file powerPlants.
        self.ID: list[int] = []

        self.UNIT_NAME: dict[int, str] = {}  #: String name of each unit.

        #: Minimum generation in pu (base `params.POWER_BASE`) if the unit is in the dispatch phase.
        self.MIN_P: dict[int, Real] = {}

        #: Maximum generation in pu (base `params.POWER_BASE`) if the unit is in the dispatch phase.
        self.MAX_P: dict[int, Real] = {}

        #: Unitary generation cost in $/pu, and scaled by params.SCAL_OBJ_F.
        self.GEN_COST: dict[int, Real] = {}

        #: Maximum increase in generation in pu/(1 h / `params.DISCRETIZATION`) between two
        #: consecutive periods when the unit is in the dispatch phase.
        self.RAMP_UP: dict[int, Real] = {}

        #: Maximum increase in generation in pu/(1 h / `params.DISCRETIZATION`) between two
        #: consecutive periods when the unit is in the dispatch phase.
        self.RAMP_DOWN: dict[int, Real] = {}

        #: Minimum number of hours in the dispatch phase once the unit is started up.
        self.MIN_UP: dict[int, int] = {}

        #: Minimum number of hours off once the unit is shut down.
        self.MIN_DOWN: dict[int, int] = {}

        #: Buses (nodes) to which the unit is connected to. If no network reduction is used, then
        #: all units are each connected to a single bus, as given by the input data.
        self.BUS: dict[int, list[int]] = {}

        #: Coefficient of the power injection of the units to the buses (nodes) they are connected
        #: to. If no network reduction is used, then all units are each connected to a single bus
        #: and the coefficient for them is 1.0.
        self.BUS_COEFF: dict[int, dict[int, Real]] = {}

        #: Constant cost in $, scaled by `params.SCAL_OBJ_F`, incurred once the unit is in the
        #: dispatch phase.
        self.CONST_COST: dict[int, Real] = {}

        #: Start-up cost in $, scaled by `params.SCAL_OBJ_F`, incurred once the unit is turned on.
        self.ST_UP_COST: dict[int, Real] = {}

        #: Start-up cost in $, scaled by `params.SCAL_OBJ_F`, incurred once the unit is shut down.
        self.ST_DW_COST: dict[int, Real] = {}

        #: Status of the unit in the period immediately before the scheduling horizon of the UC. The
        #: unit is considered OFF (False, or 0) if it was not in the dispatch phase in that period,
        #: and ON otherwise.
        self.STATE_0: dict[int, int] = {}

        #: Total generation in pu in the period immediately before the UC.
        self.T_G_0: dict[int, Real] = {}

        #: Number of hours in the previous status.
        self.N_HOURS_IN_PREVIOUS_STATE: dict[int, int] = {}

        #: A string identifier of the reserve requirement to which the unit can contribute to.
        self.RESERVE_ELEGIBILITY: dict[int, str] = {}

    def add_new_thermal(
            self: "Thermals",
            params: Params,
            row: list[str],
            header: dict[str, int]
    ):
        """Add a new thermal unit to the system

        :param self: the instance of Thermals to which the new unit is to be added
        :type sel: Thermals
        :param params: contains the relevant parameters to process the data of the new unit
        :type params: Params
        :param row: contains all data for the new unit
        :type row: list
        :param header: a map of the attributes to the indices of `row`
        :type header: dict

        :return: None
        :rtype: NoneType
        """

        self.ID.append(int(row[header['ID']]))
        self.UNIT_NAME[self.ID[-1]] = row[header['Name']]
        self.MIN_P[self.ID[-1]] = float(row[header['minP']]) / params.POWER_BASE
        self.MAX_P[self.ID[-1]] = float(row[header['maxP']]) / params.POWER_BASE
        self.GEN_COST[self.ID[-1]] = (params.DISCRETIZATION *
                                      params.POWER_BASE * float(row[header['genCost']]) *
                                      params.SCAL_OBJ_F
                                      )

        self.RAMP_UP[self.ID[-1]] = (params.DISCRETIZATION *
                                     float(row[header['rampUp']]) / params.POWER_BASE
                                     )
        self.RAMP_DOWN[self.ID[-1]] = (params.DISCRETIZATION *
                                       float(row[header['rampDown']]) / params.POWER_BASE
                                       )

        self.MIN_UP[self.ID[-1]] = (0 if params.DISCRETIZATION * int(row[header['minUp']]) <= 1
                                    else int(row[header['minUp']])
                                    )
        self.MIN_DOWN[self.ID[-1]] = (0 if params.DISCRETIZATION * int(row[header['minDown']]) <= 1
                                      else int(row[header['minDown']])
                                      )
        self.BUS[self.ID[-1]] = [(int(row[header['bus']]))]
        self.BUS_COEFF[self.ID[-1]] = {(int(row[header['bus']])): 1.00}

        self.CONST_COST[self.ID[-1]] = float(row[header['constCost']]) * params.SCAL_OBJ_F
        self.ST_UP_COST[self.ID[-1]] = float(row[header['stUpCost']]) * params.SCAL_OBJ_F
        self.ST_DW_COST[self.ID[-1]] = float(row[header['stDwCost']]) * params.SCAL_OBJ_F

        self.STATE_0[self.ID[-1]] = 0
        self.T_G_0[self.ID[-1]] = 0
        self.N_HOURS_IN_PREVIOUS_STATE[self.ID[-1]] = 0

        if header['Reserve eligibility'] is not None:
            self.RESERVE_ELEGIBILITY[self.ID[-1]] = row[header['Reserve eligibility']]
        else:
            self.RESERVE_ELEGIBILITY[self.ID[-1]] = None
