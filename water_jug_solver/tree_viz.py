"""BFS Tree visualization for Water Jug Puzzle.

Generates Graphviz visualization of BFS exploration tree.
"""

from typing import Optional
from graphviz import Digraph

from water_jug_solver.models import JugState


def create_bfs_tree(
    visited_states: list[JugState],
    solution_path: list[JugState],
    capacities: list[int],
    target: int
) -> Digraph:
    """Create Graphviz visualization of BFS tree.
    
    Args:
        visited_states: All states visited during BFS.
        solution_path: States in the solution path.
        capacities: Jug capacities.
        target: Target water level.
        
    Returns:
        Graphviz Digraph object with 3-color scheme:
        - Gray: visited states not in solution
        - Red: states in the solution path
        - Blue: target state (contains target amount)
    """
    dot = Digraph(comment='BFS Tree')
    dot.attr(rankdir='TB', splines='ortho')
    dot.attr('node', shape='circle', style='filled', fontname='Arial')
    dot.attr('edge', fontname='Arial', fontsize='10')
    
    # Convert solution path to set for quick lookup
    solution_set = set(solution_path)
    
    # Find target state (last state in solution that contains target)
    target_state = None
    for state in reversed(solution_path):
        if target in state:
            target_state = state
            break
    
    # Color mapping
    for state in visited_states:
        state_str = str(state)
        label = '\n'.join([f'J{i}: {state[i]}' for i in range(len(state))])
        
        if state == target_state:
            # Target state - blue
            dot.node(state_str, label=label, fillcolor='#1f77b4', fontcolor='white')
        elif state in solution_set:
            # Solution path (non-target) - red
            dot.node(state_str, label=label, fillcolor='#d62728', fontcolor='white')
        else:
            # Visited but not in solution - gray
            dot.node(state_str, label=label, fillcolor='#7f7f7f', fontcolor='white')
    
    # Add edges (solution edges in red, or blue for target edge)
    for i in range(len(solution_path) - 1):
        edge_color = '#d62728'  # Red for solution path
        if solution_path[i + 1] == target_state:
            edge_color = '#1f77b4'  # Blue for edge leading to target
        dot.edge(str(solution_path[i]), str(solution_path[i + 1]), color=edge_color, penwidth='2')
    
    return dot


def save_tree(tree: Digraph, output_path: str = 'bfs_tree') -> None:
    """Save tree visualization to file.
    
    Args:
        tree: Graphviz Digraph object.
        output_path: Path to save the output (without extension).
    """
    tree.render(output_path, format='png', cleanup=True)
