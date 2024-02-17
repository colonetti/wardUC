from time import time
import numpy as np
from components.network import Network, _get_isolated_subsystems

def _get_unordered_Y_B(network:Network):
    """
        get unordered Y and B matrices
        they are not ordered because the order os lines and buses does not match lists
        network.LINE_ID and network.BUS_ID
    """

    disjoint_subsys = _get_isolated_subsystems(network)

    # map lines
    map_lines = {idx: {idx_line: 0 for idx_line in range(len(subs['edges']))}
                                                    for idx, subs in disjoint_subsys.items()}
    # map buses
    map_buses = {idx: {idx_bus: 1e20 for idx_bus in range(len(subs['nodes']))}
                                                    for idx, subs in disjoint_subsys.items()}

    # incidence matrix
    A = {idx: np.zeros((len(subs['edges']), len(subs['nodes'])), dtype='d')
                                                    for idx, subs in disjoint_subsys.items()}

    # reactances in the lines of the subsystems
    Y_subs = {idx: np.zeros(len(subs['edges']), dtype='d')
                                                    for idx, subs in disjoint_subsys.items()}

    idxs_of_refs = {idx: 1e20 for idx in disjoint_subsys.keys()}

    par_lines = {edge: {'par_l': [],
                'y_eq': 0} for subs in disjoint_subsys.values() for edge in subs['edges']}

    for idx, subs in disjoint_subsys.items():
        for l_index_in_subs in range(len(subs['edges'])):
            edge = subs['edges'][l_index_in_subs]
            try:
                list_of_lines = [l for l, f_t in network.LINE_F_T.items()
                                               if f_t[0] == subs['edges'][l_index_in_subs][0] and
                                                    f_t[1] == subs['edges'][l_index_in_subs][1]]
                map_lines[idx][l_index_in_subs] = list_of_lines[0]
                map_buses[idx][subs['nodes'].index(subs['edges'][l_index_in_subs][0])] =\
                                                            network.LINE_F_T[list_of_lines[0]][0]
                map_buses[idx][subs['nodes'].index(subs['edges'][l_index_in_subs][1])] =\
                                                            network.LINE_F_T[list_of_lines[0]][1]

                terminal_buses = (network.LINE_F_T[list_of_lines[0]][0],
                                    network.LINE_F_T[list_of_lines[0]][1])

                A[idx][l_index_in_subs, subs['nodes'].index(subs['edges'][l_index_in_subs][0])] = 1
                A[idx][l_index_in_subs, subs['nodes'].index(subs['edges'][l_index_in_subs][1])] = -1

            except IndexError:
                list_of_lines = [l for l, f_t in network.LINE_F_T.items()
                                               if f_t[0] == subs['edges'][l_index_in_subs][1] and
                                                    f_t[1] == subs['edges'][l_index_in_subs][0]]
                map_lines[idx][l_index_in_subs] = list_of_lines[0]
                map_buses[idx][subs['nodes'].index(subs['edges'][l_index_in_subs][0])] =\
                                                            network.LINE_F_T[list_of_lines[0]][1]
                map_buses[idx][subs['nodes'].index(subs['edges'][l_index_in_subs][1])] =\
                                                            network.LINE_F_T[list_of_lines[0]][0]

                terminal_buses = (network.LINE_F_T[list_of_lines[0]][1],
                                  network.LINE_F_T[list_of_lines[0]][0])

                A[idx][l_index_in_subs, subs['nodes'].index(subs['edges'][l_index_in_subs][1])] = 1
                A[idx][l_index_in_subs, subs['nodes'].index(subs['edges'][l_index_in_subs][0])] = -1

            if len(list_of_lines) == 1:
                Y_subs[idx][l_index_in_subs] = 1/network.LINE_X[map_lines[idx][l_index_in_subs]]
                par_lines[edge]['par_l'].append(map_lines[idx][l_index_in_subs])
            else:
                list_of_lines = [l for l, f_t in network.LINE_F_T.items()
                                               if (f_t[0] == terminal_buses[0] and
                                                    f_t[1] == terminal_buses[1]) or
                                                        (f_t[0] == terminal_buses[1] and
                                                            f_t[1] == terminal_buses[0])]
                y_eq = 0
                for l in list_of_lines:
                    y_eq += 1/network.LINE_X[l]
                    par_lines[edge]['par_l'].append(l)

                Y_subs[idx][l_index_in_subs] = y_eq

            par_lines[edge]['y_eq'] = Y_subs[idx][l_index_in_subs]

            if subs['edges'][l_index_in_subs][0] in network.REF_BUS_ID:
                idxs_of_refs[idx] = subs['nodes'].index(subs['edges'][l_index_in_subs][0])

            if subs['edges'][l_index_in_subs][1] in network.REF_BUS_ID:
                idxs_of_refs[idx] = subs['nodes'].index(subs['edges'][l_index_in_subs][1])

        if idxs_of_refs[idx] == 1e20:
            # in case a reference bus was not defined
            idxs_of_refs[idx] = 0

    assert max(b for subs in map_buses.values() for b in subs.values()) < 1e20,\
                        "One or more buses were not found and couldnt not be mapped"

    Y = {idx: np.diag(Y_subs[idx]) for idx in disjoint_subsys.keys()}

    B = {idx: np.matmul(np.transpose(A[idx]), np.matmul(Y[idx], A[idx]))
                                                        for idx in disjoint_subsys.keys()}

    return Y, B, A, par_lines, map_buses, idxs_of_refs, disjoint_subsys


def _get_unordered_Y_B_new(network:Network,
                            buses:list,
                            lines:list) -> (np.ndarray, np.ndarray, np.ndarray):
    """
        get unordered Y and B matrices
        they are not ordered because the order os lines and buses does not match lists
        network.LINE_ID and network.BUS_ID
    """

    inverse_map_buses = {bus: b for b, bus in enumerate(buses)}

    A = np.zeros((len(lines), len(buses)), dtype='d')
    for l_idx, l in enumerate(lines):
        A[l_idx, inverse_map_buses[network.LINE_F_T[l][0]]] = 1
        A[l_idx, inverse_map_buses[network.LINE_F_T[l][1]]] = - 1

    Y = np.diag(np.array([1/network.LINE_X[l] for l in lines], dtype='d'))

    B = np.matmul(np.transpose(A), np.matmul(Y, A))

    return (Y, B, A)

def get_B(network:Network) -> np.ndarray:
    """
        get B matrix with buses in the same order as network.BUS_ID
    """
    (_0, B, _1, _2, map_buses,
        _3, disjoint_AC_subsystems) = _get_unordered_Y_B(network)

    B_dict = {bus_1: {bus_2: 0 for bus_2 in network.BUS_ID} for bus_1 in network.BUS_ID}
    for idx, subs in disjoint_AC_subsystems.items():
        for bus_index_in_subs_1 in range(len(subs['nodes'])):
            for bus_index_in_subs_2 in range(len(subs['nodes'])):
                B_dict[map_buses[idx][bus_index_in_subs_1]][map_buses[idx][bus_index_in_subs_2]] = (
                                                B[idx][bus_index_in_subs_1, bus_index_in_subs_2])

    B_arr = np.array([[B_dict[bus_1][bus_2] for bus_2 in network.BUS_ID]
                        for bus_1 in network.BUS_ID], dtype='d')
    return B_arr

def build_ptdf(network:Network):
    """
        computes the power-transfer distribution factors matrix
        network:            an instance of Network
    """

    time_0 = time()

    assert len(set(network.LINE_F_T.values())) == len(network.LINE_ID), 'there are parallel lines'

    network.PTDF = np.zeros((len(network.LINE_ID), len(network.BUS_ID)), dtype='d')

    # create a map of from-to-buses (endpoints) to line id
    map_f_t_buses = {f_t: l for l, f_t in network.LINE_F_T.items()}

    inverse_map_buses = {bus: b for b, bus in enumerate(network.BUS_ID)}
    inverse_map_lines = {line: l for l, line in enumerate(network.LINE_ID)}

    disjoint_subsys = _get_isolated_subsystems(network)

    for sub_sys in disjoint_subsys.values():

        buses = sub_sys['nodes']

        lines = []

        for end_points in sub_sys['edges']:
            if end_points in map_f_t_buses.keys():
                lines.append(map_f_t_buses[end_points])
            else:
                try:
                    lines.append(map_f_t_buses[(end_points[1], end_points[0])])
                except KeyError:
                    raise ValueError(f"There is no line with from-to buses {end_points}")

        (Y, B, A) = _get_unordered_Y_B_new(network,
                                            buses = buses,
                                                lines = lines)

        B_minus_ref = np.concatenate((B[:, 0:0], B[:, 1:]), axis = 1)

        B_minus_ref = np.concatenate((B_minus_ref[0:0,:], B_minus_ref[1:,:]), axis = 0)

        B_minus_ref_inv = np.linalg.inv(B_minus_ref)

        #### now include the reference buses again with zero coefficients
        # include a column with zeros
        B_with_ref_inv = np.concatenate((np.concatenate((B_minus_ref_inv[:, 0:0],
                                                np.zeros((len(buses) - 1, 1))), axis = 1),
                                                    B_minus_ref_inv[:, 0:]), axis = 1)

        # include a row with zeros
        B_with_ref_inv = np.concatenate((np.concatenate((B_with_ref_inv[0:0, :],
                                            np.zeros((1, len(buses)))), axis = 0),
                                                B_with_ref_inv[0:, :]), axis = 0)

        ptdf_sub_sys = np.matmul(np.matmul(Y, A), B_with_ref_inv)

        _aux = np.zeros((len(lines), len(network.BUS_ID)), dtype='d')

        lines_idxs = [inverse_map_lines[line] for line in lines]
        buses_idxs = [inverse_map_buses[bus] for bus in buses]

        _aux[:, buses_idxs] = ptdf_sub_sys

        network.PTDF[lines_idxs, :] = _aux

    print(f"\n\nIt took {time() - time_0:,.4f} seconds to build the PTDF matrix", flush=True)
