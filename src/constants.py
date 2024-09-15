from enum import Enum

from gurobipy import Model, quicksum, Var

MAX_FLOW: float = 99999.00

class NetworkModel(Enum):
    """Network model"""

    SINGLE_BUS = 1
    """All generation and load elements are connected to a single bus (node). No lines (branches)
    are represented."""

    FLUXES = 2
    """Transmission elements are represented, their limits and power balances at each node are
    enforced. However, power flows in the transmission elements are not functions of voltage angles.
    """

    B_THETA = 3
    """A formulation of the common DC model where voltage angles are explicitly represented.
    In addition to the constraints in `FLUXES`, in this model, flows in transmission lines are
    explicitly written as functions of the voltage angles at the endpoint buses."""

    PTDF = 4
    """A formulation of the DC model that is equivalent (numerical tolerances observed) to `B_theta`
    but where voltage angles are not explicitly represented. Instead, flows in the transmission
    lines are written as functions of the power injections at the network buses. Similarly, a global
    power balance is enforced for each period instead of an explicit bus-based balance."""

    @classmethod
    def _missing_(cls, value):
        raise ValueError(f"Valid types: {(', '.join([repr(member.name) for member in cls]),)}")


class NetworkSlacks(Enum):
    """
        UC models generally include slack variables that account for imbalances in
        generation-load. The imbalances are due to either a shortage or surplus of generation or
        to transmission limits. The attributes of this class are options of which slacks are to
        be included, if any.
    """

    BUS_SLACKS = 1
    """Include generation shortage and generation surplus slacks to the power balance equation
    of each node of the network."""

    LINE_SLACKS = 2
    """Include one slack variable to each limit of each transmission line. When using this option
    and the B-theta formulation, the flow limits are no longer enforced through the bounds on the
    flow variables. Instead, new constraints are added to the model, one for each bound of each
    line whose bounds can be active.
    """

    BUS_AND_LINE_SLACKS = 3
    """Include both bus and line slacks."""

    NO_SLACKS = 4
    """No slacks included in the model."""

    @classmethod
    def _missing_(cls, value):
        raise ValueError(f"Valid types: {(', '.join([repr(member.name) for member in cls]),)}")
