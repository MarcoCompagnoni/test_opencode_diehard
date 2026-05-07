# Water Jug Puzzle Solver

BFS-based solver for the classic water jug problem with mathematical pre-check.

## Description

This project solves the classic Water Jug Puzzle (popularized by the movie Die Hard 3) using a Breadth-First Search (BFS) algorithm. Given N jugs with specific capacities and a target amount of water, the solver finds the shortest sequence of actions (fill, empty, pour) to measure exactly the target amount.

The solver includes a mathematical pre-check using the Greatest Common Divisor (GCD) to quickly determine if a solution exists before running the BFS algorithm.

## Features

- **N-jug support**: Works with any number of jugs (not just 2)
- **BFS algorithm**: Guarantees the shortest solution path
- **GCD pre-check**: Mathematical verification of solvability before searching
- **Multiple output formats**: Structured actions and human-readable descriptions (planned)
- **Streamlit GUI**: Interactive web interface with real-time visualization (planned)
- **Type hints and docstrings**: Google-style docstrings with full type annotations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Current CLI Usage (via Python)

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

### Running Tests

```bash
pytest test_solver.py -v
```

### Future Streamlit App

```bash
streamlit run water_jug_solver/app.py
```

## Project Structure

```
test_opencode_diehard/
├── water_jug_solver/
│   ├── __init__.py
│   ├── models.py           # State, Action, ActionType enum
│   ├── solver.py           # BFS + pre-check GCD, path reconstruction
│   ├── formatter.py        # Output formatting (planned)
│   ├── visualization.py    # Jug rendering for Streamlit (planned)
│   ├── tree_viz.py         # BFS tree visualization (planned)
│   └── app.py              # Streamlit GUI (planned)
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
  - `get_neighbors()`: Generates all valid next states from current state
  - `reconstruct_path()`: Rebuilds action sequence from BFS tree

Both modules are fully documented with Google-style docstrings and comprehensive type hints.

### Mathematical Foundation

A solution exists if and only if:
```
GCD(capacities) divides target  AND  target <= max(capacities)
```

The invariant is that the total water in any reachable state is a multiple of the GCD of all jug capacities.

## Dependencies

- `streamlit` - Web GUI framework (planned)
- `graphviz` - BFS tree visualization (planned)
- `pytest` - Testing framework

## License

[Add license information as needed]
