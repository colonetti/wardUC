# -*- coding: utf-8 -*-
import locale

from tabulate import tabulate
import numpy as np

from model.add_network import get_bus_injection_expr

from constants import NetworkModel, NetworkSlacks

def check_flows_full_network(params,
                             thermals,
                             network,
                             t_g,
                             s_load_curtailment,
                             s_gen_surplus,
                             s_renew_curtailment
) -> None:
    """Take the generations from the reduced network and check the flows that result from them in
    the full, original network
    """

    print("\n\nFlows in the full, original network\n\n", flush=True)

    t_g_x = {k: v.x for k, v in t_g.items()}
    s_load_curtailment_x = {k: v.x for k, v in s_load_curtailment.items()}
    s_gen_surplus_x = {k: v.x for k, v in s_gen_surplus.items()}
    s_renew_curtailment_x = {k: v.x for k, v in s_renew_curtailment.items()}

    write_branch_flows(params,
                        network, thermals,
                        {},
                        t_g_x,
                        s_load_curtailment_x,
                        s_gen_surplus_x,
                        s_renew_curtailment_x,
                        ptdf_threshold=params.PTDF_COEFF_TOL,
                        write_csv=True
    )


def write_solution(params, thermals, network,
                   m,
                   st_up_t_g, st_dw_t_g, disp_stat_t_g,
                   t_g, t_g_disp,
                   s_reserve,
                   theta,
                   branch_flow,
                   s_load_curtailment, s_gen_surplus, s_renew_curtailment,
                   suffix: str=""
):

    locale.setlocale(locale.LC_ALL, '')

    print('\n\nThe total cost is ' +locale.currency(m.ObjVal/params.SCAL_OBJ_F,
                                                     grouping=True))

    print('\n\n', flush=True)

    f = open(params.OUT_DIR + '/angles and flows - '+
                    params.PS + ' - case ' + str(params.CASE) +
                    suffix + '.csv', 'w',
                    encoding = 'utf-8'
    )
    f.write('var;indices;period;x;max;min\n')
    angle_bounds = (";" + str(network.THETA_BOUND) + ";" +
                    str(-network.THETA_BOUND)
    )
    for k, v in theta.items():
        f.write("voltage angles" + ';' + str(k[0:len(k)-1]) + ';' +
                str(k[-1]) + ';' + str(v.x) + angle_bounds + '\n'
        )
    for k, v in branch_flow.items():
        f.write("flow" + ';' + str(k[0:len(k)-1]) + ';' + str(k[-1]) + ';' +
                str(v.x) +';' + str(network.LINE_FLOW_UB[k[2]][k[-1]])+';'+
                str(network.LINE_FLOW_LB[k[2]][k[-1]]) + '\n'
        )
    f.close()
    del f

    if params.NETWORK_SLACKS in (NetworkSlacks.BUS_SLACKS,
                                 NetworkSlacks.BUS_AND_LINE_SLACKS):
        f = open(params.OUT_DIR + '/network bus slacks - '+
                 params.PS + ' - case ' + str(params.CASE) +
                 suffix + '.csv', 'w',
                 encoding = 'utf-8')
        f.write('var;indices;period;x\n')
        for k, v in s_load_curtailment.items():
            f.write("s_load_curtailment" + ';' + str(k[0:len(k)-1]) + ';' +
                    str(k[-1]) + ';' + str(v.x) + '\n')
        for k, v in s_gen_surplus.items():
            f.write("s_gen_surplus" + ';' + str(k[0:len(k)-1]) + ';' +
                    str(k[-1]) + ';' + str(v.x) + '\n')
        for k, v in s_renew_curtailment.items():
            f.write("s_renew_curtailment" + ';' + str(k[0:len(k)-1]) + ';' +
                    str(k[-1]) + ';' + str(v.x) + '\n')
        for k, v in s_reserve.items():
            f.write("s_reserve" + ';' + str(k[0:len(k)-1]) + ';' +
                    str(k[-1]) + ';' + str(v.x) + '\n')
        f.close()
        del f

    t_g_x = {k: v.x for k, v in t_g.items()}
    disp_stat_t_g_x = {k: v.x for k, v in t_g_disp.items()}
    s_load_curtailment_x = {k: v.x for k, v in s_load_curtailment.items()}
    s_gen_surplus_x = {k: v.x for k, v in s_gen_surplus.items()}
    s_renew_curtailment_x = {k: v.x for k, v in s_renew_curtailment.items()}

    write_generation(params, thermals, network,
                     t_g_x,
                     disp_stat_t_g_x,
                     s_load_curtailment_x,
                     s_gen_surplus_x,
                     s_renew_curtailment_x,
                     {k: v.x for k, v in s_reserve.items()},
                     suffix=suffix
    )

    write_thermal_operation(params, thermals,
                            {k: v.x if not isinstance(v, int | float)
                                    else v for k, v in st_up_t_g.items()},
                            {k: v.x if not isinstance(v, int | float)
                                    else v for k, v in st_dw_t_g.items()},
                            {k: v.x if not isinstance(v, int | float)
                                    else v for k, v in disp_stat_t_g.items()},
                            disp_stat_t_g_x,
                            t_g_x,
                            suffix=suffix
    )

    if params.NETWORK_MODEL != NetworkModel.SINGLE_BUS:
        write_branch_flows(params,
                           network, thermals,
                           {k: v.x for k, v in branch_flow.items()},
                           t_g_x,
                           s_load_curtailment_x,
                           s_gen_surplus_x,
                           s_renew_curtailment_x,
                           ptdf_threshold=params.PTDF_COEFF_TOL,
                           write_csv=True,
                           suffix=suffix
        )


def write_generation(params, thermals, network,
                     t_g, disp_stat,
                     s_load_curtailment, s_gen_surplus, s_renewable, s_reserve,
                     suffix: str=""
):
    """Write total generation per period of hydro and thermal plants to
        a csv file 'generation and load',
        along with net load, load curtailment, and generation surpluses
    """

    f = open(params.OUT_DIR + '/generation and load - ' +
                params.PS + ' - case ' + str(params.CASE) +
                suffix + '.csv', 'w',
                encoding='ISO-8859-1')

    for g, unit_name in thermals.UNIT_NAME.items():
        f.write(unit_name + ';')
        for t in range(params.T):
            f.write(str(round(t_g[g, t]*params.POWER_BASE, 4)) + ';')
        f.write('\n')

    f.write('Load;')
    for t in range(params.T):
        f.write(str(round(np.sum(network.NET_LOAD[:, t])*params.POWER_BASE, 4))
                + ';'
        )

    f.write('\n')

    f.write('Load Shedding;')
    for t in range(params.T):
        f.write(str(round(sum(s_load_curtailment[k]
                              for k in s_load_curtailment.keys() if k[-1] == t)
                              *params.POWER_BASE, 4))
                + ';')

    f.write('\n')
    f.write('Generation surplus;')
    for t in range(params.T):
        f.write(str(round(sum(s_gen_surplus[k] for k in s_gen_surplus.keys()
                              if k[-1] == t)*params.POWER_BASE, 4))
                + ';')
    f.write('\n')

    f.write('Renewable generation curtailment;')
    for t in range(params.T):
        f.write(str(round(sum(s_renewable[k] for k in s_renewable.keys()
                              if k[-1] == t)*params.POWER_BASE, 4)) + ';')
    f.write('\n')
    for res in network.RESERVES.keys():
        f.write(f'Reserves_{res}_requirement;')
        for t in range(params.T):
            f.write(str(round(network.RESERVES[res][t]*params.POWER_BASE, 4)) +
                    ";")
        f.write('\n')
        f.write(f'Reserves_{res}_actual_reserve;')
        _r = 0
        for t in range(params.T):
            for g in [g for g in thermals.ID
                      if thermals.RESERVE_ELEGIBILITY[g] == res
            ]:
                _r += ((disp_stat[g, t]*thermals.MAX_P[g] - t_g[g, t]) *
                       params.POWER_BASE
                )
            f.write(str(round(_r, 4)) + ";")
        f.write('\n')
        f.write(f'Reserves_{res}_slack;')
        _r = 0
        for t in range(params.T):
            if network.RESERVES[res][t] > 0:
                f.write(str(round(s_reserve[res, t], 4)) + ";")
            else:
                f.write("0;")
        f.write('\n')
    f.close()


def write_thermal_operation(params, thermals, st_up_t_g, st_dw_t_g, disp_stat,
                            t_g_disp, t_g,
                            suffix: str=""
):
    """Write the decisions for the thermal units"""

    f = open(params.OUT_DIR + '/thermal decisions - ' +
                params.PS + ' - case ' + str(params.CASE) +
                suffix + '.csv', 'w',
                encoding = 'ISO-8859-1'
    )
    f.write('ID;Name;Period;')
    f.write('Start-up decision;Shut-down decision;Dispatch phase;')
    f.write('Generation in dispacth (MW);Total generation (MW);Reserve (MW);')
    f.write('Minimum generation (MW);Maximum generation (MW);')
    f.write(f"Ramp down limit (MW/{params.DISCRETIZATION} h);")
    f.write(f"Ramp up limit (MW/{params.DISCRETIZATION} h);\n")
    for g in thermals.ID:
        for t in range(params.T):
            f.write(str(g) + ';')
            f.write(thermals.UNIT_NAME[g] + ';')
            f.write(str(t) + ';')
            f.write(str(st_up_t_g[g, t]) + ';')
            f.write(str(st_dw_t_g[g, t]) + ';')
            f.write(str(disp_stat[g, t]) + ';')
            f.write(str(
                    round((t_g_disp[g, t]+thermals.MIN_P[g]*disp_stat[g, t])*
                              params.POWER_BASE, 4)) + ';'
            )
            f.write(str(round(t_g[g, t]*params.POWER_BASE, 4))+';')
            f.write(str(round((
                        (thermals.MAX_P[g] - thermals.MIN_P[g])*disp_stat[g, t]
                                - t_g_disp[g,t])*params.POWER_BASE, 4))+';'
            )
            f.write(str(round(thermals.MIN_P[g]*params.POWER_BASE, 4))+';')
            f.write(str(round(thermals.MAX_P[g]*params.POWER_BASE, 4))+';')
            f.write(str(round(thermals.RAMP_DOWN[g]*params.POWER_BASE, 4))+';')
            f.write(str(round(thermals.RAMP_UP[g]*params.POWER_BASE, 4))+';')
            f.write('\n')
    f.close()


def write_branch_flows(params,
                        network,
                        thermals,
                        branch_flow,
                        t_g,
                        s_load_curtailment,
                        s_gen_surplus,
                        s_renew_curtailment,
                        ptdf_threshold=0,
                        write_csv=True,
                        suffix: str=""
) -> None:
    """
        write branch flows to a csv file
    """

    count_active_constrs = 0

    active_lines = set()

    table_header = ['Line ID', 'End buses', 'Period',
                    'UB (MW)', 'LB (MW)', 'Flow (MW)',
                    'Active UB?','Active LB?'
    ]

    table_to_print, violated_lines = [], []

    if write_csv:
        f = open(params.OUT_DIR + '/branch flows - '+
                        params.PS + ' - case ' + params.CASE +
                        suffix + '.csv', 'w',
                        encoding='utf-8'
        )
        f.write('sep=;\n')
        f.write('var;x (pu);max (pu);min (pu);violation (pu)\n')

    if len(branch_flow.keys()) > 0:
        for k, flow in branch_flow.items():
            l, t = k[2], k[-1]

            if ((flow <= (network.LINE_FLOW_LB[l][t] + 1e-3))
                    or (flow >= (network.LINE_FLOW_UB[l][t] - 1e-3))):
                active_lines.add(l)
                count_active_constrs += 1
                table_to_print.append([l, network.LINE_F_T[l], t,
                                network.LINE_FLOW_UB[l][t]*params.POWER_BASE,
                                network.LINE_FLOW_LB[l][t]*params.POWER_BASE,
                                flow*params.POWER_BASE,
                                network.ACTIVE_UB_PER_PERIOD[l][t],
                                network.ACTIVE_LB_PER_PERIOD[l][t]]
                )
                if ((flow < (network.LINE_FLOW_LB[l][t] - 1/params.POWER_BASE))
                    or
                    (flow > (network.LINE_FLOW_UB[l][t] + 1/params.POWER_BASE))
                ):
                    violated_lines.append([l, network.LINE_F_T[l], t,
                                network.LINE_FLOW_UB[l][t]*params.POWER_BASE,
                                network.LINE_FLOW_LB[l][t]*params.POWER_BASE,
                                flow*params.POWER_BASE,
                                network.ACTIVE_UB_PER_PERIOD[l][t],
                                network.ACTIVE_LB_PER_PERIOD[l][t]])

            if write_csv:
                f.write(f"flow_{k[0]}_{k[1]}_{k[2]}_{k[3]};" + str(flow) + ';'
                        + str(network.LINE_FLOW_UB[l][t]) + ';' +
                        str(network.LINE_FLOW_LB[l][t]) + ';' +
                        str(max(flow - network.LINE_FLOW_UB[l][t],
                                network.LINE_FLOW_LB[l][t] - flow, 0)) +
                        '\n'
                )

    else:

        bus_injections = get_bus_injection_expr(thermals, network,
                                                t_g,
                                                {},
                                                s_load_curtailment,
                                                s_gen_surplus,
                                                s_renew_curtailment,
                                                periods = range(params.T),
                                                include_flows = False
        )

        buses_with_injections_idxs = np.array(
                            [b for b, bus in enumerate(network.BUS_ID)
                                if [abs(bus_injections[bus, t].getValue()) != 0
                                                    for t in range(params.T)]],
                                                        dtype = 'int64'
        )

        sub_PTDF_act_lines = network.PTDF[:]
        sub_PTDF_act_lines[np.where(abs(sub_PTDF_act_lines)<ptdf_threshold)] =0

        for l in network.LINE_ID:

            (f_bus, t_bus) = (network.LINE_F_T[l][0], network.LINE_F_T[l][1])

            l_idx = network.LINE_ID.index(l)
            non_zeros = np.intersect1d(
                            np.where(abs(sub_PTDF_act_lines[l_idx,:]) > 0)[0],
                                                    buses_with_injections_idxs
            )
            buses_of_interest = [network.BUS_ID[b] for b in non_zeros]

            flows = np.inner(
                            np.array([[bus_injections[bus, t].getValue()
                                       for bus in buses_of_interest]
                                       for t in range(params.T)]),
                                       sub_PTDF_act_lines[l_idx, non_zeros]
            )
            for t in range(params.T):
                flow = flows[t]
                if ((flow <= (network.LINE_FLOW_LB[l][t] + 1e-3))
                    or (flow >= (network.LINE_FLOW_UB[l][t] - 1e-3))
                ):
                    active_lines.add(l)
                    count_active_constrs += 1
                    table_to_print.append([l, (f_bus, t_bus), t,
                                network.LINE_FLOW_UB[l][t]*params.POWER_BASE,
                                network.LINE_FLOW_LB[l][t]*params.POWER_BASE,
                                flow*params.POWER_BASE,
                                network.ACTIVE_UB_PER_PERIOD[l][t],
                                network.ACTIVE_LB_PER_PERIOD[l][t]]
                    )

                    if (
                        (flow <
                         (network.LINE_FLOW_LB[l][t] - 1/params.POWER_BASE))
                        or (flow >
                            (network.LINE_FLOW_UB[l][t] + 1/params.POWER_BASE))
                    ):
                        violated_lines.append([l, (f_bus, t_bus), t,
                                network.LINE_FLOW_UB[l][t]*params.POWER_BASE,
                                network.LINE_FLOW_LB[l][t]*params.POWER_BASE,
                                flow*params.POWER_BASE,
                                network.ACTIVE_UB_PER_PERIOD[l][t],
                                network.ACTIVE_LB_PER_PERIOD[l][t]]
                        )
                if write_csv:
                    f.write(f"flow_{f_bus}_{t_bus}_{l}_{t};{flow};"
                        + str(network.LINE_FLOW_UB[l][t])+';'+
                        str(network.LINE_FLOW_LB[l][t]) + ';' +
                        str(max(flow - network.LINE_FLOW_UB[l][t],
                                network.LINE_FLOW_LB[l][t] - flow, 0)) +
                        '\n'
                    )
    f.close()
    del f

    print("\n\n")
    print(tabulate(table_to_print, headers=table_header))
    print(f"{count_active_constrs} transmission line constraints are active",
          flush=True)
    print(f"{len(active_lines)} lines active\n\n\n", flush=True)

    if len(violated_lines) > 0:
        print(tabulate(violated_lines, headers=table_header))
        print("The list of bounds for the lines above have been violated")
    else:
        print("\n\nNo branch limits were violated\n\n")
