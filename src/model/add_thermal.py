# -*- coding: utf-8 -*-

from typing import Union
from numbers import Real
import math

from params import Params
from components.thermal import Thermals
from components.network import Network
from constants import (Model, quicksum, Var, MAX_FLOW)


def _add_sec_constraints_only_on_thermals(
        m,
        params,
        thermals,
        network,
        t_g,
):
    """
    Add security constraints to the model
    """

    m.update()

    s_sec_constrs = {}

    # get a list of the buses whose injections appear in one or more security constraints
    constrs_w_buses = set()
    for t in range(params.T):
        for key, constr in [(item[0], item[1]) for item in network.SEC_CONSTRS[t].items()
                            if (item[1]['LB'] > -(MAX_FLOW / params.POWER_BASE) or
                                item[1]['UB'] < (MAX_FLOW / params.POWER_BASE))]:
            constrs_w_buses.add((t, key))

    constrs_w_buses = list(constrs_w_buses)
    constrs_w_buses.sort()

    power_injections = {(constr_id, t): - network.SEC_CONSTRS[t][constr_id]['net load']
                        for t, constr_id in constrs_w_buses
                        if len(network.SEC_CONSTRS[t][constr_id]['participants']['thermals']) >= 1
                        }

    for k in power_injections.keys():
        (constr_id, t) = k
        power_injections[constr_id, t] = (power_injections[constr_id, t] +
                                          quicksum(network.SEC_CONSTRS[t][constr_id]
                                                 ['participants_factors']['thermals'][g] *
                                                 t_g[g, t]
                                                 for g in
                                                 network.SEC_CONSTRS[t][constr_id]['participants'][
                                                     'thermals']
                                                 )
                                          )

    slacks = {}

    for (constr_id, t) in power_injections.keys():
        constr = network.SEC_CONSTRS[t][constr_id]

        # get all thermal units that participate in this constraint
        all_thermals = network.SEC_CONSTRS[t][constr_id]['participants']['thermals']

        if constr['LB'] != constr['UB']:
            if constr['LB'] > -(MAX_FLOW / params.POWER_BASE):
                g = all_thermals[0]
                const = - network.SEC_CONSTRS[t][constr_id]['net load']
                if len(all_thermals) == 1:
                    (var, coeff) = (t_g[g, t], network.SEC_CONSTRS[t][constr_id]
                    ['participants_factors']['thermals'][g])
                    if coeff > 0:
                        var.lb = max((constr['LB'] - const) / coeff, var.lb)
                    elif coeff < 0:
                        var.ub = min((constr['LB'] - const) / coeff, var.ub)
                else:
                    obj_coeff = params.DEFICIT_COST if t in range(params.T) else 0

                    slacks['LB', constr['name'], t] = m.addVar(obj=obj_coeff,
                                                name=f"slack_thermals_only_LB_{constr['name']}_{t}")

                    m.addConstr(power_injections[constr_id, t]
                                 + slacks['LB', constr['name'], t] >= constr['LB'],
                                 name=f"thermals_only_{constr['name']}_LB_{t}")
            if constr['UB'] < (MAX_FLOW / params.POWER_BASE):
                g = all_thermals[0]
                const = - network.SEC_CONSTRS[t][constr_id]['net load']
                if len(all_thermals) == 1 and thermals.MAX_P[g] <= (constr['UB'] - const):
                    (var, coeff) = (t_g[g, t], network.SEC_CONSTRS[t][constr_id]
                    ['participants_factors']['thermals'][g])
                    if coeff > 0:
                        var.ub = min((constr['UB'] - const) / coeff, var.ub)
                    elif coeff < 0:
                        var.lb = max((constr['UB'] - const) / coeff, var.lb)
                else:
                    obj_coeff = params.DEFICIT_COST if t in range(params.T) else 0

                    slacks['UB', constr['name'], t] = m.addVar(obj=obj_coeff,
                                                name=f"slack_thermals_only_UB_{constr['name']}_{t}")

                    m.addConstr(power_injections[constr_id, t]
                                 - slacks['UB', constr['name'], t] <= constr['UB'],
                                 name=f"thermals_only_{constr['name']}_UB_{t}")
        else:
            m.addConstr(power_injections[constr_id, t] == constr['LB'],
                         name=f"thermals_only_{constr['name']}_EQ_{t}")

        m.update()

    return s_sec_constrs

def _previous_states(params, thermals,
                     m,
                     st_up_tg, st_dw_tg, disp_status) -> None:
    """Create auxiliary keys and set variables bounds according to the states
    previous to the optimization horizon"""

    # the previous statuses of thermal units and their respective minimum up and down times, as well
    # as the ramping limits, might prevent the unit from being shut-down during a certain portion
    # of the scheduling horizon
    sd_dec = {g: 0 for g in thermals.ID}
    for g in thermals.ID:
        if thermals.STATE_0[g] and not (thermals.T_G_0[g] <= thermals.MIN_P[g]):
            sd_dec[g] = params.T
            p_decrease = 0
            for t in range(params.T):
                p_decrease += thermals.RAMP_DOWN[g]
                if (thermals.T_G_0[g] - p_decrease) <= thermals.MIN_P[g]:
                    # The unit reaches the minimum at t, and can be turned off at t + 1
                    sd_dec[g] = t + 1
                    # remember that the signal to shut down happens immediately after reaching the
                    # minimum, i.e., at t + 1
                    break

    for g in thermals.ID:
        for t in set(range(0, min(sd_dec[g], params.T), 1)):
            st_dw_tg[g, t].ub = 0

    # Previous states
    for g in thermals.ID:

        n_hours = (math.ceil((thermals.MAX_P[g] - thermals.MIN_P[g]) / thermals.RAMP_UP[g])
                   if thermals.RAMP_UP[g] > 0 else 0)

        for t in range(- 4 * thermals.MIN_UP[g] - n_hours, 0, 1):
            disp_status[g, t] = thermals.STATE_0[g]
            st_up_tg[g, t] = 0
        for t in range(- max(thermals.MIN_DOWN[g], thermals.MIN_UP[g], n_hours, 1), 0, 1):
            st_dw_tg[g, t] = 0

        for t in range(params.T, params.T + n_hours + 1, 1):
            st_dw_tg[g, t] = 0

        for t in range(- n_hours, 0, 1):
            disp_status[g, t] = thermals.STATE_0[g]

        if thermals.STATE_0[g]:
            # Either if it is currently in a start-up trajectory or it has already finished
            # the trajectory, the generator was
            # brought on at time - thermals.N_HOURS_IN_PREVIOUS_STATE[g].
            # However, if it is currently in the shut-down trajectory, then it will eventually
            # be shut-down during the scheduling horizon

            # If the unit is currently in the dispatch phase, then it means that, at some point,
            # the unit was started-up and it successfully completed its start-up trajectory.
            # Thus, the unit was started-up at period 0 minus the number of periods it has been
            # in the dispatch phase (thermals.N_HOURS_IN_PREVIOUS_STATE[g]) minus the number
            # of periods necessary to complete the start-up trajectory
            st_up_tg[g, min(- thermals.N_HOURS_IN_PREVIOUS_STATE[g], -1)] = 1
            disp_status[g, -1] = 1
        else:
            st_dw_tg[g, min(-thermals.N_HOURS_IN_PREVIOUS_STATE[g], -1)] = 1
            disp_status[g, -1] = 0

def _get_var_bounds(
        params,
        thermals,
        vtype
) -> tuple[dict[int, int], dict[int, str], dict[int, int]]:
    """get start-up and shut-down decisions bounds according the characteristics and initial
    states of the thermal units"""
    # choose the variable type and upper bound of the start-up decisions according to the
    # characteristics of the unit as well as its initial state
    st_up_ub = {g: 0 if ((thermals.MIN_P[g] + thermals.CONST_COST[g]) == 0
                             or (thermals.GEN_COST[g] + thermals.CONST_COST[g]) == 0) else 1
                for g in thermals.ID}

    for g in [g for g in thermals.ID
              if st_up_ub[g] == 1 and thermals.STATE_0[g] == 1
                 and thermals.MIN_DOWN[g] >= (params.T * params.DISCRETIZATION)
              ]:

        # then the unit has already been up for at least its minimum up time and, if it is
        # shut down, it cannot be started up again during the current unit commitment because
        # the scheduling horizon is less than or equal to its minimum down time
        st_up_ub[g] = 0

    # choose the variable type and upper bound of the shut-down decisions according to the
    # characteristics of the unit as well as its initial state
    st_dw_type = {g: 'C' if ((thermals.MIN_P[g] + thermals.CONST_COST[g]) == 0
                             or (thermals.GEN_COST[g] + thermals.CONST_COST[g]) == 0)
                        else vtype for g in thermals.ID}
    st_dw_ub = {g: 0 if ((thermals.MIN_P[g] + thermals.CONST_COST[g]) == 0
                     or (thermals.GEN_COST[g] + thermals.CONST_COST[g]) == 0)
                    else 1
                for g in thermals.ID}

    for g in [g for g in thermals.ID
              if st_dw_ub[g] == 1 and thermals.STATE_0[g] == 0
                 and thermals.MIN_UP[g] >= (params.T * params.DISCRETIZATION)
              ]:
        # in this case, the unit has already been off for the minimum number of hours
        # `thermals.MIN_DOWN[g]`, and, if it is started up, it must stay on during all periods
        # in the scheduling horizon after being turned on. thus, it cannot be shut down again
        # during the scheduling horizon
        st_dw_ub[g] = 0
        st_dw_type[g] = 'C'

    return st_up_ub, st_dw_type, st_dw_ub


def add_thermal_bin(
        m: Model,
        params: Params,
        thermals: Thermals,
        vtype: str='B'
) -> tuple[dict[tuple[int, int], Var], dict[tuple[int, int], Var], dict[tuple[int, int], Var]]:
    """Add binary variables associated with the thermals units

    :param m: Optimization model.
    :type m: Model
    :param params: Parameters of the optimization model and algorithm.
    :type params: Params
    :param thermals: Data of the thermal units.
    :type thermals: Thermals
    :param vtype: Type of variables to be added. Either "B" for binary, or "C" for continuous.
    :type vtype: str

    :return st_up_tg: Start-up decisions.
    :rtype st_up_tg: dict[tuple[int, int], Var]
    :return st_dw_tg: Shut-down decisions.
    :rtype st_dw_tg: dict[tuple[int, int], Var]
    :return disp_status: Dispatch-status decisions.
    :rtype disp_status: dict[tuple[int, int], Var]
    """

    tl_bin = [(g, t) for g in thermals.ID for t in range(params.T)]

    st_up_ub, st_dw_type, st_dw_ub = _get_var_bounds(params, thermals, vtype)

    st_up_tg = {(g, t): m.addVar(vtype=vtype, lb=0, ub=st_up_ub[g],
                                  obj=thermals.ST_UP_COST[g], name=f'st_up_tg_{g}_{t}')
                for (g, t) in tl_bin
                }

    st_dw_tg = {(g, t): m.addVar(vtype=st_dw_type[g], obj=thermals.ST_DW_COST[g],
                                  lb=0, ub=st_dw_ub[g], name=f'st_dw_tg_{g}_{t}')
                for (g, t) in tl_bin}

    disp_status = {(g, t): m.addVar(vtype=vtype,
                                     lb=1 if ((thermals.MIN_P[g] + thermals.CONST_COST[g]) == 0
                                              or (thermals.GEN_COST[g] + thermals.CONST_COST[g])
                                                    == 0)
                                     else 0,
                                     ub=1,
                                     obj=thermals.CONST_COST[g],
                                     name=f'disp_status_{g}_{t}'
                                     )
                   for (g, t) in tl_bin
                   }

    _previous_states(params, thermals, m, st_up_tg, st_dw_tg, disp_status)

    # Minimum up time
    for g in [g for g in thermals.ID if thermals.MIN_UP[g] > 0 and st_up_ub[g] == 1]:
        for t in range(params.T):
            m.addConstr(
                quicksum(st_up_tg[g, t2] for t2 in range(t - thermals.MIN_UP[g] + 1, t + 1, 1)
                       )
                <= disp_status[g, t],
                name=f'min_up_{g}_{t}'
            )

    # Minimum down time
    for g in [g for g in thermals.ID if thermals.MIN_DOWN[g] > 0 and st_dw_ub[g] == 1]:
        for t in range(params.T):
            m.addConstr(
                quicksum(st_dw_tg[g, t2] for t2 in range(t - thermals.MIN_DOWN[g] + 1, t + 1, 1)
                       )
                <= (1 - disp_status[g, t]),
                name=f'min_down_{g}_{t}'
            )

    # Logical constraints
    for g in thermals.ID:
        for t in range(params.T):
            m.addConstr((st_up_tg[g, t] - st_dw_tg[g, t]
                          - disp_status[g, t] + disp_status[g, t - 1] == 0), name=f'logical_{g}_{t}'
                        )

    _range_ub = max(range(params.T)) + 1
    st_up_tg = {(g, t): st_up_tg[g, t] for g in thermals.ID for t in range(0, _range_ub, 1)}
    st_dw_tg = {(g, t): st_dw_tg[g, t] for g in thermals.ID for t in range(0, _range_ub, 1)}
    disp_status = {(g, t): disp_status[g, t] for g in thermals.ID for t in range(0, _range_ub, 1)}

    return st_up_tg, st_dw_tg, disp_status


def add_thermal_cont(
        m: Model,
        params: Params,
        thermals: Thermals,
        network: Network,
        st_up_tg: dict[tuple[int, int], Var],
        st_dw_tg: dict[tuple[int, int], Var],
        disp_status: dict[tuple[int, int], Var]
) -> tuple[dict[tuple[int, int], Var], dict[tuple[int, int], Var]]:
    """
    Add continuous variables and their constraints to the thermal model

    :param m: Optimization model.
    :type m: Model
    :param params: Parameters of the optimization model and algorithm.
    :type params: Params
    :param thermals: Data of the thermal units.
    :type thermals: Thermals
    :param network: Data of the network.
    :type network: Network
    :param st_up_tg: Start-up decisions.
    :type st_up_tg: dict[tuple[int, int], Union[Var, Real]]
    :param st_dw_tg: Shut-down decisions.
    :type st_dw_tg: dict[tuple[int, int], Union[Var, Real]]
    :param disp_status: Dispatch statuses.
    :type disp_status: dict[tuple[int, int], Union[Var, Real]]

    :return t_g: Total thermal generation.
    :rtype t_g: dict[tuple[int, int], Var]
    :return t_g_disp: Generation in dispatch phase.
    :rtype t_g_disp: dict[tuple[int, int], Var]
    """

    st_up_ub, _, st_dw_ub = _get_var_bounds(params, thermals, 'C')


    # get the thermal units that need two generation variables: one dispatch,
    # and one total gen
    _two_vars_units = [g for g in thermals.ID if thermals.MIN_P[g] > 0]

    # and the units that need a single generation variable
    _single_var_units = list(set(thermals.ID) - set(_two_vars_units))
    _single_var_units.sort()

    t_g_disp = {}
    for g in _single_var_units:
        t_g_disp.update(
            {(g, t): m.addVar(obj=thermals.GEN_COST[g],
                              ub=thermals.MAX_P[g] - thermals.MIN_P[g],
                               name=f"t_g_disp_{g}_{t}"
                            )
             for t in range(params.T)
             }
        )

    for g in _two_vars_units:
        t_g_disp.update({(g, t): m.addVar(name=f"t_g_disp_{g}_{t}")
                         for t in range(params.T)}
        )

    t_g = {(g, t): m.addVar(obj=thermals.GEN_COST[g], name=f'tg_{g}_{t}')
           for t in range(params.T)
           for g in _two_vars_units
           }

    t_g.update({(g, t): t_g_disp[g, t] for t in range(params.T)
                for g in _single_var_units}
    )

    # lower and upper operating limits of thermal units
    for g in [g for g in thermals.ID if thermals.MIN_P[g] > 0]:
        gen_range = thermals.MAX_P[g] - thermals.MIN_P[g]
        for t in range(params.T):
            m.addConstr(t_g_disp[g, t] - gen_range * disp_status[g, t] <= 0,
                        name=f'max_p_{g}_{t}')

    # total generation
    for g in [g for g in thermals.ID if thermals.MIN_P[g] > 0]:
        for t in range(params.T):
            m.addConstr(t_g[g, t] - t_g_disp[g, t] -
                        thermals.MIN_P[g] * disp_status[g, t] == 0,
                        name=f'gen_{g}_{t}'
            )

    # ramp limits
    for g in thermals.ID:
        if not thermals.STATE_0[g]:
            m.addConstr(t_g_disp[g, 0] <= 0, name=f'ramp_up_{g}_{0}')
        else:
            # Python might mess up the arithmetics, so round it
            _rhs = max((thermals.T_G_0[g] - thermals.MIN_P[g]) + thermals.RAMP_UP[g], 0)
            m.addConstr(t_g_disp[g, 0] <= _rhs, name=f'ramp_up_{g}_{0}')
            _rhs = max(-(thermals.T_G_0[g] - thermals.MIN_P[g]) + thermals.RAMP_DOWN[g], 0)
            m.addConstr(- t_g_disp[g, 0] <= _rhs, name=f'ramp_down_{g}_{0}')

    for g in [g for g in thermals.ID
              if thermals.RAMP_UP[g] < (thermals.MAX_P[g] - thermals.MIN_P[g])
    ]:

        if (st_up_ub[g] == 1 or
            st_dw_ub[g] == 1 or
            thermals.RAMP_UP[g] != thermals.RAMP_DOWN[g]
        ):
            if st_up_ub[g] == 1:
                for t in range(1, params.T, 1):
                    m.addConstr(t_g_disp[g, t] - t_g_disp[g, t - 1]
                                 <= thermals.RAMP_UP[g] * disp_status[g, t - 1],
                                 name=f'ramp_up_{g}_{t}'
                    )
            else:
                for t in range(1, params.T, 1):
                    m.addConstr(t_g_disp[g, t] - t_g_disp[g, t - 1]
                                <= thermals.RAMP_UP[g],
                                 name=f'ramp_up_{g}_{t}'
                    )
            if st_dw_ub[g] == 1:
                for t in range(1, params.T, 1):
                    m.addConstr(- t_g_disp[g, t] + t_g_disp[g, t - 1]
                                 <= thermals.RAMP_DOWN[g] * disp_status[g, t],
                                 name=f'ramp_down_{g}_{t}'
                    )
            else:
                for t in range(1, params.T, 1):
                    m.addConstr(- t_g_disp[g, t] + t_g_disp[g, t - 1]
                                <= thermals.RAMP_DOWN[g],
                                 name=f'ramp_down_{g}_{t}'
                    )

        else:

            aux_ramp = {(g, t): m.addVar(ub=2 * thermals.RAMP_DOWN[g],
                                          name=f"ramp_aux_{g}_{t}")
                                          for t in range(1, params.T, 1)}

            for t in range(1, params.T, 1):
                m.addConstr(- t_g_disp[g, t] +
                            t_g_disp[g, t - 1] + aux_ramp[g, t]
                             == thermals.RAMP_DOWN[g],
                             name=f'ramp_{g}_{t}'
                )

    # start-up and shut-down capabilities
    for g in [g for g in thermals.ID
                if (thermals.RAMP_UP[g] >=
                    (thermals.MAX_P[g] - thermals.MIN_P[g]))
    ]:
        # the following inequalities are only added for units
        # that do not actually have meaningful
        # ramp limits. For units with ramp limits, the inequalities
        # ramp_up and ramp_down already
        # guarantee that the unit operates at its minimum when it is started-up
        # and right before being shut-down.
        gen_range = thermals.MAX_P[g] - thermals.MIN_P[g]
        if st_up_ub[g] == 1:
            for t in range(1, params.T, 1):
                m.addConstr(t_g_disp[g, t]
                            <= gen_range * disp_status[g, t - 1],
                             name=f'start_up_cap_{g}_{t}'
                )
        if st_dw_ub[g] == 1:
            for t in range(1, params.T, 1):
                m.addConstr(t_g_disp[g, t - 1]
                            <= gen_range * disp_status[g, t],
                             name=f'shut_down_cap_{g}_{t}'
                )

    for g in thermals.ID:
        if (thermals.STATE_0[g] and
            not (isinstance(st_dw_tg[g, 0], (int, float))) and
            (thermals.MAX_P[g] - thermals.MIN_P[g]) > 0
        ):
            m.addConstr(- (thermals.MAX_P[g] - thermals.T_G_0[g]) <=
                        - (thermals.MAX_P[g] - thermals.MIN_P[g]) *
                            st_dw_tg[g, 0],
                        name=f'shut_down_cap_{g}_{0}'
            )

    # additional constraints from the network reduction
    if len(network.SEC_CONSTRS) > 0:
        _ = _add_sec_constraints_only_on_thermals(m, params, thermals, network,
                                                  t_g
        )

    return t_g, t_g_disp
