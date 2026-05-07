# Water Jug Puzzle Solver

BFS-based solver for the classic water jug problem with mathematical pre-check.

## Description

This project solves the classic Water Jug Puzzle (popularized by the movie Die Hard 3) using a Breadth-First Search (BFS) algorithm. Given N jugs with specific capacities and a target amount of water, the solver finds the shortest sequence of actions (fill, empty, pour) to measure exactly the target amount.

The solver includes a mathematical pre-check using the Greatest Common Divisor (GCD) to quickly determine if a solution exists before running the BFS algorithm.

## Features

- **N-jug support**: Works with any number of jugs (not just 2)
- **BFS algorithm**: Guarantees the shortest solution path
- **GCD pre-check**: Mathematical verification of solvability before searching
- **Multiple output formats**: Structured actions and human-readable descriptions
- **BFS Tree Visualization**: Real parent-child hierarchy visualization using Graphviz with 2-color scheme:
   - **Light Red**: States visited during BFS exploration
   - **Blue**: States in the solution path (highlighted with thicker edges)
- **Deployment Optimization**: Uses Streamlit caching (`@st.cache_data`) for high-performance result retrieval and smooth UI experience. Includes a **ValueError fix** for production: implemented forced cache invalidation by renaming cached functions to prevent crashes from stale data structures.
- **Animated Streamlit GUI**: Interactive web interface with:
   - **Proportional jug scaling**: Jug height dynamically adjusted based on capacity
   - **Bottom-aligned jugs**: Jugs visually aligned to the bottom (like on a table) using spacer divs
   - **Interactive slider**: Navigate through solution steps with real-time visualization
   - **Play button**: Auto-play animation with 2.0s pause between steps for better visibility
   - **New Game button**: Reset and start a new puzzle instantly
   - **Initial jug display**: Shows empty jugs with selected capacities before solving
   - **Action animation**: Color-coded animations for FILL (🔵), EMPTY (🟠), and POUR (🟢) operations
   - **Step details**: Display action description and state transitions for each step
- **BFS Tree expandable view**: Interactive Graphviz tree visualization showing the actual search hierarchy
   - **Optimization**: Automatic node limiting (max 100 nodes) to maintain readability on large search spaces
- **Complete solution summary**: Expandable view with all steps
   - **Input change detection**: Automatically resets solution when jug capacities or target change (prevents IndexError)
- **Enhanced solver functions**: 
   - `bfs_solve_with_visited()`: Returns solution path, visited states, and solution states for visualization
   - `simulate_solution()`: Simulates and returns all intermediate states
- **Type hints and docstrings**: Google-style docstrings with full type annotations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start from PyCharm

To launch the Streamlit GUI directly from PyCharm:
1. Open `run_gui.py` in PyCharm
2. Right-click on the file and select "Run 'run_gui.py'"
3. The Streamlit web interface will open in your browser

### CLI Usage (via Python)

```python
from water_jug_solver.solver import bfs_solve, can_solve

# Check if solvable
capacities = [3, 5]
target = 4
if can_solve(capacities, target):
    solution = bfs_solve(capacities, target)
    print(f"Solution: {solution}")
else:
    print("No solution exists")
```

### CLI Entry Point (main.py)

```bash
python water_jug_solver/main.py --capacities 3 5 --target 4
```

### Running Tests

```bash
pytest test_solver.py -v
```

### Streamlit GUI (Alternative Launch)

```bash
streamlit run water_jug_solver/app.py
```

## Project Structure

```
test_opencode_diehard/
├── water_jug_solver/
│   ├── __init__.py
│   ├── models.py           # State, Action, ActionType enum
│   ├── solver.py           # BFS + pre-check GCD, bfs_solve_with_visited, simulate_solution
│   ├── formatter.py        # Output formatting (structured + readable)
│   ├── tree_viz.py         # BFS tree visualization (Graphviz, 3-color scheme)
│   ├── main.py             # CLI entry point
│   └── app.py              # Streamlit GUI with animated visualization + BFS tree
├── run_gui.py              # Launcher for Streamlit GUI (PyCharm)
├── test_solver.py          # Comprehensive test suite
├── requirements.txt        # Project dependencies
├── PLAN.md                 # Detailed implementation plan
└── README.md               # This file
```

## Implementation Details

### Core Modules

- **models.py**: Defines `JugState` (immutable tuple of water levels), `ActionType` enum (FILL, EMPTY, POUR), and `Action` type aliases. Documented with Google-style docstrings and type hints.

- **solver.py**: Implements the BFS algorithm with:
  - `can_solve()`: GCD-based pre-check for solvability
  - `bfs_solve()`: Main BFS solver returning action sequence
  - `bfs_solve_with_visited()`: Enhanced solver returning (actions, visited_states, solution_states) for visualization
  - `simulate_solution()`: Simulates solution and returns all intermediate states
  - `get_neighbors()`: Generates all valid next states from current state
  - `reconstruct_path()`: Rebuilds action sequence from BFS tree

- **tree_viz.py**: BFS tree visualization module with:
  - `create_bfs_tree()`: Creates Graphviz Digraph with real parent-child relationships and 2-color scheme (light red=visited, blue=solution)
  - Automatic complexity management: ensures solution path is always visible while limiting total nodes for performance.

Both modules are fully documented with Google-style docstrings and comprehensive type hints.

### Production Robustness

- **Cache Invalidation**: To prevent `ValueError` during deployment (often caused by schema changes in cached objects), the application uses a function renaming strategy. This forces Streamlit to invalidate old cache entries, ensuring the app always runs with the latest data structures.

### Mathematical Foundation

A solution exists if and only if:
```
GCD(capacities) divides target  AND  target <= max(capacities)
```

The invariant is that the total water in any reachable state is a multiple of the GCD of all jug capacities.

## Dependencies

- `streamlit` - Web GUI framework with animated visualization and BFS tree display
- `graphviz` - BFS tree visualization (integrated with Streamlit)
- `pytest` - Testing framework

## License

[Add license information as needed]
