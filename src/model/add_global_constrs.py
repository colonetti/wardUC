# -*- coding: utf-8 -*-

from typing import Union
from numbers import Real

from src.params import Params
from components.thermal import Thermals
from components.network import Network

from constants import Model, quicksum, Var

def add_global_constrs(
        m: Model,
        params: Params,
        thermals: Thermals,
        network: Network,
        disp_status: dict[tuple[int, int], Union[Var, Real]],
        t_g_disp: dict[tuple[int, int], Var]
):
    """Add variables and constrains of system-wide requirements that are not directly dependent
    on voltage angles and transmission flows

    :param m: Optimization model.
    :type m: Model
    :param params: Parameters of the optimization model and algorithm.
    :type params: Params
    :param thermals: Data of the thermal units.
    :type thermals: Thermals
    :param network: Data of the network.
    :type network: Network
    :param disp_status: Dispatch statuses.
    :type disp_status: dict[tuple[int, int], Union[Var, Real]]
    :param t_g: thermal generation.
    :type t_g: dict[tuple[int, int], Var]
    :param t_g_disp: thermal generation in dispatch phase.
    :type t_g_disp: dict[tuple[int, int], Var]

    :return: s_reserve
    :rtype: dict[str, Var]
    """

    overlapping_costs = 0

    s_reserve = {(res, t): m.addVar(obj=params.DEFICIT_COST, name=f'slack_reserve_{res}_{t}')
                 for res in network.RESERVES.keys()
                 for t in [t for t in range(params.T) if network.RESERVES[res][t] > 0]}

    for res in network.RESERVES.keys():
        for t in [t for t in range(params.T) if network.RESERVES[res][t] > 0]:
            m.addConstr(
                quicksum(
                    (disp_status[g, t] * (thermals.MAX_P[g] - thermals.MIN_P[g]) - t_g_disp[g, t])
                    for g in thermals.ID if thermals.RESERVE_ELEGIBILITY[g] == res
                )
                + s_reserve[res, t]
                >= network.RESERVES[res][t],
                name=f"{res}_{t}"
            )

    return s_reserve
