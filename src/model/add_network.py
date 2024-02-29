# -*- coding: utf-8 -*-
from timeit import default_timer as dt
import numpy as np

from parameters.params import Params
from components.thermal import Thermals
from components.network import Network, _get_isolated_subsystems

from constants import (NetworkModel, NetworkSlacks, Model, quicksum, Var)



def PTDF_formulation(
        m: Model,
        params: Params,
        thermals: Thermals,
        network: Network,
        t_g: dict[tuple[int, int], Var],
        s_load_curtailment: dict[tuple[int, int], Var],
        s_gen_surplus: dict[tuple[int, int], Var],
        s_renew_curtailment: dict[tuple[int, int], Var],
        s_line_violation: dict[tuple[int, int], Var],
        branch_flow: dict[tuple[int, int], Var],
        periods: list[int]
) -> None:
    """
    Use the PTDF formulation to represent the DC model
    """

    time_0 = dt()

    exp = get_bus_injection_expr(thermals, network,
                                 t_g,
                                 branch_flow,
                                 s_load_curtailment, s_gen_surplus, s_renew_curtailment,
                                 periods,
                                 include_flows=False
                                 )

    # get a set of buses for which at least in one period there might be a power injection
    # these are the buses to which either a load or a generating unit is connected to at some
    # point in time
    buses_with_injections_idxs = np.array([b for b, bus in enumerate(network.BUS_ID)
                                           if any((exp[bus, t].size() >= 1 or
                                                   abs(exp[bus, t].getConstant()) != 0
                                                   for t in periods))], dtype='int64')

    _PTDF = network.PTDF[:]
    _PTDF[np.where(abs(_PTDF) < params.PTDF_COEFF_TOL)] = 0

    possibly_active_bounds = [l for l in network.LINE_ID if network.ACTIVE_BOUNDS[l]]
    possibly_active_bounds_idxs = [l_idx for l_idx, l in enumerate(network.LINE_ID)
                                   if network.ACTIVE_BOUNDS[l]]
    map_idx = {l: l_sub_idx for l_sub_idx, l in enumerate(possibly_active_bounds)}

    constrs = []

    count_constrs_added = 0

    sub_PTDF_only_act_lines = _PTDF[possibly_active_bounds_idxs, :]

    non_zeros = np.intersect1d(np.where(abs(sub_PTDF_only_act_lines) > 0)[1],
                               buses_with_injections_idxs)
    buses_of_interest = [network.BUS_ID[b] for b in non_zeros]

    all_flows = (sub_PTDF_only_act_lines[:, non_zeros]
                 @ [[exp[bus, t] for t in periods] for bus in buses_of_interest])

    for l in possibly_active_bounds:
        l_idx = map_idx[l]

        ts = [t for t in periods if network.ACTIVE_UB_PER_PERIOD[l][t]
              or network.ACTIVE_LB_PER_PERIOD[l][t]]

        flows = all_flows[l_idx, :]

        for t in ts:

            l_key = network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t

            flow_exp = flows[ts.index(t)]

            if flow_exp.size() >= 1:
                if network.ACTIVE_UB_PER_PERIOD[l][t]:
                    constrs.append(m.addConstr(
                        flow_exp - s_line_violation[l_key] <= network.LINE_FLOW_UB[l][t],
                        name=f"ptdf_UB_{network.LINE_F_T[l][0]}_" +
                             f"{network.LINE_F_T[l][1]}_{l}_{t}"
                    )
                    )
                    count_constrs_added += 1

                if network.ACTIVE_LB_PER_PERIOD[l][t]:
                    constrs.append(m.addConstr(
                        flow_exp + s_line_violation[l_key] >= network.LINE_FLOW_LB[l][t],
                        name=f"ptdf_LB_{network.LINE_F_T[l][0]}_" +
                             f"{network.LINE_F_T[l][1]}_{l}_{t}"
                    )
                    )
                    count_constrs_added += 1

    for constr in constrs:
        constr.Lazy = 3

    disjoint_subsys = _get_isolated_subsystems(network)

    buses_in_system = set()

    for disj_subs, sub_sys in disjoint_subsys.items():
        buses_in_system = buses_in_system | set(sub_sys['nodes'])
        for t in periods:
            m.addConstr(quicksum(exp[bus, t] for bus in sub_sys['nodes']) == 0,
                        name=f"power_balance_{disj_subs}_{t}")

    #### some buses might not be in any subsystem because they are isolated
    for bus in [bus for bus in network.BUS_ID if bus not in buses_in_system]:
        for t in [t for t in periods if exp[bus, t].size() >= 1]:
            m.addConstr(exp[bus, t] == 0, name=f"power_balance_{bus}_{t}")

    time_end = dt()

    print(f"\nIt took {time_end - time_0:,.4f} sec to add the PTDF constraints", flush=True)


def single_bus(
        m: Model,
        params: Params,
        network: Network,
        thermals: Thermals,
        t_g: dict[tuple[int, int], Var],
        subhorizon_periods: list[int],
        overlapping_periods: list[int],
        overlapping_costs
) -> "Expr":
    """Add single-bus power balances for the periods in `periods`.

    :param m: Optimization model.
    :type m: Model
    :param params: Parameters of the optimization model and algorithm.
    :type params: Params
    :param network: Data of the network.
    :type network: Network
    :param thermals: Data of the thermal units.
    :type thermals: Thermals
    :param t_g: Total thermal generation.
    :type t_g: dict[tuple[int, int], Var]
    :param subhorizon_periods: Periods for which the variables and constraints are to be added.
    :type subhorizon_periods: list[int]

    :return overlapping_costs: The updated overlapping costs `overlapping_costs` with the slack
        variables of the power balance, if slack variables are used. If slacks are not used, then
        `overlapping_costs` is not changed.
    :rtype overlapping_costs: "Expr"
    """

    disjoint_subsys = _get_isolated_subsystems(network)
    _map_bus_system = {bus: None for bus in network.BUS_ID}

    for disj_subs, sub_sys in disjoint_subsys.items():
        for bus in sub_sys['nodes']:
            _map_bus_system[bus] = disj_subs

    if params.NETWORK_SLACKS in (NetworkSlacks.BUS_SLACKS, NetworkSlacks.BUS_AND_LINE_SLACKS):
        s_gen_single_bus = {(disj_subs, t): m.addVar(obj=params.DEFICIT_COST,
                                                      name=f'slack_gen_subsys_{disj_subs}_{t}')
                            for t in subhorizon_periods
                            for disj_subs, sub_sys in disjoint_subsys.items()
                            }
        s_load_single_bus = {(disj_subs, t): m.addVar(obj=params.DEFICIT_COST,
                                                       name=f'slack_load_subsys_{disj_subs}_{t}')
                             for t in subhorizon_periods
                             for disj_subs, sub_sys in disjoint_subsys.items()
                             }
        s_gen_single_bus.update({(disj_subs, t): m.addVar(
                                                      name=f'slack_gen_subsys_{disj_subs}_{t}')
                            for t in overlapping_periods
                            for disj_subs, sub_sys in disjoint_subsys.items()
                            })
        s_load_single_bus.update({(disj_subs, t): m.addVar(
                                                       name=f'slack_load_subsys_{disj_subs}_{t}')
                             for t in overlapping_periods
                             for disj_subs, sub_sys in disjoint_subsys.items()
                             })
    else:
        s_gen_single_bus = {(disj_subs, t): 0 for t in subhorizon_periods + overlapping_periods
                            for disj_subs, sub_sys in disjoint_subsys.items()
                            }
        s_load_single_bus = {(disj_subs, t): 0 for t in subhorizon_periods + overlapping_periods
                             for disj_subs, sub_sys in disjoint_subsys.items()
                             }

    exps = get_bus_injection_expr(thermals, network,
                                  t_g,
                                  {},
                                  {}, {}, {},
                                  subhorizon_periods + overlapping_periods,
                                  include_flows=False)

    for t in subhorizon_periods + overlapping_periods:
        for disj_subs, sub_sys in disjoint_subsys.items():
            m.addConstr(
                quicksum(exps[bus, t] for bus in sub_sys['nodes'])
                + s_gen_single_bus[disj_subs, t] - s_load_single_bus[disj_subs, t]
                == 0,
                name=f"single_bus_power_balance_{disj_subs}_{t}"
            )

    overlapping_costs += params.DEFICIT_COST * quicksum(
                                                        s_gen_single_bus[disj_subs, t] +
                                                        s_load_single_bus[disj_subs, t]
                                                        for t in overlapping_periods
                                                        for disj_subs in disjoint_subsys.keys()
    )

    return overlapping_costs


def get_bus_injection_expr(
        thermals: Thermals,
        network: Network,
        t_g: dict[tuple[int, int], Var],
        branch_flow: dict[tuple[int, int, int, int], Var],
        s_load_curtailment: dict[tuple[int, int], Var],
        s_gen_surplus: dict[tuple[int, int], Var],
        s_renew_curtailment: dict[tuple[int, int], Var],
        periods: list[int],
        include_flows: bool=True,
        buses: list=None
) -> dict[tuple[int, int], "Expr"]:
    """Get a linear expression of the power injection at each bus of the network for each period
    in `periods`. If `include_flows == True`, then the flows in the lines are included in the
    power injection expressions, otherwise only the power from generating units, loads and slacks
    are considered.

    :param thermals: Data of the thermal units.
    :type thermals: Thermals
    :param network: Data of the network.
    :type network: Network
    :param t_g: Total thermal generation.
    :type t_g: dict[tuple[int, int], Var]
    :param branch_flow: Flows in the transmission lines.
    :type branch_flow: dict[tuple[int, int, int, int], Var]
    :param s_load_curtailment: Load curtailments.
    :type s_load_curtailment: dict[tuple[int, int], Var]
    :param s_gen_surplus: Generation surplus.
    :type s_gen_surplus: dict[tuple[int, int], Var]
    :param s_renew_curtailment: Renewable generation curtailment.
    :type s_renew_curtailment: dict[tuple[int, int], Var]
    :param periods: Periods for which the variables and constraints are to be added.
    :type periods: list[int]
    :param include_flows: A flag to indicate whether or not the flows in the transmission lines
        are to be included in the power injection expressions, default to True.
    :type include_flows: bool

    :return exp: linear expressions of the power injections at each bus.
    :rtype exp: dict[tuple[int, int], "Expr"]
    """

    if buses is None:
        buses = network.BUS_ID

    gen_buses = network.get_gen_buses(thermals)

    thermals_per_bus = {bus: [] for bus in buses}

    thermals_per_bus.update({bus: [g for g in thermals.ID if bus in thermals.BUS[g]]
                             for bus in gen_buses})

    (s_load, s_gen, s_ren) = ({(bus, t): 0 for bus in buses for t in periods},
                                {(bus, t): 0 for bus in buses for t in periods},
                                {(bus, t): 0 for bus in buses for t in periods})

    s_load.update(s_load_curtailment)
    s_gen.update(s_gen_surplus)
    s_ren.update(s_renew_curtailment)

    exp = {(bus, t): 0 for t in periods for bus in buses}
    if include_flows:
        for bus in buses:
            for t in periods:
                exp[bus, t] = (
                        - network.NET_LOAD[network.BUS_HEADER[bus]][t]
                        - quicksum(branch_flow[network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t]
                                 for l in network.LINES_FROM_BUS[bus]
                                 )
                        + quicksum(branch_flow[network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t]
                                 for l in network.LINES_TO_BUS[bus]
                                 )
                        + quicksum(thermals.BUS_COEFF[g][bus] * t_g[g, t]
                                 for g in thermals_per_bus[bus]
                                 )
                        + s_load[bus, t] - s_gen[bus, t] - s_ren[bus, t]
                )
    else:
        for bus in buses:
            for t in periods:
                exp[bus, t] = (
                        - network.NET_LOAD[network.BUS_HEADER[bus]][t]
                        + quicksum(thermals.BUS_COEFF[g][bus] * t_g[g, t]
                                 for g in thermals_per_bus[bus]
                                 )
                        + s_load[bus, t] - s_gen[bus, t] - s_ren[bus, t]
                )
    return exp


def _line_capacities_with_slacks(
        m: Model,
        network: Network,
        s_line_violation: dict[tuple[int, int], Var],
        branch_flow: dict[tuple[int, int, int, int], Var],
        periods: list[int]
):
    """Add constraints on the transmission line flows with slack variables"""
    for l in [l for l in network.LINE_ID if network.ACTIVE_BOUNDS[l]]:
        for t in [t for t in periods if network.ACTIVE_UB_PER_PERIOD[l][t]]:
            m.addConstr(
                branch_flow[network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t]
                - s_line_violation[network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t]
                <= network.LINE_FLOW_UB[l][t],
                name=f"flow_UB_{network.LINE_F_T[l][0]}" +
                     f"_{network.LINE_F_T[l][1]}_{l}_{t}"
            )

        for t in [t for t in periods if network.ACTIVE_LB_PER_PERIOD[l][t]]:
            m.addConstr(branch_flow[network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t]
                         + s_line_violation[network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t]
                         >= network.LINE_FLOW_LB[l][t],
                         name=f"flow_LB_{network.LINE_F_T[l][0]}" +
                              f"_{network.LINE_F_T[l][1]}_{l}_{t}"
                         )


def B_theta_network_model(
        m: Model,
        params: Params,
        thermals: Thermals,
        network: Network,
        t_g: dict[tuple[int, int], Var],
        s_load_curtailment: dict[tuple[int, int], Var],
        s_gen_surplus: dict[tuple[int, int], Var],
        s_renew_curtailment: dict[tuple[int, int], Var],
        s_line_violation: dict[tuple[int, int], Var],
        branch_flow: dict[tuple[int, int, int, int], Var],
        periods: list[int]
) -> dict[tuple[int, int], Var]:
    """B-theta formulation of the DC network model.
    This function adds the bus-wise power balance constraints, voltage angle variables, and
    the linear constraints that enforce the relation between flows and angles. Moreover,
    if line slacks are enabled through either `NetworkSlack.LINE_SLACKS` or
    `NetworkSlack.BUS_AND_LINE_SLACKS` then, instead of enforcing the branch_flow capacities through
    the bounds of the branch_flow variables, these capacities are included as linear inequalities together
    with heavily penalized slacks associated with these inequalities.

    :param m: Optimization model.
    :type m: Model
    :param params: Parameters of the optimization model and algorithm.
    :type params: Params
    :param thermals: Data of the thermal units.
    :type thermals: Thermals
    :param network: Data of the network.
    :type network: Network
    :param t_g: Total thermal generation.
    :type t_g: dict[tuple[int, int], Var]
    :return s_load_curtailment: Load curtailments.
    :rtype s_load_curtailment: dict[tuple[int, int], Var]
    :return s_gen_surplus: Generation surplus.
    :rtype s_gen_surplus: dict[tuple[int, int], Var]
    :return s_renew_curtailment: Renewable generation curtailment.
    :rtype s_renew_curtailment: dict[tuple[int, int], Var]
    :return branch_flow: Flows in the transmission lines.
    :rtype branch_flow: dict[tuple[int, int, int, int], Var]
    :param periods: Periods for which the variables and constraints are to be added.
    :type periods: list[int]

    :return theta: Voltage angle.
    :rtype theta: dict[tuple[int, int], Var]
    """

    exp = get_bus_injection_expr(thermals, network,
                                 t_g,
                                 branch_flow,
                                 s_load_curtailment,
                                 s_gen_surplus,
                                 s_renew_curtailment,
                                 periods,
                                 include_flows=True)

    for bus in network.BUS_ID:
        for t in periods:
            m.addConstr(exp[bus, t] == 0, name=f"bus_{bus}_{t}")

    theta = {
        (bus, t):
            m.addVar(lb=0, name=f'theta_{bus}_{t}')
        for t in periods
        for bus in network.BUS_ID
    }

    # Set the voltage angle reference
    for bus in network.REF_BUS_ID:
        for t in periods:
            theta[bus, t].lb = network.THETA_BOUND
            theta[bus, t].ub = network.THETA_BOUND

    for l in network.LINE_ID:
        ADMT = 1 / network.LINE_X[l]
        if abs(ADMT) <= 1e-1:
            for t in periods:
                m.addConstr(1e2 * branch_flow[network.LINE_F_T[l][0],
                network.LINE_F_T[l][1], l, t]
                             == 1e2 * ADMT *
                             (theta[network.LINE_F_T[l][0], t] -
                              theta[network.LINE_F_T[l][1], t]),
                             name=f"ACflow_{network.LINE_F_T[l][0]}" +
                                  f"_{network.LINE_F_T[l][1]}_{l}_{t}")
        elif abs(ADMT) >= 1e3:
            for t in periods:
                m.addConstr(1e-2 * branch_flow[network.LINE_F_T[l][0],
                network.LINE_F_T[l][1], l, t]
                             == 1e-2 * ADMT *
                             (theta[network.LINE_F_T[l][0], t] -
                              theta[network.LINE_F_T[l][1], t]),
                             name=f"ACflow_{network.LINE_F_T[l][0]}" +
                                  f"_{network.LINE_F_T[l][1]}_{l}_{t}")
        else:
            for t in periods:
                m.addConstr(branch_flow[network.LINE_F_T[l][0],
                network.LINE_F_T[l][1], l, t]
                             == ADMT *
                             (theta[network.LINE_F_T[l][0], t] -
                              theta[network.LINE_F_T[l][1], t]),
                             name=f"ACflow_{network.LINE_F_T[l][0]}" +
                                  f"_{network.LINE_F_T[l][1]}_{l}_{t}")

    if params.NETWORK_SLACKS in (NetworkSlacks.LINE_SLACKS, NetworkSlacks.BUS_AND_LINE_SLACKS):
        _line_capacities_with_slacks(m, network, s_line_violation, branch_flow, periods)

    return theta


def add_network(
        m: Model,
        params: Params,
        thermals: Thermals,
        network: Network,
        t_g: dict[tuple[int, int], Var],
        flow_periods: list[int],
        single_bus_periods: list[int]
) -> dict:
    """
    Add variables and constrains associated with the network to model `m`.
    Which variables and constraints will be added depend on the model chosen in
    `params.NetworkModel` and periods provided in either `flow_periods` or `single_bus_periods`.
    Only one of these lists must be nonempty, and the periods it contains must be contiguous.
    If the model chosen in `params.NetworkModel` is either `NetworkModel.B_THETA` or
    `NetworkModel.FLUXES` and `flow_periods` is not empty, then transmission line flows' variables
    will be added to `m`, along with bus-wise power balances, and, for `NetworkModel.B_THETA`,
    line branch_flow expressions tying flows to voltage angles. On the other hand, if
    `single_bus_periods` is not empty, then global power balance constraints will be added, but
    no line branch_flow variables.

    :param m: Optimization model.
    :type m: Model
    :param params: Parameters of the optimization model and algorithm.
    :type params: Params
    :param thermals: Data of the thermal units.
    :type thermals: Thermals
    :param network: Data of the network.
    :type network: Network
    :param t_g: Total thermal generation.
    :type t_g: dict[tuple[int, int], Var]
    :param flow_periods: A contiguous list of periods for which line flows and associated
        constraints will be added, as long as `params.NetworkModel` includes such representation.
    :type flow_periods: list[int]
    :param single_bus_periods: For the contiguous periods in this list, global power balance
        constraints for the system will be added.
    :type single_bus_periods: list[int]

    :return theta: Voltage angle.
    :rtype theta: dict[tuple[int, int], Var]
    :return branch_flow: Flows in the branches in p.u..
    :rtype branch_flow: dict[tuple[int, int, int, int], Var]
    :return s_load_curtailment: Load curtailments.
    :rtype s_load_curtailment: dict[tuple[int, int], Var]
    :return s_gen_surplus: Generation surplus.
    :rtype s_gen_surplus: dict[tuple[int, int], Var]
    :return s_renew_curtailment: Renewable generation curtailment.
    :rtype s_renew_curtailment: dict[tuple[int, int], Var]
    """

    (theta, branch_flow,
     s_load_curtailment, s_gen_surplus, s_renew_curtailment,
     s_line_violation) = ({}, {}, {}, {}, {}, {})

    # Flows transmission lines
    if params.NETWORK_MODEL in (NetworkModel.B_THETA, NetworkModel.FLUXES):
        if params.NETWORK_SLACKS in (NetworkSlacks.LINE_SLACKS, NetworkSlacks.BUS_AND_LINE_SLACKS):
            branch_flow = {
                (network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t):
                    m.addVar(
                        lb=-999.99,
                        ub=999.99,
                        name=f"flow_{network.LINE_F_T[l][0]}_{network.LINE_F_T[l][1]}_{l}_{t}"
                    )
                for t in flow_periods
                for l in network.LINE_F_T
            }
        else:
            branch_flow = {
                (network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t):
                    m.addVar(
                        lb=network.LINE_FLOW_LB[l][t],
                        ub=network.LINE_FLOW_UB[l][t],
                        name=f"flow_{network.LINE_F_T[l][0]}_{network.LINE_F_T[l][1]}_{l}_{t}"
                    )
                for t in flow_periods
                for l in network.LINE_F_T
            }

    if len(flow_periods) > 0:

        if params.NETWORK_SLACKS in (NetworkSlacks.BUS_SLACKS, NetworkSlacks.BUS_AND_LINE_SLACKS):
            renewable_gen_buses = list(network.get_renewable_gen_buses())
            renewable_gen_buses.sort()
            s_renew_curtailment.update(
                {(bus, t): m.addVar(obj=params.DEFICIT_COST, name=f'slack_ren_curtail_{bus}_{t}')
                 for t in flow_periods
                 for bus in renewable_gen_buses
                 }
            )

            load_buses = list(network.get_load_buses())
            load_buses.sort()
            s_load_curtailment.update(
                {(bus, t): m.addVar(obj=params.DEFICIT_COST, name=f'slack_load_curtail_{bus}_{t}')
                 for t in flow_periods
                 for bus in load_buses
                 }
            )

            slack_gen_buses = list(network.get_gen_buses(thermals) - set(renewable_gen_buses))
            slack_gen_buses.sort()
            s_gen_surplus.update(
                {(bus, t): m.addVar(obj=params.DEFICIT_COST, name=f'slack_gen_surplus_{bus}_{t}')
                 for t in flow_periods
                 for bus in slack_gen_buses
                 }
            )

        if params.NETWORK_SLACKS in (NetworkSlacks.LINE_SLACKS, NetworkSlacks.BUS_AND_LINE_SLACKS):
            s_line_violation.update(
                {
                    (network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t):
                        m.addVar(lb=0, obj=params.DEFICIT_COST,
                                  name=f"slack_line_{network.LINE_F_T[l][0]}_" +
                                       f"{network.LINE_F_T[l][1]}_{l}_{t}"
                                  )
                    for t in flow_periods
                    for l in network.LINE_F_T
                    if network.ACTIVE_UB_PER_PERIOD[l][t] or network.ACTIVE_LB_PER_PERIOD[l][t]
                }
            )
        else:
            s_line_violation.update(
                {
                    (network.LINE_F_T[l][0], network.LINE_F_T[l][1], l, t): 0
                    for t in flow_periods
                    for l in network.LINE_F_T
                    if network.ACTIVE_UB_PER_PERIOD[l][t] or network.ACTIVE_LB_PER_PERIOD[l][t]
                }
            )
        if params.NETWORK_MODEL == NetworkModel.PTDF:
            PTDF_formulation(m, params, thermals, network,
                             t_g,
                             s_load_curtailment, s_gen_surplus, s_renew_curtailment,
                             s_line_violation,
                             branch_flow,
                             flow_periods)

        elif params.NETWORK_MODEL == NetworkModel.FLUXES:
            exp = get_bus_injection_expr(thermals, network,
                                         t_g,
                                         branch_flow,
                                         s_load_curtailment,
                                         s_gen_surplus,
                                         s_renew_curtailment,
                                         flow_periods,
                                         include_flows=True)

            for bus in network.BUS_ID:
                for t in flow_periods:
                    m.addConstr(exp[bus, t] == 0, name=f"bus_{bus}_{t}")

            if params.NETWORK_SLACKS in (NetworkSlacks.LINE_SLACKS,
                                         NetworkSlacks.BUS_AND_LINE_SLACKS):
                _line_capacities_with_slacks(m, network,
                                             s_line_violation,
                                             branch_flow,
                                             flow_periods)

        elif params.NETWORK_MODEL == NetworkModel.B_THETA:
            theta = B_theta_network_model(m, params, thermals, network,
                                          t_g,
                                          s_load_curtailment,
                                          s_gen_surplus,
                                          s_renew_curtailment,
                                          s_line_violation,
                                          branch_flow, flow_periods)

    if len(single_bus_periods) > 0 or params.NETWORK_MODEL == NetworkModel.SINGLE_BUS:
        single_bus(m, params, network, thermals, t_g, single_bus_periods)

    return (theta, branch_flow, s_load_curtailment, s_gen_surplus, s_renew_curtailment)
