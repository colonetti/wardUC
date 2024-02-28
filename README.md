# Under construction

$$
 \begin{align}
  \sum_{g \in \mathcal{G}\_{b}}p_{g} - \sum_{l \in \mathcal{L}^{-}}f_{l} + \sum_{l \in \mathcal{L}^{+}}f_{l} + s_{b} = \mathrm{\mathbf{D}}_{b} & \qquad \forall b \in \mathcal {B}\\
 \end{align}
$$ 

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

$$
 \begin{align}
  {-}10 \leq 0.103 \cdot \left(p_2 + s_2 - 1 \right)  -0.1273 \cdot  \left(p_3 + s_3 - 1 \right) -0.3576 \cdot \left(s_4 - 1 \right) -0.103 \cdot \left(s_5 - 1 \right) -0.1576 \cdot \left(p_4 + s_6 - 1 \right) -0.3394 \cdot p_5 -0.3212 \cdot \left(s_9 - 1 \right) -0.2667\cdot \left(s_{10} - 1 \right) -0.2121\cdot \left(s_{11} - 1 \right) -0.1576\cdot \left(s_{12} - 1 \right) -0.1576\cdot \left(s_{13} - 1 \right) -0.1576 \cdot \left(s_{14} - 1 \right) \leq 10 & \qquad \text{(l = 4)}\\
    {-}10 \leq - p_5 \leq 10 & \qquad \text{(l = 13)}\\
    {-}10 \leq 0.0091 \cdot \left(p_2 + s_2 - 1 \right) + 0.0182 \cdot  \left(p_3 + s_3 - 1 \right) + 0.0273 \cdot \left(s_4 - 1 \right) -0.0091 \cdot \left(s_5 - 1 \right) -0.0727 \cdot \left(p_4 + s_6 - 1 \right) + 0.3818 \cdot p_5 -0.2636 \cdot \left(s_9 - 1 \right) -0.2\cdot \left(s_{10} - 1 \right) -0.1364\cdot \left(s_{11} - 1 \right) -0.0727\cdot \left(s_{12} - 1 \right) -0.0727\cdot \left(s_{13} - 1 \right) -0.0727 \cdot \left(s_{14} - 1 \right) \leq 10 & \qquad \text{(l = 14)}\\
    {-}10 \leq 0.0273 \cdot \left(p_2 + s_2 - 1 \right) + 0.0545 \cdot  \left(p_3 + s_3 - 1 \right) + 0.0818 \cdot \left(s_4 - 1 \right) -0.0273 \cdot \left(s_5 - 1 \right) -0.2182 \cdot \left(p_4 + s_6 - 1 \right) + 0.1455 \cdot p_5 + 0.2091 \cdot \left(s_9 - 1 \right) + 0.4\cdot \left(s_{10} - 1 \right) -0.4091\cdot \left(s_{11} - 1 \right) -0.2182\cdot \left(s_{12} - 1 \right) -0.2182\cdot \left(s_{13} - 1 \right) -0.2182 \cdot \left(s_{14} - 1 \right) \leq 10 & \qquad \text{(l = 16)}\\
 \end{align}
$$ 

$$
 \begin{align}
   f_{l} - 10 \cdot \left( \theta_{\text{from}(l)} - \theta_{\text{to}(l)} \right)= 0 & \qquad \forall l \in \mathcal {L}\\
   {-}10 \leq f_{l} \leq 10                                                           & \qquad \forall l \in \\{4, 13, 14\\}\\
   {-}inf \leq f_{l} \leq inf                                                         & \qquad \forall l \in \mathcal {L} \setminus \\{4, 13, 14\\}\\
 \end{align}
$$ 

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

After the third iteration:
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
 A = \begin{bmatrix}
          1 & -1 & 0  & 0  &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 & 0\\ 
          1 & 0  &  0 &  0 & -1 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 & 0\\ 
          0 & 1  & -1 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 & 0\\  
          0 & 1  &  0 & -1 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 & 0\\ 
          0 & 1  &  0 &  0 & -1 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 & 0\\ 
          0 & 0  &  1 & -1 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 & 0\\ 
          0 & 0  &  0 &  1 & -1 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 & 0\\ 
          0 & 0  &  0 &  1 &  0 &  0 & -1 &  0 &  0 &  0 &  0 &  0 &  0 & 0\\ 
          0 & 0  &  0 &  1 &  0 &  0 &  0 &  0 & -1 &  0 &  0 &  0 &  0 & 0\\ 
          0 & 0  &  0 &  0 &  1 & -1 &  0 &  0 &  0 &  0 &  0 &  0 &  0 & 0\\
          0 & 0  &  0 &  0 &  0 &  1 &  0 &  0 &  0 &  0 & -1 &  0 &  0 & 0\\ 
          0 & 0  &  0 &  0 &  0 &  1 &  0 &  0 &  0 &  0 &  0 & -1 &  0 & 0\\ 
          0 & 0  &  0 &  0 &  0 &  0 &  1 & -1 &  0 &  0 &  0 &  0 &  0 & 0\\ 
          0 & 0  &  0 &  0 &  0 &  0 &  1 &  0 & -1 &  0 &  0 &  0 &  0 & 0\\ 
          0 & 0  &  0 &  0 &  0 &  0 &  0 &  0 &  1 & -1 &  0 &  0 &  0 & 0\\ 
          0 & 0  &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  1 & -1 &  0 &  0 & 0\\
          0 & 0  &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  1 & -1 & 0\\ 
          0 & 0  &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  0 &  1 &-1\\ 
     \end{bmatrix} 
$$

$$ 
 Y = diag(\begin{bmatrix}
          10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 & 10 \\
         \end{bmatrix}) 
$$

$$
 B = A ^ \top \cdot (Y \cdot A)
$$

$$
 PTDF = (Y \cdot A) \cdot \hat{B} 
$$

$$
 PTDF =     \begin{bmatrix}
               0   & -0.6152& -0.5636& -0.5121& -0.3848& -0.4121& -0.503 & -0.503 & -0.4939& -0.4667& -0.4394& -0.4121& -0.4121& -0.4121\\
               0   & -0.3848& -0.4364& -0.4879& -0.6152& -0.5879& -0.497 & -0.497 & -0.5061& -0.5333& -0.5606& -0.5879& -0.5879& -0.5879\\
               0   &  0.0515& -0.5636& -0.1788& -0.0515& -0.0788& -0.1697& -0.1697& -0.1606& -0.1333& -0.1061& -0.0788& -0.0788& -0.0788\\
               0   &  0.103 & -0.1273& -0.3576& -0.103 & -0.1576& -0.3394& -0.3394& -0.3212& -0.2667& -0.2121& -0.1576& -0.1576& -0.1576\\
               0   &  0.2303&  0.1273&  0.0242& -0.2303& -0.1758&  0.0061& 0.0061& -0.0121& -0.0667& -0.1212& -0.1758& -0.1758& -0.1758\\
               0   &  0.0515&  0.4364& -0.1788& -0.0515& -0.0788& -0.1697& -0.1697& -0.1606& -0.1333& -0.1061& -0.0788& -0.0788& -0.0788\\
               0   &  0.1273&  0.2545&  0.3818& -0.1273& -0.0182&  0.3455& 0.3455&  0.3091&  0.2   &  0.0909& -0.0182& -0.0182& -0.0182\\
               0   &  0.0091&  0.0182&  0.0273& -0.0091& -0.0727& -0.6182& -0.6182& -0.2636& -0.2   & -0.1364& -0.0727& -0.0727& -0.0727\\
               0   &  0.0182&  0.0364&  0.0545& -0.0182& -0.1455& -0.2364& -0.2364& -0.5273& -0.4   & -0.2727& -0.1455& -0.1455& -0.1455\\
               0   & -0.0273& -0.0545& -0.0818&  0.0273& -0.7818& -0.1455& -0.1455& -0.2091& -0.4   & -0.5909& -0.7818& -0.7818& -0.7818\\
               0   & -0.0273& -0.0545& -0.0818&  0.0273&  0.2182& -0.1455& -0.1455& -0.2091& -0.4   & -0.5909&  0.2182&  0.2182&  0.2182\\
               0   &  0   &  0   &  0   &  0   &  0   &  0   & 0   &  0   &  0   &  0   & -1.    & -1.    & -1.    \\
               0   &  0   &  0   &  0   &  0   &  0   &  0   & -1.    &  0   &  0   &  0   &  0   &  0   &  0   \\
               0   &  0.0091&  0.0182&  0.0273& -0.0091& -0.0727&  0.3818& 0.3818& -0.2636& -0.2   & -0.1364& -0.0727& -0.0727& -0.0727\\
               0   &  0.0273&  0.0545&  0.0818& -0.0273& -0.2182&  0.1455& 0.1455&  0.2091& -0.6   & -0.4091& -0.2182& -0.2182& -0.2182\\
               0   &  0.0273&  0.0545&  0.0818& -0.0273& -0.2182&  0.1455& 0.1455&  0.2091&  0.4   & -0.4091& -0.2182& -0.2182& -0.2182\\
               0   &  0   &  0   &  0   &  0   &  0   &  0   & 0   &  0   &  0   &  0   &  0   & -1.    & -1.    \\
               0   &  0   &  0   &  0   &  0   &  0   &  0   & 0   &  0   &  0   &  0   &  0   &  0   & -1.\\
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

