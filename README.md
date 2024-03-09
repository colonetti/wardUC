# Under construction

We intend to show some of the most important features of our algorithm with this example. Hence, in this example, we follow the same steps taken in the algorithm.
If you wish, you can follow the same steps by debugging our code with your favorite IDE.

The first thing we want to show is how the network model looks like when no reduction is used. 
Thus, we have the complete power transfer distribution factors (PTDF) matrix below. 

$$
 PTDF =     \begin{bmatrix}
              0.615&  0  &  0.052&  0.103&  0.23 &  0.203&  0.112&  0.112& 0.121&  0.148&  0.176&  0.203&  0.203&  0.203\\
              0.385&  0  & -0.052& -0.103& -0.23 & -0.203& -0.112& -0.112& -0.121& -0.148& -0.176& -0.203& -0.203& -0.203\\
             -0.052&  0  & -0.615& -0.23 & -0.103& -0.13 & -0.221& -0.221& -0.212& -0.185& -0.158& -0.13 & -0.13 & -0.13 \\
             -0.103&  0  & -0.23 & -0.461& -0.206& -0.261& -0.442& -0.442& -0.424& -0.37 & -0.315& -0.261& -0.261& -0.261\\
             -0.23 &  0  & -0.103& -0.206& -0.461& -0.406& -0.224& -0.224& -0.242& -0.297& -0.352& -0.406& -0.406& -0.406\\
             -0.052&  0  &  0.385& -0.23 & -0.103& -0.13 & -0.221& -0.221& -0.212& -0.185& -0.158& -0.13 & -0.13 & -0.13 \\
             -0.127&  0  &  0.127&  0.255& -0.255& -0.145&  0.218&  0.218& 0.182&  0.073& -0.036& -0.145& -0.145& -0.145\\
             -0.009&  0  &  0.009&  0.018& -0.018& -0.082& -0.627& -0.627& -0.273& -0.209& -0.145& -0.082& -0.082& -0.082\\
             -0.018&  0  &  0.018&  0.036& -0.036& -0.164& -0.255& -0.255& -0.545& -0.418& -0.291& -0.164& -0.164& -0.164\\
              0.027&  0  & -0.027& -0.055&  0.055& -0.755& -0.118& -0.118& -0.182& -0.373& -0.564& -0.755& -0.755& -0.755\\
              0.027&  0  & -0.027& -0.055&  0.055&  0.245& -0.118& -0.118& -0.182& -0.373& -0.564&  0.245&  0.245&  0.245\\
              0  &  0  &  0  &  0  &  0  &  0  &  0  &  0  & 0  &  0  &  0  & -1  & -1  & -1  \\
              0  &  0  &  0  &  0  &  0  &  0  & 0 & -1  & 0  & 0 & 0 & 0 & 0 & 0 \\
             -0.009&  0  &  0.009&  0.018& -0.018& -0.082&  0.373&  0.373& -0.273& -0.209& -0.145& -0.082& -0.082& -0.082\\
             -0.027&  0  &  0.027&  0.055& -0.055& -0.245&  0.118&  0.118& 0.182& -0.627& -0.436& -0.245& -0.245& -0.245\\
             -0.027&  0  &  0.027&  0.055& -0.055& -0.245&  0.118&  0.118& 0.182&  0.373& -0.436& -0.245& -0.245& -0.245\\
              0  &  0  & 0 & 0 &  0  &  0  &  0  &  0  & 0  &  0  &  0  &  0  & -1  & -1  \\
             0 &  0  &  0  &  0  & 0 &  0  & 0 & 0 & 0  &  0  &  0  &  0  & 0 & -1  \\
           \end{bmatrix}
$$

In our code, this matrix is computed in https://github.com/colonetti/ward_UC_pscc2024/blob/e71b4caff9d4ca70743ca9296af9262a6ec3dfd7/pre_processing/build_ptdf.py#L148.
You can also see the computation for this particular example in [LINK_TO_THE_CODE_EX.PY]

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
  p_1 + p_2 + p_3 + p_4 + p_5 + s_2 + s_3 + s_4 + s_5 + s_6 + s_9 + s_10 + s_11 + s_12 + s_13 + s_14 = 11\\
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

And we need to gurantee that the flows are within their limits.

$$
 \begin{align}
   f_{l} - 10 \cdot \left( \theta_{\text{from}(l)} - \theta_{\text{to}(l)} \right)= 0 & \qquad \forall l \in \mathcal {L}\\
   {-}10 \leq f_{l} \leq 10                                                           & \qquad \forall l \in \\{4, 13, 14\\}\\
   {-}inf \leq f_{l} \leq inf                                                         & \qquad \forall l \in \mathcal {L} \setminus \\{4, 13, 14\\}\\
 \end{align}
$$ 


### Removal of node 8

### Removal of nodes 14, 13 and 12

### Removal of node 10

### Removal of node 11

### Removal of node 1

### Removal of node 3

### Removal of node 5

After the first iteration:
$$\mathcal{B} = \mathcal{B} \setminus \\{8, 14\\}$$
$$\mathcal{L} = \mathcal{L} \setminus \\{13, 18\\}$$

$$
 \begin{align}
  \sum_{g \in \mathcal{G}\_{b}}p_{g} - \sum_{l \in \mathcal{L}^{-}}f_{l} + \sum_{l \in \mathcal{L}^{+}}f_{l} + s_{b} = \mathrm{\mathbf{D}}\_{b}& \qquad \forall b \in \mathcal{B} \setminus \\{7, 13\\}\\
  p_{5} + f_{8} - f_{14} = 0 & \\
  f_{17} + s_{13} = 1 + 1 & \\
 \end{align}
$$ 

$$
 \begin{align}
  p_{5} \leq 10 & \\
 \end{align}
$$ 

$$
 \begin{align}
   f_{l} - 10 \cdot \left( \theta_{\text{from}(l)} - \theta_{\text{to}(l)} \right)= 0 & \qquad \forall l \in \mathcal {L}\\
   {-}10 \leq f_{l} \leq 10                                                           & \qquad \forall l \in \\{4, 14\\}\\
   {-}inf \leq f_{l} \leq inf                                                         & \qquad \forall l \in \mathcal {L} \setminus \\{4, 14\\}\\
 \end{align}
$$ 

$$
 \begin{align}
  {-}10 \leq 0.103 \cdot \left(p_2 + s_2 - 1 \right)  -0.1273 \cdot  \left(p_3 + s_3 - 1 \right) -0.3576 \cdot \left(s_4 - 1 \right) -0.103 \cdot \left(s_5 - 1 \right) -0.1576 \cdot \left(p_4 + s_6 - 1 \right) -0.3394 \cdot p_5 -0.3212 \cdot \left(s_9 - 1 \right) -0.2667\cdot \left(s_{10} - 1 \right) -0.2121\cdot \left(s_{11} - 1 \right) -0.1576\cdot \left(s_{12} - 1 \right) -0.1576\cdot \left(s_{13} - 2 \right)  \leq 10 & \qquad \text{(l = 4)}\\
    {-}10 \leq 0.0091 \cdot \left(p_2 + s_2 - 1 \right) + 0.0182 \cdot  \left(p_3 + s_3 - 1 \right) + 0.0273 \cdot \left(s_4 - 1 \right) -0.0091 \cdot \left(s_5 - 1 \right) -0.0727 \cdot \left(p_4 + s_6 - 1 \right) + 0.3818 \cdot p_5 -0.2636 \cdot \left(s_9 - 1 \right) -0.2\cdot \left(s_{10} - 1 \right) -0.1364\cdot \left(s_{11} - 1 \right) -0.0727\cdot \left(s_{12} - 1 \right) -0.0727\cdot \left(s_{13} - 2 \right)  \leq 10 & \qquad \text{(l = 14)}\\
    {-}10 \leq 0.0273 \cdot \left(p_2 + s_2 - 1 \right) + 0.0545 \cdot  \left(p_3 + s_3 - 1 \right) + 0.0818 \cdot \left(s_4 - 1 \right) -0.0273 \cdot \left(s_5 - 1 \right) -0.2182 \cdot \left(p_4 + s_6 - 1 \right) + 0.1455 \cdot p_5 + 0.2091 \cdot \left(s_9 - 1 \right) + 0.4\cdot \left(s_{10} - 1 \right) -0.4091\cdot \left(s_{11} - 1 \right) -0.2182\cdot \left(s_{12} - 1 \right) -0.2182\cdot \left(s_{13} - 2 \right)  \leq 10 & \qquad \text{(l = 16)}\\
 \end{align}
$$ 

After the second iteration:
$$\mathcal{B} = \mathcal{B} \setminus \\{13\\}$$
$$\mathcal{L} = \mathcal{L} \setminus \\{17\\}$$

After the third iteration:
$$\mathcal{B} = \mathcal{B} \setminus \\{12\\}$$
$$\mathcal{L} = \mathcal{L} \setminus \\{12\\}$$

$$
 \begin{align}
  \sum_{g \in \mathcal{G}\_{b}}p_{g} - \sum_{l \in \mathcal{L}^{-}}f_{l} + \sum_{l \in \mathcal{L}^{+}}f_{l} + s_{b} = \mathrm{\mathbf{D}}\_{b}& \qquad \forall b \in \mathcal{B} \setminus \\{6, 7\\}\\
  p_{4} + f_{10} - f_{11} + s_{6} = 4 & \\
  p_{5} + f_{8} - f_{14} = 0 & \\
 \end{align}
$$ 

$$
 \begin{align}
  p_{5} \leq 10 & \\
 \end{align}
$$ 

$$
 \begin{align}
   f_{l} - 10 \cdot \left( \theta_{\text{from}(l)} - \theta_{\text{to}(l)} \right)= 0 & \qquad \forall l \in \mathcal {L}\\
   {-}10 \leq f_{l} \leq 10                                                           & \qquad \forall l \in \\{4, 14\\}\\
   {-}inf \leq f_{l} \leq inf                                                         & \qquad \forall l \in \mathcal {L} \setminus \\{4, 14\\}\\
 \end{align}
$$ 

$$
 PTDF =     \begin{bmatrix}
              0 & -0.615 & -0.23 & -0.103 & -0.13 & -0.221 & -0.212 & -0.185 & -0.158\\
              0 & -0.23 & -0.461 & -0.206 & -0.261 & -0.442 & -0.424 & -0.37 & -0.315\\
              0 & 0.385 & -0.23 & -0.103 & -0.13 & -0.221 & -0.212 & -0.185 & -0.158\\
              0 & 0.127 & 0.255 & -0.255 & -0.145 & 0.218 & 0.182 & 0.073 & -0.036\\
              0 & 0.009 & 0.018 & -0.018 & -0.082 & -0.627 & -0.273 & -0.209 & -0.145\\
              0 & 0.018 & 0.036 & -0.036 & -0.164 & -0.255 & -0.545 & -0.418 & -0.291\\
              0 & -0.027 & -0.055 & 0.055 & -0.755 & -0.118 & -0.182 & -0.373 & -0.564\\
              0 & -0.027 & -0.055 & 0.055 & 0.245 & -0.118 & -0.182 & -0.373 & -0.564\\
              0 & 0.009 & 0.018 & -0.018 & -0.082 & 0.373 & -0.273 & -0.209 & -0.145\\
              0 & 0.027 & 0.055 & -0.055 & -0.245 & 0.118 & 0.182 & -0.627 & -0.436\\
              0 & 0.027 & 0.055 & -0.055 & -0.245 & 0.118 & 0.182 & 0.373 & -0.436\\
              0 & -0.155 & -0.309 & -0.691 & -0.609 & -0.336 & -0.364 & -0.445 & -0.527\\
           \end{bmatrix}
$$



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

