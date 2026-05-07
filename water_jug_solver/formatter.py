"""Formatter for Water Jug Puzzle solution output.

Provides structured and human-readable formatting of solution steps.
"""

from typing import Optional, Tuple
from water_jug_solver.models import Action, ActionType


def format_action(action: Action, capacities: list[int]) -> str:
    """Format a single action into human-readable string.
    
    Args:
        action: The action tuple to format.
        capacities: List of jug capacities for context.
        
    Returns:
        Human-readable description of the action.
    """
    action_type = action[0]
    
    if action_type == ActionType.FILL:
        jug_index = action[1]
        return f"Riempire vaso {jug_index} (capacità: {capacities[jug_index]})"
    elif action_type == ActionType.EMPTY:
        jug_index = action[1]
        return f"Svuotare vaso {jug_index}"
    elif action_type == ActionType.POUR:
        from_jug = action[1]
        to_jug = action[2]
        return f"Travasare vaso {from_jug} → vaso {to_jug}"
    
    return "Azione sconosciuta"


def format_solution(
    actions: list[Action],
    capacities: list[int]
) -> Tuple[list[Action], list[str]]:
    """Format the complete solution into structured and readable formats.
    
    Args:
        actions: List of actions in the solution path.
        capacities: List of jug capacities.
        
    Returns:
        Tuple of (structured_actions, readable_descriptions).
    """
    readable = [format_action(action, capacities) for action in actions]
    return actions, readable


def format_no_solution(target: int) -> str:
    """Format error message when no solution exists.
    
    Args:
        target: The target amount that cannot be measured.
        
    Returns:
        Error message string.
    """
    return f"Errore: nessuna soluzione esiste per raggiungere il target {target}."


def simulate_solution(
    actions: list[Action],
    capacities: list[int]
) -> list[tuple[int, ...]]:
    """Simulate the solution and return all intermediate states.
    
    Args:
        actions: List of actions to execute.
        capacities: List of jug capacities.
        
    Returns:
        List of states after each action, starting from initial state.
    """
    state = tuple([0] * len(capacities))
    states = [state]
    
    for action in actions:
        action_type = action[0]
        current = list(state)
        
        if action_type == ActionType.FILL:
            jug_index = action[1]
            current[jug_index] = capacities[jug_index]
        elif action_type == ActionType.EMPTY:
            jug_index = action[1]
            current[jug_index] = 0
        elif action_type == ActionType.POUR:
            from_jug = action[1]
            to_jug = action[2]
            transfer = min(current[from_jug], capacities[to_jug] - current[to_jug])
            current[from_jug] -= transfer
            current[to_jug] += transfer
        
        state = tuple(current)
        states.append(state)
    
    return states
