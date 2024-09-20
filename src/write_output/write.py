# -*- coding: utf-8 -*-
import locale

from tabulate import tabulate
import numpy as np

from model.add_network import get_bus_injection_expr

from constants import NetworkModel, NetworkSlacks, Model

def write_full_solution(params, thermals, network,
                            ub,
                                present_costs, future_costs, full_solution):

    locale.setlocale(locale.LC_ALL, '')

    print('\n\nThe total present cost is ' +
                        locale.currency(sum(present_costs)/params.SCAL_OBJ_F, grouping=True))

    print('The future cost is ' +
                        locale.currency(sum(future_costs)/params.SCAL_OBJ_F, grouping=True))

    print('The total cost is ' +
        locale.currency((sum(present_costs)+sum(future_costs))/params.SCAL_OBJ_F,grouping=True),
                                                                                flush=True)

    print('\nThe upper bound given by pddip is ' +
                locale.currency(ub/params.SCAL_OBJ_F, grouping = True), flush=True)

    print('\nA difference of ' +
            locale.currency((ub - (sum(present_costs)+sum(future_costs)))/params.SCAL_OBJ_F,
            grouping = True) + f' ({100*(ub - (sum(present_costs)+sum(future_costs)))/ub:.4f}%)'
            + ' between the UB computed with pDDiP and the total cost obtained after ' +
            'reconstructing a full solution using the incumbent vector', flush=True
    )

    print('\n\n', flush=True)

    f = open(params.OUT_DIR + '/final results - '+
                params.PS + ' - case ' + str(params.CASE) + '.csv', 'w', encoding = 'utf-8'
    )
    f.write('Present cost ($);' + str(sum(present_costs)/params.SCAL_OBJ_F) + '\n')
    f.write('Future cost ($);' + str(sum(future_costs)/params.SCAL_OBJ_F) + '\n')
    f.write('Total cost ($);' +str((sum(present_costs)+sum(future_costs))/params.SCAL_OBJ_F) +'\n')
    f.write('Upper bound in the DDiP ($);' + str(ub/params.SCAL_OBJ_F)+'\n')
    f.write('Difference ($);' +
                        str((ub - (sum(present_costs)+sum(future_costs)))/params.SCAL_OBJ_F)+'\n'
    )
    f.write('Difference (%);' + str(100*(ub - (sum(present_costs)+sum(future_costs)))/ub))
    f.close()
    del f

    f = open(params.OUT_DIR + '/angles and flows - '+
                    params.PS + ' - case ' + str(params.CASE) + '.csv', 'w', encoding = 'utf-8')
    f.write('var;indices;period;x;max;min\n')
    angle_bounds = ";" + str(network.THETA_BOUND) + ";" + str(-network.THETA_BOUND)
    for key, value in full_solution['theta'].items():
        f.write("voltage angles" + ';' + str(key[0:len(key)-1]) + ';' + str(key[-1]) + ';' +
                                str(value) + angle_bounds + '\n')
    for key, value in full_solution['flow'].items():
        f.write("flow" + ';' + str(key[0:len(key)-1]) + ';' + str(key[-1]) + ';' + str(value) + ';'
                            + str(network.LINE_FLOW_UB[key[2]][key[-1]])+';'+
                                str(network.LINE_FLOW_LB[key[2]][key[-1]]) + '\n')
    for key, value in full_solution['link_flow'].items():
        f.write("DC flow" + ';' + str(key[0:len(key)-1]) + ';' + str(key[-1]) + ';' + str(value)
                + ';' + str(network.LINK_MAX_P[key[2]]) + ';' +
                str(-1*network.LINK_MAX_P[key[2]]) + '\n')
    f.close()
    del f

    if params.NETWORK_SLACKS in (NetworkSlacks.BUS_SLACKS, NetworkSlacks.BUS_AND_LINE_SLACKS):
        f = open(params.OUT_DIR + '/network bus slacks - '+
                    params.PS + ' - case ' + str(params.CASE) + '.csv', 'w', encoding = 'utf-8')
        f.write('var;indices;period;x\n')
        for key, value in full_solution['s_load_curtailment'].items():
            f.write("s_load_curtailment" + ';' + str(key[0:len(key)-1]) + ';' + str(key[-1]) + ';' +
                                    str(value) + '\n')
        for key, value in full_solution['s_gen_surplus'].items():
            f.write("s_gen_surplus" + ';' + str(key[0:len(key)-1]) + ';' + str(key[-1]) + ';'
                    + str(value) + '\n')
        for key, value in full_solution['s_renew_curtailment'].items():
            f.write("s_renew_curtailment" + ';' + str(key[0:len(key)-1]) + ';' + str(key[-1]) + ';'
                    + str(value) + '\n')
        for key, value in full_solution['s_reserve'].items():
            f.write("s_reserve" + ';' + str(key[0:len(key)-1]) + ';' + str(key[-1]) + ';' +
                    str(value) + '\n')

        f.close()
        del f


    write_generation(params, thermals, network,
                    full_solution['h_g'],
                    full_solution['t_g'],
                    full_solution['disp_stat_tg'],
                    full_solution['s_load_curtailment'],
                    full_solution['s_gen_surplus'],
                    full_solution['s_renew_curtailment'],
                    full_solution['s_reserve']
    )

    write_thermal_operation(params, thermals,
                            full_solution['st_up_tg'],
                            full_solution['st_dw_tg'],
                            full_solution['disp_stat_tg'],
                            full_solution['t_g_disp'],
                            full_solution['t_g']
    )

    if params.NETWORK_MODEL != NetworkModel.SINGLE_BUS:
        write_branch_flows(params,
                        network, thermals,
                            full_solution['flow'],
                            full_solution['link_flow'],
                            full_solution['t_g'],
                            full_solution['h_g'],
                            full_solution['s_load_curtailment'],
                            full_solution['s_gen_surplus'],
                            full_solution['s_renew_curtailment']
        )

def write_event_tracker(params, event_tracker:list, W_RANK:int):
    """
        Write metrics for the general coordinator
    """

    name = 'generalCoordinator - ' if W_RANK == 0 else 'worker W_RANK ' + str(W_RANK) + ' - '

    f = open(params.OUT_DIR + name +
            params.PS + ' - case ' + str(params.CASE) + '.csv', 'w', encoding = 'ISO-8859-1')
    f.write('Event;Code line;Upper bound ($);Lower bound ($);')
    f.write('bRank origin;bRank destination;fRank origin;fRank destination;')
    f.write('Iteration of origin;Subhorizon of origin;')
    f.write('Iteration of destination;Subhorizon of destination;')
    f.write('Elapsed time (sec)')
    f.write('\n')
    if len(event_tracker) > 0:
        for row in event_tracker:
            for col in row[0:2]:
                f.write(str(col) + ';')

            if row[2] != ' ':
                f.write(str(row[2]/params.SCAL_OBJ_F) + ';')
            else:
                f.write(str(row[2]) + ';')

            if row[3] != ' ':
                f.write(str(row[3]/params.SCAL_OBJ_F) + ';')
            else:
                f.write(str(row[3]) + ';')

            for col in row[4:]:
                f.write(str(col) + ';')
            f.write('\n')
    f.close()
    del f

def write_generation(params, thermals, network,
                        hgEachBus, tg, disp_stat,
                            s_load_curtailment, s_gen_surplus, s_renewable, s_reserve):
    """Write total generation per period of hydro and thermal plants to
        a csv file 'generation and load',
        along with net load, load curtailment, and generation surpluses
    """

    f = open(params.OUT_DIR + 'generation and load - ' +
                params.PS + ' - case ' + str(params.CASE) + '.csv', 'w', encoding = 'ISO-8859-1')
    for g in thermals.ID:
        f.write(thermals.UNIT_NAME[g] + ';')
        for t in range(params.T):
            f.write(str(round(tg[g, t]*params.POWER_BASE, 4)) + ';')
        f.write('\n')

    f.write('Load;')
    for t in range(params.T):
        f.write(str(round(np.sum(network.NET_LOAD[:, t])*params.POWER_BASE, 4)) + ';')

    f.write('\n')

    f.write('Load Shedding;')
    for t in range(params.T):
        f.write(str(round(sum(s_load_curtailment[k] for k in s_load_curtailment.keys() if k[-1] == t)*params.POWER_BASE, 4))
                + ';')

    f.write('\n')
    f.write('Generation surplus;')
    for t in range(params.T):
        f.write(str(round(sum(s_gen_surplus[k] for k in s_gen_surplus.keys() if k[-1] == t)*params.POWER_BASE, 4))
                + ';')
    f.write('\n')

    f.write('Renewable generation curtailment;')
    for t in range(params.T):
        f.write(str(round(sum(s_renewable[k] for k in s_renewable.keys() if k[-1] == t)
                                                                    *params.POWER_BASE, 4)) + ';')
    f.write('\n')
    for res in network.RESERVES.keys():
        f.write(f'Reserves_{res}_requirement;')
        for t in range(params.T):
            f.write(str(round(network.RESERVES[res][t]*params.POWER_BASE, 4)) + ";")
        f.write('\n')
        f.write(f'Reserves_{res}_actual_reserve;')
        _r = 0
        for t in range(params.T):
            for g in [g for g in thermals.ID if thermals.RESERVE_ELEGIBILITY[g] == res]:
                _r += (disp_stat[g, t]*thermals.MAX_P[g] - tg[g, t])*params.POWER_BASE
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

def write_thermal_operation(params, thermals, stUpTG, stDwTG, disp_stat, tgDisp, tg):
    """Write the decisions for the thermal units"""

    f = open(params.OUT_DIR + 'thermal decisions - ' +
                params.PS + ' - case ' + str(params.CASE) + '.csv', 'w', encoding = 'ISO-8859-1')
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
            f.write(str(stUpTG[g, t]) + ';')
            f.write(str(stDwTG[g, t]) + ';')
            f.write(str(disp_stat[g, t]) + ';')
            f.write(str(round((tgDisp[g, t]+thermals.MIN_P[g]*disp_stat[g, t])*params.POWER_BASE, 4))
                                                                                            + ';')
            f.write(str(round(tg[g, t]*params.POWER_BASE, 4))+';')
            f.write(str(round(((thermals.MAX_P[g] - thermals.MIN_P[g])*disp_stat[g, t]
                                - tgDisp[g,t])*params.POWER_BASE, 4))+';')
            f.write(str(round(thermals.MIN_P[g]*params.POWER_BASE, 4))+';')
            f.write(str(round(thermals.MAX_P[g]*params.POWER_BASE, 4))+';')
            f.write(str(round(thermals.RAMP_DOWN[g]*params.POWER_BASE, 4))+';')
            f.write(str(round(thermals.RAMP_UP[g]*params.POWER_BASE, 4))+';')
            f.write('\n')
    f.close()

def writeDDiPdata(params, worker_configs, pLog, subh_info, backwardInfo, W_RANK):
    """Write data of the optimization process"""

    if W_RANK == 0:
        f = open(params.OUT_DIR + '/convergence - '+
                params.PS + ' - case ' + str(params.CASE) + '.csv', 'w', encoding = 'ISO-8859-1')
        f.write('Iteration;Lower bound;Upper bound;Gap (%);Forward time;')
        f.write('Backward time\n')
        for i in range(len(pLog['lb'])):
            f.write(str(i) + ';')
            f.write(str(pLog['lb'][i]/params.SCAL_OBJ_F) + ';')
            f.write(str(pLog['ub'][i]/params.SCAL_OBJ_F) + ';')
            f.write(str(pLog['gap'][i]*100) + ';')
            f.write(str(pLog['runTimeForward'][i]) + ';')
            f.write(str(pLog['runTimeBackward'][i]))
            f.write('\n')
        f.close()
        del f

    if worker_configs._I_AM_A_FORWARD_WORKER:
        f = open(params.OUT_DIR + '/forwardInfo - W_RANK ' + str(W_RANK) + ' - '+
                params.PS + ' - case ' + str(params.CASE) + '.csv', 'w', encoding = 'ISO-8859-1')
        f.write('Iteration;Subhorizon;Present costs ($);Future Costs ($)')
        f.write(';Time (sec);Iterations;Gap (%);Optimization Status')
        f.write(';Distance from previous solution (Euclidean distance)')
        f.write(';Distance from previous solution - binary variables')
        f.write(' (Hamming distance)')
        f.write(';Communication (sec)')
        f.write(';Time to add cuts (sec);Time stamp (sec)')
        f.write('\n')
        for i in range(len(subh_info[0]['presentCots'])):
            for p in range(worker_configs._N_SUBHORIZONS):
                f.write(str(i) + ';')
                f.write(str(p) + ';')
                f.write(str(subh_info[p]['presentCots'][i]/params.SCAL_OBJ_F)+';')
                f.write(str(subh_info[p]['future_costs'][i]/params.SCAL_OBJ_F)+';')
                f.write(str(subh_info[p]['time'][i]) + ';')
                f.write(str(subh_info[p]['iterations'][i]) + ';')
                f.write(str(subh_info[p]['gap'][i]*100) + ';')
                f.write(str(subh_info[p]['optStatus'][i]) + ';')
                f.write(str(subh_info[p]['distanceFromPreviousSol'][i]) + ';')
                f.write(str(subh_info[p]['distBinVars'][i]**2) + ';')
                f.write(str(subh_info[p]['comm'][i]) + ';')
                f.write(str(subh_info[p]['cuts'][i]) + ';')
                f.write(str(subh_info[p]['timeStamp'][i]))
                f.write('\n')
        f.close()
        del f

    if worker_configs._I_AM_A_BACKWARD_WORKER:
        f = open(params.OUT_DIR + '/backwardInfo - W_RANK ' + str(W_RANK) + ' - ' +
                params.PS + ' - case ' + str(params.CASE) + '.csv', 'w', encoding = 'ISO-8859-1')
        f.write('Iteration;Subhorizon;LB ($);UB ($)')
        f.write(';Time (sec);Gap (%);Optimization Status')
        f.write(';Communication (sec)')
        f.write(';Time to add cuts (sec); Time stamp (sec)')
        f.write('\n')
        for i in range(len(backwardInfo[0]['lb'])):
            for p in range(worker_configs._N_SUBHORIZONS):
                f.write(str(i) + ';')
                f.write(str(p) + ';')
                f.write(str(backwardInfo[p]['lb'][i] / params.SCAL_OBJ_F) + ';')
                f.write(str(backwardInfo[p]['ub'][i] / params.SCAL_OBJ_F) + ';')
                f.write(str(backwardInfo[p]['time'][i]) + ';')
                f.write(str(backwardInfo[p]['gap'][i]*100) + ';')
                f.write(str(backwardInfo[p]['optStatus'][i]) + ';')
                f.write(str(backwardInfo[p]['comm'][i]) + ';')
                f.write(str(backwardInfo[p]['cuts'][i]) + ';')
                f.write(str(backwardInfo[p]['timeStamp'][i]))
                f.write('\n')
        f.close()
        del f

def write_branch_flows(params,
                            network, thermals, flow_AC_from,
                                                    link_flow,
                                                        t_g, h_g,
                                                            s_load_curtailment,
                                                            s_gen_surplus,
                                                            s_renew_curtailment) -> None:
    '''
        write branch flows to a csv file
    '''

    count_active_constrs = 0

    active_lines = set()

    table_header = ['Line ID', 'End buses', 'Period', 'UB (MW)', 'LB (MW)', 'Flow (MW)',
                            'Active UB?','Active LB?']

    table_to_print, violated_lines = [], []

    f = open(params.OUT_DIR + '/branch flows - '+
                    params.PS + ' - case ' + params.CASE + '.csv', 'w', encoding = 'utf-8')
    f.write('sep=;\n')
    f.write('var;x (pu);max (pu);min (pu);violation (pu)\n')

    if len(flow_AC_from.keys()) > 0:
        for k, flow in flow_AC_from.items():
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
                                            network.ACTIVE_LB_PER_PERIOD[l][t]])
                if ((flow < (network.LINE_FLOW_LB[l][t] - 1/params.POWER_BASE))
                    or (flow > (network.LINE_FLOW_UB[l][t] + 1/params.POWER_BASE))):
                    violated_lines.append([l, network.LINE_F_T[l], t,
                                            network.LINE_FLOW_UB[l][t]*params.POWER_BASE,
                                            network.LINE_FLOW_LB[l][t]*params.POWER_BASE,
                                            flow*params.POWER_BASE,
                                            network.ACTIVE_UB_PER_PERIOD[l][t],
                                            network.ACTIVE_LB_PER_PERIOD[l][t]])

            f.write(f"flow_{k[0]}_{k[1]}_{k[2]}_{k[3]};" + str(flow) + ';'
                    + str(network.LINE_FLOW_UB[l][t]) + ';' +
                    str(network.LINE_FLOW_LB[l][t]) + ';' +
                    str(max(max(flow - network.LINE_FLOW_UB[l][t], 0),
                            max(network.LINE_FLOW_LB[l][t] - flow, 0))) +
                    '\n')

    else:
        class surrogate_model:
            """Used so the power injections can be computed without an actual optimization mode.
                The only thing necessary is that the object has an attribute xsum, which is a
                sum function"""
            def __init__(self):
                self.xsum = sum

        m = surrogate_model()

        bus_injections = get_bus_injection_expr(thermals, network,
                                    t_g, h_g,
                                        {}, link_flow,
                                            s_load_curtailment, s_gen_surplus, s_renew_curtailment,
                                                periods = range(params.T),
                                                    include_flows = False)

        buses_with_injections_idxs = np.array([b for b, bus in enumerate(network.BUS_ID)
                                            if [abs(bus_injections[bus, t]) != 0
                                                    for t in range(params.T)]],
                                                        dtype = 'int64')

        sub_PTDF_act_lines = network.PTDF[:]
        sub_PTDF_act_lines[np.where(abs(sub_PTDF_act_lines) < params.PTDF_COEFF_TOL)] = 0

        for l in network.LINE_ID:

            l_idx = network.LINE_ID.index(l)
            non_zeros = np.intersect1d(np.where(abs(sub_PTDF_act_lines[l_idx,:]) > 0)[0],
                                                    buses_with_injections_idxs)
            buses_of_interest = [network.BUS_ID[b] for b in non_zeros]

            flows = np.inner(
                            np.array([[bus_injections[bus, t] for bus in buses_of_interest]
                                        for t in range(params.T)]),
                                        sub_PTDF_act_lines[l_idx, non_zeros]
                    )
            for t in range(params.T):
                flow = flows[t]
                if ((flow <= (network.LINE_FLOW_LB[l][t] + 1e-3))
                        or (flow >= (network.LINE_FLOW_UB[l][t] - 1e-3))):
                    active_lines.add(l)
                    count_active_constrs += 1
                    table_to_print.append([l, network.LINE_F_T[l], t,
                                            network.LINE_FLOW_UB[l][t]*params.POWER_BASE,
                                            network.LINE_FLOW_LB[l][t]*params.POWER_BASE,
                                            flow*params.POWER_BASE,
                                            network.ACTIVE_UB_PER_PERIOD[l][t],
                                            network.ACTIVE_LB_PER_PERIOD[l][t]])

                    if ((flow < (network.LINE_FLOW_LB[l][t] - 1/params.POWER_BASE))
                        or (flow > (network.LINE_FLOW_UB[l][t] + 1/params.POWER_BASE))):
                        violated_lines.append([l, network.LINE_F_T[l], t,
                                            network.LINE_FLOW_UB[l][t]*params.POWER_BASE,
                                            network.LINE_FLOW_LB[l][t]*params.POWER_BASE,
                                            flow*params.POWER_BASE,
                                            network.ACTIVE_UB_PER_PERIOD[l][t],
                                            network.ACTIVE_LB_PER_PERIOD[l][t]])

                f.write(f"flow_{network.LINE_F_T[l][0]}_{network.LINE_F_T[l][1]}_{l}_{t};{flow};"
                        + str(network.LINE_FLOW_UB[l][t])+';'+
                        str(network.LINE_FLOW_LB[l][t]) + ';' +
                        str(max(max(flow - network.LINE_FLOW_UB[l][t], 0),
                                max(network.LINE_FLOW_LB[l][t] - flow, 0))) +
                        '\n')
    f.close()
    del f

    print("\n\n")
    print(tabulate(table_to_print, headers = table_header))
    print(f"{count_active_constrs} transmission line constraints are active", flush=True)
    print(f"{len(active_lines)} lines active\n\n\n", flush=True)

    if len(violated_lines) > 0:
        print(tabulate(violated_lines, headers = table_header))
        print("The list of bounds for the lines above have been violated")
        #raise ValueError("The list of bounds for the lines above have been violated")
