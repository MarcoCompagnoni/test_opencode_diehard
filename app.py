"""Streamlit GUI for Water Jug Puzzle Solver.

Provides visual interface with animated jug visualization, interactive slider, and BFS tree.
"""

import streamlit as st
from water_jug_solver.solver import bfs_solve, bfs_solve_with_visited, can_solve
from water_jug_solver.formatter import format_solution, format_no_solution
from water_jug_solver.models import ActionType
from water_jug_solver.tree_viz import create_bfs_tree
from typing import Optional

# Page config
st.set_page_config(
    page_title="Water Jug Puzzle Solver",
    page_icon="🧪",
    layout="wide"
)

# Constants
MAX_HEIGHT = 300
JUG_WIDTH = 100
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]


def get_jug_height(capacity: int, max_capacity: int) -> int:
    """Calculate jug height proportional to its capacity.
    
    Args:
        capacity: Capacity of the jug.
        max_capacity: Maximum capacity among all jugs.
        
    Returns:
        Height in pixels proportional to capacity.
    """
    if max_capacity == 0:
        return 100
    return int((capacity / max_capacity) * MAX_HEIGHT)


def render_jug(
    level: int,
    capacity: int,
    jug_name: str,
    color: str,
    height: int
) -> None:
    """Render a single jug with proportional height.
    
    Args:
        level: Current water level.
        capacity: Maximum capacity.
        jug_name: Label for the jug.
        color: Water color.
        height: Jug height in pixels.
    """
    fill_height = int((level / capacity) * height) if capacity > 0 else 0
    
    st.markdown(
        f"""
        <div style="text-align: center;">
            <div style="
                position: relative;
                width: {JUG_WIDTH}px;
                height: {height}px;
                border: 3px solid #333;
                border-radius: 0 0 15px 15px;
                margin: 0 auto;
                background: #f8f9fa;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    bottom: 0;
                    width: 100%;
                    height: {fill_height}px;
                    background: {color};
                    transition: height 0.5s ease;
                "></div>
            </div>
            <p style="margin-top: 10px; font-weight: bold;">{jug_name}</p>
            <p style="color: #666; font-size: 14px;">{level} / {capacity}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_jugs_row(
    state: tuple[int, ...],
    capacities: list[int],
    highlight_jugs: Optional[list[int]] = None
) -> None:
    """Render all jugs with proportional heights, aligned to bottom.
    
    Args:
        state: Current water levels.
        capacities: Maximum capacities.
        highlight_jugs: List of jug indices to highlight.
    """
    max_capacity = max(capacities) if capacities else 1
    max_height = get_jug_height(max_capacity, max_capacity)
    num_jugs = len(capacities)
    
    cols = st.columns(num_jugs)
    for i in range(num_jugs):
        with cols[i]:
            height = get_jug_height(capacities[i], max_capacity)
            # Spacer to align jugs to bottom
            spacer_height = max_height - height
            if spacer_height > 0:
                st.markdown(f'<div style="height: {spacer_height}px;"></div>', unsafe_allow_html=True)
            render_jug(state[i], capacities[i], f"Vaso {i}", COLORS[i % len(COLORS)], height)


def render_action_animation(
    action: tuple,
    state_before: tuple[int, ...],
    state_after: tuple[int, ...],
    capacities: list[int]
) -> None:
    """Render animation for a single action.
    
    Args:
        action: The action tuple.
        state_before: State before action.
        state_after: State after action.
        capacities: Jug capacities.
    """
    action_type = action[0]
    
    if action_type == ActionType.FILL:
        jug_idx = action[1]
        st.info(f"🔵 Riempimento vaso {jug_idx}...")
        render_jugs_row(state_after, capacities, highlight_jugs=[jug_idx])
        
    elif action_type == ActionType.EMPTY:
        jug_idx = action[1]
        st.info(f"🟠 Svuotamento vaso {jug_idx}...")
        render_jugs_row(state_after, capacities, highlight_jugs=[jug_idx])
        
    elif action_type == ActionType.POUR:
        from_jug = action[1]
        to_jug = action[2]
        st.info(f"🟢 Travaso da vaso {from_jug} a vaso {to_jug}...")
        render_jugs_row(state_after, capacities, highlight_jugs=[from_jug, to_jug])


def auto_play_solution(
    solution: list,
    states: list,
    readable: list,
    capacities: list[int]
) -> None:
    """Auto-play the solution with smooth animation.
    
    Args:
        solution: List of actions.
        states: List of states during solution.
        readable: List of readable action descriptions.
        capacities: Jug capacities.
    """
    total_steps = len(solution)
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for step in range(total_steps + 1):
        if step == 0:
            # Initial state
            st.session_state.current_step = 0
            with st.session_state.jug_placeholder.container():
                render_jugs_row(states[0], capacities)
            with st.session_state.info_placeholder.container():
                st.info("Stato iniziale: tutti i vasi vuoti")
        else:
            action = solution[step - 1]
            state_before = states[step - 1]
            state_after = states[step]
            
            st.session_state.current_step = step
            with st.session_state.jug_placeholder.container():
                render_action_animation(action, state_before, state_after, capacities)
            with st.session_state.info_placeholder.container():
                st.markdown(f"**Passo {step}**")
                st.markdown(f"**Azione:** {readable[step - 1]}")
                st.markdown(f"**Prima:** {state_before}")
                st.markdown(f"**Dopo:** {state_after}")
        
        # Update progress
        progress_bar.progress((step + 1) / (total_steps + 1))
        status_text.text(f"Passo {step}/{total_steps}")
        
        if step < total_steps:
            import time
            time.sleep(2.0)  # Longer pause for better visibility
    
    status_text.text("✅ Soluzione completata!")
    st.balloons()


@st.cache_data
def cached_solve(capacities: list[int], target: int):
    """Wrapper function to cache BFS results."""
    return bfs_solve_with_visited(capacities, target)


def main() -> None:
    """Main Streamlit app."""
    st.title("🧪 Water Jug Puzzle Solver")
    st.markdown("---")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Configurazione")
        
        num_jugs = st.number_input(
            "Numero di vasi",
            min_value=1,
            max_value=6,
            value=2,
            step=1
        )
        
        st.subheader("Capacità dei vasi")
        capacities = []
        default_caps = [3, 5, 8, 11, 13, 15]
        for i in range(num_jugs):
            cap = st.number_input(
                f"Capacità vaso {i}",
                min_value=1,
                value=default_caps[i] if i < len(default_caps) else 1,
                step=1,
                key=f"cap_{i}"
            )
            capacities.append(cap)
        
        target = st.number_input(
            "Target (acqua da misurare)",
            min_value=0,
            value=4,
            step=1
        )
        
        st.markdown("---")
        solve_button = st.button("🔍 Risolvi", type="primary", use_container_width=True)
    
    # Initialize session state
    if "solution" not in st.session_state:
        st.session_state.solution = None
        st.session_state.states = None
        st.session_state.readable = None
        st.session_state.current_step = 0
        st.session_state.auto_play = False
        st.session_state.last_capacities = None
        st.session_state.last_target = None
        st.session_state.parent_map = None
    
    # Check if inputs changed, reset solution if needed
    inputs_changed = (
        st.session_state.last_capacities != capacities or
        st.session_state.last_target != target
    )
    if inputs_changed and st.session_state.solution is not None:
        st.session_state.solution = None
        st.session_state.states = None
        st.session_state.readable = None
        st.session_state.current_step = 0
        st.session_state.parent_map = None
    
    # Update tracked inputs
    st.session_state.last_capacities = capacities.copy()
    st.session_state.last_target = target
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Visualizzazione Vasi")
        jug_placeholder = st.empty()
        st.session_state.jug_placeholder = jug_placeholder
    
    with col2:
        st.subheader("Dettagli Azione")
        info_placeholder = st.empty()
        st.session_state.info_placeholder = info_placeholder
    
    # Show initial jugs with current capacities (before solving)
    if st.session_state.solution is None:
        initial_state = tuple([0] * len(capacities))
        with jug_placeholder.container():
            render_jugs_row(initial_state, capacities)
    
    # Solve logic
    if solve_button:
        if not can_solve(capacities, target):
            st.error(format_no_solution(target))
            return
        
        with st.spinner("Ricerca soluzione in corso..."):
            result = cached_solve(capacities, target)
        
        if result[0] is None:
            st.error(format_no_solution(target))
            return
        
        solution, visited, solution_states, parent_map = result
        structured, readable = format_solution(solution, capacities)
        
        st.session_state.solution = structured
        st.session_state.states = solution_states
        st.session_state.readable = readable
        st.session_state.visited = visited
        st.session_state.solution_states = solution_states
        st.session_state.parent_map = parent_map
        st.session_state.current_step = 0
        
        st.success(f"✅ Soluzione trovata in {len(solution)} passi!")
    
    # Display solution with slider and play button
    if st.session_state.solution is not None:
        solution = st.session_state.solution
        states = st.session_state.states
        readable = st.session_state.readable
        visited = st.session_state.get('visited', [])
        solution_states = st.session_state.get('solution_states', [])
        parent_map = st.session_state.get('parent_map', {})
        
        # Controls: slider, play button, new game button
        col_play, col_slider, col_new = st.columns([1, 3, 1])
        with col_play:
            play_button = st.button("▶️ Play", type="secondary", use_container_width=True)
        with col_slider:
            step = st.slider(
                "Naviga tra i passaggi",
                min_value=0,
                max_value=len(solution),
                value=st.session_state.current_step,
                key="step_slider"
            )
        with col_new:
            new_game = st.button("🔄 Nuova Partita", type="primary", use_container_width=True)
        
        # New game logic
        if new_game:
            st.session_state.solution = None
            st.session_state.states = None
            st.session_state.readable = None
            st.session_state.visited = None
            st.session_state.solution_states = None
            st.session_state.parent_map = None
            st.session_state.current_step = 0
            st.rerun()
        
        st.session_state.current_step = step
        
        # Auto-play logic
        if play_button:
            auto_play_solution(solution, states, readable, capacities)
            return
        
        # Display current state
        if step == 0:
            # Initial state
            with jug_placeholder.container():
                render_jugs_row(states[0], capacities)
            with info_placeholder.container():
                st.info("Stato iniziale: tutti i vasi vuoti")
        else:
            action = solution[step - 1]
            state_before = states[step - 1]
            state_after = states[step]
            
            with jug_placeholder.container():
                render_action_animation(action, state_before, state_after, capacities)
            
            with info_placeholder.container():
                st.markdown(f"**Passo {step}**")
                st.markdown(f"**Azione:** {readable[step - 1]}")
                st.markdown(f"**Prima:** {state_before}")
                st.markdown(f"**Dopo:** {state_after}")
        
        # BFS Tree Visualization
        if visited and solution_states and parent_map:
            with st.expander("🌳 Albero BFS", expanded=False):
                st.caption("Rosso: stati esplorati | Blu: percorso soluzione")
                try:
                    tree = create_bfs_tree(visited, solution_states, parent_map, capacities, target)
                    st.graphviz_chart(tree)
                except Exception as e:
                    st.warning(f"Impossibile generare l'albero: {e}")
        
        # Show all steps summary
        with st.expander("📋 Riepilogo completo"):
            for i, desc in enumerate(readable, 1):
                st.markdown(f"{i}. {desc}")
        
        st.info(f"🎯 Stato finale: {states[-1]}")


if __name__ == "__main__":
    main()
