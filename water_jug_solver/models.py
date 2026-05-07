"""Models for Water Jug Puzzle Solver.

Contains state, action, and type definitions.
"""

from enum import Enum
from typing import Union

class ActionType(Enum):
    """Enum for possible actions on jugs.
    
    Attributes:
        FILL: Fill a jug to its full capacity.
        EMPTY: Empty a jug completely.
        POUR: Pour water from one jug to another.
    """
    FILL = "fill"
    EMPTY = "empty"
    POUR = "pour"

# Type alias for immutable jug state (water levels per jug)
JugState = tuple[int, ...]

# Type alias for actions:
# - Fill/Empty: (ActionType, jug_index: int)
# - Pour: (ActionType, from_jug: int, to_jug: int)
Action = tuple[Union[ActionType, int], ...]
