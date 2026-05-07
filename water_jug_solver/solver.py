"""Solver for Water Jug Puzzle using BFS algorithm.

Includes mathematical pre-check (GCD) and path reconstruction.
"""

from collections import deque
from typing import Optional
from math import gcd
from functools import reduce

from water_jug_solver.models import JugState, Action, ActionType

def gcd_list(capacities: list[int]) -> int:
    """Calculate GCD of a list of integers.
    
    Args:
        capacities: List of integers (jug capacities).
        
    Returns:
        GCD of all elements in the list.
    """
    return reduce(gcd, capacities)


def can_solve(capacities: list[int], target: int) -> bool:
    """Check if the target is solvable mathematically.
    
    Args:
        capacities: List of jug capacities.
        target: Target water level to measure.
        
    Returns:
        True if solvable, False otherwise.
    """
    if not capacities:
        return False
    if target > max(capacities):
        return False
    return target % gcd_list(capacities) == 0


def get_neighbors(state: JugState, capacities: list[int]) -> list[tuple[JugState, Action]]:
    """Generate all possible next states and actions from current state.
    
    Args:
        state: Current water levels per jug.
        capacities: Maximum capacities per jug.
        
    Returns:
        List of (next_state, action) tuples.
    """
    neighbors = []
    num_jugs = len(capacities)
    
    for i in range(num_jugs):
        # FILL action
        if state[i] < capacities[i]:
            new_state = list(state)
            new_state[i] = capacities[i]
            neighbors.append((tuple(new_state), (ActionType.FILL, i)))
        
        # EMPTY action
        if state[i] > 0:
            new_state = list(state)
            new_state[i] = 0
            neighbors.append((tuple(new_state), (ActionType.EMPTY, i)))
        
        # POUR action: from jug i to jug j
        for j in range(num_jugs):
            if i == j:
                continue
            if state[i] > 0 and state[j] < capacities[j]:
                transfer = min(state[i], capacities[j] - state[j])
                new_state = list(state)
                new_state[i] -= transfer
                new_state[j] += transfer
                neighbors.append((tuple(new_state), (ActionType.POUR, i, j)))
    
    return neighbors

def reconstruct_path(
    goal_state: JugState,
    parent: dict[JugState, Optional[JugState]],
    action_map: dict[JugState, Optional[Action]]
) -> list[Action]:
    """Reconstruct the action path from initial state to goal state.
    
    Args:
        goal_state: Target state where solution was found.
        parent: Dictionary mapping state to its parent state.
        action_map: Dictionary mapping state to the action that led to it.
        
    Returns:
        List of actions in order from initial to goal.
    """
    path = []
    current = goal_state
    
    while parent.get(current) is not None:
        path.append(action_map[current])
        current = parent[current]
    
    path.reverse()
    return path

def bfs_solve(capacities: list[int], target: int) -> Optional[list[Action]]:
    """Solve Water Jug Puzzle using BFS algorithm.
    
    Args:
        capacities: List of jug capacities.
        target: Target water level to measure.
        
    Returns:
        List of actions to reach target, or None if unsolvable.
    """
    if not can_solve(capacities, target):
        return None
    
    initial_state: JugState = tuple([0] * len(capacities))
    queue = deque([initial_state])
    visited = {initial_state}
    parent = {initial_state: None}
    action_map = {initial_state: None}
    
    while queue:
        current = queue.popleft()
        
        # Check if target is reached
        if target in current:
            return reconstruct_path(current, parent, action_map)
        
        for next_state, action in get_neighbors(current, capacities):
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = current
                action_map[next_state] = action
                queue.append(next_state)
    
    return None  # No solution found
