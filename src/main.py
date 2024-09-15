import mpi4py
mpi4py.rc.thread_level = 'single'
from mpi4py import MPI
from copy import deepcopy

from read_input.read import read
from solver import run_solver
from write import write_solution, check_flows_full_network
from constants import NetworkModel
from components.network import Network

from pre_processing.build_ptdf import build_ptdf
from pre_processing.reduce_network import reduce_network
from pre_processing.identify_redundant_line_bounds import (
                                    remove_redundant_flow_limits_without_opt,
                                    redundant_line_bounds
)

W_COMM = MPI.COMM_WORLD
W_RANK = W_COMM.Get_rank()
W_SIZE = W_COMM.Get_size()
host = MPI.Get_processor_name()

def _check_number_of_buses(network: Network):
    """Check whether there are buses left in the network"""

    if len(network.LINE_F_T) == 0:
        raise ValueError("After reducing the network, there are no " +
                         "transmission lines left in the system. " +
                         "Either use the single bus model " +
                         "or disable network reduction"
        )

def main(args):
    """main function"""

    params, original_thermals, original_network = read(args=args)

    thermals = deepcopy(original_thermals)
    network = deepcopy(original_network)

    if params.REDUCE_SYSTEM and (params.NETWORK_MODEL in (NetworkModel.B_THETA,
                                                          NetworkModel.FLUXES,
                                                          NetworkModel.PTDF)):

        build_ptdf(original_network)

        reduce_network(params, thermals, network)

        _check_number_of_buses(network)

        build_ptdf(network)

        remove_redundant_flow_limits_without_opt(params, thermals, network)

        reduce_network(params, thermals, network)

        _check_number_of_buses(network)

        build_ptdf(network)
        redundant_line_bounds(params, thermals, network,
                              time_limit=360,
                              run_single_period_models=False)

        reduce_network(params, thermals, network)

        _check_number_of_buses(network)

    if params.NETWORK_MODEL not in (NetworkModel.SINGLE_BUS,
                                    NetworkModel.FLUXES):
        build_ptdf(network)

    print(f"{'':#<70}")
    print(f"{' Overview of the system ':#^70}")
    print("System: " + params.PS)
    print("Case: " + params.CASE)
    print(f"Scheduling horizon in hours: {params.T*params.DISCRETIZATION}")
    print(f"Time steps: {params.T}")
    print(f"Time step resolution: {params.DISCRETIZATION} h")
    print(f"{len(thermals.ID)} generating units")
    inst_cap = sum(thermals.MAX_P.values())*params.POWER_BASE
    print(f"Total installed capacity (MW): {inst_cap:,.4f}")
    peak_load = (max(sum(network.NET_LOAD[:, t]) for t in range(params.T)) *
                 params.POWER_BASE
    )
    print(f"Peak net load (MW): {peak_load:,.4f}")
    print(f"Network model: {params.NETWORK_MODEL}")
    if params.NETWORK_MODEL != NetworkModel.SINGLE_BUS:
        print(f"Buses: {len(network.BUS_ID)}")
        print(f"AC transmission lines: {len(network.LINE_F_T)}")
        n_p_act = len([l for l in network.LINE_ID if network.ACTIVE_BOUNDS[l]])
        print(f"The total number of possibly active lines is {n_p_act}",
              flush=True)
    print(f"{'':#<70}")
    print(flush=True)

    (m,
     st_up_tg, st_dw_tg, disp_stat_tg,
     t_g, t_g_disp,
     s_reserve,
     theta,
     branch_flow,
     s_load_curtailment, s_gen_surplus,
                    s_renew_curtailment) = run_solver(params, thermals,
                                                      network)

    if m.SolCount >= 1:
        # if at least one solution was found
        write_solution(params, thermals, network,
                       m,
                       st_up_tg, st_dw_tg, disp_stat_tg,
                       t_g, t_g_disp,
                       s_reserve,
                       theta,
                       branch_flow,
                       s_load_curtailment, s_gen_surplus, s_renew_curtailment)

        if (params.REDUCE_SYSTEM and
            (params.NETWORK_MODEL in (NetworkModel.B_THETA,
                                      NetworkModel.FLUXES,
                                      NetworkModel.PTDF))
        ):
            check_flows_full_network(params,
                                     original_thermals,
                                     original_network,
                                     t_g,
                                     s_load_curtailment,
                                     s_gen_surplus,
                                     s_renew_curtailment
            )

if __name__ == '__main__':
    from treat_args import _treat_args

    args = _treat_args(W_RANK, W_SIZE)

    main(args)
