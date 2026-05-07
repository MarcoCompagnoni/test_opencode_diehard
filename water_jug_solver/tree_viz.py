"""BFS Tree visualization for Water Jug Puzzle.

Generates Graphviz visualization of BFS exploration tree with parent-child relationships.
"""

from typing import Optional
from graphviz import Digraph
from water_jug_solver.models import JugState


def create_bfs_tree(
    visited_states: list[JugState],
    solution_path: list[JugState],
    parent_map: dict[JugState, Optional[JugState]],
    capacities: list[int],
    target: int
) -> Digraph:
    """Create a real BFS tree visualization with parent-child links.
    
    Args:
        visited_states: All states visited during BFS.
        solution_path: States in the solution path.
        parent_map: Map of state to its parent state.
        capacities: Jug capacities.
        target: Target water level.
        
    Returns:
        Graphviz Digraph object.
    """
    # Limit visualization if tree is too large to prevent "merda atomica"
    MAX_NODES = 100
    if len(visited_states) > MAX_NODES:
        visited_states = visited_states[:MAX_NODES]
        # Ensure solution nodes are included even if beyond limit
        for state in solution_path:
            if state not in visited_states:
                visited_states.append(state)

    dot = Digraph(comment='BFS Search Tree')
    
    # improved layout settings
    dot.attr(rankdir='TB', size='10,10', ratio='fill')
    dot.attr('node', shape='box', style='filled,rounded', fontname='Helvetica', fontsize='10')
    dot.attr('edge', arrowhead='vee', arrowsize='0.7', color='#cccccc')
    
    solution_set = set(solution_path)
    
    for state in visited_states:
        state_str = str(state)
        # Compact label: (0,3,5)
        label = f"{state}"
        
        # Color nodes based on role
        if state in solution_set:
            fill = '#1f77b4' # Blue
            font = 'white'
        else:
            fill = '#ffcccc' # Light Red (traversed)
            font = 'black'
            
        # Highlight initial state
        if all(s == 0 for state_val in state for s in [state_val]): # Simplified check for (0,0,...)
             if sum(state) == 0:
                dot.attr('node', penwidth='3')
             
        dot.node(state_str, label=label, fillcolor=fill, fontcolor=font, color=fill)

    # Add ALL edges from parent map
    for child, parent in parent_map.items():
        if child in visited_states and parent in visited_states:
            color = '#1f77b4' if (child in solution_set and parent in solution_set) else '#cccccc'
            width = '2.0' if (child in solution_set and parent in solution_set) else '1.0'
            dot.edge(str(parent), str(child), color=color, penwidth=width)
    
    return dot
