# -*- coding: utf-8 -*-
from typing import Tuple, Union
from numbers import Real
from numpy import ndarray

from constants import OptimizationStatus as OptS, Package, Model

from model.add_network import add_network
from model.add_thermal import add_thermal_bin, add_thermal_cont
from model.add_global_constrs import add_global_constrs


from src.params import Params
from components.thermal import Thermals
from components.network import Network

def build_full_solution(
        params:Params,
        thermals:Thermals,
        network:Network,
        incumbent:ndarray
    ) -> Union[list, list, dict[str, dict[tuple, Real]]]:
    """
    pddip only keeps track of the values of the coupling variables. Thus, once the
    optimization process is finished, if a full solution is sought, an additional step must be
    taken to build a full solution from the incumbent vector of coupling variables values.

    This function takes the incumbent, builds optimization models and fixes the values of the
    coupling variables in these models to their values in the incumbent, and then calls the
    appropriate solver to solve the optimization model. Then, if the optimization is successful,
    a full solution, including both coupling variables and all state variables, will be available.
    """

    for n_periods_per_subh in range(8, 0, -1):
        if (params.T % n_periods_per_subh) == 0:
            periods_per_subhorizon = {b: list(range(b*n_periods_per_subh,
                                                (b + 1)*n_periods_per_subh, 1))
                                            for b in range(int(params.T/n_periods_per_subh))}
            break

    (present_costs, future_costs) = ([0 for b in periods_per_subhorizon.keys()],
                                                        [0 for b in periods_per_subhorizon.keys()])

    full_solution = {'h_g': {}, 'vol': {}, 'turb': {}, 'by_pass': {}, 'pump': {}, 'spil': {},
                    'inflow': {}, 'outflow': {},
                    'st_up_tg': {}, 'st_dw_tg': {}, 'disp_stat_tg': {}, 't_g': {}, 't_g_disp': {},
                    's_load_curtailment': {}, 's_gen_surplus': {}, 's_renew_curtailment': {},
                    's_reserve': {}, 'theta': {}, 'flow': {}, 'link_flow': {}}

    for (b, periods) in periods_per_subhorizon.items():

        if params.PACKAGE == Package.MIP:
            m = ModelMIP('m', solver_name = params.SOLVER)
        elif params.PACKAGE == Package.PYOMO_KERNEL:
            m = ModelKERNEL('m', solver_name = params.SOLVER)
        elif params.PACKAGE == Package.PYOMO_CONCRETE:
            m = ModelCONCR('m', solver_name = params.SOLVER)

        m.verbose = 0

        if b != max(list(periods_per_subhorizon.keys())):
            m.set_obj_coeff(alpha, 0)

        st_up_t_g, st_dw_t_g, disp_stat_tg, _0 = add_thermal_bin(m,
                                                                params, thermals, network,
                                                                {}, {}, {},
                                                                incumbent, periods,
                                                                vtype = 'B')

        t_g, t_g_disp, _0 = add_thermal_cont(m, params, thermals, network,
                                            {}, incumbent,
                                            periods, st_up_t_g, st_dw_t_g, disp_stat_tg)

        s_reserve, _0 = add_global_constrs(m, params, thermals, network,
                                            disp_stat_tg,
                                                t_g,
                                                    t_g_disp,
                                                        periods)

        (theta, flow, link_flow,
                        s_load_curtailment, s_gen_surplus, s_renew_curtailment, _0) = add_network(m,
                                                                    params,
                                                                        thermals, network,
                                                                            t_g,
                                                                                periods, [])

        for g in thermals.ID:
            for t in periods:
                m.addConstr(st_up_t_g[g, t] == incumbent[params._MAP['st_up_tg'][g,t]],
                                                                    name = f'constrStUpTG_{g}_{t}')
                m.addConstr(st_dw_t_g[g, t] == incumbent[params._MAP['st_dw_tg'][g,t]],
                                                                    name = f'constrStDwTG_{g}_{t}')
                m.addConstr(disp_stat_tg[g, t] == incumbent[params._MAP['disp_stat_tg'][g,t]],
                                                                    name = f'constrDpTG_{g}_{t}')
                m.addConstr(t_g_disp[g,t] == incumbent[params._MAP['tg_disp'][g,t]],
                                                                    name = f'constrDpGenTG_{g}_{t}')

        m.max_mip_gap = 1e-6
        status = m.optimize()

        #m.write(f"post_solve_{b}.lp")

        if status not in (OptS.OPTIMAL, OptS.FEASIBLE):
            break

        print(f"Subhorizon {b}\t\t" +
                f"Gap (%): {100*((m.ObjVal - m.objective_bound)/m.ObjVal):.4f}",
                    flush=True)

        present_costs[b] = m.ObjVal
        if b == max(list(periods_per_subhorizon.keys())):
            present_costs[b] = m.ObjVal - m.get_var_x(alpha)
            future_costs[b] = m.get_var_x(alpha)

        full_solution['h_g'].update({k: m.get_var_x(hg[k]) for k in [k for k in hg.keys()
                                                            if k[-1] in periods]})
        full_solution['vol'].update({k:m.get_var_x(vol[k]) for k in [k for k in vol.keys()
                                                            if k[-1] in periods]})
        full_solution['turb'].update({k:m.get_var_x(turb[k]) for k in [k for k in turb.keys()
                                                            if k[-1] in periods]})
        full_solution['by_pass'].update({k: m.get_var_x(by_pass[k])
                                            for k in [k for k in by_pass.keys()
                                                if not(isinstance(by_pass[k], (int, float))) and
                                                                k[-1] in periods]})
        full_solution['pump'].update({k: m.get_var_x(pump[k]) for k in [k for k in pump.keys()
                                                if not(isinstance(pump[k], (int, float))) and
                                                                k[-1] in periods]})
        full_solution['spil'].update({k:m.get_var_x(spil[k]) for k in [k for k in spil.keys()
                                                            if k[-1] in periods]})
        full_solution['inflow'].update({k: m.get_var_x(inflow[k]) for k in [k for k in inflow.keys()
                                                if not(isinstance(inflow[k], (int, float))) and
                                                                k[-1] in periods]})
        full_solution['inflow'].update({k: inflow[k] for k in [k for k in inflow.keys()
                                                if isinstance(inflow[k], (int, float)) and
                                                                k[-1] in periods]})
        full_solution['outflow'].update({k: m.get_var_x(outflow[k])
                                                for k in [k for k in outflow.keys()
                                                            if k[-1] in periods]})
        full_solution['st_up_tg'].update({k: m.get_var_x(st_up_t_g[k])
                                                        for k in [k for k in st_up_t_g.keys()
                                                            if k[-1] in periods]})
        full_solution['st_dw_tg'].update({k: m.get_var_x(st_dw_t_g[k])
                                                        for k in [k for k in st_dw_t_g.keys()
                                                            if k[-1] in periods]})
        full_solution['disp_stat_tg'].update({k: m.get_var_x(disp_stat_tg[k])
                                                for k in [k for k in disp_stat_tg.keys()
                                                            if k[-1] in periods]})
        full_solution['t_g'].update({k: m.get_var_x(t_g[k]) for k in [k for k in t_g.keys()
                                                            if k[-1] in periods]})
        full_solution['t_g_disp'].update({k: m.get_var_x(t_g_disp[k])
                                                        for k in [k for k in t_g_disp.keys()
                                                            if k[-1] in periods]})
        full_solution['s_load_curtailment'].update({k: m.get_var_x(s_load_curtailment[k])
                                                    for k in [k for k in s_load_curtailment.keys()
                                            if not(isinstance(s_load_curtailment[k], (int, float)))
                                                        and k[-1] in periods]})
        full_solution['s_load_curtailment'].update({k: s_load_curtailment[k]
                                                    for k in [k for k in s_load_curtailment.keys()
                                                if isinstance(s_load_curtailment[k], (int, float))
                                                            and k[-1] in periods]})
        full_solution['s_gen_surplus'].update({k: s_gen_surplus[k]
                                                    for k in [k for k in s_gen_surplus.keys()
                                                if isinstance(s_gen_surplus[k], (int, float))
                                                                and k[-1] in periods]})
        full_solution['s_gen_surplus'].update({k: m.get_var_x(s_gen_surplus[k])
                                                    for k in [k for k in s_gen_surplus.keys()
                                                if not(isinstance(s_gen_surplus[k], (int, float)))
                                                                and k[-1] in periods]})
        full_solution['s_renew_curtailment'].update({k: s_renew_curtailment[k]
                                                    for k in [k for k in s_renew_curtailment.keys()
                                                if isinstance(s_renew_curtailment[k], (int, float))
                                                            and k[-1] in periods]})
        full_solution['s_renew_curtailment'].update({k: m.get_var_x(s_renew_curtailment[k])
                                                    for k in [k for k in s_renew_curtailment.keys()
                                            if not(isinstance(s_renew_curtailment[k], (int, float)))
                                                            and k[-1] in periods]})
        full_solution['s_reserve'].update({k: m.get_var_x(s_reserve[k])
                                                            for k in [k for k in s_reserve.keys()
                                                            if k[-1] in periods]})
        full_solution['theta'].update({k: m.get_var_x(theta[k]) for k in [k for k in theta.keys()
                                                            if k[-1] in periods]})
        full_solution['flow'].update({k: m.get_var_x(flow[k])
                                                        for k in [k for k in flow.keys()
                                                            if k[-1] in periods]})
        full_solution['link_flow'].update({k: m.get_var_x(link_flow[k])
                                                        for k in [k for k in link_flow.keys()
                                                            if k[-1] in periods]})

    if status not in (OptS.OPTIMAL, OptS.FEASIBLE):
        m.write(params.OUT_DIR + 'post_optimization.lp')
        m.write(params.OUT_DIR + 'post_optimization.mps')

        raise ValueError('The status of the post-optimization model is ' + str(status))

    return present_costs, future_costs, full_solution