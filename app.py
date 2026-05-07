"""Streamlit GUI for Water Jug Puzzle Solver.

Provides visual interface with animated jug visualization and interactive slider.
"""

from typing import Optional
import streamlit as st
from water_jug_solver.solver import bfs_solve, can_solve
from water_jug_solver.formatter import format_solution, format_no_solution, simulate_solution
from water_jug_solver.models import ActionType

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
    """Render all jugs with proportional heights.
    
    Args:
        state: Current water levels.
        capacities: Maximum capacities.
        highlight_jugs: List of jug indices to highlight.
    """
    max_capacity = max(capacities) if capacities else 1
    num_jugs = len(capacities)
    
    cols = st.columns(num_jugs)
    for i in range(num_jugs):
        with cols[i]:
            color = COLORS[i % len(COLORS)]
            height = get_jug_height(capacities[i], max_capacity)
            
            if highlight_jugs and i in highlight_jugs:
                st.markdown(f"<p style='color: {color}; font-weight: bold;'>⬇️</p>", unsafe_allow_html=True)
            
            render_jug(state[i], capacities[i], f"Vaso {i}", color, height)


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
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Visualizzazione Vasi")
        jug_placeholder = st.empty()
    
    with col2:
        st.subheader("Dettagli Azione")
        info_placeholder = st.empty()
    
    # Solve logic
    if solve_button:
        if not can_solve(capacities, target):
            st.error(format_no_solution(target))
            return
        
        with st.spinner("Ricerca soluzione in corso..."):
            solution = bfs_solve(capacities, target)
        
        if solution is None:
            st.error(format_no_solution(target))
            return
        
        structured, readable = format_solution(solution, capacities)
        states = simulate_solution(solution, capacities)
        
        st.session_state.solution = structured
        st.session_state.states = states
        st.session_state.readable = readable
        st.session_state.current_step = 0
        
        st.success(f"✅ Soluzione trovata in {len(solution)} passi!")
    
    # Display solution with slider
    if st.session_state.solution is not None:
        solution = st.session_state.solution
        states = st.session_state.states
        readable = st.session_state.readable
        
        # Slider for navigation
        step = st.slider(
            "Naviga tra i passaggi",
            min_value=0,
            max_value=len(solution),
            value=st.session_state.current_step,
            key="step_slider"
        )
        st.session_state.current_step = step
        
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
        
        # Show all steps summary
        with st.expander("📋 Riepilogo completo"):
            for i, desc in enumerate(readable, 1):
                st.markdown(f"{i}. {desc}")
        
        st.info(f"🎯 Stato finale: {states[-1]}")


if __name__ == "__main__":
    main()
