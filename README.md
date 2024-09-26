# Ward Reduction in Unit-Commitment Problems

In this work, we analyse how we can use the famous Ward reduction to reduce the computational burden of
unit-commitment models. The UC model we currently study has two main components:
-    Typical model for thermal generating units: linear generation costs, generation limits, ramps, and minimum up and down times.
-    Lossless DC network model.

The resulting mathematical model is mixed-integer linear.

For the lack of a better name, in the following, we refer to this package as `the package`.

### Test system 1354pegase with full network
<img src="https://drive.google.com/uc?id=1HUGqtqFunX0rqG8CkmdaOJwKs5fY4o0Q"
     alt="1354rte full"
     style="width: 50%" />

### Test system 1354pegase with reduced network
<img src="https://drive.google.com/uc?id=1HP957gd5OvADYJGKJAv5fzy4rmZ7Auvn"
     alt="1354rte reduced"
     style="width: 50%" />

### Test system 6515rte with full network
<img src="https://drive.google.com/uc?id=1HcgPrdrQWcOslxPN6BeGm5ON07PxQsw5"
     alt="6515rte full"
     style="width: 50%" />
     
### Test system 6515rte with reduced network
<img src="https://drive.google.com/uc?id=1HWdZ8o-KxSUk9ASqNsP11NXUaiuA4qep"
     alt="6515rte reduced"
     style="width: 50%" />

## Functionality

-    The package first determines sets of branch elements whose limits cannot be reached during the planning horizon
-    Then, it applies succesive Ward reductions to the power system by explointing the redundant branch limits
     previously found. In the Ward reduction, nodes connected to branches with redundant limits are deemed **external**;
     nodes directly connected to any external nodes are defined **frontier** nodes; and the remaining, those connected to at
     least one branch element whose limit can be reached and those who are not directly connected to external nodes, are called
     **internal** nodes.

## Usage

On Windows:

```
mpiexec -np 1 python "main.py" %1 [--EXP_NAME=exp_1] [--T=36] [--CASE=1] [--PS=ieee118] [--IN_DIR=""] [--OUT_DIR=""] [--THREADS=0] [--VERBOSE=1] [--DISCRETIZATION=1] [--MILP_GAP=0.0001] [--DEFICIT_COST=100000000] [--REDUCE_SYSTEM=0] [--POWER_BASE=100] [--SCAL_OBJ_F=0.001] [--MIN_GEN_CUT_MW=1] [--PTDF_COEFF_TOL=0.00001] [--MAX_NUMBER_OF_CONNECTIONS=20] [--MAX_PROCESS_REDUCE_NETWORK=1] [--NETWORK_MODEL=B_THETA] [--NETWORK_SLACKS=BUS_SLACKS] 
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

The complete package dependency is described in 'requirements.txt'. We summarize the roles of the main packages below.

-   [gurobipy](https://www.gurobi.com/) for solving the optimization models
-   [numpy](http://www.numpy.org/) for matrix computations
-   [networkx](https://networkx.github.io/) for network computations
-   [mpi4py](https://mpi4py.readthedocs.io/en/stable/) for parallel computing

If you have an MPI implementation, you can launch multiple processes to accelerate the branch-limit's redundancy identification step.
We test our codes with the Microsoft implementation, [MS-MPI](https://learn.microsoft.com/en-us/message-passing-interface/microsoft-mpi), Version 10.1.12498.18, 
on an Intel machine running Win11. And on Ubuntu 20, with [Open-MPI](https://www.open-mpi.org/), version 4, also on a Intel machine.

## Citing

TODO

# Licence

TODO


# 14-node system example

## Original network

Consider the following 14-node system.

<img src="https://drive.google.com/uc?id=1xeFtii1CcXhDphXqDH5UOAmYSSBtGnJD"
     alt="original network"
     style="width: 50%" />

The system has 18 branches, 5 generators (represented in green), and 11 nodes with load (represented by the red arrows). 
Assume for simplicity that all branches have reactances of 0.1 p.u.. Moreover, throughout this example, node 2 is used as the reference node for the voltage angles.
The first order of businness is to compute the Power Transfer Distribution Factors (PTDF) matrix for this system.

Now, assume that the individual loads are 1 p.u., then adding up to a total system load of 11 p.u..
Moreover, assume that only 4 of all 18 branches can possibly reach their limits under any feasible operation of this system for this load profile --- these are the branches 4, 13, 14 and 16, represented in red in the image.
For the possibly binding branches, assume lower and upper limits for the flows of 10 p.u.. For all other branches, the limits -inf and +inf.

We intend to show some of the most important features of our algorithm with this example. Hence, in this example, we follow the same steps taken in the algorithm.
If you wish, you can follow the same steps by debugging our code with your favorite IDE.

For this system, the PTDF matrix (rounded) is

$$
 PTDF =     \begin{bmatrix}
              0.615&  0  &  0.052&  0.103&  0.23 &  0.203&  0.112&  0.112& 0.121&  0.148&  0.176&  0.203&  0.203&  0.203 & (l = 1)\\
              0.385&  0  & -0.052& -0.103& -0.23 & -0.203& -0.112& -0.112& -0.121& -0.148& -0.176& -0.203& -0.203& -0.203 & (l = 2)\\
             -0.052&  0  & -0.615& -0.23 & -0.103& -0.13 & -0.221& -0.221& -0.212& -0.185& -0.158& -0.13 & -0.13 & -0.13  & (l = 3)\\
             -0.103&  0  & -0.23 & -0.461& -0.206& -0.261& -0.442& -0.442& -0.424& -0.37 & -0.315& -0.261& -0.261& -0.261 & (l = 4)\\
             -0.23 &  0  & -0.103& -0.206& -0.461& -0.406& -0.224& -0.224& -0.242& -0.297& -0.352& -0.406& -0.406& -0.406 & (l = 5)\\
             -0.052&  0  &  0.385& -0.23 & -0.103& -0.13 & -0.221& -0.221& -0.212& -0.185& -0.158& -0.13 & -0.13 & -0.13  & (l = 6)\\
             -0.127&  0  &  0.127&  0.255& -0.255& -0.145&  0.218&  0.218& 0.182&  0.073& -0.036& -0.145& -0.145& -0.145 & (l = 7)\\
             -0.009&  0  &  0.009&  0.018& -0.018& -0.082& -0.627& -0.627& -0.273& -0.209& -0.145& -0.082& -0.082& -0.082 & (l = 8)\\
             -0.018&  0  &  0.018&  0.036& -0.036& -0.164& -0.255& -0.255& -0.545& -0.418& -0.291& -0.164& -0.164& -0.164 & (l = 9)\\
              0.027&  0  & -0.027& -0.055&  0.055& -0.755& -0.118& -0.118& -0.182& -0.373& -0.564& -0.755& -0.755& -0.755 & (l = 10)\\
              0.027&  0  & -0.027& -0.055&  0.055&  0.245& -0.118& -0.118& -0.182& -0.373& -0.564&  0.245&  0.245&  0.245 & (l = 111)\\
              0  &  0  &  0  &  0  &  0  &  0  &  0  &  0  & 0  &  0  &  0  & -1  & -1  & -1   & (l = 12)\\
              0  &  0  &  0  &  0  &  0  &  0  & 0 & -1  & 0  & 0 & 0 & 0 & 0 & 0  & (l = 13)\\
             -0.009&  0  &  0.009&  0.018& -0.018& -0.082&  0.373&  0.373& -0.273& -0.209& -0.145& -0.082& -0.082& -0.082 & (l = 14)\\
             -0.027&  0  &  0.027&  0.055& -0.055& -0.245&  0.118&  0.118& 0.182& -0.627& -0.436& -0.245& -0.245& -0.245 & (l = 15)\\
             -0.027&  0  &  0.027&  0.055& -0.055& -0.245&  0.118&  0.118& 0.182&  0.373& -0.436& -0.245& -0.245& -0.245 & (l = 16)\\
              0  &  0  & 0 & 0 &  0  &  0  &  0  &  0  & 0  &  0  &  0  &  0  & -1  & -1   & (l = 17)\\
             0 &  0  &  0  &  0  & 0 &  0  & 0 & 0 & 0  &  0  &  0  &  0  & 0 & -1   & (l = 18)\\
           \end{bmatrix}
$$

The above steps are taken in https://github.com/colonetti/wardUC/blob/7fccda443ffaaeef2cd6d0bfcae8b41ce32d4656/pre_processing/build_ptdf.py#L148

With the PTDF, we can add the flow constraints for the branches whose limits might be reached in the UC, as we explain in the paper. For this example, there are 4 possibly binding branches, 4, 13, 14 and 16. Their flows, as described by the PTDF, are force to be within their respective limits by the constraints below.

$$
 \begin{align}
  {-}10 \leq -0.103 \cdot p_1 -0.23 \cdot (p_3 + s_3 - 1)  -0.461 \cdot (s_4 - 1 ) -0.206 \cdot (s_5 - 1) -0.261 \cdot (p_4 + s_6 - 1) -0.442 \cdot p_5 -0.424 \cdot (s_9 - 1) -0.37 \cdot (s_{10} - 1) -0.315 \cdot (s_{11} - 1) -0.261 \cdot (s_{12} - 1) -0.261 \cdot (s_{13} - 1) -0.261 \cdot (s_{14} - 1) \leq 10 & \qquad \text{(l = 4)}\\
    {-}10 \leq - p_5 \leq 10 & \qquad \text{(l = 13)}\\
    {-}10 \leq -0.009 \cdot p_1  +  0.009 \cdot (p_3 + s_3 - 1) +  0.018 \cdot (s_4 - 1 )  -0.018 \cdot (s_5 - 1) -0.082 \cdot (p_4 + s_6 - 1) + 0.373 \cdot p_5 -0.273 \cdot (s_9 - 1) -0.209 \cdot (s_{10} - 1) -0.145 \cdot (s_{11} - 1) -0.082 \cdot (s_{12} - 1) -0.082 \cdot (s_{13} - 1) -0.082 \cdot (s_{14} - 1) \leq 10 & \qquad \text{(l = 14)}\\
    {-}10 \leq -0.027 \cdot p_1 +  0.027 \cdot (p_3 + s_3 - 1) +  0.055 \cdot (s_4 - 1 ) -0.055 \cdot (s_5 - 1) -0.245 \cdot (p_4 + s_6 - 1) + 0.118 \cdot p_5 + 0.182 \cdot (s_9 - 1) + 0.373 \cdot (s_{10} - 1) -0.436 \cdot (s_{11} - 1) -0.245 \cdot (s_{12} - 1) -0.245 \cdot (s_{13} - 1) -0.245 \cdot (s_{14} - 1) \leq 10 & \qquad \text{(l = 16)}\\
 \end{align}
$$ 

In addition to the flow constraints, we need to make sure that the total generation equals total load for the system.

$$
 \begin{align}
  p_1 + p_2 + p_3 + p_4 + p_5 + s_2 + s_3 + s_4 + s_5 + s_6 + s_9 + s_{10} + s_{11} + s_{12} + s_{13} + s_{14} = 11\\
 \end{align}
$$ 

On the other hand, for the B-theta formulation, we explictly enforce the power balance for each node.

$$
 \begin{align}
  p_1 - f_{1} - f_{2} = 0 & \qquad \text{(b = 1)}\\
  p_2 + f_{1} - f_{3} - f_{4} - f_{5} + s_{2} = 1 & \qquad \text{(b = 2)}\\
  p_3 + f_{3} - f_{6} + s_{3} = 1 & \qquad \text{(b = 3)}\\
  f_{4} + f_{6} - f_{7} - f_{8} - f_{9} + s_{4} = 1 & \qquad \text{(b = 4)}\\
  f_{2} + f_{5} f_{7} - f_{10} + s_{5} = 1 & \qquad \text{(b = 5)}\\
  p_4 + f_{10} - f_{11} - f_{12} + s_{6} = 1 & \qquad \text{(b = 6)}\\
  f_{8} - f_{13} - f_{14} = 0 & \qquad \text{(b = 7)}\\
  p_5 + f_{13} = 0 & \qquad \text{(b = 8)}\\
  f_{9} f_{14} - f_{15} + s_{9} = 1 & \qquad \text{(b = 9)}\\
  f_{15} - f_{16} + s_{10} = 1 & \qquad \text{(b = 10)}\\
  f_{11} + f_{16} + s_{11} = 1 & \qquad \text{(b = 11)}\\
  f_{12} - f_{17} + s_{12} = 1 & \qquad \text{(b = 12)}\\
  f_{17} - f_{18} + s_{13} = 1 & \qquad \text{(b = 13)}\\
  f_{18} + s_{14} = 1 & \qquad \text{(b = 14)}\\
 \end{align}
$$ 

Where $p$ are generation outputs, $f$ are flows in the branches, and $s$ are slack variables that account for shortage of generation.

For this formulation, the flow expressions and their respective limits are as follows.

$$
 \begin{align}
   f_{l} - 10 \cdot \left( \theta_{\text{from}(l)} - \theta_{\text{to}(l)} \right)= 0 & \qquad \forall l \in \mathcal {L}\\
   {-}10 \leq f_{l} \leq 10                                                           & \qquad \forall l \in \\{4, 13, 14\\}\\
   {-}inf \leq f_{l} \leq inf                                                         & \qquad \forall l \in \mathcal {L} \setminus \\{4, 13, 14\\}\\
 \end{align}
$$ 

The above formulations are used when the network is not reduced. That is, for the full network, or original system.
As the network is reduced, nodes, branches and slack variables are eliminated from the model. Thus reflecting in changes both in the B-theta and the PTDF formulations

## Reduced network

Below we show the step-by-step transformation that these formulations undergo as the network is reduced.

### Removal of node 8

For this system, our algorithm firstly removes node 8. This node is connected to the rest of the system through a single, and it is one branch that is possibly binding. Furthermore, generator G5 is connected to node 8. Hence, after removing this, we need to ensure that the limits of the branch removed with it, branch 13, is still enforced in the reduced network, and we need to properly reassign the generation of G5.

<img src="https://drive.google.com/uc?id=1LcOv0M03y0jnhgyNAC1PI652LDjj9nh9"
     alt="network after removing node 8"
     style="width: 50%" />

In the B-theta formulation, in addition to removing the constraints associated with node 8 and branch 13, the power balance constraint of node 7 now becomes

$$
 \begin{align}
  p_{5} + f_{8} - f_{14} = 0 & \\
 \end{align}
$$ 

In our strategy, because the limits of branch 13 are possibly binding but it has been removed, its limits are now enforced on the injections connected to the node being deleted.
For branch 13, this simply means enforcing its limits on the generation of G5.

$$
 \begin{align}
  p_{5} \leq 10 & \\
 \end{align}
$$ 

For this particular node deletion, nothing changes for the PTDF formulation.
     
### Removal of nodes 14, 13 and 12

The next step is to remove node 14. This is a load node also connected to the rest of the network through a single branch. Different from node 8, however, the branch connecting node 14 is not possibly binding. Thus, all we need to do is carefully reassign the load then connected to node 14. Because it was connected by a single branch, all injections of node 14 are then reassigned to the node that it was connected to: node 13. Thus, node 13 now receives an additional 1 p.u. load.

<img src="https://drive.google.com/uc?id=1Lcy_0DmHGwouK4NUKiUBlCb3PQNwrA0B"
     alt="network after removing node 14"
     style="width: 50%" />

For the B-theta formulation, removing node 14, in addition to removing the variables and constraints associated with it and with the branch deleted, boils down to modifying the power balance constraint of node 13 as follows.

$$
 \begin{align}
  f_{17} + s_{13} = 2 & \\
 \end{align}
$$ 

For the PTDF formulation, in addition to relocating the load, we need to remember to remove the slack variables previously associated with node 14 from the flow expressions, as follows.

$$
 \begin{align}
  {-}10 \leq -0.103 \cdot p_1 -0.23 \cdot (p_3 + s_3 - 1)  -0.461 \cdot (s_4 - 1 ) -0.206 \cdot (s_5 - 1) -0.261 \cdot (p_4 + s_6 - 1) -0.442 \cdot p_5 -0.424 \cdot (s_9 - 1) -0.37 \cdot (s_{10} - 1) -0.315 \cdot (s_{11} - 1) -0.261 \cdot (s_{12} - 1) -0.261 \cdot (s_{13} - 2) \leq 10 & \qquad \text{(l = 4)}\\
    {-}10 \leq - p_5 \leq 10 & \qquad \text{(l = 13)}\\
    {-}10 \leq -0.009 \cdot p_1  +  0.009 \cdot (p_3 + s_3 - 1) +  0.018 \cdot (s_4 - 1 )  -0.018 \cdot (s_5 - 1) -0.082 \cdot (p_4 + s_6 - 1) + 0.373 \cdot p_5 -0.273 \cdot (s_9 - 1) -0.209 \cdot (s_{10} - 1) -0.145 \cdot (s_{11} - 1) -0.082 \cdot (s_{12} - 1) -0.082 \cdot (s_{13} - 2)  \leq 10 & \qquad \text{(l = 14)}\\
    {-}10 \leq -0.027 \cdot p_1 +  0.027 \cdot (p_3 + s_3 - 1) +  0.055 \cdot (s_4 - 1 ) -0.055 \cdot (s_5 - 1) -0.245 \cdot (p_4 + s_6 - 1) + 0.118 \cdot p_5 + 0.182 \cdot (s_9 - 1) + 0.373 \cdot (s_{10} - 1) -0.436 \cdot (s_{11} - 1) -0.245 \cdot (s_{12} - 1) -0.245 \cdot (s_{13} - 2)  \leq 10 & \qquad \text{(l = 16)}\\
 \end{align}
$$ 

Naturally, the slack variable associated with the deleted node 14 also needs to be removed from the global balance equation.

$$
 \begin{align}
  p_1 + p_2 + p_3 + p_4 + p_5 + s_2 + s_3 + s_4 + s_5 + s_6 + s_9 + s_{10} + s_{11} + s_{12} + s_{13} = 11\\
 \end{align}
$$ 

This same procedure is then applied to node 13 and then to node 12, which results in the reduced network shown below.

<img src="https://drive.google.com/uc?id=1LdnHoQOPfKnn8tkLRzie0cRDdf0eTFjW"
     alt="network after removing nodes 14, 13 and 12"
     style="width: 50%" />

After these steps, the loads originally located at 14, 13 and 12 are placed at node 6, whose power balance equation becomes

$$
 \begin{align}
  p_4 + f_{10} - f_{11} - f_{12} + s_{6} = 4. & \qquad \\
 \end{align}
$$ 

For the PTDF formulation, the reduced network now has the following constraints.

$$
 \begin{align}
  {-}10 \leq -0.103 \cdot p_1 -0.23 \cdot (p_3 + s_3 - 1)  -0.461 \cdot (s_4 - 1 ) -0.206 \cdot (s_5 - 1) -0.261 \cdot (p_4 + s_6 - 4) -0.442 \cdot p_5 -0.424 \cdot (s_9 - 1) -0.37 \cdot (s_{10} - 1) -0.315 \cdot (s_{11} - 1) \leq 10 & \qquad \text{(l = 4)}\\
    {-}10 \leq - p_5 \leq 10 & \qquad \text{(l = 13)}\\
    {-}10 \leq -0.009 \cdot p_1  +  0.009 \cdot (p_3 + s_3 - 1) +  0.018 \cdot (s_4 - 1 )  -0.018 \cdot (s_5 - 1) -0.082 \cdot (p_4 + s_6 - 4) + 0.373 \cdot p_5 -0.273 \cdot (s_9 - 1) -0.209 \cdot (s_{10} - 1) -0.145 \cdot (s_{11} - 1)   \leq 10 & \qquad \text{(l = 14)}\\
    {-}10 \leq -0.027 \cdot p_1 +  0.027 \cdot (p_3 + s_3 - 1) +  0.055 \cdot (s_4 - 1 ) -0.055 \cdot (s_5 - 1) -0.245 \cdot (p_4 + s_6 - 4) + 0.118 \cdot p_5 + 0.182 \cdot (s_9 - 1) + 0.373 \cdot (s_{10} - 1) -0.436 \cdot (s_{11} - 1) \leq 10 & \qquad \text{(l = 16)}\\
 \end{align}
$$ 

and

$$
 \begin{align}
  p_1 + p_2 + p_3 + p_4 + p_5 + s_2 + s_3 + s_4 + s_5 + s_6 + s_9 + s_{10} + s_{11} = 11.\\
 \end{align}
$$ 

### Removal of node 10

The next node removed is node 10. Different from the previous nodes deleted, node 10 is connected to two branches and one of them is possibly them. Removing node 10 then divides its injection between the nodes it was connected to (11 and 9), and creates a new branch between these nodes (branch 19). The amount of injection of node 10 that goes to 9 and the amount that goes to 11, as well as the reactance and limits of the new branch, depend on the reactances of the branches then connecting node 10. The new branch's limits, in fact, are also dependent on the injection of node 10.

<img src="https://drive.google.com/uc?id=1LRvhjhHniwASSGwo-DSSqEHEpwnCCT50"
     alt="network after removing node 10"
     style="width: 50%" />

B-theta:

$$
 \begin{align}
  f_{9} f_{14} - f_{15} + s_{9} = 1.5 & \qquad \text{(b = 9)}\\
  f_{11} + f_{16} + s_{11} = 1.5 & \qquad \text{(b = 11)}\\
 \end{align}
$$ 

$$
 \begin{align}
   f_{19} - 5 \cdot \left( \theta_{9} - \theta_{11} \right)= 0 & \qquad\\
   {-}9.5 \leq f_{19} \leq 10.5                                 & \qquad \\
 \end{align}
$$ 

PTDF:

$$
 \begin{align}
  {-}10 \leq -0.103 \cdot p_1 -0.23 \cdot (p_3 + s_3 - 1)  -0.461 \cdot (s_4 - 1 ) -0.206 \cdot (s_5 - 1) -0.261 \cdot (p_4 + s_6 - 4) -0.442 \cdot p_5 -0.424 \cdot (s_9 - 1.5) -0.315 \cdot (s_{11} - 1.5) \leq 10 & \qquad \text{(l = 4)}\\
    {-}10 \leq - p_5 \leq 10 & \qquad \text{(l = 13)}\\
    {-}10 \leq -0.009 \cdot p_1  +  0.009 \cdot (p_3 + s_3 - 1) +  0.018 \cdot (s_4 - 1 )  -0.018 \cdot (s_5 - 1) -0.082 \cdot (p_4 + s_6 - 4) + 0.373 \cdot p_5 -0.273 \cdot (s_9 - 1.5) -0.145 \cdot (s_{11} - 1.5)   \leq 10 & \qquad \text{(l = 14)}\\
    {-}9.5 \leq -0.027 \cdot p_1  + 0.027 \cdot (p_3 + s_3 - 1) + 0.055 \cdot (s_4 - 1 ) -0.055 \cdot (s_5 - 1) -0.245 \cdot (p_4 + s_6 - 4) + 0.118 \cdot p_5 + 0.182  \cdot (s_9 - 1.5) -0.436 \cdot (s_{11} - 1.5) \leq 10.5 & \qquad \text{(l = 19)}\\
 \end{align}
$$ 

and

$$
 \begin{align}
  p_1 + p_2 + p_3 + p_4 + p_5 + s_2 + s_3 + s_4 + s_5 + s_6 + s_9 + s_{11} = 11\\
 \end{align}
$$ 
     
### Removal of node 11

By following the same procedure applied to node 10, we can safely remove node 11 and reduce the network to the one shown below.

<img src="https://drive.google.com/uc?id=1LfU_K9SoSVe3UqISsYKq3W7YMgP8pQvl"
     alt="network after removing node 11"
     style="width: 50%" />

### Removal of node 1

Then, we further reduce the network by deleting node 1. This node is connected to two branches but it has one generator connected to it. Naturally, the generation from G1 is then split between nodes 2 and 5, according to the reactances of the branches between deleted.

<img src="https://drive.google.com/uc?id=1LXdOFH8ZGXO8rjS_NYYVwKcSUC4f7vrm"
     alt="original system"
     style="width: 50%" />

Note that the only thing that changes is that the generator now simultaneously injects power into two nodes. However, its total power injection is still the same: the injection has only been fractioned among more nodes. Furthermore, from the point-of-view of the generator, its model remains unchanged.

$$
 \begin{align}
  0.5 \cdot p_1 + p_2 - f_3 - f_4 - f_{21} + s_{2} = 1 & \qquad \text{(b = 2)}\\
  0.5 \cdot p_1 + f_7 + f_{21} - f_{10} + s_{5} = 1 & \qquad \text{(b = 5)}\\
 \end{align}
$$ 

$$
 \begin{align}
   f_{21} - 15 \cdot \left( \theta_{2} - \theta_{5} \right)= 0 & \qquad \\
   {-}inf \leq f_{21} \leq inf                                 & \qquad \\
 \end{align}
$$ 

$$
 \begin{align}
  {-}10 \leq -0.23 \cdot (p_3 + s_3 - 1)  -0.461 \cdot (s_4 - 1 ) -0.206 \cdot (0.5 \cdot p_1 + s_5 - 1) -0.261 \cdot (p_4 + s_6 - 5) -0.442 \cdot p_5 -0.424 \cdot (s_9 - 2) \leq 10 & \qquad \text{(l = 4)}\\
    {-}10 \leq - p_5 \leq 10 & \qquad \text{(l = 13)}\\
    {-}10 \leq  0.009 \cdot (p_3 + s_3 - 1) +  0.018 \cdot (s_4 - 1 )  -0.018 \cdot (0.5 \cdot p_1 + s_5 - 1) -0.082 \cdot (p_4 + s_6 - 5) + 0.373 \cdot p_5 -0.273 \cdot (s_9 - 2) \leq 10 & \qquad \text{(l = 14)}\\
    {-}9.5 \leq 0.027 \cdot (p_3 + s_3 - 1) + 0.055 \cdot (s_4 - 1 ) -0.055 \cdot (0.5 \cdot p_1 + s_5 - 1) -0.245 \cdot (p_4 + s_6 - 5) + 0.118 \cdot p_5 + 0.182  \cdot (s_9 - 2)  \leq 10.5 & \qquad \text{(l = 20)}\\
 \end{align}
$$ 

and

$$
 \begin{align}
  p_1 + p_2 + p_3 + p_4 + p_5 + s_2 + s_3 + s_4 + s_5 + s_6 + s_9 = 11\\
 \end{align}
$$ 

### Removal of node 3

The same steps applied to node 1 are replicated to node 3, with the exception that the new branch between nodes 2 and 4 is parallel to a existing branch, which happens to be possibly binding.

<img src="https://drive.google.com/uc?id=1LPazOYuVSXWQ9pRd4m2bqPIZwhLNCe5C"
     alt="original system"
     style="width: 50%" />

In this scenario, the limits of the new branch 22 are defined by the maximum angular difference that could be applied to branch 4. The result is a lower bound of -15 p.u. and an upper bound of 15 p.u..

$$
 \begin{align}
  0.5 \cdot p_1 + p_2 + 0.5 \cdot p_3 - f_{21} - f_{22} + s_{2} = 1.5 & \qquad \text{(b = 2)}\\
  0.5 \cdot p_1 + 0.5 \cdot p_3 + f_{22} - f_{7} - f_8 - f_9 + s_{4} = 1.5 & \qquad \text{(b = 4)}\\
 \end{align}
$$ 

$$
 \begin{align}
   f_{22} - 15 \cdot \left( \theta_{2} - \theta_{4} \right)= 0 & \qquad\\
   {-}15 \leq f_{22} \leq 15                                 & \qquad \\
 \end{align}
$$ 

PTDF:
 
$$
 \begin{align}
    {-}10 \leq - p_5 \leq 10 & \qquad \text{(l = 13)}\\
    {-}10 \leq  0.018 \cdot (0.5 \cdot p_3 +s_4 -1.5) - 0.018 \cdot (0.5 \cdot p_1 +s_5-1) - 0.082 \cdot ( p_4+s_6-5) + 0.373 \cdot p_5 - 0.273 \cdot (s_9 -2) \leq 10 & \qquad \text{(l = 14)}\\
    {-}9.5 \leq -0.055 \cdot (0.5 \cdot p_3+s_4-1.5) + 0.055 \cdot (0.5 \cdot p_1 +s_5-1) + 0.245 \cdot (p_4+s_6-5) -0.118 \cdot p_5 -0.182 \cdot (s_9-2) \leq 10.5 & \qquad \text{(l = 20)}\\
  {-}15 \leq -0.691 \cdot (0.5 \cdot p_3+s_4-1.5) -0.309 \cdot (0.5 \cdot p_1 +s_5-1) -0.391 \cdot (p_4+s_6-5) -0.664 \cdot p_5 -0.636 \cdot (s_9-2) \leq 15 & \qquad \text{(l = 22)}\\
 \end{align}
$$ 

and

$$
 \begin{align}
  p_1 + p_2 + p_3 + p_4 + p_5 + s_2 + s_4 + s_5 + s_6 + s_9 = 11\\
 \end{align}
$$ 

### Removal of node 5

<img src="https://drive.google.com/uc?id=1LTk_OrofAhIQXy5yuQuJulZViqpcZw5q"
     alt="original system"
     style="width: 50%" />

B-theta:

$$
 \begin{align}
  0.72 \cdot p_1 + p_2 + 0.5 \cdot p_3 + f_{1} - f_{3} - f_{4} - f_{5} + s_{2} = 1.93 & \qquad \text{(b = 2)}\\
  0.14 \cdot p_1  + 0.5 \cdot p_3 + f_{4} + f_{6} - f_{7} - f_{8} - f_{9} + s_{4} = 1.79 & \qquad \text{(b = 4)}\\
  0.14 \cdot p_1 + p_4 + f_{10} - f_{11} - f_{12} + s_{6} = 5.28 & \qquad \text{(b = 6)}\\
  p_5 + f_{8} - f_{13} - f_{14} = 0 & \qquad \text{(b = 7)}\\
  f_{9} + f_{14} - f_{15} + s_{9} = 2 & \qquad \text{(b = 9)}\\
 \end{align}
$$ 

$$
 \begin{align}
   f_{8} - 10 \cdot ( \theta_{4} - \theta_{7} )= 0 & \qquad \\
   f_{9} - 10 \cdot ( \theta_{4} - \theta_{9} )= 0 & \qquad \\
   f_{14} - 10 \cdot ( \theta_{7} - \theta_{9} )= 0 & \qquad \\
   f_{20} - 3.333 \cdot ( \theta_{6} - \theta_{9} )= 0 & \qquad \\
   f_{23} - 19.286 \cdot ( \theta_{2} - \theta_{4} )= 0 & \qquad \\
   f_{24} - 4.286 \cdot ( \theta_2 - \theta_{6} )= 0 & \qquad \\
   f_{25} - 2.857 \cdot ( \theta_{4} - \theta_{6})= 0 & \qquad \\
   {-}inf \leq f_{8} \leq inf                                        & \qquad \\
   {-}inf \leq f_{9} \leq inf                                        & \qquad \\
   {-}10 \leq f_{14} \leq 10                                        & \qquad \\
   {-}10 \leq f_{20} \leq 10                                        & \qquad \\
   {-}19.286 \leq f_{23} \leq 19.286                             & \qquad \\
   {-}inf \leq f_{24} \leq inf                                        & \qquad \\
   {-}inf \leq f_{25} \leq inf                                        & \qquad \\
 \end{align}
$$

PTDF:

$$
 \begin{align}
    {-}10 \leq - p_5 \leq 10 & \qquad \text{(l = 13)}\\
    {-}10 \leq  0.018 \cdot (0.14 \cdot p_1  + 0.5 \cdot p_3 + s_{4} - 1.79) - 0.082 \cdot (0.14 \cdot p_1 + p_4 + s_{6} - 5.28) + 0.373 \cdot p_5 - 0.273 \cdot (s_{9} - 2) \leq 10 & \qquad \text{(l = 14)}\\
    {-}10 \leq  -0.055 \cdot (0.14 \cdot p_1  + 0.5 \cdot p_3 + s_{4} - 1.79) + 0.245 \cdot (0.14 \cdot p_1 + p_4 + s_{6} - 5.28) - 0.118 \cdot p_5 - 0.182 \cdot (s_{9} - 2) \leq 10 & \qquad \text{(l = 20)}\\
  {-}19.286 \leq  -0.888 \cdot (0.14 \cdot p_1  + 0.5 \cdot p_3 + s_{4} - 1.79) - 0.503 \cdot (0.14 \cdot p_1 + p_4 + s_{6} - 5.28) -0.853 \cdot p_5 - 0.818 \cdot (s_{9} - 2) \leq 19.286 & \qquad \text{(l = 23)}\\
 \end{align}
$$ 

$$
 \begin{align}
  p_1 + p_2 + p_3 + p_4 + p_5 + s_2 + s_4 + s_6 + s_9 = 11\\
 \end{align}
$$ 

 
