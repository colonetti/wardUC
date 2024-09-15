from time import time
import numpy as np
from components.network import Network, _get_isolated_subsystems

def _get_unordered_Y_B(network:Network,
                       buses:list,
                       lines:list) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    get unordered Y and B matrices
    they are not ordered because the order os lines and buses does not match
    lists network.LINE_ID and network.BUS_ID
    """

    inverse_map_buses = {bus: b for b, bus in enumerate(buses)}

    A = np.zeros((len(lines), len(buses)), dtype='d')
    for l_idx, l in enumerate(lines):
        A[l_idx, inverse_map_buses[network.LINE_F_T[l][0]]] = 1
        A[l_idx, inverse_map_buses[network.LINE_F_T[l][1]]] = - 1

    Y = np.diag(np.array([1/network.LINE_X[l] for l in lines], dtype='d'))

    B = np.matmul(np.transpose(A), np.matmul(Y, A))

    return Y, B, A


def build_ptdf(network:Network):
    """
        computes the power-transfer distribution factors matrix
        network:            an instance of Network
    """

    time_0 = time()

    if len(set(network.LINE_F_T.values())) != len(network.LINE_ID):
        raise ValueError('there are parallel lines')

    network.PTDF = np.zeros((len(network.LINE_ID), len(network.BUS_ID)),
                            dtype='d')

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
                except KeyError as error:
                    s = f"There is no line between buses {end_points}"
                    raise ValueError(s) from error

        (Y, B, A) = _get_unordered_Y_B(network, buses=buses, lines=lines)

        B_minus_ref = np.concatenate((B[:, 0:0], B[:, 1:]), axis=1)

        B_minus_ref = np.concatenate((B_minus_ref[0:0,:], B_minus_ref[1:,:]),
                                     axis=0)

        B_minus_ref_inv = np.linalg.inv(B_minus_ref)

        #### now include the reference buses again with zero coefficients
        # include a column with zeros
        B_with_ref_inv = np.concatenate(
                        (np.concatenate((B_minus_ref_inv[:, 0:0],
                                    np.zeros((len(buses) - 1, 1))), axis=1),
                                    B_minus_ref_inv[:, 0:]), axis=1
        )

        # include a row with zeros
        B_with_ref_inv = np.concatenate(
                        (np.concatenate((B_with_ref_inv[0:0, :],
                                        np.zeros((1, len(buses)))), axis=0),
                                        B_with_ref_inv[0:, :]), axis=0
        )

        ptdf_sub_sys = np.matmul(np.matmul(Y, A), B_with_ref_inv)

        _aux = np.zeros((len(lines), len(network.BUS_ID)), dtype='d')

        lines_idxs = [inverse_map_lines[line] for line in lines]
        buses_idxs = [inverse_map_buses[bus] for bus in buses]

        _aux[:, buses_idxs] = ptdf_sub_sys

        network.PTDF[lines_idxs, :] = _aux

    print(f"\n\nIt took {time()-time_0:,.4f} seconds to build the PTDF matrix",
          flush=True)
