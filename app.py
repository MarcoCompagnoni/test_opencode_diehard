"""Streamlit GUI for Water Jug Puzzle Solver.

Provides visual interface with jug visualization and solution display.
"""

from typing import Optional
import streamlit as st
import time

from water_jug_solver.solver import bfs_solve, can_solve
from water_jug_solver.formatter import format_solution, format_no_solution, simulate_solution
from water_jug_solver.models import ActionType


# Page config
st.set_page_config(
    page_title="Water Jug Puzzle Solver",
    page_icon="🧪",
    layout="wide"
)


def render_jug(level: int, capacity: int, jug_name: str, color: str = "#1f77b4") -> None:
    """Render a single jug visualization.
    
    Args:
        level: Current water level in the jug.
        capacity: Maximum capacity of the jug.
        jug_name: Name/label for the jug.
        color: Color for the water fill.
    """
    height = 200
    width = 80
    fill_height = int((level / capacity) * height) if capacity > 0 else 0
    
    st.markdown(
        f"""
        <div style="text-align: center;">
            <div style="
                position: relative;
                width: {width}px;
                height: {height}px;
                border: 3px solid #333;
                border-radius: 0 0 10px 10px;
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
                    transition: height 0.3s ease;
                "></div>
            </div>
            <p style="margin-top: 10px; font-weight: bold;">{jug_name}</p>
            <p style="color: #666;">{level} / {capacity}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_jugs_row(state: tuple[int, ...], capacities: list[int]) -> None:
    """Render all jugs in a row.
    
    Args:
        state: Current water levels for all jugs.
        capacities: Maximum capacities for all jugs.
    """
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
    
    cols = st.columns(len(capacities))
    for i, (level, capacity) in enumerate(zip(state, capacities)):
        with cols[i]:
            render_jug(level, capacity, f"Vaso {i}", colors[i % len(colors)])


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
        for i in range(num_jugs):
            cap = st.number_input(
                f"Capacità vaso {i}",
                min_value=1,
                value=[3, 5][i] if i < 2 else 1,
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
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Stato Attuale dei Vasi")
        initial_state = tuple([0] * len(capacities))
        jug_placeholder = st.empty()
        jug_placeholder.container()
        render_jugs_row(initial_state, capacities)
    
    with col2:
        st.subheader("Soluzione")
        solution_placeholder = st.empty()
        solution_placeholder.info("Premi 'Risolvi' per iniziare.")
    
    # Solve logic
    if solve_button:
        # Check mathematical feasibility
        if not can_solve(capacities, target):
            solution_placeholder.error(format_no_solution(target))
            return
        
        # Solve with BFS
        with st.spinner("Ricerca soluzione in corso..."):
            solution = bfs_solve(capacities, target)
        
        if solution is None:
            solution_placeholder.error(format_no_solution(target))
            return
        
        # Format solution
        structured, readable = format_solution(solution, capacities)
        states = simulate_solution(solution, capacities)
        
        # Display solution info
        solution_placeholder.success(f"✅ Soluzione trovata in {len(solution)} passi!")
        
        # Animated visualization
        st.subheader("Animazione Soluzione")
        
        for i, (action, description) in enumerate(zip(structured, readable)):
            state_before = states[i]
            state_after = states[i + 1]
            
            # Show step
            with st.container():
                col_a, col_b, col_c = st.columns([1, 2, 1])
                
                with col_a:
                    st.markdown(f"**Passo {i + 1}**")
                    st.caption(description)
                
                with col_b:
                    render_jugs_row(state_after, capacities)
                
                with col_c:
                    if i < len(structured) - 1:
                        st.markdown("⬇️")
            
            time.sleep(0.8)  # Animation delay
        
        # Final state
        st.markdown("---")
        st.subheader("Riepilogo Passi")
        for i, desc in enumerate(readable, 1):
            st.markdown(f"{i}. {desc}")
        
        st.markdown("---")
        st.info(f"🎯 Stato finale: {states[-1]}")


if __name__ == "__main__":
    main()
