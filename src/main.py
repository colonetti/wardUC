import mpi4py
mpi4py.rc.thread_level = 'single'
from mpi4py import MPI

from read_input.read import read
from src.solver import run_solver
from write import write_solution, check_flows_full_network
from constants import NetworkModel

W_COMM = MPI.COMM_WORLD
W_RANK = W_COMM.Get_rank()
W_SIZE = W_COMM.Get_size()
host = MPI.Get_processor_name()

def main(args):
    """main function"""

    (params, thermals, network, original_thermals, original_network) = read(args=args)

    print(f"{'':#<70}")
    print(f"{' Overview of the system ':#^70}")
    print("System: " + params.PS)
    print("Case: " + params.CASE)
    print(f"Scheduling horizon in hours: {params.T*params.DISCRETIZATION}")
    print(f"Time steps: {params.T}")
    print(f"Time step resolution: {params.DISCRETIZATION} h")
    print(f"{len(thermals.ID)} generating units")
    print(f"Total installed capacity (MW): {sum(thermals.MAX_P.values())*params.POWER_BASE:,.4f}")
    print("Peak net load (MW): " +
            f"{max(sum(network.NET_LOAD[:, t]) for t in range(params.T))*params.POWER_BASE:,.4f}")
    print(f"Network model: {params.NETWORK_MODEL}")
    if params.NETWORK_MODEL != NetworkModel.SINGLE_BUS:
        print(f"Buses: {len(network.BUS_ID)}")
        print(f"AC transmission lines: {len(network.LINE_F_T)}")
        n_p_act = len([l for l in network.LINE_ID if network.ACTIVE_BOUNDS[l]])
        print(f"The total number of possibly active lines is {n_p_act}", flush=True)
    print(f"{'':#<70}")
    print(flush=True)

    (m,
     st_up_tg, st_dw_tg, disp_stat_tg,
     t_g, t_g_disp,
     s_reserve,
     theta,
     branch_flow,
     s_load_curtailment, s_gen_surplus, s_renew_curtailment) = run_solver(params,
                                                                          thermals,
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

        if params.REDUCE_SYSTEM and (params.NETWORK_MODEL in (NetworkModel.B_THETA,
                                                                NetworkModel.FLUXES,
                                                                NetworkModel.PTDF)):
            check_flows_full_network(params,
                                     original_thermals,
                                     original_network,
                                     t_g,
                                     s_load_curtailment,
                                     s_gen_surplus,
                                     s_renew_curtailment)

if __name__ == '__main__':
    from treat_args import _treat_args

    args = _treat_args(W_RANK, W_SIZE)

    main(args)
