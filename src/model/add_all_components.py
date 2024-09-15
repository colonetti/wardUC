# -*- coding: utf-8 -*-

from params import Params
from components.thermal import Thermals
from components.network import Network

from constants import NetworkModel
from model.add_network import add_network
from model.add_thermal import add_thermal_bin, add_thermal_cont
from model.add_global_constrs import add_global_constrs


def add_all_comp(
        params: Params,
        thermals: Thermals,
        network: Network,
        m: "Model",
        vtype: str='B'
    ) -> tuple[dict, dict, dict, dict, dict, dict, dict, dict, dict, dict, dict]:
    """
    Add all components of the unit-commitment problem to the Gurobi optimization model.

    :param params: Parameters of the optimization model and algorithm.
    :type params: Params
    :param thermals: Data of the thermal units.
    :type thermals: Thermals
    :param network: Data of the network.
    :type network: Network
    :param m: Optimization model. All binary variables and constraints where only binary variables
        appear will be added to this model
    :type m: Model
    :param vtype: Variable type for the variables that are originally binary. Either
        "B" or "C", defaults to "B".
    :type vtype: str
    :return st_up_tg: Start-up decision
    :rtype st_up_tg: dict[tuple[int, int], Var]
    :return st_dw_tg: Shut-down decisions
    :rtype st_dw_tg: dict[tuple[int, int], Var]
    :return disp_stat_tg: Dispatch-status decisions
    :rtype disp_stat_tg: dict[tuple[int, int], Var]
    :return tg: Total generation
    :rtype tg: dict[tuple[int, int], Var]
    :return t_g_disp: Generation in the dispatch phase
    :rtype t_g_disp: dict[tuple[int, int], Var]
    :return s_reserve: Slack variables associated with the reserve requirements.
    :rtype s_reserve: dict[tuple[int, int], Var]
    :return theta: Voltage angle
    :rtype theta: dict[tuple[int, int], Var]
    :return branch_flow: Branch flows
    :rtype branch_flow: dict[tuple[int, int, int, int], Var]
    :return s_load_curtailment: Load curtailment (load shedding) slack variables
    :rtype s_load_curtailment: dict[tuple[int, int], Var]
    :return s_gen_surplus: Generation surplus slack variables
    :rtype s_gen_surplus: dict[tuple[int, int], Var]
    :return s_renew_curtailment: Renewable generation curtailment slack variables
    :rtype s_renew_curtailment: dict[tuple[int, int], Var]
    """

    # Add the thermal binary variables and related constraints to model
    st_up_tg, st_dw_tg, disp_stat_tg = add_thermal_bin(m,
                                                       params,
                                                       thermals,
                                                       vtype=vtype
    )

    # Add the continuous part of the thermal units to the optimization model
    tg, t_g_disp = add_thermal_cont(m, params, thermals, network,
                                    st_up_tg, st_dw_tg, disp_stat_tg
    )

    # Add reserve constraints, if there is any
    s_reserve = add_global_constrs(m,
                                   params,
                                   thermals,
                                   network,
                                   disp_stat_tg,
                                   t_g_disp
    )

    # Add the network model
    if params.NETWORK_MODEL in (NetworkModel.B_THETA,
                                NetworkModel.FLUXES,
                                NetworkModel.PTDF
    ):
        (theta, branch_flow, s_load_curtailment,
         s_gen_surplus, s_renew_curtailment) = add_network(
                                                m,
                                                params, thermals, network,
                                                tg,
                                                flow_periods=
                                                 list(range(params.T)),
                                                single_bus_periods=[])
    else:
        (theta, branch_flow, s_load_curtailment,
         s_gen_surplus, s_renew_curtailment) = add_network(
                                                m,
                                                params, thermals, network,
                                                tg,
                                                flow_periods=[],
                                                single_bus_periods=
                                                 list(range(params.T)))

    return (st_up_tg, st_dw_tg, disp_stat_tg,
            tg, t_g_disp,
            s_reserve,
            theta,
            branch_flow,
            s_load_curtailment, s_gen_surplus, s_renew_curtailment)
