# Under construction

# Ward Reduction in Unit-Commitment Problems

This is a implementation of the ideas presented in the paper "Ward Reduction in Unit-Commitment Problems",
conditionally accepted for publication in XXIII Power Systems Computation Conference, PSCC 2024.

In this work, we analyse how we can use the famous Ward reduction to reduce the computational burden of
unit-commitment models. The UC model we currently study has two main components:
-    Typical model for thermal generating units: linear generation costs, generation limits, ramps, and minimum up and down times.
-    Lossless DC network model.

The resulting mathematical model is mixed-integer linear.

For a lack of a better name, in the following, we refer to this package as `the package`.

## Functionality

-    The package first determines sets of branch elements whose limits cannot be reached during the planning horizon
-    Then, it applies succesive Ward reductions to the power system by explointing the redundant branch limits
     previously found. In the Ward reduction, nodes connected to branches with redundant limits are deemed **external**;
     nodes directly connected to any external nodes are defined **frontier** nodes; and the remaining, those connected to at
     least one branch element whose limit can be reached and those who are not directly connected to external nodes, are called
     **internal** nodes.

## Documentation

TODO

## Installation

TODO

## Usage

On Windows:

```
mpiexec -np 1 python "main.py" %1 [--EXP_NAME=exp_1] [--T=36] [--CASE=1] [--PS=ieee118] [--IN_DIR=""] [--OUT_DIR=""] [--THREADS=0] [--VERBOSE=1] [--DISCRETIZATION=1] [--MILP_GAP=0.0001] [--DEFICIT_COST=100000000] [--REDUCE_SYSTEM=0] [--POWER_BASE=100] [--SCAL_OBJ_F=0.001] [--MIN_GEN_CUT_MW=1] [--PTDF_COEFF_TOL=0.00001] [--MAX_NUMBER_OF_CONNECTIONS=20] [--MAX_PROCESS_REDUCE_NETWORK=1] [--NETWORK_MODEL=B_THETA] [--NETWORK_SLACKS=BUS_SLACKS] 
```

On Linux:

```
TODO
```

<p align="center">
     
| Command  | Description |
| ------------- | ------------- |
| EXP_NAME | Name that uniquely identifies the current experiment. If an output directory, OUT_DIR, is not provided, then an output directory EXP_NAME will be created, defaults to "exp1" |
| T | Number of periods in the scheduling horizon, defaults to 36 |
| TIME_LIMIT | Time limit in seconds, defaults to 3600.0 |
| CASE | ID of the case under study, defaults to "1" |
| PS | Name of the power system under study, defaults to "ieee118" |
| IN_DIR | dir where the input files are located, defaults to ''. If not given, the input directory is assumed to be in the parent directory |
| OUT_DIR | dir to which the output is to be written to, defaults to ''. If not given, an directory will be created in the parent directory |
| THREADS | Maximum number of threads available to each process, defaults to 0 |
| DISCRETIZATION | Length in hours of each time period in the scheduling horizon, defaults to 1.0 |
| VERBOSE | Flag that indicates whether the optimization solvers console output is enabled, defaults to True|
| DISCRETIZATION | Length in hours of each time period in the scheduling horizon, defaults to 1.0 |
| MILP_GAP | Relative gap tolerance for the UC MILP, defaults to 1e-4 |
| REDUCE_SYSTEM | Flag to indicate whether the transmission system should be reduced, defaults to False |
| DEFICIT_COST | Unitary cost for load curtailment and generation surplus, defaults to 1e8 |
| REDUCE_SYSTEM | Flag to indicate whether the transmission system should be reduced, defaults to False |
| POWER_BASE | Power base in MVA, defaults to 100 |
| SCAL_OBJ_F | Scaling factor applied to the objective function. The objective function is multiplied by this factor, defaults to 1e-3.|
| MIN_GEN_CUT_MW | Threshold for the minimum generation of generating units. Units whose minimum generation is strictly less than this value are assumed to have no minimum generation, i.e., the minimum generation is replaced by 0, default to 1.00. |
| PTDF_COEFF_TOL | Threshold for the coefficient of the PTDF matrix. Coefficients whose magnitudes are less than this value are substituted by 0, defaults to 1e-5. |
| MAX_NUMBER_OF_CONNECTIONS | In the strategy used to reduce the network, it is possible to determine the maximum number of connections that the network nodes may have after the reduction is applied, defaults to 20 |
| MAX_PROCESS_REDUCE_NETWORK | Maximum number of processes launched to identify inactive transmission line bounds, defaults to 1 |
| NETWORK_MODEL | Network model used |
| NETWORK_SLACKS  | Network slacks to be included (default = `NetworkSlacks.BUS_SLACKS`)  |

</p>

## Dependencies
-   [gurobipy](https://www.gurobi.com/) for solving the optimization models
-   [numpy](http://www.numpy.org/) and [scipy](http://scipy.org/) matrix computations
-   [networkx](https://networkx.github.io/) for network computations and plots
-   [matplotlib](https://matplotlib.org/) for plotting the network

If you have an MPI implementation, you can launch multiple processes to accelerate the branch-limit's redundancy identification step.
We test our codes with the Microsoft implementation, [MS-MPI](https://learn.microsoft.com/en-us/message-passing-interface/microsoft-mpi), Version 10.1.12498.18, 
on an Intel machine running Win11. And on Ubuntu 20, with [Open-MPI](https://www.open-mpi.org/), version 4, also on a Intel machine.

## Citing

If you want to cide this work, please use ...

# Licence

