# -*- coding: utf-8 -*-
from timeit import default_timer as dt
import gurobipy as grbpy

from constants import Model, Var
from model.add_all_components import add_all_comp

from parameters.params import Params
from components.thermal import Thermals
from components.network import Network

def run_solver(params: Params, thermals: Thermals, network: Network):
    """
    Build the optimization model and solve it with Gurobi.

    :param params: Parameters of the optimization model and algorithm.
    :type params: Params
    :param thermals: Data of the thermal units.
    :type thermals: Thermals
    :param network: Data of the network.
    :type network: Network

    :return m: Gurobi optimization model object
    :rtype m: Model
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
    ini = dt()

    env = grbpy.Env(empty=True)
    env.setParam('OutputFlag', params.VERBOSE)
    env.setParam('LogFile', params.OUT_DIR + f"/unit_commitment_{params.PS}.log")
    env.start()
    m = grbpy.Model(name=f"unit_commitment_{params.PS}", env=env)
    m.setParam("LogToConsole", params.VERBOSE)

    (st_up_tg, st_dw_tg, disp_stat_tg,
            tg, t_g_disp,
            s_reserve,
            theta,
            branch_flow,
            s_load_curtailment, s_gen_surplus, s_renew_curtailment) = add_all_comp(params,
                                                                                   thermals,
                                                                                   network,
                                                                                   m,
                                                                                   vtype='B')

    print(f'\n\n{dt() - ini:.2f} seconds to build the optimization model.\n\n', flush=True)

    m.setParam("Threads", params.THREADS)
    m.setParam("MIPGap", params.MILP_GAP)
    m.setParam("TimeLimit", params._LAST_TIME - dt())
    m.write("new.lp")
    m.optimize()

    return (m,
            st_up_tg, st_dw_tg, disp_stat_tg,
            tg, t_g_disp,
            s_reserve,
            theta,
            branch_flow,
            s_load_curtailment, s_gen_surplus, s_renew_curtailment)
